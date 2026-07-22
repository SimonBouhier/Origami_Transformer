#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
compare_cpu_gpu.py — contrôle d'équivalence v6.1 phase A
========================================================

Compare les sorties de `probe_fisher_gpu.py` aux sorties CPU **gelées** qui ont
produit le verdict v6, énoncé par énoncé et couche par couche, puis rejoue le
LODO de `analysis_v6.py` sur les sorties GPU.

Critère d'acceptation SUBSTANTIEL (fixé dans PLAN_v6.1.md avant toute mesure) :
    |BA_geo_lodo(GPU) − BA_geo_lodo(CPU gelé)| <= 0.005  sur les 4 modèles.

Les erreurs relatives sur les observables sont rapportées de façon
DESCRIPTIVE. Elles ne sont pas un seuil pré-enregistré : GPU et CPU somment
dans un ordre différent, et le niveau de bruit attendu doit être constaté
avant d'être normé. C'est de l'étalonnage, pas un verdict.

Usage :
    python compare_cpu_gpu.py --gpu-results results_gpu --cpu-results results
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np

import analysis_v6 as A6

sys.stdout.reconfigure(encoding="utf-8")

ARMS = [("contested_fisher", "contested"),
        ("consensualv6_fisher", "consensual_v6")]
BA_TOLERANCE = 0.005          # critère d'acceptation, fixé d'avance


def _arr(block):
    return np.array([[np.nan if v is None else float(v) for v in row]
                     for row in block], dtype=float)


def rel_err(a, b):
    """Erreur relative élément par élément, ignorant les NaN concordants."""
    ok = np.isfinite(a) & np.isfinite(b)
    denom = np.maximum(np.abs(b[ok]), 1e-30)
    return np.abs(a[ok] - b[ok]) / denom, int((~ok).sum())


def compare_arm(cpu_path: Path, gpu_path: Path):
    cpu = json.loads(cpu_path.read_text(encoding="utf-8"))
    gpu = json.loads(gpu_path.read_text(encoding="utf-8"))
    for key in ("model_id", "corpus_sha256_file", "n_layers", "vocab_size",
                "k_topk_vol"):
        if cpu.get(key) != gpu.get(key):
            raise SystemExit(f"{gpu_path.name}: {key} diverge "
                             f"({gpu.get(key)!r} vs {cpu.get(key)!r}) — STOP")
    out = {}
    for obs in ("o_vol", "o_rank", "o_aniso", "nll"):
        e, n_null = rel_err(_arr(gpu["results"][obs]), _arr(cpu["results"][obs]))
        out[obs] = {"median": float(np.median(e)) if e.size else float("nan"),
                    "p99": float(np.percentile(e, 99)) if e.size else float("nan"),
                    "max": float(e.max()) if e.size else float("nan"),
                    "n_null_or_mismatch": n_null}
    return out, gpu.get("port_v61", {})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cpu-results", default="results")
    ap.add_argument("--gpu-results", default="results_gpu")
    ap.add_argument("--corpora", default="corpora")
    ap.add_argument("--out", default="results_gpu/equivalence_v61.json")
    args = ap.parse_args()
    cpu_dir, gpu_dir = Path(args.cpu_results), Path(args.gpu_results)
    corpora = Path(args.corpora)

    A6.check_corpus_files(corpora)
    fold_names, groups = A6.load_folds(corpora)
    texts = A6.load_texts(corpora)

    report = {"schema_version": "equivalence_v61.0",
              "ba_tolerance": BA_TOLERANCE, "per_model": []}
    all_ok = True

    for short in A6.MODELS:
        gpu_files = {a: gpu_dir / f"{short}_{a}.json" for a, _ in ARMS}
        if not all(p.exists() for p in gpu_files.values()):
            print(f"{short}: sorties GPU incomplètes — sauté")
            continue

        obs_report, port = {}, {}
        for arm, _key in ARMS:
            obs_report[arm], port = compare_arm(
                cpu_dir / f"{short}_{arm}.json", gpu_dir / f"{short}_{arm}.json")

        # LODO sur les mesures GPU, conventions gelées d'analysis_v6
        con = A6._load(gpu_dir / f"{short}_contested_fisher.json",
                       "probe_fisher_v4.0", "contested")
        cons = A6._load(gpu_dir / f"{short}_consensualv6_fisher.json",
                        "probe_fisher_v4.0", "consensual_v6")
        Xg, y, n_nan = A6.features_geo(con, cons)
        ba_gpu, auc_gpu, _ = A6.lodo_scores_dense(Xg, y, groups, fold_names)

        ref = json.loads(Path("results/analysis_v6_report.json")
                         .read_text(encoding="utf-8"))
        ba_cpu = next(r["BA_geo_lodo"] for r in ref["per_model"]
                      if r["short"] == short)
        delta = abs(ba_gpu - ba_cpu)
        ok = delta <= BA_TOLERANCE
        all_ok &= ok

        print(f"[{'OK' if ok else '!!'}] {con['model_id']:<26} "
              f"BA_geo GPU={ba_gpu:.4f} CPU={ba_cpu:.4f} Δ={delta:.4f}")
        for arm, _ in ARMS:
            r = obs_report[arm]
            print(f"     {arm:<20} err.rel médiane "
                  + "  ".join(f"{o}={r[o]['median']:.2e}"
                              for o in ("o_vol", "o_rank", "o_aniso")))
        if port.get("seconds_total"):
            print(f"     temps GPU={port['seconds_total']}s "
                  f"(dont fisher_scalars {port.get('seconds_in_fisher_scalars')}s)"
                  f" | eig sur {port.get('eig_device')}")

        report["per_model"].append({
            "short": short, "model_id": con["model_id"],
            "BA_geo_lodo_gpu": ba_gpu, "AUC_geo_lodo_gpu": auc_gpu,
            "BA_geo_lodo_cpu_frozen": ba_cpu, "delta_BA": delta,
            "accepted": bool(ok), "n_nan_imputed": n_nan,
            "observables": obs_report, "port_v61": port})

    if not report["per_model"]:
        raise SystemExit("aucune sortie GPU trouvée — rien à comparer")

    report["all_accepted"] = bool(all_ok)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(report, indent=2))
    print(f"\n=== {'GPU QUALIFIÉ' if all_ok else 'GPU NON QUALIFIÉ'} "
          f"(tolérance BA ±{BA_TOLERANCE}) ===")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
