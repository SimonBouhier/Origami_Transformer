#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
bench_spectral_v61.py — v6.1 phase B : précision et coût de la diagonalisation
=============================================================================

Répond à la VRAIE question Q7, telle que reformulée dans PLAN_v6.1.md §0.
La question du cahier (« la troncature top-k reste-t-elle fidèle à grand
vocabulaire ? ») ne s'appliquait pas : l'instrument calcule la Fisher exacte sur
le vocabulaire complet. Ce qui coûte, c'est `eigvalsh` sur d x d en float64,
en O(d^3), sur une carte où le float64 tourne à 1/64 du float32.

Deux mesures, aucune décision :

  B-1 PRÉCISION — sur de VRAIES matrices g(h) extraites d'un modèle réel :
      float32 au lieu de float64 change-t-il O_vol / O_rank / O_aniso ?
      C'est la seule question qui peut invalider un raccourci.

  B-2 COÛT — temps de `eigvalsh` à d = 1024 / 2048 / 2560 / 4096, en float64 et
      float32, sur CPU et sur GPU. Donne la courbe qui permet d'extrapoler le
      budget d'une campagne AVANT de s'y engager, et tranche l'hypothèse
      « GEMM sur GPU, diagonalisation sur CPU ».

Usage :
    python bench_spectral_v61.py --model EleutherAI/pythia-410m --n-samples 12
    python bench_spectral_v61.py --timing-only
