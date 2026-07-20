#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
analysis_v5.py — Verdict pre-enregistre v5 (H-C : contested vs consensual)
==========================================================================

Applique les seuils GELES de PREREGISTRATION_v5.md
(commit de gel ca588c38618325b2c54d0d78ab1c61baff379dc1) sur les sorties de
probe_fisher.py (2 bras) et probe_fisher_shuffle.py (2 bras melanges).
DO NOT EDIT les seuils.

Conditions par modele :
  C1 — separation :        BA_geo >= 0.65
  C2 — pas de surface :    AUC_geo - AUC_surf >= 0.10
  C3 — porte par contenu : BA_geo - BA_geo_shuf >= 0.08
  B1 — sanity instrument (PAS une condition de confirmation) : le couplage
       O_rank<->NLL valide en v4 doit se reproduire sur le corpus poole
       (max_l |Spearman| >= 0.30, seuil herite du C3 de la v4). Si B1 echoue,
       le run du modele est VOID (ni confirme ni dementi).

Verdict par modele : HC_CONFIRME si C1 et C2 et C3 ; HC_DEMENTI sinon ;
VOID si B1 echoue. Global : confirme sur >= 3 modeles ET fraction >= 0.66
(un VOID ne compte ni au numerateur ni comme dementi ; il peut mecaniquement
empecher une confirmation globale — c'est voulu : un instrument invalide ne
confirme rien).

Conventions d'implementation, FIXEES A L'ECRITURE DE CE FICHIER, avant toute
lecture de donnees v5 (le commit de ce fichier precede toute sortie de mesure) :
  - O1 : X[s] = concat sur l de [O_vol(s,l), O_rank(s,l), O_aniso(s,l)],
    z-score PAR COLONNE sur le corpus poole des 240 enonces (texte gele :
    "z-scored per layer across the pooled corpus" — transformation aveugle aux
    labels) ; les null (O_vol) deviennent 0.0 apres z-score (= moyenne), leur
    nombre est journalise.
  - Classifieur : LogisticRegression(L2, C=1.0, lbfgs, max_iter=5000),
    StratifiedKFold(n_splits=5, shuffle=True, random_state=0) — graine 0
    globale (PREREGISTRATION_v5 §Scope), MEMES plis pour O1/O2/O3.
  - BA/AUC calcules UNE FOIS sur les predictions out-of-fold poolees.
  - O2 : n_tokens = comptes du tokenizer DU MODELE (enregistres par la sonde) ;
    log-frequence unigramme = moyenne de wordfreq.zipf_frequency(mot, "en")
    sur les mots \\w+ ; ponctuation = nb de caracteres string.punctuation.
  - Integrite : sha256 des 4 fichiers corpus REVERIFIES contre les constantes
    du gel ; sorties pilotes (max-statements) refusees ; 120 enonces par bras.

Usage :
    python analysis_v5.py --results results --out results/analysis_v5_report.json
Attend, pour chaque modele m dans {gpt2, pythia410m, opt350m, bloom560m} :
    results/{m}_contested_fisher.json      results/{m}_consensual_fisher.json
    results/{m}_contested_shuffle.json     results/{m}_consensual_shuffle.json
