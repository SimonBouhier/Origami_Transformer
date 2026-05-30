#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
probe.py — Origami DI Probe v3
==============================

INSTRUMENT PUR. Mesure la dimension intrinseque par couche pour un modele
HuggingFace, sur un corpus donne, avec DEUX estimateurs independants et un
bootstrap reel. Ne produit AUCUN verdict, AUCUNE signature EPP, AUCUNE
recommandation. Sortie = JSON brut.

Le verdict est dans analysis.py, applique apres coup avec des seuils
preenregistres. L'integration EPP est dans epp_adapter.py, et reste un stub
tant que l'instrument n'est pas valide sur >= 4 familles de modeles.

Dependances :
    pip install torch transformers scikit-dimension numpy

Usage :
    python probe.py --model gpt2 --out results/gpt2.json
    python probe.py --model mistralai/Mistral-7B-v0.1 --corpus claims.txt \
                    --out results/mistral7b.json --n-subsample 1500
"""

import argparse
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# --------------------------------------------------------------------------- #
# Corpus par defaut — modeste, generique. Pour resultats publiables : >= 200
# enonces diversifies, fournis via --corpus.
# --------------------------------------------------------------------------- #
DEFAULT_CORPUS = [
    "The mitochondria is the powerhouse of the cell.",
    "Water boils at one hundred degrees Celsius at sea level.",
    "Photosynthesis converts light energy into chemical energy in plants.",
    "A transformer processes tokens in parallel using self-attention.",
    "The 2008 financial crisis began with the US subprime mortgage market.",
    "Prime numbers have exactly two distinct positive divisors.",
    "A folded sheet of paper concentrates stress along its creases.",
    "The Hurst exponent measures long-range dependence in a time series.",
    "Intrinsic dimension is the minimal number of coordinates a manifold needs.",
    "Bitcoin uses a proof-of-work consensus to order transactions.",
    "Proteins fold into low-energy three-dimensional native structures.",
    "Photons are massless quanta of the electromagnetic field.",
    "Tectonic plates move at roughly the speed fingernails grow.",
    "DNA replication is semiconservative, as shown by Meselson and Stahl.",
    "The general theory of relativity describes gravity as spacetime curvature.",
    "Chess has more legal positions than atoms in the observable universe.",
    "Antibodies recognize antigens through their variable Fab regions.",
    "The Fourier transform decomposes a signal into frequency components.",
    "Volcanic eruptions can inject sulfate aerosols into the stratosphere.",
    "Neural networks approximate functions by composing affine maps and nonlinearities.",
]

# --------------------------------------------------------------------------- #
# Estimateurs — deux methodes independantes via scikit-dimension.
# Hypotheses theoriques distinctes, donc convergence = signal reel.
# --------------------------------------------------------------------------- #
def estimate_di(X: np.ndarray, method: str) -> float:
    """DI globale d'un nuage X (n, d). Methods: 'twonn', 'mle'.

    TwoNN (Facco 2017) : ratios des 1er/2e voisins, hypothese de densite
    localement uniforme. Estimation par regression.

    MLE (Levina-Bickel 2004) : log-vraisemblance sur les k plus proches
    voisins, hypothese de processus de Poisson local. Estimation par
    maximum de vraisemblance.

    Hypotheses orthogonales -> convergence non triviale.
    """
    from skdim import id as skid
    X = X.astype(np.float32)
    if method == "twonn":
        est = skid.TwoNN()
    elif method == "mle":
        est = skid.MLE(K=20)
    else:
        raise ValueError(f"unknown method: {method}")
    est.fit(X)
    return float(est.dimension_)


def bootstrap_di(X: np.ndarray, method: str, n_boot: int, rng) -> tuple:
    """Vrai bootstrap : rechantillonnage AVEC remise a chaque tirage."""
    n = X.shape[0]
    dims = []
    for _ in range(n_boot):
        idx = rng.choice(n, n, replace=True)
        try:
            dims.append(estimate_di(X[idx], method))
        except Exception:
            continue
    if not dims:
        return float("nan"), float("nan")
    return float(np.mean(dims)), float(np.std(dims))


# --------------------------------------------------------------------------- #
# Extraction des activations
# --------------------------------------------------------------------------- #
def extract_hidden_states(texts, model, tokenizer, device, max_length=128):
    """Renvoie une liste (1 par couche) d'arrays (n_tokens_reels, hidden).
    Index 0 = embeddings, suivants = blocs transformer."""
    buckets = None
    for text in texts:
        enc = tokenizer(text, return_tensors="pt", truncation=True,
                        max_length=max_length).to(device)
        with torch.no_grad():
            out = model(**enc, output_hidden_states=True)
        mask = enc["attention_mask"].bool()
        if buckets is None:
            buckets = [[] for _ in out.hidden_states]
        for i, h in enumerate(out.hidden_states):     # h: (1, T, D)
            real = h[0][mask[0]].float().cpu().numpy()
            buckets[i].append(real)
    return [np.concatenate(chunk, axis=0) for chunk in buckets]


def subsample(M, n_target, rng):
    if M.shape[0] <= n_target:
        return M
    idx = rng.choice(M.shape[0], n_target, replace=False)
    return M[idx]


# --------------------------------------------------------------------------- #
# Pipeline principal
# --------------------------------------------------------------------------- #
def run_probe(model_id, corpus, n_subsample, n_boot, max_length, seed, device):
    rng = np.random.default_rng(seed)
    torch.manual_seed(seed)

    print(f"[probe] loading {model_id} on {device}...")
    tok = AutoTokenizer.from_pretrained(model_id)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    dtype = torch.float16 if device == "cuda" else torch.float32
    model = AutoModelForCausalLM.from_pretrained(
        model_id, torch_dtype=dtype).to(device).eval()

    print(f"[probe] extracting hidden states on {len(corpus)} texts...")
    layers = extract_hidden_states(corpus, model, tok, device, max_length)
    n_layers = len(layers)
    hidden_dim = layers[0].shape[1]
    total_tokens = layers[0].shape[0]
    print(f"[probe] {n_layers} layers, hidden_dim={hidden_dim}, "
          f"total_tokens={total_tokens}")

    if total_tokens < 200:
        print(f"[probe] WARNING: only {total_tokens} tokens. DI estimates "
              f"will be unstable. Provide a larger --corpus for real results.")

    results = {"twonn": {"mean": [], "std": []},
               "mle":   {"mean": [], "std": []}}

    for i, M in enumerate(layers):
        Ms = subsample(M, n_subsample, rng)
        for method in ("twonn", "mle"):
            mean, std = bootstrap_di(Ms, method, n_boot, rng)
            results[method]["mean"].append(mean)
            results[method]["std"].append(std)
        print(f"[probe] layer {i:>2} | twonn={results['twonn']['mean'][-1]:6.2f}"
              f" ± {results['twonn']['std'][-1]:4.2f}"
              f" | mle={results['mle']['mean'][-1]:6.2f}"
              f" ± {results['mle']['std'][-1]:4.2f}")

    return {
        "schema_version": "probe_v3.0",
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
    ap.add_argument("--model", required=True, help="HuggingFace model ID")
    ap.add_argument("--out", required=True, help="Output JSON path")
    ap.add_argument("--corpus", default=None,
                    help="Optional text file, one statement per line")
    ap.add_argument("--n-subsample", type=int, default=2000,
                    help="Max points per layer fed to estimators")
    ap.add_argument("--n-boot", type=int, default=20,
                    help="Bootstrap resamples per estimator per layer")
    ap.add_argument("--max-length", type=int, default=128)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    if args.corpus:
        corpus = [line.strip() for line in Path(args.corpus).read_text(
            encoding="utf-8").splitlines() if line.strip()]
    else:
        corpus = DEFAULT_CORPUS

    device = "cuda" if torch.cuda.is_available() else "cpu"
    out = run_probe(args.model, corpus, args.n_subsample, args.n_boot,
                    args.max_length, args.seed, device)

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(out, indent=2))
    print(f"[probe] wrote {args.out}")


if __name__ == "__main__":
    main()
