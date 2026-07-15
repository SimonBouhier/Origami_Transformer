#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
analysis_v4.py — Verdict pre-enregistre v4 (Fisher baseline / repasse V3)
=========================================================================

Applique les seuils GELES de PREREGISTRATION_v4.md
(commit de gel 4e9683efead2fafea26b26ce2d37611e97f69269) sur les sorties de
probe_fisher.py. DO NOT EDIT les seuils.

Conditions par modele (P_rank(l) = moyenne sur le corpus de O_rank(s,l)) :

  C1 — pic interieur : 1 <= argmax_l P_rank(l) <= n_couches - 2.
       Convention d'indice heritee de la v3 (analysis.py: L = NOMBRE de
       couches captees, pic exclu de la premiere et de la derniere couche),
       conforme a la glose "strictly interior" du texte gele. Lecture fixee
       AVANT toute donnee v4 — cf. RESEARCH_LOG (entree du 2026-07-09).
  C2 — compression finale : P_rank(derniere) < P_rank(pic), strict.
  C3 — couplage reproduit : max_l |Spearman(O_rank(:,l), NLL(:,l))| >= 0.30.

Verdict par modele : HA_CONFIRME si C1 et C2 et C3, sinon HA_DEMENTI.
Verdict global : confirme sur >= 3 modeles ET fraction >= 0.66.

