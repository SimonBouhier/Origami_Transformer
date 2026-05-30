#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
spectrum.py — Effective Rank Probe (diagnostic LINEAIRE, hors verdict)
======================================================================

Complement de probe.py. Mesure, par couche, la dimensionnalite LINEAIRE du
nuage d'activations via le spectre de la covariance (PCA globale). C'est
volontairement orthogonal a la DI non-lineaire de probe.py (TwoNN/MLE) :

  - probe.py   : dimension INTRINSEQUE (variete courbe, voisinages locaux).
  - spectrum.py: dimension LINEAIRE effective (etalement du spectre PCA).

Si la DI non-lineaire et l'effective rank chutent ENSEMBLE a la derniere
couche, la compression est aussi spectrale (le nuage tient dans moins de
directions). Si seule la DI bouge, la compression est purement non-lineaire.

CE SCRIPT NE PRODUIT AUCUN VERDICT. Il n'alimente pas analysis.py et ne
touche pas au pre-enregistrement v3. C'est un diagnostic, point.

Mesures par couche :
  - participation_ratio  = (Sum lambda)^2 / Sum(lambda^2)   [Gao et al. 2017]
  - spectral_entropy_dim = exp(-Sum p_i ln p_i), p_i = lambda_i / Sum lambda
  - n_pc_90 / n_pc_95    = nb de composantes pour 90% / 95% de variance
  - top1_var_fraction    = part de variance de la 1ere composante
Pour un nuage isotrope de dimension d, participation_ratio et
spectral_entropy_dim valent tous deux ~ d. Pour un nuage de rang 1, ~ 1.

Usage :
    python spectrum.py --model gpt2 --corpus claims.txt \
                       --out results/gpt2_spectrum.json

Dependances : torch, transformers, numpy (reutilise les helpers de probe.py).
"""

import argparse
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from probe import DEFAULT_CORPUS, extract_hidden_states, subsample


def spectrum_stats(X: np.ndarray) -> dict:
    """Statistiques d'effective rank sur un nuage X (n, d).

    On travaille sur les valeurs propres de la covariance, obtenues via les
    valeurs singulieres de X centre (plus stable qu'une covariance explicite).
    Les ratios sont invariants au facteur 1/(n-1), on garde donc s**2 brut.
    """
    Xc = X.astype(np.float64)
    Xc = Xc - Xc.mean(axis=0, keepdims=True)
    # valeurs singulieres -> lambda_i = s_i**2 (a un facteur 1/(n-1) pres)
    s = np.linalg.svd(Xc, compute_uv=False)
    lam = s ** 2
    total = float(lam.sum())
    if total <= 1e-12:
        return {"participation_ratio": float("nan"),
                "spectral_entropy_dim": float("nan"),
                "n_pc_90": 0, "n_pc_95": 0,
                "top1_var_fraction": float("nan"),
                "total_variance": 0.0}

    participation = float((lam.sum() ** 2) / (lam ** 2).sum())

    p = lam / total
    p = p[p > 0]
    entropy = float(-(p * np.log(p)).sum())
    entropy_dim = float(np.exp(entropy))

    csum = np.cumsum(lam) / total
    n_pc_90 = int(np.searchsorted(csum, 0.90) + 1)
    n_pc_95 = int(np.searchsorted(csum, 0.95) + 1)
    top1 = float(lam[0] / total)

    return {
        "participation_ratio": participation,
        "spectral_entropy_dim": entropy_dim,
        "n_pc_90": n_pc_90,
        "n_pc_95": n_pc_95,
        "top1_var_fraction": top1,
        "total_variance": total,
    }


def run_spectrum(model_id, corpus, n_subsample, max_length, seed, device):
    rng = np.random.default_rng(seed)
    torch.manual_seed(seed)

    print(f"[spectrum] loading {model_id} on {device}...")
    tok = AutoTokenizer.from_pretrained(model_id)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    dtype = torch.float16 if device == "cuda" else torch.float32
    model = AutoModelForCausalLM.from_pretrained(
        model_id, torch_dtype=dtype).to(device).eval()

    print(f"[spectrum] extracting hidden states on {len(corpus)} texts...")
    layers = extract_hidden_states(corpus, model, tok, device, max_length)
    n_layers = len(layers)
    hidden_dim = layers[0].shape[1]
    total_tokens = layers[0].shape[0]
    print(f"[spectrum] {n_layers} layers, hidden_dim={hidden_dim}, "
          f"total_tokens={total_tokens}")

    per_layer = []
    for i, M in enumerate(layers):
        Ms = subsample(M, n_subsample, rng)
        st = spectrum_stats(Ms)
        st = {"layer": i, "n_points": int(Ms.shape[0]), **st}
        per_layer.append(st)
        print(f"[spectrum] layer {i:>2} | PR={st['participation_ratio']:6.2f}"
              f" | H_dim={st['spectral_entropy_dim']:6.2f}"
              f" | pc90={st['n_pc_90']:>3} pc95={st['n_pc_95']:>3}"
              f" | top1={st['top1_var_fraction']:.3f}")

    return {
        "schema_version": "spectrum_v1.0",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "model_id": model_id,
        "n_layers": n_layers,
        "hidden_dim": hidden_dim,
        "total_tokens": total_tokens,
        "n_subsample": min(n_subsample, total_tokens),
        "max_seq_length": max_length,
        "seed": seed,
        "corpus_hash": hashlib.sha256(
            "\n".join(corpus).encode("utf-8")).hexdigest(),
        "corpus_size": len(corpus),
        "per_layer": per_layer,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, help="HuggingFace model ID")
    ap.add_argument("--out", required=True, help="Output JSON path")
    ap.add_argument("--corpus", default=None,
                    help="Optional text file, one statement per line")
    ap.add_argument("--n-subsample", type=int, default=2000)
    ap.add_argument("--max-length", type=int, default=128)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    if args.corpus:
        corpus = [line.strip() for line in Path(args.corpus).read_text(
            encoding="utf-8").splitlines() if line.strip()]
    else:
        corpus = DEFAULT_CORPUS

    device = "cuda" if torch.cuda.is_available() else "cpu"
    out = run_spectrum(args.model, corpus, args.n_subsample,
                       args.max_length, args.seed, device)

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(out, indent=2))
    print(f"[spectrum] wrote {args.out}")


if __name__ == "__main__":
    main()
