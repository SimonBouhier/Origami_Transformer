#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
curvature.py — Local Curvature Probe v3
=======================================

Complement de probe.py. Mesure, par couche et par point, une grandeur
scalaire qui quantifie a quel point la variete s'ecarte localement de son
plan tangent : la "courbure locale" au sens d'un residu de PCA locale.

Methode :
---------
Pour chaque point x sur la couche k :
  1. Trouver ses K plus proches voisins.
  2. Faire une PCA locale sur ces voisins.
  3. Soit d = DI estimee globalement par probe.py (ou fournie). Garder les
     d premieres composantes principales -> "plan" tangent local de
     dimension d.
  4. Courbure locale = fraction de variance NON capturee par ce plan,
     i.e. somme des valeurs propres a partir de la (d+1)-eme, normalisee
     par la variance totale locale.

Interpretation :
----------------
- Courbure ~ 0 : la variete est localement plate (le voisinage de x tient
  bien dans un sous-espace de dim d).
- Courbure -> 1 : la variete est tres pliee ici (le voisinage deborde
  largement du plan tangent).

C'est une mesure EXTRINSEQUE simple. Pour de la courbure intrinseque
(Riemann), il faudrait estimer la metrique induite et ses derivees
secondes — projet plus lourd, pour plus tard.

Sortie :
--------
Pour chaque couche : un vecteur de courbures (un scalaire par point).
On agrege en moyenne, mediane, p90 — pour donner un profil par couche
et garder la distribution. La projection 2D (UMAP) coloree par courbure
locale se fait dans visualize.py (a faire dans un second temps).

Usage :
    python curvature.py --model gpt2 --probe-json results/gpt2.json \
                        --out results/gpt2_curvature.json

Le --probe-json est utilise pour recuperer la DI par couche (estimee par
probe.py) et l'utiliser comme d dans l'etape 3. Si non fourni, fallback
sur d = max(2, round(DI_globale)) avec une DI globale par defaut.

