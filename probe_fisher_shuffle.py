#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
probe_fisher_shuffle.py — Controle O3 v5 : Fisher sur entrees MELANGEES
=======================================================================

Implemente le controle de destruction de contenu gele par PREREGISTRATION_v5.md
(commit de gel ca588c38618325b2c54d0d78ab1c61baff379dc1) :

  O3 : les scalaires de Fisher (O_vol, O_rank, O_aniso) recalcules sur des
  entrees dont l'ORDRE des tokens est melange avant le forward. La distribution
  des tokens (sac de mots) est conservee ; la structure linguistique est
  detruite. Mecanisme de melange herite de control_probe.py (v3) ; estimateur =
  probe_fisher.py IMPORTE tel quel (aucune copie, aucune derive — meme patron
  que control_probe vis-a-vis de probe.py).

CE SCRIPT NE PRODUIT AUCUN VERDICT : analysis_v5.py applique les seuils geles.

Determinisme du melange : rng = default_rng(seed), une permutation par enonce,
tiree SEQUENTIELLEMENT dans l'ordre du corpus (meme convention que
control_probe.py) — relancer sur le meme corpus et la meme graine redonne
exactement les memes entrees melangees.

NLL : non calculee ici (la NLL logit-lens d'une sequence melangee ne participe
a aucune condition gelee ; B1 se calcule sur les runs NON melanges).

Usage :
    python probe_fisher_shuffle.py --model gpt2 --corpus corpora/contested.txt \
        --out results/gpt2_contested_shuffle.json
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

# Estimateur GELE — importe, jamais copie.
from probe_fisher import get_unembedding, fisher_scalars

V5_FREEZE_COMMIT = "ca588c38618325b2c54d0d78ab1c61baff379dc1"


def run_shuffle_probe(model_id, corpus, corpus_path, k, chunk, max_length, seed):
    rng = np.random.default_rng(seed)
    torch.manual_seed(seed)
    torch.set_flush_denormal(True)          # meme regime numerique que v4
    device = "cpu"                          # gele

    print(f"[fisher-shuf] loading {model_id} on {device} (float32)...")
    tok = AutoTokenizer.from_pretrained(model_id)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        model_id, torch_dtype=torch.float32).to(device).eval()

    lenses = get_unembedding(model)
    o_rank, o_vol, o_aniso, n_tok = [], [], [], []
    n_layers, layer_dims = None, None
    t0 = time.time()

    for si, text in enumerate(corpus):
        enc = tok(text, return_tensors="pt", truncation=True,
                  max_length=max_length)
        ids = enc["input_ids"][0]
        T = int(ids.shape[0])
        # --- LE controle : permutation de l'ordre des tokens (herite v3) ---
        if T > 1:
            perm = torch.from_numpy(rng.permutation(T))
            ids = ids[perm]
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
            print(f"[fisher-shuf] {n_layers} couches, dims={sorted(set(layer_dims))}")

        row_r, row_v, row_a = [], [], []
        for l in range(n_layers):
            H = hs[l][0].float()
            W, b = lenses[int(H.shape[-1])]
            sc = fisher_scalars(W, b, H[-1], k, chunk)
            row_r.append(sc["o_rank"])
            row_v.append(sc["o_vol"])
            row_a.append(sc["o_aniso"])
        o_rank.append(row_r)
        o_vol.append(row_v)
        o_aniso.append(row_a)
        n_tok.append(T)

        done = si + 1
        if done % 5 == 0 or done == len(corpus):
            el = time.time() - t0
            print(f"[fisher-shuf] {done:>3}/{len(corpus)} | {el/60:6.1f} min | "
                  f"ETA {(el/done*(len(corpus)-done))/60:6.1f} min", flush=True)

    raw = Path(corpus_path).read_bytes()
    return {
        "schema_version": "probe_fisher_shuffle_v5.0",
        "preregistration": "PREREGISTRATION_v5.md",
        "freeze_commit": V5_FREEZE_COMMIT,
        "control_mode": "shuffle",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "model_id": model_id,
        "n_layers": n_layers,
        "hidden_dims_per_layer": layer_dims,
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
            "o_rank": o_rank,
            "o_vol": o_vol,
            "o_aniso": o_aniso,
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
    ap.add_argument("--max-statements", type=int, default=None,
                    help="DEBUG uniquement (pilote, non analysable)")
    args = ap.parse_args()

    corpus = [l.strip() for l in Path(args.corpus).read_text(
        encoding="utf-8").splitlines() if l.strip()]
    if args.max_statements is not None:
        corpus = corpus[:args.max_statements]

    out = run_shuffle_probe(args.model, corpus, args.corpus, args.k,
                            args.chunk, args.max_length, args.seed)
    if args.max_statements is not None:
        out["pilot_debug_only"] = True

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(out, indent=2))
    print(f"[fisher-shuf] wrote {args.out}")


if __name__ == "__main__":
    main()
