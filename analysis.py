#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
analysis.py — Origami DI Analysis v3
====================================

Applique le verdict PREENREGISTRE sur une ou plusieurs sorties de probe.py.

PRE-ENREGISTREMENT (fige le 2026-05-30, AVANT regard sur les donnees) :
---------------------------------------------------------------------
Hypothese H1 (Ansuini et al.) : la DI suit un profil en BOSSE — expansion
dans les premieres couches, puis compression, derniere couche < pic.

Conditions cumulatives par modele :
  C1. ACCORD INTER-ESTIMATEUR : sur au moins 70% des couches, l'ecart
      relatif entre TwoNN et MLE est <= 20%.
  C2. PIC INTERIEUR : argmax(DI) appartient a [1, L-2] strictement.
  C3. COMPRESSION FINALE : DI[derniere] < DI[pic], strictement, sans
      tolerance, sans coussin.

Verdict par modele : H1_CONFIRME si C1 et C2 et C3, sinon H1_DEMENTI.

Verdict global (multi-modeles) : H1_CONFIRME si confirme sur >= 4 modeles
ET >= 66% du total fourni. Sinon H1_DEMENTI.

Un dementi global N'EST PAS un echec. C'est un negatif publiable et c'est
la condition d'arret prevue.

Usage :
    python analysis.py results/*.json --out analysis_report.json
"""

import argparse
import json
import glob
from pathlib import Path
from datetime import datetime, timezone

import numpy as np

# --------------------------------------------------------------------------- #
# Seuils preenregistres — DO NOT EDIT after first run on real data.
# --------------------------------------------------------------------------- #
THRESHOLDS = {
    "schema_version": "analysis_v3.0",
    "frozen_on": "2026-05-30",
    "C1_inter_estimator_relative_diff_max": 0.20,
    "C1_min_layer_agreement_fraction":      0.70,
    "C2_peak_must_be_strictly_interior":    True,
    "C3_last_strictly_below_peak":          True,
    "global_min_models_confirmed":          4,
    "global_min_fraction_confirmed":        0.66,
}


def analyze_one(probe_output: dict) -> dict:
    twonn = np.asarray(probe_output["results"]["twonn"]["mean"], dtype=float)
    mle   = np.asarray(probe_output["results"]["mle"]["mean"],   dtype=float)
    L = len(twonn)
    assert L == len(mle), "estimator length mismatch"

    # C1 : accord inter-estimateur
    denom = np.maximum(np.maximum(np.abs(twonn), np.abs(mle)), 1e-9)
    rel_diff = np.abs(twonn - mle) / denom
    layer_agrees = rel_diff <= THRESHOLDS["C1_inter_estimator_relative_diff_max"]
    agree_fraction = float(layer_agrees.mean())
    c1 = agree_fraction >= THRESHOLDS["C1_min_layer_agreement_fraction"]

    # Estimateur primaire pour C2/C3 : moyenne des deux (gere les cas ou
    # un seul estimateur a un outlier sur une couche).
    primary = (twonn + mle) / 2.0
    peak = int(np.argmax(primary))

    # C2 : pic strictement interieur
    c2 = (1 <= peak <= L - 2)

    # C3 : compression finale stricte, sans tolerance
    c3 = bool(primary[-1] < primary[peak])

    confirmed = bool(c1 and c2 and c3)

    return {
        "model_id": probe_output["model_id"],
        "n_layers": L,
        "agreement_fraction": agree_fraction,
        "C1_pass": bool(c1),
        "peak_layer": peak,
        "peak_di_primary": float(primary[peak]),
        "last_di_primary": float(primary[-1]),
        "C2_pass": bool(c2),
        "C3_pass": bool(c3),
        "verdict": "H1_CONFIRME" if confirmed else "H1_DEMENTI",
        "twonn_profile": probe_output["results"]["twonn"]["mean"],
        "mle_profile":   probe_output["results"]["mle"]["mean"],
        "twonn_std":     probe_output["results"]["twonn"]["std"],
        "mle_std":       probe_output["results"]["mle"]["std"],
    }


def aggregate(per_model: list) -> dict:
    n_total = len(per_model)
    n_confirmed = sum(1 for r in per_model if r["verdict"] == "H1_CONFIRME")
    frac = (n_confirmed / n_total) if n_total else 0.0
    global_confirmed = (
        n_confirmed >= THRESHOLDS["global_min_models_confirmed"]
        and frac >= THRESHOLDS["global_min_fraction_confirmed"]
    )
    return {
        "n_models_total": n_total,
        "n_models_confirmed": n_confirmed,
        "fraction_confirmed": frac,
        "global_verdict": "H1_CONFIRME" if global_confirmed else "H1_DEMENTI",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inputs", nargs="+", help="probe output JSON files (globs ok)")
    ap.add_argument("--out", default="analysis_report.json")
    args = ap.parse_args()

    paths = []
    for pat in args.inputs:
        paths.extend(sorted(glob.glob(pat)) or [pat])

    per_model = []
    for p in paths:
        data = json.loads(Path(p).read_text())
        r = analyze_one(data)
        per_model.append(r)
        flag = "OK" if r["verdict"] == "H1_CONFIRME" else "--"
        print(f"[{flag}] {r['model_id']:<40} peak@{r['peak_layer']:>2} "
              f"agree={r['agreement_fraction']:.2f} "
              f"C1={int(r['C1_pass'])} C2={int(r['C2_pass'])} "
              f"C3={int(r['C3_pass'])} -> {r['verdict']}")

    agg = aggregate(per_model)
    print(f"\n=== GLOBAL: {agg['n_models_confirmed']}/{agg['n_models_total']} "
          f"confirmed ({agg['fraction_confirmed']:.0%}) "
          f"-> {agg['global_verdict']} ===")

    report = {
        "schema_version": "analysis_v3.0",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "thresholds": THRESHOLDS,
        "per_model": per_model,
        "global": agg,
    }
    Path(args.out).write_text(json.dumps(report, indent=2))
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
