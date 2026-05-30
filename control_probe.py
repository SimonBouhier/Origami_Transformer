#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
control_probe.py — Controles nuls pour la DI (sonde #6, hors verdict)
=====================================================================

Reprend EXACTEMENT les estimateurs de probe.py (TwoNN + MLE, meme bootstrap
sans remise, meme dedup) mais sur des entrees DEGRADEES, pour repondre a une
seule question : le profil de DI en bosse depend-il du langage, ou est-ce une
propriete de l'architecture traitant n'importe quelle entree ?

Deux controles :
  --control shuffle : on melange l'ORDRE des tokens de chaque sequence avant
                      de la passer au modele. La distribution des tokens (et
                      donc des embeddings) est conservee, la syntaxe et la
                      structure positionnelle sont detruites.
  --control random  : on remplace chaque token par un id tire uniformement
                      dans le vocabulaire. Geometrie du bruit pur.

Lecture :
  - Si la bosse PERSISTE sous shuffle/random -> elle ne vient pas du langage
    mais du traitement par couches lui-meme. Resultat fort, et publiable.
  - Si la bosse S'EFFONDRE -> elle est portee par la structure linguistique.

CE SCRIPT NE PRODUIT AUCUN VERDICT. Sortie au meme schema que probe.py (champ
"control_mode" en plus) pour pouvoir superposer les profils. Il n'alimente PAS
analysis.py et ne touche pas au pre-enregistrement v3. probe.py reste fige.

Usage :
    python control_probe.py --model gpt2 --corpus claims.txt \
        --control shuffle --out results/gpt2_shuffle.json
    python control_probe.py --model gpt2 --control random \
        --out results/gpt2_random.json

Dependances : torch, transformers, numpy (+ skdim via probe.py).
"""

import argparse
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# Reutilise les estimateurs FIGES de probe.py (aucune copie, aucune derive).
from probe import DEFAULT_CORPUS, estimate_di, bootstrap_di, subsample


def extract_controlled(texts, model, tokenizer, device, control, rng,
                       max_length=128):
    """Comme probe.extract_hidden_states, mais applique une transformation de
    controle sur les token ids AVANT le forward.

    control == "none"    : identique au probe (utile comme sanity-check).
    control == "shuffle" : permutation aleatoire de l'ordre des tokens.
    control == "random"  : tokens remplaces par des ids uniformes du vocab.
    """
    vocab = int(getattr(model.config, "vocab_size",
                        model.get_input_embeddings().weight.shape[0]))
    buckets = None
    for text in texts:
        enc = tokenizer(text, return_tensors="pt", truncation=True,
                        max_length=max_length)
        ids = enc["input_ids"]
        T = ids.shape[1]
        if control == "shuffle" and T > 1:
            perm = torch.from_numpy(rng.permutation(T))
            ids = ids[:, perm]
        elif control == "random":
            ids = torch.from_numpy(
                rng.integers(0, vocab, size=ids.shape)).long()
        ids = ids.to(device)
        attn = torch.ones_like(ids).to(device)
        with torch.no_grad():
            out = model(input_ids=ids, attention_mask=attn,
                        output_hidden_states=True)
        if buckets is None:
            buckets = [[] for _ in out.hidden_states]
        for i, h in enumerate(out.hidden_states):      # h: (1, T, D)
            buckets[i].append(h[0].float().cpu().numpy())
    return [np.concatenate(chunk, axis=0) for chunk in buckets]


def run_control(model_id, corpus, control, n_subsample, n_boot, max_length,
                seed, device):
    rng = np.random.default_rng(seed)
    torch.manual_seed(seed)

    print(f"[control:{control}] loading {model_id} on {device}...")
    tok = AutoTokenizer.from_pretrained(model_id)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    dtype = torch.float16 if device == "cuda" else torch.float32
    model = AutoModelForCausalLM.from_pretrained(
        model_id, torch_dtype=dtype).to(device).eval()

    print(f"[control:{control}] extracting hidden states on {len(corpus)} texts...")
    layers = extract_controlled(corpus, model, tok, device, control, rng,
                                max_length)
    n_layers = len(layers)
    hidden_dim = layers[0].shape[1]
    total_tokens = layers[0].shape[0]
    print(f"[control:{control}] {n_layers} layers, hidden_dim={hidden_dim}, "
          f"total_tokens={total_tokens}")
    if total_tokens < 200:
        print(f"[control:{control}] WARNING: only {total_tokens} tokens; "
              f"DI estimates will be unstable.")

    results = {"twonn": {"mean": [], "std": []},
               "mle":   {"mean": [], "std": []}}
    for i, M in enumerate(layers):
        Ms = subsample(M, n_subsample, rng)
        for method in ("twonn", "mle"):
            mean, std = bootstrap_di(Ms, method, n_boot, rng)
            results[method]["mean"].append(mean)
            results[method]["std"].append(std)
        print(f"[control:{control}] layer {i:>2} | "
              f"twonn={results['twonn']['mean'][-1]:6.2f} | "
              f"mle={results['mle']['mean'][-1]:6.2f}")

    return {
        "schema_version": "probe_v3.0",
        "control_mode": control,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "model_id": model_id,
        "n_layers": n_layers,
        "hidden_dim": hidden_dim,
        "total_tokens": total_tokens,
        "n_subsample": min(n_subsample, total_tokens),
        "n_bootstrap": n_boot,
        "max_seq_length": max_length,
        "seed": seed,
        "corpus_hash": hashlib.sha256(
            "\n".join(corpus).encode("utf-8")).hexdigest(),
        "corpus_size": len(corpus),
        "estimators": ["twonn", "mle"],
        "results": results,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--control", choices=["none", "shuffle", "random"],
                    default="shuffle")
    ap.add_argument("--corpus", default=None)
    ap.add_argument("--n-subsample", type=int, default=2000)
    ap.add_argument("--n-boot", type=int, default=20)
    ap.add_argument("--max-length", type=int, default=128)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    if args.corpus:
        corpus = [line.strip() for line in Path(args.corpus).read_text(
            encoding="utf-8").splitlines() if line.strip()]
    else:
        corpus = DEFAULT_CORPUS

    device = "cuda" if torch.cuda.is_available() else "cpu"
    out = run_control(args.model, corpus, args.control, args.n_subsample,
                      args.n_boot, args.max_length, args.seed, device)

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(out, indent=2))
    print(f"[control:{args.control}] wrote {args.out}")


if __name__ == "__main__":
    main()
