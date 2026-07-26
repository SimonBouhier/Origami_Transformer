#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
probe_fisher_gpu.py — portage GPU de la sonde Fisher (v6.1, phase A)
====================================================================

**Ne modifie PAS l'instrument gelé.** `get_unembedding` et `layer_nll` sont
**importées telles quelles** depuis `probe_fisher.py` — ce sont littéralement
les mêmes objets code, et elles sont agnostiques au support.

`fisher_scalars` ne peut PAS l'être : elle alloue ses accumulateurs sans
argument `device` (`probe_fisher.py:107-108`), donc elle échoue sur des tenseurs
CUDA. Elle est ici **transcrite ligne à ligne** dans `fisher_scalars_device`,
avec pour seule modification l'ajout de `device=W.device` aux deux allocations.
Aucune autre différence : mêmes dtypes, même ordre des opérations, même
symétrisation, mêmes seuils.

Cette transcription est **vérifiée contre l'originale** par `--selfcheck`, qui
exécute les deux sur CPU sur de vraies matrices et exige l'égalité stricte. Le
portage n'est donc pas cru sur parole : il est testé sur le support où
l'original fait autorité, avant d'être utilisé là où l'original ne tourne pas.

Ce qui change, et rien d'autre :
  - le modèle et les états cachés vivent sur `--device` ;
  - l'unembedding W (et b) y vivent aussi ;
  - `eigvalsh` peut être exécuté sur un autre appareil que l'accumulation
    (`--eig-device`), pour mesurer en phase B le partage optimal : le GEMM sur
    |V| lignes favorise le GPU, la diagonalisation float64 favorise peut-être
    le CPU (le float64 d'une carte GeForce tourne à 1/64 du float32).

TF32 EST DÉSACTIVÉ EXPLICITEMENT. Sur Ampere et au-delà, laisser TF32 actif
ferait tourner les GEMM « float32 » avec une mantisse de 10 bits : les petites
valeurs propres seraient détruites en silence et le spectre — donc `O_rank` et
`O_aniso` — serait faux sans qu'aucune erreur ne soit levée.

Le schéma de sortie est celui de la sonde gelée (`probe_fisher_v4.0`) augmenté
d'un bloc `port_v61` qui trace le support ; `analysis_v6.py` le lit sans
modification. Les sorties GPU s'écrivent AILLEURS que les sorties CPU gelées :
ce module n'écrase jamais une mesure de verdict.

Usage :
    python probe_fisher_gpu.py --model gpt2 --corpus corpora/contested.txt \
        --out results_gpu/gpt2_contested_fisher.json --device cuda
"""

import argparse
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# L'instrument gelé. get_unembedding et layer_nll sont agnostiques au support :
# importées, jamais recopiées. fisher_scalars est importée UNIQUEMENT pour être
# comparée à sa transcription (--selfcheck).
from probe_fisher import (FREEZE_COMMIT, fisher_scalars, get_unembedding,
                          layer_nll)


def fisher_scalars_device(W: torch.Tensor, b: torch.Tensor | None,
                          h: torch.Tensor, k: int, chunk: int) -> dict:
    """Transcription de probe_fisher.fisher_scalars (lignes 95-134).

    SEULE différence avec l'original : `device=W.device` sur les deux
    allocations d'accumulateurs. Tout le reste est identique caractère pour
    caractère. Vérifié par --selfcheck.
    """
    N, d = W.shape
    logits = W @ h
    if b is not None:
        logits = logits + b
    p64 = torch.softmax(logits.double(), dim=0)

    G = torch.zeros((d, d), dtype=torch.float64, device=W.device)   # <- device
    m = torch.zeros(d, dtype=torch.float64, device=W.device)        # <- device
    for start in range(0, N, chunk):
        Wc = W[start:start + chunk]
        pc = p64[start:start + chunk].float()
        G += ((Wc * pc.unsqueeze(1)).T @ Wc).double()
        m += (Wc.T @ pc).double()
    G -= torch.outer(m, m)
    G = 0.5 * (G + G.T)

    lam = torch.linalg.eigvalsh(G).flip(0)
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
        o_vol = None
    else:
        o_vol = float(0.5 * topk.log().sum())
    return {"o_rank": o_rank, "o_vol": o_vol, "o_aniso": o_aniso}


def selfcheck(model_id: str, corpus_path: str, n: int, k: int, chunk: int):
    """Exige l'egalite STRICTE entre la transcription et l'originale, sur CPU."""
    from transformers import AutoModelForCausalLM, AutoTokenizer
    torch.set_flush_denormal(True)
    print(f"[selfcheck] {model_id} sur CPU — transcription vs original gelé")
    tok = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(
        model_id, torch_dtype=torch.float32).eval()
    lenses = get_unembedding(model)
    corpus = [l.strip() for l in Path(corpus_path).read_text(
        encoding="utf-8").splitlines() if l.strip()][:n]

    n_cmp = 0
    for text in corpus:
        ids = tok(text, return_tensors="pt", truncation=True,
                  max_length=128)["input_ids"][0]
        with torch.no_grad():
            hs = model(input_ids=ids.unsqueeze(0),
                       attention_mask=torch.ones_like(ids).unsqueeze(0),
                       output_hidden_states=True).hidden_states
        for l in range(len(hs)):
            h = hs[l][0].float()[-1]
            W, b = lenses[int(h.shape[-1])]
            a = fisher_scalars(W, b, h, k, chunk)          # gelé
            c = fisher_scalars_device(W, b, h, k, chunk)   # transcription
            for key in ("o_vol", "o_rank", "o_aniso"):
                if a[key] != c[key]:
                    raise SystemExit(
                        f"[selfcheck] ECHEC couche {l} {key}: "
                        f"{c[key]!r} != {a[key]!r} — la transcription DIVERGE")
            n_cmp += 1
    print(f"[selfcheck] OK — {n_cmp} points comparés, égalité stricte sur les "
          f"trois observables. La transcription est fidèle.")


def _configure_backend(device: str) -> dict:
    """Verrouille la précision. Renvoie l'état pour traçabilité."""
    torch.set_flush_denormal(True)          # comme la sonde gelée (effet CPU)
    state = {"tf32_matmul": None, "tf32_cudnn": None}
    if device.startswith("cuda"):
        # CRITIQUE : sans ça, "float32" peut signifier TF32 (mantisse 10 bits).
        torch.backends.cuda.matmul.allow_tf32 = False
        torch.backends.cudnn.allow_tf32 = False
        torch.backends.cuda.matmul.allow_fp16_reduced_precision_reduction = False
        torch.backends.cuda.matmul.allow_bf16_reduced_precision_reduction = False
        state["tf32_matmul"] = torch.backends.cuda.matmul.allow_tf32
        state["tf32_cudnn"] = torch.backends.cudnn.allow_tf32
    return state


def run_probe_gpu(model_id, corpus, corpus_path, k, chunk, max_length, seed,
                  device, eig_device, weights_dtype="float32", shuffle=False):
    # Controle O3 : permutation de l'ordre des tokens, UNE par enonce, tiree
    # sequentiellement dans l'ordre du corpus — exactement comme la sonde gelee
    # probe_fisher_shuffle.py (lignes 50, 72-75). Meme graine + memes longueurs
    # de tokens => memes permutations qu'une passe CPU.
    rng = np.random.default_rng(seed)
    torch.manual_seed(seed)
    backend = _configure_backend(device)

    print(f"[fisher-gpu] {model_id} sur {device} (float32), "
          f"eigvalsh sur {eig_device}")
    tok = AutoTokenizer.from_pretrained(model_id)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    wdt = {"float32": torch.float32, "bfloat16": torch.bfloat16,
           "float16": torch.float16}[weights_dtype]
    model = AutoModelForCausalLM.from_pretrained(
        model_id, torch_dtype=wdt).to(device).eval()

    # NB : get_unembedding remonte W en float32 (probe_fisher.py:80) et les
    # etats caches sont remontes par H.float(). Seule la PASSE AVANT tourne
    # dans wdt — c'est exactement l'effet que la qualification bf16 mesure.

    # get_unembedding travaille sur les poids du modèle : déjà sur `device`.
    lenses = {d: (W, b) for d, (W, b) in get_unembedding(model).items()}
    N = next(iter(lenses.values()))[0].shape[0]
    print(f"[fisher-gpu] unembedding: N={N}, espaces={sorted(lenses.keys())}")

    o_rank, o_vol, o_aniso, nll_arr, n_tok = [], [], [], [], []
    n_layers = layer_dims = None
    t_fisher = t_eig = 0.0
    t0 = time.time()

    for si, text in enumerate(corpus):
        enc = tok(text, return_tensors="pt", truncation=True,
                  max_length=max_length)
        ids = enc["input_ids"][0]
        if shuffle:
            T = int(ids.shape[0])
            if T > 1:
                ids = ids[torch.from_numpy(rng.permutation(T))]
        ids = ids.to(device)
        with torch.no_grad():
            out = model(input_ids=ids.unsqueeze(0),
                        attention_mask=torch.ones_like(ids).unsqueeze(0),
                        output_hidden_states=True)
        hs = out.hidden_states
        if n_layers is None:
            n_layers = len(hs)
            layer_dims = [int(h.shape[-1]) for h in hs]
            missing = sorted({d for d in layer_dims} - set(lenses))
            if missing:
                raise RuntimeError(f"pas de decode-map pour {missing}")
            print(f"[fisher-gpu] {n_layers} couches, "
                  f"dims={sorted(set(layer_dims))}")

        row_r, row_v, row_a, row_n = [], [], [], []
        for l in range(n_layers):
            H = hs[l][0].float()
            W, b = lenses[int(H.shape[-1])]
            ta = time.time()
            sc = fisher_scalars_device(W, b, H[-1], k, chunk)  # transcription
            t_fisher += time.time() - ta
            row_r.append(sc["o_rank"])
            row_v.append(sc["o_vol"])
            row_a.append(sc["o_aniso"])
            row_n.append(layer_nll(W, b, H, ids))        # fonction GELÉE
        o_rank.append(row_r); o_vol.append(row_v)
        o_aniso.append(row_a); nll_arr.append(row_n)
        n_tok.append(int(ids.shape[0]))

        done = si + 1
        if done % 5 == 0 or done == len(corpus):
            el = time.time() - t0
            pts = done * n_layers
            print(f"[fisher-gpu] {done:>3}/{len(corpus)} | {el/60:6.1f} min | "
                  f"{el/pts:5.3f} s/point | "
                  f"ETA {(el/done*(len(corpus)-done))/60:6.1f} min", flush=True)

    raw = Path(corpus_path).read_bytes()
    return {
        "schema_version": ("probe_fisher_shuffle_v5.0" if shuffle
                           else "probe_fisher_v4.0"),
        "control_mode": "shuffle" if shuffle else None,
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
        "results": {"o_rank": o_rank, "o_vol": o_vol,
                    "o_aniso": o_aniso, "nll": nll_arr},
        # Traçabilité du portage — ignoré par analysis_v6.py.
        "port_v61": {
            "port": "probe_fisher_gpu.py",
            "math": "fisher_scalars transcrite (device=W.device) + "
                "layer_nll/get_unembedding importes tels quels",
            "eig_device": eig_device,
            "weights_dtype": weights_dtype,
            "torch_version": torch.__version__,
            "cuda_version": torch.version.cuda,
            "gpu_name": (torch.cuda.get_device_name(0)
                         if device.startswith("cuda") else None),
            "tf32_disabled": backend,
            "seconds_in_fisher_scalars": round(t_fisher, 1),
            "seconds_total": round(time.time() - t0, 1),
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--corpus", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--k", type=int, default=50)
    ap.add_argument("--chunk", type=int, default=65536)
    ap.add_argument("--max-length", type=int, default=128)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--weights-dtype", default="float32",
                    choices=["float32", "bfloat16", "float16"],
                    help="dtype de la PASSE AVANT ; W et h sont toujours "
                         "remontes en float32 pour la Fisher")
    ap.add_argument("--eig-device", default="same",
                    choices=["same", "cpu", "cuda"],
                    help="phase B : où exécuter eigvalsh")
    ap.add_argument("--shuffle", action="store_true",
                    help="controle O3 : permute l'ordre des tokens (graine)")
    ap.add_argument("--selfcheck", action="store_true",
                    help="compare la transcription a l'original gele, sur CPU")
    ap.add_argument("--max-statements", type=int, default=None,
                    help="DEBUG/PILOTE : sortie marquée non analysable")
    args = ap.parse_args()

    if args.selfcheck:
        selfcheck(args.model, args.corpus, args.max_statements or 2,
                  args.k, args.chunk)
        return

    if args.device.startswith("cuda") and not torch.cuda.is_available():
        raise SystemExit("[fisher-gpu] CUDA indisponible — STOP")

    corpus = [l.strip() for l in Path(args.corpus).read_text(
        encoding="utf-8").splitlines() if l.strip()]
    if args.max_statements is not None:
        corpus = corpus[:args.max_statements]
        print(f"[fisher-gpu] PILOTE: {len(corpus)} énoncés — non analysable")

    out = run_probe_gpu(args.model, corpus, args.corpus, args.k, args.chunk,
                        args.max_length, args.seed, args.device,
                        args.eig_device, args.weights_dtype, args.shuffle)
    if args.max_statements is not None:
        out["pilot_debug_only"] = True

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(out, indent=2))
    print(f"[fisher-gpu] wrote {args.out}")


if __name__ == "__main__":
    main()
