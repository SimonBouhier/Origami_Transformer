#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
plot_results.py — Visualisation automatique des sorties (hors verdict)
======================================================================

Lit tous les JSON d'un dossier de resultats et genere des figures PNG, sans
intervention manuelle. A relancer tel quel a chaque nouveau modele.

Gere trois schemas :
  - probe_v3.0     (probe.py)          -> profil DI : TwoNN + MLE par couche,
                                          bande +/- ecart-type, pic marque.
  - probe_v3.0 + control_mode          -> meme trace, titre annote du controle.
  - spectrum_v1.0  (spectrum.py)       -> effective rank : participation ratio
                                          + entropie spectrale par couche.

Produit, dans <results>/figures/ :
  - <model>[_<control>]_di.png         (un par sortie de probe/controle)
  - <model>_spectrum.png               (un par sortie de spectrum)
  - _overlay_di.png                    (tous les probes, profondeur normalisee)

CE SCRIPT NE JUGE RIEN. Il ne lit pas les seuils, ne produit pas de verdict :
il dessine ce qui est dans les JSON. Le verdict reste dans analysis.py.

Usage :
    python plot_results.py                      # lit ./results, ecrit ./results/figures
    python plot_results.py --results-dir results --out-dir results/figures
    python plot_results.py --show-std           # ajoute les bandes d'ecart-type

Dependances : numpy, matplotlib.
"""

import argparse
import json
import glob
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")           # backend sans affichage, sortie fichier
import matplotlib.pyplot as plt

TWONN_C = "#378ADD"   # bleu
MLE_C   = "#D85A30"   # corail
PR_C    = "#1D9E75"   # teal
ENT_C   = "#7F77DD"   # violet


def _safe_name(model_id: str) -> str:
    return model_id.replace("/", "_").replace(" ", "_")


def plot_di(data: dict, out_dir: Path, show_std: bool) -> Path:
    tw = np.asarray(data["results"]["twonn"]["mean"], float)
    ml = np.asarray(data["results"]["mle"]["mean"], float)
    tw_s = np.asarray(data["results"]["twonn"].get("std", [0] * len(tw)), float)
    ml_s = np.asarray(data["results"]["mle"].get("std", [0] * len(ml)), float)
    x = np.arange(len(tw))

    primary = (tw + ml) / 2.0
    peak = int(np.nanargmax(primary))

    ctrl = data.get("control_mode")
    title = data["model_id"] + (f"  [control: {ctrl}]" if ctrl else "")

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(x, tw, color=TWONN_C, lw=2, label="TwoNN")
    ax.plot(x, ml, color=MLE_C, lw=2, ls="--", label="MLE")
    if show_std:
        ax.fill_between(x, tw - tw_s, tw + tw_s, color=TWONN_C, alpha=0.15)
        ax.fill_between(x, ml - ml_s, ml + ml_s, color=MLE_C, alpha=0.15)
    ax.axvline(peak, color="#888780", lw=1, ls=":", alpha=0.8)
    ax.annotate(f"pic primaire @ {peak}", xy=(peak, primary[peak]),
                xytext=(4, 6), textcoords="offset points",
                fontsize=9, color="#5F5E5A")

    ax.set_xlabel("couche")
    ax.set_ylabel("dimension intrinseque")
    ax.set_ylim(bottom=0)
    ax.set_title(title, fontsize=11)
    ax.legend(frameon=False, fontsize=9)
    ax.grid(True, alpha=0.2)
    fig.tight_layout()

    name = _safe_name(data["model_id"]) + (f"_{ctrl}" if ctrl else "") + "_di.png"
    path = out_dir / name
    fig.savefig(path, dpi=140)
    plt.close(fig)
    return path


def plot_spectrum(data: dict, out_dir: Path) -> Path:
    per = data["per_layer"]
    x = [r["layer"] for r in per]
    pr = [r["participation_ratio"] for r in per]
    ent = [r["spectral_entropy_dim"] for r in per]

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(x, pr, color=PR_C, lw=2, label="participation ratio")
    ax.plot(x, ent, color=ENT_C, lw=2, ls="--", label="entropie spectrale")
    ax.set_xlabel("couche")
    ax.set_ylabel("rang effectif (lineaire)")
    ax.set_ylim(bottom=0)
    ax.set_title(data["model_id"] + "  [spectrum]", fontsize=11)
    ax.legend(frameon=False, fontsize=9)
    ax.grid(True, alpha=0.2)
    fig.tight_layout()

    path = out_dir / (_safe_name(data["model_id"]) + "_spectrum.png")
    fig.savefig(path, dpi=140)
    plt.close(fig)
    return path


def plot_overlay(probes: list, out_dir: Path) -> Path:
    """Profil DI primaire (moyenne TwoNN/MLE) de chaque modele, en profondeur
    NORMALISEE [0,1] pour comparer des modeles a nombres de couches differents."""
    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    cmap = plt.get_cmap("viridis")
    for k, data in enumerate(probes):
        tw = np.asarray(data["results"]["twonn"]["mean"], float)
        ml = np.asarray(data["results"]["mle"]["mean"], float)
        primary = (tw + ml) / 2.0
        depth = np.linspace(0, 1, len(primary))
        label = data["model_id"] + (f" [{data['control_mode']}]"
                                    if data.get("control_mode") else "")
        ax.plot(depth, primary, lw=2, color=cmap(k / max(1, len(probes) - 1)),
                label=label)
    ax.set_xlabel("profondeur normalisee (couche / derniere)")
    ax.set_ylabel("DI primaire (moyenne TwoNN/MLE)")
    ax.set_ylim(bottom=0)
    ax.set_title("Profils DI superposes", fontsize=11)
    ax.legend(frameon=False, fontsize=8)
    ax.grid(True, alpha=0.2)
    fig.tight_layout()

    path = out_dir / "_overlay_di.png"
    fig.savefig(path, dpi=140)
    plt.close(fig)
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results-dir", default="results")
    ap.add_argument("--out-dir", default=None,
                    help="defaut: <results-dir>/figures")
    ap.add_argument("--show-std", action="store_true",
                    help="ajoute les bandes +/- ecart-type sur les profils DI")
    args = ap.parse_args()

    rdir = Path(args.results_dir)
    out_dir = Path(args.out_dir) if args.out_dir else rdir / "figures"
    out_dir.mkdir(parents=True, exist_ok=True)

    files = sorted(glob.glob(str(rdir / "*.json")))
    if not files:
        print(f"[plot] aucun JSON dans {rdir}/")
        return

    probes, written = [], []
    for f in files:
        data = json.loads(Path(f).read_text())
        schema = data.get("schema_version", "")
        if schema.startswith("probe_v3"):
            written.append(plot_di(data, out_dir, args.show_std))
            probes.append(data)
        elif schema.startswith("spectrum_v"):
            written.append(plot_spectrum(data, out_dir))
        else:
            print(f"[plot] schema inconnu, ignore: {f}")

    if len(probes) >= 2:
        written.append(plot_overlay(probes, out_dir))

    for p in written:
        print(f"[plot] wrote {p}")
    print(f"[plot] {len(written)} figure(s) dans {out_dir}/")


if __name__ == "__main__":
    main()