"""

import argparse
import hashlib
import json
import re
import string
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold
from wordfreq import zipf_frequency

# --------------------------------------------------------------------------- #
# Seuils geles — PREREGISTRATION_v5.md. DO NOT EDIT.
# --------------------------------------------------------------------------- #
THRESHOLDS = {
    "schema_version": "analysis_v5.0",
    "preregistration": "PREREGISTRATION_v5.md",
    "freeze_commit": "ca588c38618325b2c54d0d78ab1c61baff379dc1",
    "frozen_on": "2026-07-19",
    "C1_min_BA_geo": 0.65,
    "C2_min_AUC_margin": 0.10,
    "C3_min_BA_shuffle_margin": 0.08,
    "B1_min_abs_spearman": 0.30,     # herite du C3 v4 (couplage valide)
    "global_min_models_confirmed": 3,
    "global_min_fraction_confirmed": 0.66,
}

# sha256 des corpus AU GEL (PREREGISTRATION_v5.md) — reverifies au run time.
FROZEN_SHA256 = {
    "contested": "3eb7bae8506e97e274f407cf8f6d8357cdc06555d727e71f5aa8f9bb668850f2",
    "consensual": "c4617bfa0750eb33fd6338da3fec0ac7f078619c19ff92b2907a3356af127f63",
}

MODELS = {
    "gpt2": "gpt2",
    "pythia410m": "EleutherAI/pythia-410m",
    "opt350m": "facebook/opt-350m",
    "bloom560m": "bigscience/bloom-560m",
}
ARMS = ("contested", "consensual")
MIN_PAIRS_SPEARMAN = 10
SEED = 0


def _load(path: Path, expected_schema: str) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("pilot_debug_only"):
        raise ValueError(f"{path.name}: sortie PILOTE — non analysable")
    if data.get("schema_version") != expected_schema:
        raise ValueError(f"{path.name}: schema {data.get('schema_version')!r}, "
                         f"attendu {expected_schema!r}")
    return data


def _to_float(arr):
    return np.array([[np.nan if v is None else float(v) for v in row]
                     for row in arr], dtype=float)


def _check_corpus_integrity(probe: dict, arm: str) -> None:
    got = probe.get("corpus_sha256_file")
    want = FROZEN_SHA256[arm]
    if got != want:
        raise ValueError(
            f"{probe['model_id']}/{arm}: sha256 corpus {got!r} != gel {want!r} "
            f"— le corpus mesure n'est pas le corpus gele")


def _features_geo(con: dict, cons: dict) -> tuple[np.ndarray, np.ndarray, int]:
    """X (240, 3L) dans l'ordre [contested; consensual], y = 1 contested."""
    mats = []
    for probe in (con, cons):
        r = probe["results"]
        block = np.concatenate([_to_float(r["o_vol"]),
                                _to_float(r["o_rank"]),
                                _to_float(r["o_aniso"])], axis=1)
        mats.append(block)
    X = np.concatenate(mats, axis=0)
    y = np.concatenate([np.ones(len(mats[0])), np.zeros(len(mats[1]))])
    n_nan = int(np.isnan(X).sum())
    # z-score par colonne sur le corpus poole (texte gele), puis NaN -> 0
    mu = np.nanmean(X, axis=0, keepdims=True)
    sd = np.nanstd(X, axis=0, ddof=1, keepdims=True)
    sd[sd == 0] = 1.0
    X = (X - mu) / sd
    X = np.nan_to_num(X, nan=0.0)
    return X, y, n_nan


def _features_surf(con: dict, cons: dict, corpora_dir: Path) -> np.ndarray:
    """[n_tokens (tokenizer du modele), zipf moyen, nb ponctuation] — (240, 3)."""
    rows = []
    for probe, arm in ((con, "contested"), (cons, "consensual")):
        texts = [l.strip() for l in
                 (corpora_dir / f"{arm}.txt").read_text(encoding="utf-8")
                 .splitlines() if l.strip()]
        if len(texts) != probe["corpus_size"]:
            raise ValueError(f"{arm}: {len(texts)} lignes vs "
                             f"corpus_size={probe['corpus_size']}")
        ntoks = probe["n_tokens_per_statement"]
        for text, nt in zip(texts, ntoks):
            words = re.findall(r"[A-Za-z']+", text.lower())
            zipf = float(np.mean([zipf_frequency(w, "en") for w in words])) \
                if words else 0.0
            punct = sum(1 for c in text if c in string.punctuation)
            rows.append([float(nt), zipf, float(punct)])
    X = np.asarray(rows, dtype=float)
    mu, sd = X.mean(0, keepdims=True), X.std(0, ddof=1, keepdims=True)
    sd[sd == 0] = 1.0
    return (X - mu) / sd


