#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
analysis_v6.py — Verdict pre-enregistre v6 (H-D : transfert inter-domaines)
===========================================================================

Applique les seuils GELES de PREREGISTRATION_v6.md
(commit de gel 10b6c89895403be0df2731a2953870f80a26c6a2) sur :
  - le bras CONTESTE : sorties v5 REUTILISEES telles quelles (decision gelee) —
    results/{m}_contested_fisher.json et results/{m}_contested_shuffle.json ;
  - le bras CONSENSUEL PAR DOMAINE (nouveau) —
    results/{m}_consensualv6_fisher.json et results/{m}_consensualv6_shuffle.json.
DO NOT EDIT les seuils.

Conditions par modele (evaluation LEAVE-ONE-DOMAIN-OUT, folds = les 7
super-domaines geles de corpora/domain_map_v6.json) :
  C1 — transfert au-dela du hasard :   BA_geo_lodo >= 0.60
  C2 — bat tout le bon marche :        BA_geo_lodo - BA_lex_lodo >= 0.08
  C3 — porte par la structure :        BA_geo_lodo - BA_geo_shuf_lodo >= 0.08
  B1 — sanity instrument (porte VOID, inchangee) : max_l |Spearman(O_rank,NLL)|
       >= 0.30 sur le corpus poole, sinon run VOID.

Verdict par modele : HD_CONFIRME / HD_DEMENTI / VOID.
Global : confirme sur >= 3/4 modeles ET fraction >= 0.66.

