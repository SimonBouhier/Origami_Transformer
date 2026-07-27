#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verdict_v7.py — applique le critère GELÉ de PREREGISTRATION_v7.md (aa120bd).

Critère (§5, gelé le 2026-07-26, δ=0.00, F=2/3) — une rung SOUTIENT H-F si :
   (1) BA_geo > floor(n)              plancher de permutation à son propre n
   (2) IC_bas(marge bootstrap) > δ    avec δ = 0.00
H-F confirmée pour un modèle si les rungs soutenantes sont ≥ F de toutes les
rungs ET incluent la rung LA PLUS DURE (BA_cheap minimal).

LACUNE DU PRÉ-ENREGISTREMENT, déclarée : le plancher n'a été calculé qu'une
rung sur quatre (9 ancres sur 33). Le gel ne dit pas comment traiter les rungs
intermédiaires. Deux résolutions sont calculées ici et rapportées toutes les
deux ; si elles divergeaient, aucune ne pourrait être choisie après coup :
  - INTERPOLÉE   : plancher interpolé linéairement entre ancres ;
  - CONSERVATRICE: plancher = max des ancres encadrantes (plus exigeant).
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
DELTA, F = 0.00, 2.0 / 3.0
REPORT = Path("results_v7/sweep_report.json")


def floors(rs, mode):
    anc = [(r["rung"], r["perm_floor_geo"]["p95"]) for r in rs if "perm_floor_geo" in r]
    xs = np.array([a[0] for a in anc], float)
    ys = np.array([a[1] for a in anc], float)
    out = {}
    for r in rs:
        k = r["rung"]
        if mode == "interp":
            out[k] = float(np.interp(k, xs, ys))
        else:                                    # conservatrice
            lo = ys[xs <= k]
            hi = ys[xs >= k]
            out[k] = float(max(lo[-1] if len(lo) else ys[0],
                               hi[0] if len(hi) else ys[-1]))
    return out


def main():
    R = json.loads(REPORT.read_text(encoding="utf-8"))
    print("VERDICT v7 — critère gelé (aa120bd) : δ = 0.00, F = 2/3\n")
    print(f"{'modèle':<24}{'soutien':>9}{'requis':>8}{'+dure':>7}  {'verdict':<14}")
    print("-" * 66)
    summary = {}
    for m, d in R["per_model"].items():
        rs = d["rungs"]
        hardest = min(rs, key=lambda r: r["BA_cheap_lodo"])["rung"]
        res = {}
        for mode in ("interp", "conserv"):
            fl = floors(rs, mode)
            sup = [r["rung"] for r in rs
                   if r["BA_geo_lodo"] > fl[r["rung"]]
                   and r["bootstrap"]["margin_ci95"][0] > DELTA]
            need = int(np.ceil(F * len(rs)))
            ok = len(sup) >= need and hardest in sup
            res[mode] = {"n_support": len(sup), "need": need,
                         "hardest_supports": hardest in sup,
                         "confirmed": bool(ok), "supporting_rungs": sup}
        v = ("HF_CONFIRME" if res["interp"]["confirmed"] and res["conserv"]["confirmed"]
             else "HF_DEMENTI")
        print(f"{d['model_id']:<24}{res['interp']['n_support']:>4}/{len(rs):<4}"
              f"{res['interp']['need']:>8}{'oui' if res['interp']['hardest_supports'] else 'non':>7}"
              f"  {v:<14}")
        summary[m] = {"model_id": d["model_id"], "hardest_rung": hardest,
                      "n_rungs": len(rs), "verdict": v, **res}

    n_conf = sum(1 for s in summary.values() if s["verdict"] == "HF_CONFIRME")
    print("-" * 66)
    print(f"GLOBAL : {n_conf}/{len(summary)} modèles confirment H-F")
    same = all(s["interp"]["confirmed"] == s["conserv"]["confirmed"]
               for s in summary.values())
    print(f"Résolution du plancher (interpolée vs conservatrice) : "
          f"{'MÊME verdict partout' if same else 'DIVERGE — à trancher'}")
    Path("results_v7/verdict_v7.json").write_text(
        json.dumps({"delta": DELTA, "F": F, "freeze_commit": "aa120bd",
                    "per_model": summary, "n_confirmed": n_conf,
                    "floor_resolutions_agree": same}, indent=2))
    print("\nwrote results_v7/verdict_v7.json")


if __name__ == "__main__":
    main()