Un dementi global est le resultat negatif pre-enregistre (la bosse ou le
couplage ne survit pas a l'instrument density-free) — publiable.

Usage :
    python analysis_v4.py results/*_fisher.json --out results/analysis_v4_report.json

Refuse les sorties pilotes (champ pilot_debug_only) : elles ne sont pas
analysables au sens du skill preregistration.
"""

import argparse
import json
import glob
from pathlib import Path
from datetime import datetime, timezone

import numpy as np
from scipy.stats import spearmanr

# --------------------------------------------------------------------------- #
# Seuils geles — PREREGISTRATION_v4.md. DO NOT EDIT.
# --------------------------------------------------------------------------- #
THRESHOLDS = {
    "schema_version": "analysis_v4.0",
    "preregistration": "PREREGISTRATION_v4.md",
    "freeze_commit": "4e9683efead2fafea26b26ce2d37611e97f69269",
    "frozen_on_file": "2026-05-31",
    "freeze_commit_date": "2026-06-02",
    "C1_peak_strictly_interior": True,
    "C2_last_strictly_below_peak": True,
    "C3_min_abs_spearman": 0.30,
    "global_min_models_confirmed": 3,
    "global_min_fraction_confirmed": 0.66,
}

MIN_PAIRS_SPEARMAN = 10  # garde-fou numerique: rho indefini sous ~10 paires


def _to_float(arr):
    """[S][L] avec None -> ndarray float avec NaN."""
    return np.array([[np.nan if v is None else float(v) for v in row]
                     for row in arr], dtype=float)


def analyze_one(probe: dict) -> dict:
    if probe.get("pilot_debug_only"):
        raise ValueError(
            f"{probe.get('model_id')}: sortie PILOTE (max-statements), "
            f"non analysable — relancer probe_fisher.py sur le corpus complet")

    o_rank = _to_float(probe["results"]["o_rank"])   # (S, L)
    nll    = _to_float(probe["results"]["nll"])      # (S, L)
    S, L = o_rank.shape

    # P_rank(l) : moyenne corpus (nanmean: les rares None sont exclus)
    p_rank = np.nanmean(o_rank, axis=0)
    peak = int(np.nanargmax(p_rank))

    # C1 : pic strictement interieur (ni premiere ni derniere couche)
    c1 = bool(1 <= peak <= L - 2)

    # C2 : compression finale stricte
    c2 = bool(p_rank[-1] < p_rank[peak])

    # C3 : couplage O_rank <-> NLL par couche (Spearman), max en valeur absolue
    b1 = []
    for l in range(L):
        x, y = o_rank[:, l], nll[:, l]
        ok = np.isfinite(x) & np.isfinite(y)
        if ok.sum() < MIN_PAIRS_SPEARMAN or np.ptp(x[ok]) == 0 or np.ptp(y[ok]) == 0:
            b1.append(float("nan"))
            continue
        rho = spearmanr(x[ok], y[ok]).statistic
        b1.append(float(rho))
    b1 = np.asarray(b1, dtype=float)
    if np.isfinite(b1).any():
        best_l = int(np.nanargmax(np.abs(b1)))
        max_abs_rho = float(np.abs(b1[best_l]))
    else:
        best_l, max_abs_rho = -1, float("nan")
    c3 = bool(np.isfinite(max_abs_rho)
              and max_abs_rho >= THRESHOLDS["C3_min_abs_spearman"])

    confirmed = bool(c1 and c2 and c3)
    return {
        "model_id": probe["model_id"],
        "n_layers": L,
        "n_statements": S,
        "corpus_hash_joined": probe.get("corpus_hash_joined"),
        "peak_layer": peak,
        "p_rank_profile": [float(v) for v in p_rank],
        "p_rank_peak": float(p_rank[peak]),
        "p_rank_last": float(p_rank[-1]),
        "p_vol_profile": [None if not np.isfinite(v) else float(v)
                          for v in np.nanmean(_to_float(probe["results"]["o_vol"]), axis=0)],
        "p_aniso_profile": [float(v) for v in
                            np.nanmean(_to_float(probe["results"]["o_aniso"]), axis=0)],
        "b1_spearman_profile": [None if not np.isfinite(v) else float(v) for v in b1],
        "b1_max_abs_rho": None if not np.isfinite(max_abs_rho) else max_abs_rho,
        "b1_best_layer": best_l,
        "C1_pass": c1,
        "C2_pass": c2,
        "C3_pass": c3,
        "verdict": "HA_CONFIRME" if confirmed else "HA_DEMENTI",
    }


def aggregate(per_model: list) -> dict:
    n_total = len(per_model)
    n_conf = sum(1 for r in per_model if r["verdict"] == "HA_CONFIRME")
    frac = (n_conf / n_total) if n_total else 0.0
    ok = (n_conf >= THRESHOLDS["global_min_models_confirmed"]
          and frac >= THRESHOLDS["global_min_fraction_confirmed"])
    return {
        "n_models_total": n_total,
        "n_models_confirmed": n_conf,
        "fraction_confirmed": frac,
        "global_verdict": "HA_CONFIRME" if ok else "HA_DEMENTI",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inputs", nargs="+", help="sorties probe_fisher (globs ok)")
    ap.add_argument("--out", default="results/analysis_v4_report.json")
    args = ap.parse_args()

    paths = []
    for pat in args.inputs:
        paths.extend(sorted(glob.glob(pat)) or [pat])

    per_model = []
    for p in paths:
        data = json.loads(Path(p).read_text())
        if data.get("schema_version") != "probe_fisher_v4.0":
            print(f"[analysis_v4] schema inconnu, ignore: {p}")
            continue
        r = analyze_one(data)
        per_model.append(r)
        flag = "OK" if r["verdict"] == "HA_CONFIRME" else "--"
        rho = r["b1_max_abs_rho"]
        rho_s = f"{rho:.2f}@{r['b1_best_layer']}" if rho is not None else "  nan"
        print(f"[{flag}] {r['model_id']:<28} pic@{r['peak_layer']:>2}/{r['n_layers']-1} "
              f"P_rank(pic)={r['p_rank_peak']:7.2f} P_rank(fin)={r['p_rank_last']:7.2f} "
              f"|rho|max={rho_s} "
              f"C1={int(r['C1_pass'])} C2={int(r['C2_pass'])} C3={int(r['C3_pass'])} "
              f"-> {r['verdict']}")

    agg = aggregate(per_model)
    print(f"\n=== GLOBAL: {agg['n_models_confirmed']}/{agg['n_models_total']} "
          f"confirmes ({agg['fraction_confirmed']:.0%}) "
          f"-> {agg['global_verdict']} ===")

    report = {
        "schema_version": "analysis_v4.0",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "thresholds": THRESHOLDS,
        "per_model": per_model,
        "global": agg,
    }
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(report, indent=2))
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