Conventions d'implementation, FIXEES A L'ECRITURE (ce fichier est committe
avant que toute sortie de mesure v6 n'existe) :
  - Geometrie : X[s] = concat sur l de [O_vol, O_rank, O_aniso], z-score PAR
    COLONNE sur le pool des 240 (convention v5, aveugle aux labels) ; les null
    -> 0.0 apres z-score, comptes et journalises.
  - LODO : pour chaque super-domaine D, entrainement sur les 6 autres, test sur
    D ; predictions poolees out-of-fold ; BA/AUC calcules UNE FOIS sur le pool.
    La ligne i des DEUX bras porte le meme domaine (construction v6) — les 240
    enonces se repartissent donc en 7 folds equilibres entre classes.
  - Classifieur : LogisticRegression(L2, C=1.0, lbfgs, max_iter=5000) — v5.
  - O2 (baseline non geometrique DURCIE, texte gele) : TF-IDF mots
    (unigrammes+bigrammes, min_df=2, sublinear_tf) AJUSTE SUR LES PLIS
    D'ENTRAINEMENT SEULEMENT, concatene aux 3 features de surface v5
    (n_tokens du tokenizer DU MODELE tel qu'enregistre par la sonde, zipf
    moyen wordfreq-en, nb de ponctuation ; z-scorees globalement, convention
    v5). Memes plis LODO que O1.
  - O3 : memes features geometriques calculees sur les runs SHUFFLE des deux
    bras, memes plis.
  - Integrite : sha256 des 4 artefacts corpus REVERIFIES contre les constantes
    du gel ; chaque sortie de sonde doit porter le sha256 du bras qu'elle
    pretend mesurer ; pilotes refuses ; 120 enonces par bras.
  - --selftest : verifie corpus/hashes/folds SANS lire aucune sortie de mesure
    (utilisable avant la campagne).

Usage :
    python analysis_v6.py --selftest
    python analysis_v6.py --results results --out results/analysis_v6_report.json
"""

import argparse
import hashlib
import json
import re
import string
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy.sparse import hstack, csr_matrix
from scipy.stats import spearmanr
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, roc_auc_score
from wordfreq import zipf_frequency

# --------------------------------------------------------------------------- #
# Seuils geles — PREREGISTRATION_v6.md. DO NOT EDIT.
# --------------------------------------------------------------------------- #
THRESHOLDS = {
    "schema_version": "analysis_v6.0",
    "preregistration": "PREREGISTRATION_v6.md",
    "freeze_commit": "10b6c89895403be0df2731a2953870f80a26c6a2",
    "frozen_on": "2026-07-21",
    "C1_min_BA_geo_lodo": 0.60,
    "C2_min_margin_vs_cheap": 0.08,
    "C3_min_margin_vs_shuffle": 0.08,
    "B1_min_abs_spearman": 0.30,
    "global_min_models_confirmed": 3,
    "global_min_fraction_confirmed": 0.66,
}

FROZEN_SHA256 = {
    "contested": "3eb7bae8506e97e274f407cf8f6d8357cdc06555d727e71f5aa8f9bb668850f2",
    "consensual_v6": "711709204cfc64b5969c2b71706803c5d12a0201530672425ac67c634fbe7f04",
    "domain_map_v6": "5a8abe901f09bb8e18d8a5ba2cf8e87be68e49f1602185a43683510e74fc2b78",
    "matching_report_v6": "d78cd60f7fc6cd81463b44720daaf4ce61ce91426fbcdc73ad50c36bbb0131cc",
}

MODELS = {
    "gpt2": "gpt2",
    "pythia410m": "EleutherAI/pythia-410m",
    "opt350m": "facebook/opt-350m",
    "bloom560m": "bigscience/bloom-560m",
}
MIN_PAIRS_SPEARMAN = 10
SEED = 0  # gele (Scope) — ici purement documentaire : le LODO n'a aucun aleatoire


# --------------------------------------------------------------------------- #
# Chargement & integrite
# --------------------------------------------------------------------------- #
def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_corpus_files(corpora: Path) -> None:
    pairs = [("contested.txt", "contested"),
             ("consensual_v6.txt", "consensual_v6"),
             ("domain_map_v6.json", "domain_map_v6"),
             ("matching_report_v6.json", "matching_report_v6")]
    for fname, key in pairs:
        got = _sha(corpora / fname)
        if got != FROZEN_SHA256[key]:
            raise SystemExit(f"corpora/{fname}: sha256 {got[:16]}… != gel — STOP")


def _load(path: Path, expected_schema: str, arm_key: str) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("pilot_debug_only"):
        raise ValueError(f"{path.name}: sortie PILOTE — non analysable")
    if data.get("schema_version") != expected_schema:
        raise ValueError(f"{path.name}: schema {data.get('schema_version')!r} != {expected_schema!r}")
    if data.get("corpus_sha256_file") != FROZEN_SHA256[arm_key]:
        raise ValueError(f"{path.name}: le bras mesure ne porte pas le sha256 gele de {arm_key}")
    if data.get("corpus_size") != 120:
        raise ValueError(f"{path.name}: corpus_size={data.get('corpus_size')} != 120")
    return data


def load_folds(corpora: Path):
    dm = json.loads((corpora / "domain_map_v6.json").read_text(encoding="utf-8"))
    fine = dm["per_line_fine_domain"]                     # 120 domaines fins, ligne i
    f2s = dm["fine_to_super"]
    supers = [f2s[d] for d in fine]                       # super-domaine de la ligne i
    fold_names = sorted(set(supers))
    if len(fold_names) != 7:
        raise SystemExit(f"{len(fold_names)} super-domaines != 7 geles")
    # ligne i des DEUX bras = meme domaine -> l'index de fold vaut pour les 240
    groups = np.array(supers + supers)                    # [conteste; consensuel]
    return fold_names, groups


# --------------------------------------------------------------------------- #
# Features
# --------------------------------------------------------------------------- #
def _to_float(arr):
    return np.array([[np.nan if v is None else float(v) for v in row]
                     for row in arr], dtype=float)


def features_geo(con: dict, cons: dict):
    mats = []
    for probe in (con, cons):
        r = probe["results"]
        mats.append(np.concatenate([_to_float(r["o_vol"]),
                                    _to_float(r["o_rank"]),
                                    _to_float(r["o_aniso"])], axis=1))
    X = np.concatenate(mats, axis=0)
    y = np.concatenate([np.ones(120), np.zeros(120)])
    n_nan = int(np.isnan(X).sum())
    mu = np.nanmean(X, axis=0, keepdims=True)
    sd = np.nanstd(X, axis=0, ddof=1, keepdims=True)
    sd[sd == 0] = 1.0
    X = np.nan_to_num((X - mu) / sd, nan=0.0)
    return X, y, n_nan


def surface_features(con: dict, cons: dict, corpora: Path):
    rows = []
    for probe, fname in ((con, "contested.txt"), (cons, "consensual_v6.txt")):
        texts = [l.strip() for l in (corpora / fname).read_text(encoding="utf-8")
                 .splitlines() if l.strip()]
        for text, nt in zip(texts, probe["n_tokens_per_statement"]):
            words = re.findall(r"[A-Za-z']+", text.lower())
            zipf = float(np.mean([zipf_frequency(w, "en") for w in words])) if words else 0.0
            punct = sum(1 for c in text if c in string.punctuation)
            rows.append([float(nt), zipf, float(punct)])
    X = np.asarray(rows, dtype=float)
    mu, sd = X.mean(0, keepdims=True), X.std(0, ddof=1, keepdims=True)
    sd[sd == 0] = 1.0
    return (X - mu) / sd


def load_texts(corpora: Path):
    con = [l.strip() for l in (corpora / "contested.txt").read_text(encoding="utf-8")
           .splitlines() if l.strip()]
    cons = [l.strip() for l in (corpora / "consensual_v6.txt").read_text(encoding="utf-8")
            .splitlines() if l.strip()]
    return con + cons


# --------------------------------------------------------------------------- #
# LODO
# --------------------------------------------------------------------------- #
def lodo_scores_dense(X, y, groups, fold_names):
    """BA/AUC sur predictions out-of-fold poolees ; folds = super-domaines."""
    pred = np.zeros_like(y)
    proba = np.zeros_like(y, dtype=float)
    per_fold = {}
    for name in fold_names:
        te = groups == name
        tr = ~te
        clf = LogisticRegression(penalty="l2", C=1.0, solver="lbfgs", max_iter=5000)
        clf.fit(X[tr], y[tr])
        pred[te] = clf.predict(X[te])
        proba[te] = clf.predict_proba(X[te])[:, 1]
        per_fold[name] = float(balanced_accuracy_score(y[te], pred[te]))
    return (float(balanced_accuracy_score(y, pred)),
            float(roc_auc_score(y, proba)), per_fold)


def lodo_scores_cheap(texts, Xsurf, y, groups, fold_names):
    """Baseline non geometrique : TF-IDF ajuste par pli + surface. Memes plis."""
    pred = np.zeros_like(y)
    proba = np.zeros_like(y, dtype=float)
    texts = np.array(texts, dtype=object)
    for name in fold_names:
        te = groups == name
        tr = ~te
        vec = TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True)
        Xtr = hstack([vec.fit_transform(texts[tr]), csr_matrix(Xsurf[tr])]).tocsr()
        Xte = hstack([vec.transform(texts[te]), csr_matrix(Xsurf[te])]).tocsr()
        clf = LogisticRegression(penalty="l2", C=1.0, solver="lbfgs", max_iter=5000)
        clf.fit(Xtr, y[tr])
        pred[te] = clf.predict(Xte)
        proba[te] = clf.predict_proba(Xte)[:, 1]
    return (float(balanced_accuracy_score(y, pred)),
            float(roc_auc_score(y, proba)))


def b1_sanity(con: dict, cons: dict):
    o_rank = np.concatenate([_to_float(con["results"]["o_rank"]),
                             _to_float(cons["results"]["o_rank"])], axis=0)
    nll = np.concatenate([_to_float(con["results"]["nll"]),
                          _to_float(cons["results"]["nll"])], axis=0)
    best, best_l = float("nan"), -1
    for l in range(o_rank.shape[1]):
        x, yv = o_rank[:, l], nll[:, l]
        ok = np.isfinite(x) & np.isfinite(yv)
        if ok.sum() < MIN_PAIRS_SPEARMAN or np.ptp(x[ok]) == 0 or np.ptp(yv[ok]) == 0:
            continue
        rho = abs(float(spearmanr(x[ok], yv[ok]).statistic))
        if not np.isfinite(best) or rho > best:
            best, best_l = rho, l
    return best, best_l


# --------------------------------------------------------------------------- #
# Par modele
# --------------------------------------------------------------------------- #
def analyze_model(short, results: Path, corpora: Path, fold_names, groups, texts):
    con = _load(results / f"{short}_contested_fisher.json", "probe_fisher_v4.0", "contested")
    cons = _load(results / f"{short}_consensualv6_fisher.json", "probe_fisher_v4.0", "consensual_v6")
    con_sh = _load(results / f"{short}_contested_shuffle.json",
                   "probe_fisher_shuffle_v5.0", "contested")
    cons_sh = _load(results / f"{short}_consensualv6_shuffle.json",
                    "probe_fisher_shuffle_v5.0", "consensual_v6")

    b1_rho, b1_layer = b1_sanity(con, cons)
    b1_pass = bool(np.isfinite(b1_rho) and b1_rho >= THRESHOLDS["B1_min_abs_spearman"])

    Xg, y, n_nan = features_geo(con, cons)
    ba_geo, auc_geo, per_fold = lodo_scores_dense(Xg, y, groups, fold_names)

    Xsurf = surface_features(con, cons, corpora)
    ba_lex, auc_lex = lodo_scores_cheap(texts, Xsurf, y, groups, fold_names)

    Xg_sh, y_sh, n_nan_sh = features_geo(con_sh, cons_sh)
    ba_shuf, _, _ = lodo_scores_dense(Xg_sh, y_sh, groups, fold_names)

    c1 = bool(ba_geo >= THRESHOLDS["C1_min_BA_geo_lodo"])
    c2 = bool(ba_geo - ba_lex >= THRESHOLDS["C2_min_margin_vs_cheap"])
    c3 = bool(ba_geo - ba_shuf >= THRESHOLDS["C3_min_margin_vs_shuffle"])
    verdict = ("VOID" if not b1_pass
               else "HD_CONFIRME" if (c1 and c2 and c3) else "HD_DEMENTI")

    return {
        "model_id": con["model_id"], "short": short,
        "BA_geo_lodo": ba_geo, "AUC_geo_lodo": auc_geo,
        "BA_lex_lodo": ba_lex, "AUC_lex_lodo": auc_lex,
        "BA_geo_shuf_lodo": ba_shuf,
        "margin_C2": ba_geo - ba_lex, "margin_C3": ba_geo - ba_shuf,
        "per_fold_BA_geo": per_fold,
        "n_nan_imputed_geo": n_nan, "n_nan_imputed_shuffle": n_nan_sh,
        "B1_max_abs_rho": None if not np.isfinite(b1_rho) else b1_rho,
        "B1_best_layer": b1_layer, "B1_pass": b1_pass,
        "C1_pass": c1, "C2_pass": c2, "C3_pass": c3,
        "verdict": verdict,
    }


def aggregate(per_model):
    n_total = len(per_model)
    n_conf = sum(1 for r in per_model if r["verdict"] == "HD_CONFIRME")
    n_void = sum(1 for r in per_model if r["verdict"] == "VOID")
    frac = (n_conf / n_total) if n_total else 0.0
    ok = (n_conf >= THRESHOLDS["global_min_models_confirmed"]
          and frac >= THRESHOLDS["global_min_fraction_confirmed"])
    return {"n_models_total": n_total, "n_models_confirmed": n_conf,
            "n_models_void": n_void, "fraction_confirmed": frac,
            "global_verdict": "HD_CONFIRME" if ok else "HD_DEMENTI"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default="results")
    ap.add_argument("--corpora", default="corpora")
    ap.add_argument("--out", default="results/analysis_v6_report.json")
    ap.add_argument("--selftest", action="store_true",
                    help="verifie corpus/hashes/folds sans lire aucune mesure")
    args = ap.parse_args()
    corpora = Path(args.corpora)

    check_corpus_files(corpora)
    fold_names, groups = load_folds(corpora)
    texts = load_texts(corpora)
    assert len(texts) == 240 and len(groups) == 240

    if args.selftest:
        counts = {n: int((groups == n).sum()) for n in fold_names}
        print("[selftest] sha256 corpus : OK (4/4 = gel)")
        print(f"[selftest] folds LODO ({len(fold_names)}) : {counts}")
        print("[selftest] 240 enonces, ligne i des 2 bras = meme domaine : OK")
        print("[selftest] PRET — aucune sortie de mesure n'a ete lue.")
        return

    per_model = []
    for short in MODELS:
        try:
            r = analyze_model(short, Path(args.results), corpora, fold_names, groups, texts)
        except FileNotFoundError as e:
            print(f"[analysis_v6] {short}: fichier manquant ({e.filename}) — saute")
            continue
        per_model.append(r)
        flag = {"HD_CONFIRME": "OK", "HD_DEMENTI": "--", "VOID": "!!"}[r["verdict"]]
        b1 = r["B1_max_abs_rho"]
        print(f"[{flag}] {r['model_id']:<28} BA_lodo={r['BA_geo_lodo']:.3f} "
              f"lex={r['BA_lex_lodo']:.3f} shuf={r['BA_geo_shuf_lodo']:.3f} "
              f"C2={r['margin_C2']:+.3f} C3={r['margin_C3']:+.3f} "
              f"B1={'nan' if b1 is None else round(b1,2)} "
              f"C1={int(r['C1_pass'])} C2={int(r['C2_pass'])} C3={int(r['C3_pass'])} "
              f"-> {r['verdict']}")

    if not per_model:
        raise SystemExit(
            "[analysis_v6] AUCUN resultat v6 trouve — la campagne n'a pas tourne. "
            "Pas de verdict sur du vide : aucun rapport ecrit.")

    agg = aggregate(per_model)
    print(f"\n=== GLOBAL: {agg['n_models_confirmed']}/{agg['n_models_total']} confirmes "
          f"({agg['fraction_confirmed']:.0%}), {agg['n_models_void']} VOID "
          f"-> {agg['global_verdict']} ===")

    report = {
        "schema_version": "analysis_v6.0",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "thresholds": THRESHOLDS,
        "frozen_sha256": FROZEN_SHA256,
        "per_model": per_model,
        "global": agg,
    }
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(report, indent=2))
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
