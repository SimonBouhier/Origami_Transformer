#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
diag_v7.py — Diagnostics DESCRIPTIFS, HORS VERDICT (preparation v7)
===================================================================

Ce script ne rend AUCUN verdict et ne touche AUCUN seuil gele. Il repond aux
points 2, 3 et au diagnostic de style listes dans NOTE_RESULTATS_v6.md
(« Prochaines marches »), en reutilisant les mesures v6 deja calculees : il
n'exige aucune nouvelle passe modele.

Questions posees :

  D1 — DECOMPOSITION DE LA BASELINE. La baseline gelee O2 = TF-IDF U surface
       atteint BA ~= 0.74 en LODO. Quelle part vient de quoi ? On evalue, sous
       les MEMES plis, quatre blocs bon marche :
         (a) TF-IDF seul        (b) surface seule
         (c) union = O2 v6      (d) MARQUEURS DE CONSTRUCTION seuls (8 compteurs
             regex : comparatif, attribution causale, modal/irrealis, quantifieur
             de portee, copule definitionnelle, negation, preposition de
             mecanisme, nom abstrait meta)
       Si (d) seul approche (c), le confond est bien la CONSTRUCTION et non le
       vocabulaire de domaine — ce qui designe la cible de v7.

  D2 — BARRES D'ERREUR. Bootstrap apparie (2000 tirages, stratifie par classe)
       sur les predictions out-of-fold poolees -> IC 95 % pour BA_geo, BA_lex et
       la marge C2. AVERTISSEMENT : ces IC decrivent l'incertitude
       d'echantillonnage de la metrique A MODELES AJUSTES FIXES ; ils
       n'integrent pas la variabilite du reajustement ni celle du decoupage en
       plis. Ils sont donc OPTIMISTES (trop etroits). A lire comme un ordre de
       grandeur, jamais comme un test.

  D3 — DISPERSION PAR PLI. BA_geo et BA_lex pli par pli : un seul super-domaine
       peut porter la marge.

Usage :
    python diag_v7.py
    python diag_v7.py --out results/diag_v7_report.json