Dependances : torch, transformers, scikit-learn, numpy.
"""

import argparse
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from sklearn.neighbors import NearestNeighbors

# Reutilise les helpers de probe.py
from probe import (
    DEFAULT_CORPUS,
    extract_hidden_states,
    subsample,
)


def local_curvature(X: np.ndarray, d: int, K: int = 30) -> np.ndarray:
    """Pour chaque point de X (n, D), renvoie la courbure locale = fraction
    de variance non captee par les d premieres composantes de la PCA
    locale calculee sur ses K plus proches voisins.

    Returns: array (n,) dans [0, 1].
    """
    n = X.shape[0]
    K = min(K, n - 1)
    if K < d + 2:
        # voisinage trop petit pour estimer une PCA jusqu'a d+1
        return np.full(n, np.nan, dtype=np.float64)

    nn = NearestNeighbors(n_neighbors=K + 1).fit(X)
    _, idx = nn.kneighbors(X)
    idx = idx[:, 1:]  # exclut le point lui-meme

    curvatures = np.empty(n, dtype=np.float64)
    for i in range(n):
        neigh = X[idx[i]]                # (K, D)
        c = neigh - neigh.mean(axis=0)   # centrage local
        # valeurs propres de la covariance locale, decroissantes
        # SVD sur c est equivalent et plus stable
        s = np.linalg.svd(c, compute_uv=False)
        var = s ** 2
        total = var.sum()
        if total <= 1e-12:
            curvatures[i] = 0.0
        else:
            tail = var[d:].sum()
            curvatures[i] = float(tail / total)
    return curvatures


def get_dim_per_layer(probe_json_path: str, n_layers: int, fallback: int):
    """Charge la DI par couche depuis la sortie de probe.py et renvoie une
    liste d'entiers (max(2, round(mean(twonn, mle)))) par couche."""
    if probe_json_path is None:
        return [fallback] * n_layers
    data = json.loads(Path(probe_json_path).read_text())
    twonn = np.asarray(data["results"]["twonn"]["mean"], dtype=float)
    mle   = np.asarray(data["results"]["mle"]["mean"],   dtype=float)
    assert len(twonn) == n_layers, (
        f"probe JSON has {len(twonn)} layers, model gives {n_layers}")
    dims = []
    for a, b in zip(twonn, mle):
        vals = [v for v in (a, b) if np.isfinite(v)]
        d = int(round(np.mean(vals))) if vals else fallback
        dims.append(max(2, d))
    return dims


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--probe-json", default=None,
                    help="probe.py output to pull per-layer DI from")
    ap.add_argument("--fallback-dim", type=int, default=20,
                    help="DI used per layer if --probe-json is absent")
    ap.add_argument("--corpus", default=None)
    ap.add_argument("--n-subsample", type=int, default=2000)
    ap.add_argument("--k-neighbors", type=int, default=30)
    ap.add_argument("--max-length", type=int, default=128)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    rng = np.random.default_rng(args.seed)
    torch.manual_seed(args.seed)

    if args.corpus:
        corpus = [line.strip() for line in Path(args.corpus).read_text(
            encoding="utf-8").splitlines() if line.strip()]
    else:
        corpus = DEFAULT_CORPUS

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[curvature] loading {args.model} on {device}...")
    tok = AutoTokenizer.from_pretrained(args.model)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    dtype = torch.float16 if device == "cuda" else torch.float32
    model = AutoModelForCausalLM.from_pretrained(
        args.model, torch_dtype=dtype).to(device).eval()

    print(f"[curvature] extracting hidden states on {len(corpus)} texts...")
    layers = extract_hidden_states(corpus, model, tok, device, args.max_length)
    n_layers = len(layers)
    dims = get_dim_per_layer(args.probe_json, n_layers, args.fallback_dim)
    print(f"[curvature] per-layer d used: {dims}")

    per_layer_stats = []
    per_layer_samples = []  # garde un sous-echantillon pour la viz future

    for i, (M, d) in enumerate(zip(layers, dims)):
        Ms = subsample(M, args.n_subsample, rng)
        curv = local_curvature(Ms, d=d, K=args.k_neighbors)
        valid = curv[np.isfinite(curv)]
        if valid.size == 0:
            stats = {"mean": float("nan"), "median": float("nan"),
                     "p90": float("nan"), "n_valid": 0}
        else:
            stats = {
                "mean":   float(np.mean(valid)),
                "median": float(np.median(valid)),
                "p90":    float(np.percentile(valid, 90)),
                "n_valid": int(valid.size),
            }
        per_layer_stats.append({"layer": i, "d_used": d, **stats})
        # echantillon (max 500) pour visualize.py
        keep = min(500, valid.size)
        if keep > 0:
            sample_idx = rng.choice(valid.size, keep, replace=False)
            per_layer_samples.append(valid[sample_idx].tolist())
        else:
            per_layer_samples.append([])
        print(f"[curvature] layer {i:>2} | d={d:>3} | "
              f"mean={stats['mean']:.3f} median={stats['median']:.3f} "
              f"p90={stats['p90']:.3f} n={stats['n_valid']}")

    out = {
        "schema_version": "curvature_v3.0",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "model_id": args.model,
        "n_layers": n_layers,
        "k_neighbors": args.k_neighbors,
        "n_subsample": args.n_subsample,
        "seed": args.seed,
        "corpus_hash": hashlib.sha256(
            "\n".join(corpus).encode("utf-8")).hexdigest(),
        "corpus_size": len(corpus),
        "probe_json": args.probe_json,
        "per_layer_d": dims,
        "per_layer_stats": per_layer_stats,
        "per_layer_curvature_samples": per_layer_samples,
    }
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(out, indent=2))
    print(f"[curvature] wrote {args.out}")


if __name__ == "__main__":
    main()