def _oof_scores(X: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    """BA et AUC sur les predictions out-of-fold poolees (plis fixes, seed 0)."""
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    pred = np.zeros_like(y)
    proba = np.zeros_like(y, dtype=float)
    for tr, te in skf.split(X, y):
        clf = LogisticRegression(penalty="l2", C=1.0, solver="lbfgs",
                                 max_iter=5000)
        clf.fit(X[tr], y[tr])
        pred[te] = clf.predict(X[te])
        proba[te] = clf.predict_proba(X[te])[:, 1]
    return (float(balanced_accuracy_score(y, pred)),
            float(roc_auc_score(y, proba)))


def _b1_sanity(con: dict, cons: dict) -> tuple[float, int]:
    """Couplage O_rank<->NLL par couche sur le corpus poole ; max |rho|."""
    o_rank = np.concatenate([_to_float(con["results"]["o_rank"]),
                             _to_float(cons["results"]["o_rank"])], axis=0)
    nll = np.concatenate([_to_float(con["results"]["nll"]),
                          _to_float(cons["results"]["nll"])], axis=0)
    best_rho, best_l = float("nan"), -1
    for l in range(o_rank.shape[1]):
        x, yv = o_rank[:, l], nll[:, l]
        ok = np.isfinite(x) & np.isfinite(yv)
        if ok.sum() < MIN_PAIRS_SPEARMAN or np.ptp(x[ok]) == 0 or np.ptp(yv[ok]) == 0:
            continue
        rho = abs(float(spearmanr(x[ok], yv[ok]).statistic))
        if not np.isfinite(best_rho) or rho > best_rho:
            best_rho, best_l = rho, l
    return best_rho, best_l


def analyze_model(short: str, results_dir: Path, corpora_dir: Path) -> dict:
    con = _load(results_dir / f"{short}_contested_fisher.json", "probe_fisher_v4.0")
    cons = _load(results_dir / f"{short}_consensual_fisher.json", "probe_fisher_v4.0")
    con_sh = _load(results_dir / f"{short}_contested_shuffle.json",
                   "probe_fisher_shuffle_v5.0")
    cons_sh = _load(results_dir / f"{short}_consensual_shuffle.json",
                    "probe_fisher_shuffle_v5.0")
    for probe, arm in ((con, "contested"), (cons, "consensual"),
                       (con_sh, "contested"), (cons_sh, "consensual")):
        _check_corpus_integrity(probe, arm)

    # B1 d'abord : instrument valide, sinon VOID
    b1_rho, b1_layer = _b1_sanity(con, cons)
    b1_pass = bool(np.isfinite(b1_rho)
                   and b1_rho >= THRESHOLDS["B1_min_abs_spearman"])

    Xg, y, n_nan = _features_geo(con, cons)
    ba_geo, auc_geo = _oof_scores(Xg, y)
    Xs = _features_surf(con, cons, corpora_dir)
    ba_surf, auc_surf = _oof_scores(Xs, y)
    Xg_sh, y_sh, n_nan_sh = _features_geo(con_sh, cons_sh)
    ba_shuf, _ = _oof_scores(Xg_sh, y_sh)

    c1 = bool(ba_geo >= THRESHOLDS["C1_min_BA_geo"])
    c2 = bool(auc_geo - auc_surf >= THRESHOLDS["C2_min_AUC_margin"])
    c3 = bool(ba_geo - ba_shuf >= THRESHOLDS["C3_min_BA_shuffle_margin"])

    if not b1_pass:
        verdict = "VOID"
    elif c1 and c2 and c3:
        verdict = "HC_CONFIRME"
    else:
        verdict = "HC_DEMENTI"

    return {
        "model_id": con["model_id"],
        "short": short,
        "n_statements_per_arm": con["corpus_size"],
        "n_features_geo": int(Xg.shape[1]),
        "n_nan_imputed_geo": n_nan,
        "n_nan_imputed_shuffle": n_nan_sh,
        "BA_geo": ba_geo, "AUC_geo": auc_geo,
        "BA_surf": ba_surf, "AUC_surf": auc_surf,
        "BA_geo_shuf": ba_shuf,
        "AUC_margin_C2": auc_geo - auc_surf,
        "BA_margin_C3": ba_geo - ba_shuf,
        "B1_max_abs_rho": None if not np.isfinite(b1_rho) else b1_rho,
        "B1_best_layer": b1_layer,
        "B1_pass": b1_pass,
        "C1_pass": c1, "C2_pass": c2, "C3_pass": c3,
        "verdict": verdict,
    }


def aggregate(per_model: list) -> dict:
    n_total = len(per_model)
    n_conf = sum(1 for r in per_model if r["verdict"] == "HC_CONFIRME")
    n_void = sum(1 for r in per_model if r["verdict"] == "VOID")
    frac = (n_conf / n_total) if n_total else 0.0
    ok = (n_conf >= THRESHOLDS["global_min_models_confirmed"]
          and frac >= THRESHOLDS["global_min_fraction_confirmed"])
    return {
        "n_models_total": n_total,
        "n_models_confirmed": n_conf,
        "n_models_void": n_void,
        "fraction_confirmed": frac,
        "global_verdict": "HC_CONFIRME" if ok else "HC_DEMENTI",
        "note": ("VOID present : instrument invalide sur au moins un modele — "
                 "a traiter avant toute interpretation" if n_void else ""),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default="results")
    ap.add_argument("--corpora", default="corpora")
    ap.add_argument("--out", default="results/analysis_v5_report.json")
    args = ap.parse_args()
    results_dir, corpora_dir = Path(args.results), Path(args.corpora)

    # integrite corpus sur disque AVANT tout (les sondes ont leur propre copie du hash)
    for arm, want in FROZEN_SHA256.items():
        got = hashlib.sha256((corpora_dir / f"{arm}.txt").read_bytes()).hexdigest()
        if got != want:
            raise SystemExit(f"corpora/{arm}.txt: sha256 != gel — STOP")

    per_model = []
    for short in MODELS:
        try:
            r = analyze_model(short, results_dir, corpora_dir)
        except FileNotFoundError as e:
            print(f"[analysis_v5] {short}: fichier manquant ({e.filename}) — saute")
            continue
        per_model.append(r)
        flag = {"HC_CONFIRME": "OK", "HC_DEMENTI": "--", "VOID": "!!"}[r["verdict"]]
        print(f"[{flag}] {r['model_id']:<28} BA_geo={r['BA_geo']:.3f} "
              f"AUC_geo={r['AUC_geo']:.3f} AUC_surf={r['AUC_surf']:.3f} "
              f"BA_shuf={r['BA_geo_shuf']:.3f} "
              f"B1={r['B1_max_abs_rho'] if r['B1_max_abs_rho'] is None else round(r['B1_max_abs_rho'],2)} "
              f"C1={int(r['C1_pass'])} C2={int(r['C2_pass'])} C3={int(r['C3_pass'])} "
              f"-> {r['verdict']}")

    agg = aggregate(per_model)
    print(f"\n=== GLOBAL: {agg['n_models_confirmed']}/{agg['n_models_total']} "
          f"confirmes ({agg['fraction_confirmed']:.0%}), {agg['n_models_void']} VOID "
          f"-> {agg['global_verdict']} ===")

    report = {
        "schema_version": "analysis_v5.0",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "thresholds": THRESHOLDS,
        "frozen_corpus_sha256": FROZEN_SHA256,
        "per_model": per_model,
        "global": agg,
    }
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(report, indent=2))
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