"""

import argparse
import json
import re
import string
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy.sparse import csr_matrix, hstack
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score

# Conventions gelees reutilisees telles quelles (charte : une idee, une
# implementation). analysis_v6 n'execute rien a l'import.
import analysis_v6 as A6

N_BOOT = 2000
BOOT_SEED = 12345

# --------------------------------------------------------------------------- #
# D1 — les 8 marqueurs de construction (specifies A LA MAIN, avant toute mesure)
# --------------------------------------------------------------------------- #
CONSTRUCTION_MARKERS = {
    "comparatif": r"\b(more|less|greater|higher|lower|larger|smaller|better|worse|"
                  r"faster|slower|longer|shorter|outperform\w*|exceed\w*|outweigh\w*)\b"
                  r"|\b\w+er than\b|\brather than\b|\bthan\b",
    "attribution_causale": r"\b(cause[sd]?|causing|drive[sn]?|driven|lead[s]? to|"
                           r"result\w* (in|from)|due to|responsible for|attributable|"
                           r"increase[sd]?|reduce[sd]?|raise[sd]?|improve[sd]?)\b",
    "modal_irrealis": r"\b(would|will|can|could|should|may|might)\b",
    "quantif_portee": r"\b(most|all|many|few|majority|significant\w*|substantial\w*|"
                      r"largely|primarily|mainly|meaningful|measurabl\w*)\b",
    "copule_definitionnelle": r"\b(is|are|was|were|consists? of|refers? to|means)\b",
    "negation": r"\b(no|not|cannot|never|without|nor)\b",
    "prep_mecanisme": r"\b(through|into|across|between|within|onto|via|by means of)\b",
    "nom_abstrait_meta": r"\b(social|economic|political|cultural|cognitive|systemic|"
                         r"structural|institutional|moral|ethical)\b",
}


def construction_features(texts):
    """8 compteurs regex par enonce, z-scores globalement (convention surface v5)."""
    rows = []
    rxs = [(n, re.compile(p, re.I)) for n, p in CONSTRUCTION_MARKERS.items()]
    for t in texts:
        rows.append([float(len(rx.findall(t))) for _, rx in rxs])
    X = np.asarray(rows, dtype=float)
    mu, sd = X.mean(0, keepdims=True), X.std(0, ddof=1, keepdims=True)
    sd[sd == 0] = 1.0
    return (X - mu) / sd


# --------------------------------------------------------------------------- #
# LODO renvoyant les PREDICTIONS (necessaire au bootstrap apparie)
# --------------------------------------------------------------------------- #
def _fit_predict(Xtr, ytr, Xte):
    clf = LogisticRegression(penalty="l2", C=1.0, solver="lbfgs", max_iter=5000)
    clf.fit(Xtr, ytr)
    return clf.predict(Xte)


def lodo_pred_dense(X, y, groups, fold_names):
    pred = np.zeros_like(y)
    per_fold = {}
    for name in fold_names:
        te = groups == name
        pred[te] = _fit_predict(X[~te], y[~te], X[te])
        per_fold[name] = float(balanced_accuracy_score(y[te], pred[te]))
    return pred, per_fold


def lodo_pred_cheap(texts, Xdense, y, groups, fold_names, use_tfidf, use_dense):
    """TF-IDF ajuste par pli (jamais sur le test) et/ou un bloc dense."""
    pred = np.zeros_like(y)
    per_fold = {}
    texts = np.array(texts, dtype=object)
    for name in fold_names:
        te = groups == name
        tr = ~te
        blocks_tr, blocks_te = [], []
        if use_tfidf:
            vec = TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True)
            blocks_tr.append(vec.fit_transform(texts[tr]))
            blocks_te.append(vec.transform(texts[te]))
        if use_dense:
            blocks_tr.append(csr_matrix(Xdense[tr]))
            blocks_te.append(csr_matrix(Xdense[te]))
        Xtr = hstack(blocks_tr).tocsr()
        Xte = hstack(blocks_te).tocsr()
        pred[te] = _fit_predict(Xtr, y[tr], Xte)
        per_fold[name] = float(balanced_accuracy_score(y[te], pred[te]))
    return pred, per_fold


# --------------------------------------------------------------------------- #
# D2 — bootstrap apparie sur les predictions out-of-fold
# --------------------------------------------------------------------------- #
def boot_ci(y, pred_a, pred_b=None, n=N_BOOT, seed=BOOT_SEED):
    """IC 95 % de BA(pred_a) et, si pred_b fourni, de BA(a) - BA(b).
    Reechantillonnage stratifie par classe, APPARIE entre a et b."""
    rng = np.random.default_rng(seed)
    idx_pos = np.flatnonzero(y == 1)
    idx_neg = np.flatnonzero(y == 0)
    stat_a, stat_d = [], []
    for _ in range(n):
        take = np.concatenate([rng.choice(idx_pos, idx_pos.size, replace=True),
                               rng.choice(idx_neg, idx_neg.size, replace=True)])
        ba_a = balanced_accuracy_score(y[take], pred_a[take])
        stat_a.append(ba_a)
        if pred_b is not None:
            stat_d.append(ba_a - balanced_accuracy_score(y[take], pred_b[take]))
    out = {"BA_ci95": [float(np.percentile(stat_a, 2.5)),
                       float(np.percentile(stat_a, 97.5))]}
    if pred_b is not None:
        out["margin_ci95"] = [float(np.percentile(stat_d, 2.5)),
                              float(np.percentile(stat_d, 97.5))]
        out["margin_frac_above_0.08"] = float(np.mean(np.array(stat_d) >= 0.08))
    return out


# --------------------------------------------------------------------------- #
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default="results")
    ap.add_argument("--corpora", default="corpora")
    ap.add_argument("--out", default="results/diag_v7_report.json")
    args = ap.parse_args()
    corpora, results = Path(args.corpora), Path(args.results)

    A6.check_corpus_files(corpora)          # meme garde d'integrite qu'au verdict
    fold_names, groups = A6.load_folds(corpora)
    texts = A6.load_texts(corpora)
    Xcons = construction_features(texts)

    print("Diagnostics HORS VERDICT — aucune nouvelle mesure modele.\n")
    report = {"schema_version": "diag_v7.0",
              "timestamp_utc": datetime.now(timezone.utc).isoformat(),
              "verdict_bearing": False,
              "construction_markers": list(CONSTRUCTION_MARKERS),
              "n_boot": N_BOOT, "boot_seed": BOOT_SEED,
              "caveat_ci": "IC a modeles ajustes fixes : optimistes, descriptifs.",
              "per_model": []}

    for short in A6.MODELS:
        try:
            con = A6._load(results / f"{short}_contested_fisher.json",
                           "probe_fisher_v4.0", "contested")
            cons = A6._load(results / f"{short}_consensualv6_fisher.json",
                            "probe_fisher_v4.0", "consensual_v6")
        except FileNotFoundError as e:
            print(f"{short}: mesure manquante ({e.filename}) — saute")
            continue

        Xg, y, _ = A6.features_geo(con, cons)
        Xsurf = A6.surface_features(con, cons, corpora)

        pred_geo, fold_geo = lodo_pred_dense(Xg, y, groups, fold_names)
        blocks = {
            "tfidf_seul":     lodo_pred_cheap(texts, None,   y, groups, fold_names, True,  False),
            "surface_seule":  lodo_pred_cheap(texts, Xsurf,  y, groups, fold_names, False, True),
            "union_O2_v6":    lodo_pred_cheap(texts, Xsurf,  y, groups, fold_names, True,  True),
            "construction":   lodo_pred_cheap(texts, Xcons,  y, groups, fold_names, False, True),
        }

        ba = {"geometrie": float(balanced_accuracy_score(y, pred_geo))}
        for k, (p, _f) in blocks.items():
            ba[k] = float(balanced_accuracy_score(y, p))

        ci_geo = boot_ci(y, pred_geo)
        ci_c2 = boot_ci(y, pred_geo, blocks["union_O2_v6"][0])

        print(f"--- {con['model_id']}")
        print(f"    geometrie      BA={ba['geometrie']:.3f}  "
              f"IC95 [{ci_geo['BA_ci95'][0]:.3f}, {ci_geo['BA_ci95'][1]:.3f}]")
        for k in ("tfidf_seul", "surface_seule", "union_O2_v6", "construction"):
            print(f"    {k:<15}BA={ba[k]:.3f}")
        print(f"    marge C2 = {ba['geometrie'] - ba['union_O2_v6']:+.3f}  "
              f"IC95 [{ci_c2['margin_ci95'][0]:+.3f}, {ci_c2['margin_ci95'][1]:+.3f}]  "
              f"P(marge>=0.08) = {ci_c2['margin_frac_above_0.08']:.0%}")
        print(f"    BA_geo par pli : "
              + ", ".join(f"{k}={v:.2f}" for k, v in sorted(fold_geo.items())))
        print()

        report["per_model"].append({
            "short": short, "model_id": con["model_id"],
            "BA_lodo": ba,
            "margin_C2": ba["geometrie"] - ba["union_O2_v6"],
            "ci_geo": ci_geo, "ci_margin_C2": ci_c2,
            "per_fold_BA_geo": fold_geo,
            "per_fold_BA_construction": blocks["construction"][1],
        })

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(report, indent=2))
    print(f"wrote {args.out}  (descriptif — ne modifie aucun verdict)")


if __name__ == "__main__":
    main()
