#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
probe_fisher.py — Fisher-Metric Probe v4
========================================

INSTRUMENT PUR. Implemente les observables geles par PREREGISTRATION_v4.md
(commit de gel 4e9683efead2fafea26b26ce2d37611e97f69269). Ne produit AUCUN
verdict : analysis_v4.py applique les seuils geles apres coup. Sortie = JSON.

Pour chaque enonce s et chaque couche l (l = 0..L, embeddings incluses) :

  h(s,l)   = etat cache du DERNIER token (residual stream)
  logits   = W_u h + b_u   -- logit-lens BRUT : unembedding du modele, SANS
                              LayerNorm finale (gele ; la forme close de
                              Mabrok Prop. 5.2 est exacte sous cette condition)
  p        = softmax(logits)
  g(h)     = W_u^T (diag(p) - p p^T) W_u          (d x d, PSD)
  O_rank   = exp(-sum_i q_i log q_i),  q_i = lam_i / sum_j lam_j
  O_vol    = 0.5 * sum_{i=1..k} log lam_i          (k = 50, gele)
  O_aniso  = lam_1 / sum_j lam_j
  NLL(s,l) = moyenne sur les positions t de -log p_l(x_{t+1} | lens couche l)

Cas particulier : OPT-350m decode via project_out (hidden 1024 -> 512) avant
lm_head ; l'unembedding effectif est W_u = lm_head.weight @ project_out.weight
(rang de g <= 512 pour ce modele, c'est une propriete du modele, pas un bug).

Numerique (n'affecte pas les definitions ci-dessus) :
  - flush-to-zero actif (torch.set_flush_denormal(True)) : la queue de la
    softmax contient des milliers de probabilites subnormales (<1.2e-38) qui
    declenchent l'assist microcode x86 et ralentissent les GEMM ~8-10x. Le
    FTZ les met a zero ; contribution aux valeurs propres <= ~1e-32, tres
    sous le bruit float32 (verifie : scalaires identiques a 1e-10 pres) ;
  - g est accumulee en float64 a partir de GEMMs float32 par blocs de
    vocabulaire (borne la memoire pour Bloom, vocab ~250k) ;
  - eigvalsh en float64 sur la matrice symetrisee ; valeurs propres clampees
    a 0 ; si une lam du top-k est <= 0, O_vol = null (JSON) et la valeur est
    exclue des moyennes de couche par analysis_v4.py ;
  - NLL indefinie (enonce d'un seul token) -> null.

--max-statements est un flag de DEBUG (pilote) uniquement : toute sortie
produite avec ce flag est un pilote au sens du skill preregistration
(gitignoree, non analysee).

Usage :
    python probe_fisher.py --model gpt2 --corpus claims.txt --out results/gpt2_fisher.json
"""

import argparse
import json
import hashlib
import time
from pathlib import Path
from datetime import datetime, timezone

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

FREEZE_COMMIT = "4e9683efead2fafea26b26ce2d37611e97f69269"


# --------------------------------------------------------------------------- #
# Unembedding
# --------------------------------------------------------------------------- #
def get_unembedding(model) -> dict[int, tuple[torch.Tensor, torch.Tensor | None]]:
    """Renvoie {dim_espace: (W_u (N, dim), b_u (N,) ou None)} : la decode-map
    du modele depuis CHAQUE espace de representation present dans
    hidden_states, SANS LayerNorm finale (logit-lens brut, gele).

    Cas standard (gpt2, pythia, bloom) : un seul espace, celui du stream.
    Cas OPT-350m (word_embed_proj_dim=512 != hidden_size=1024) : transformers
    capture les couches 0..L-1 en 1024 et la DERNIERE en 512 (post
    project_out, l'espace que lm_head lit directement). La decode-map propre
    du modele est donc lm_head o project_out pour les etats 1024, et lm_head
    seul pour l'etat 512. Lecture fidele du texte gele ("the model's own
    unembedding"), fixee avant toute valeur OPT observee — cf. RESEARCH_LOG
    (2026-07-09)."""
    lm = model.get_output_embeddings()
    W0 = lm.weight.detach().to(torch.float32).contiguous()       # (N, e)
    b0 = lm.bias.detach().to(torch.float32) if lm.bias is not None else None
    lenses = {W0.shape[1]: (W0, b0)}
    inner = getattr(model, "model", None)
    dec = getattr(inner, "decoder", None) if inner is not None else None
    proj = getattr(dec, "project_out", None) if dec is not None else None
    if proj is not None:
        W1 = (W0 @ proj.weight.detach().to(torch.float32)).contiguous()
        lenses[W1.shape[1]] = (W1, b0)                           # (N, d)
    return lenses


# --------------------------------------------------------------------------- #
# Observables par point (enonce, couche)
# --------------------------------------------------------------------------- #
def fisher_scalars(W: torch.Tensor, b: torch.Tensor | None, h: torch.Tensor,
                   k: int, chunk: int) -> dict:
    """Spectre de g(h) = W^T (diag(p) - p p^T) W et scalaires geles.

    g = W^T diag(p) W - m m^T avec m = W^T p ; accumulation par blocs de
    vocabulaire (GEMM float32, accumulateur float64)."""
    N, d = W.shape
    logits = W @ h
    if b is not None:
        logits = logits + b
    p64 = torch.softmax(logits.double(), dim=0)                  # (N,) f64

    G = torch.zeros((d, d), dtype=torch.float64)
    m = torch.zeros(d, dtype=torch.float64)
    for start in range(0, N, chunk):
        Wc = W[start:start + chunk]                              # (c, d) f32
        pc = p64[start:start + chunk].float()                    # (c,)  f32
        G += ((Wc * pc.unsqueeze(1)).T @ Wc).double()
        m += (Wc.T @ pc).double()
    G -= torch.outer(m, m)
    G = 0.5 * (G + G.T)                                          # symetrise

    lam = torch.linalg.eigvalsh(G).flip(0)                       # decroissant
    lam = torch.clamp(lam, min=0.0)
    total = float(lam.sum())
    if total <= 0.0:
        return {"o_rank": None, "o_vol": None, "o_aniso": None}

    q = lam / total
    qpos = q[q > 0]
    entropy = float(-(qpos * qpos.log()).sum())
    o_rank = float(np.exp(entropy))
    o_aniso = float(lam[0] / total)

    topk = lam[:k]
    if topk.shape[0] < k or bool((topk <= 0).any()):
        o_vol = None                                             # rang < k
    else:
        o_vol = float(0.5 * topk.log().sum())
    return {"o_rank": o_rank, "o_vol": o_vol, "o_aniso": o_aniso}


def layer_nll(W: torch.Tensor, b: torch.Tensor | None, H: torch.Tensor,
              ids: torch.Tensor) -> float | None:
    """NLL logit-lens de l'enonce a une couche : moyenne sur t de
    -log p(x_{t+1} | lens(h_t)). None si moins de 2 tokens."""
    T = H.shape[0]
    if T < 2:
        return None
    logits = H @ W.T                                             # (T, N)
    if b is not None:
        logits = logits + b
    logp = torch.log_softmax(logits, dim=-1)
    nxt = ids[1:].unsqueeze(1)                                   # (T-1, 1)
    nll = -logp[:-1].gather(1, nxt).mean()
    return float(nll)


# --------------------------------------------------------------------------- #
# Pipeline
# --------------------------------------------------------------------------- #
def run_probe(model_id, corpus, corpus_path, k, chunk, max_length, seed):
    torch.manual_seed(seed)
    # Denormaux : cf. note "Numerique" du module. Sans FTZ, les GEMM sur
    # W * p tombent a ~80 GFlops (assist microcode) ; avec, ~700 GFlops.
    torch.set_flush_denormal(True)
    device = "cpu"                                               # gele (v4)

    print(f"[fisher] loading {model_id} on {device} (float32)...")
    tok = AutoTokenizer.from_pretrained(model_id)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        model_id, torch_dtype=torch.float32).to(device).eval()

    lenses = get_unembedding(model)
    N = next(iter(lenses.values()))[0].shape[0]
    print(f"[fisher] unembedding: N={N}, espaces={sorted(lenses.keys())}")

    o_rank, o_vol, o_aniso, nll_arr, n_tok = [], [], [], [], []
    n_layers = None
    layer_dims = None
    t0 = time.time()

    for si, text in enumerate(corpus):
        enc = tok(text, return_tensors="pt", truncation=True,
                  max_length=max_length)
        ids = enc["input_ids"][0]
        with torch.no_grad():
            out = model(input_ids=ids.unsqueeze(0),
                        attention_mask=torch.ones_like(ids).unsqueeze(0),
                        output_hidden_states=True)
        hs = out.hidden_states                                   # L+1 x (1,T,D)
        if n_layers is None:
            n_layers = len(hs)
            layer_dims = [int(h.shape[-1]) for h in hs]
            missing = sorted({d for d in layer_dims} - set(lenses))
            if missing:
                raise RuntimeError(
                    f"pas de decode-map pour les espaces {missing} "
                    f"(disponibles: {sorted(lenses)})")
            print(f"[fisher] {n_layers} couches captees (embeddings incluses), "
                  f"dims={sorted(set(layer_dims))}")

        row_r, row_v, row_a, row_n = [], [], [], []
        for l in range(n_layers):
            H = hs[l][0].float()                                 # (T, d_l)
            W, b = lenses[int(H.shape[-1])]
            sc = fisher_scalars(W, b, H[-1], k, chunk)
            row_r.append(sc["o_rank"])
            row_v.append(sc["o_vol"])
            row_a.append(sc["o_aniso"])
            row_n.append(layer_nll(W, b, H, ids))
        o_rank.append(row_r)
        o_vol.append(row_v)
        o_aniso.append(row_a)
        nll_arr.append(row_n)
        n_tok.append(int(ids.shape[0]))

        done = si + 1
        if done % 5 == 0 or done == len(corpus):
            el = time.time() - t0
            pts = done * n_layers
            print(f"[fisher] {done:>3}/{len(corpus)} enonces | "
                  f"{el/60:6.1f} min | {el/pts:5.2f} s/point | "
                  f"ETA {(el/done*(len(corpus)-done))/60:6.1f} min", flush=True)

    raw = Path(corpus_path).read_bytes()
    return {
        "schema_version": "probe_fisher_v4.0",
        "preregistration": "PREREGISTRATION_v4.md",
        "freeze_commit": FREEZE_COMMIT,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "model_id": model_id,
        "n_layers": n_layers,
        "hidden_dim": max(layer_dims),
        "hidden_dims_per_layer": layer_dims,
        "unembedding_spaces": sorted(lenses.keys()),
        "vocab_size": N,
        "k_topk_vol": k,
        "chunk_size": chunk,
        "max_seq_length": max_length,
        "seed": seed,
        "device": device,
        "corpus_path": str(corpus_path),
        "corpus_size": len(corpus),
        "corpus_sha256_file": hashlib.sha256(raw).hexdigest(),
        "corpus_hash_joined": hashlib.sha256(
            "\n".join(corpus).encode("utf-8")).hexdigest(),
        "n_tokens_per_statement": n_tok,
        "results": {
            "o_rank": o_rank,       # [S][L]  effective rank de g
            "o_vol": o_vol,         # [S][L]  0.5 * sum log lam_(1..k), nullable
            "o_aniso": o_aniso,     # [S][L]  lam_1 / sum lam
            "nll": nll_arr,         # [S][L]  NLL logit-lens, nullable
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, help="HuggingFace model ID")
    ap.add_argument("--corpus", required=True,
                    help="fichier texte, un enonce par ligne")
    ap.add_argument("--out", required=True, help="chemin du JSON de sortie")
    ap.add_argument("--k", type=int, default=50,
                    help="top-k pour O_vol (gele: 50)")
    ap.add_argument("--chunk", type=int, default=65536,
                    help="taille de bloc vocabulaire pour l'accumulation de g")
    ap.add_argument("--max-length", type=int, default=128)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--max-statements", type=int, default=None,
                    help="DEBUG/PILOTE uniquement: tronque le corpus; la "
                         "sortie est un pilote, non analysable")
    args = ap.parse_args()

    corpus = [l.strip() for l in Path(args.corpus).read_text(
        encoding="utf-8").splitlines() if l.strip()]
    if args.max_statements is not None:
        corpus = corpus[:args.max_statements]
        print(f"[fisher] MODE PILOTE: {len(corpus)} enonces seulement — "
              f"sortie non analysable (debug)")

    out = run_probe(args.model, corpus, args.corpus, args.k, args.chunk,
                    args.max_length, args.seed)
    if args.max_statements is not None:
        out["pilot_debug_only"] = True

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(out, indent=2))
    print(f"[fisher] wrote {args.out}")


if __name__ == "__main__":
    main()