"""

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch

sys.stdout.reconfigure(encoding="utf-8")

DIMS = [1024, 2048, 2560, 4096]     # pythia 410m / 1.4b / 2.8b / 6.9b


def observables_from_lam(lam: torch.Tensor, k: int = 50) -> dict:
    """Les trois observables, à partir d'un spectre. Reproduit exactement la
    logique gelée de probe_fisher.fisher_scalars (lignes 118-134)."""
    lam = torch.clamp(lam.flip(0), min=0.0)
    total = float(lam.sum())
    if total <= 0.0:
        return {"o_rank": None, "o_vol": None, "o_aniso": None}
    q = lam / total
    qpos = q[q > 0]
    o_rank = float(np.exp(float(-(qpos * qpos.log()).sum())))
    o_aniso = float(lam[0] / total)
    topk = lam[:k]
    o_vol = (None if topk.shape[0] < k or bool((topk <= 0).any())
             else float(0.5 * topk.log().sum()))
    return {"o_rank": o_rank, "o_vol": o_vol, "o_aniso": o_aniso}


# --------------------------------------------------------------------------- #
# B-1 : précision sur de vraies matrices
# --------------------------------------------------------------------------- #
def bench_precision(model_id, corpus_path, n_samples, chunk):
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from probe_fisher import get_unembedding

    torch.set_flush_denormal(True)
    print(f"[B-1] {model_id} sur CPU — extraction de vraies matrices g(h)")
    tok = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(
        model_id, torch_dtype=torch.float32).eval()
    lenses = get_unembedding(model)

    corpus = [l.strip() for l in Path(corpus_path).read_text(
        encoding="utf-8").splitlines() if l.strip()]

    rows = []
    rng = np.random.default_rng(0)
    for text in corpus[:n_samples]:
        ids = tok(text, return_tensors="pt", truncation=True,
                  max_length=128)["input_ids"][0]
        with torch.no_grad():
            hs = model(input_ids=ids.unsqueeze(0),
                       attention_mask=torch.ones_like(ids).unsqueeze(0),
                       output_hidden_states=True).hidden_states
        l = int(rng.integers(1, len(hs)))          # une couche au hasard
        h = hs[l][0].float()[-1]
        W, b = lenses[int(h.shape[-1])]

        # accumulation identique à l'instrument gelé
        N, d = W.shape
        logits = W @ h
        if b is not None:
            logits = logits + b
        p64 = torch.softmax(logits.double(), dim=0)
        G = torch.zeros((d, d), dtype=torch.float64)
        m = torch.zeros(d, dtype=torch.float64)
        for s in range(0, N, chunk):
            Wc = W[s:s + chunk]
            pc = p64[s:s + chunk].float()
            G += ((Wc * pc.unsqueeze(1)).T @ Wc).double()
            m += (Wc.T @ pc).double()
        G -= torch.outer(m, m)
        G = 0.5 * (G + G.T)

        o64 = observables_from_lam(torch.linalg.eigvalsh(G))
        o32 = observables_from_lam(torch.linalg.eigvalsh(G.float()).double())
        row = {"layer": l}
        for key in ("o_vol", "o_rank", "o_aniso"):
            a, bb = o32[key], o64[key]
            row[key] = (abs(a - bb) / max(abs(bb), 1e-30)
                        if (a is not None and bb is not None) else None)
        rows.append(row)
        print(f"   couche {l:>3} | " + " ".join(
            f"{k}: {row[k]:.3e}" if row[k] is not None else f"{k}: null"
            for k in ("o_vol", "o_rank", "o_aniso")))

    print("\n[B-1] erreur relative float32 vs float64 (médiane / max) :")
    summary = {}
    for key in ("o_vol", "o_rank", "o_aniso"):
        vals = [r[key] for r in rows if r[key] is not None]
        if vals:
            summary[key] = {"median": float(np.median(vals)),
                            "max": float(np.max(vals)), "n": len(vals)}
            print(f"   {key:<9} médiane={np.median(vals):.3e}  "
                  f"max={np.max(vals):.3e}  (n={len(vals)})")
    return summary


# --------------------------------------------------------------------------- #
# B-2 : coût de eigvalsh
# --------------------------------------------------------------------------- #
def bench_timing(reps=3):
    print("\n[B-2] coût de eigvalsh (matrices SPD synthétiques ; le temps ne "
          "dépend pas des valeurs)")
    devices = ["cpu"] + (["cuda"] if torch.cuda.is_available() else [])
    out = []
    for d in DIMS:
        A = torch.randn(d, d, dtype=torch.float64)
        G = (A @ A.T) / d
        for dev in devices:
            for dt in (torch.float64, torch.float32):
                M = G.to(device=dev, dtype=dt)
                if dev == "cuda":
                    torch.linalg.eigvalsh(M); torch.cuda.synchronize()  # warmup
                t0 = time.time()
                for _ in range(reps):
                    torch.linalg.eigvalsh(M)
                if dev == "cuda":
                    torch.cuda.synchronize()
                dt_s = (time.time() - t0) / reps
                out.append({"d": d, "device": dev,
                            "dtype": str(dt).split(".")[-1], "seconds": dt_s})
                print(f"   d={d:<5} {dev:<5} {str(dt).split('.')[-1]:<8} "
                      f"{dt_s*1000:9.1f} ms")
        del A, G
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="EleutherAI/pythia-410m")
    ap.add_argument("--corpus", default="corpora/contested.txt")
    ap.add_argument("--n-samples", type=int, default=12)
    ap.add_argument("--chunk", type=int, default=65536)
    ap.add_argument("--timing-only", action="store_true")
    ap.add_argument("--out", default="results_gpu/bench_spectral_v61.json")
    args = ap.parse_args()

    report = {"schema_version": "bench_spectral_v61.0",
              "torch": torch.__version__, "cuda": torch.version.cuda,
              "gpu": (torch.cuda.get_device_name(0)
                      if torch.cuda.is_available() else None)}
    if not args.timing_only:
        report["precision_f32_vs_f64"] = bench_precision(
            args.model, args.corpus, args.n_samples, args.chunk)
    report["timing_eigvalsh"] = bench_timing()

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(report, indent=2))
    print(f"\nwrote {args.out}")
    print("\nCes chiffres NE DÉCIDENT RIEN : ils dimensionnent. Le passage en "
          "float32 n'est adopté que si B-1 montre une erreur négligeable\n"
          "devant l'écart CPU/GPU mesuré en phase A.")


if __name__ == "__main__":
    main()
