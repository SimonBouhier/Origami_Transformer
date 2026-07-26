#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
analysis_sweep_v7.py — cartographie difficulté × capacité

Pour chaque MODÈLE et chaque RUNG de la famille gelée, calcule :
    BA_geo_lodo, BA_cheap_lodo, marge = BA_geo − BA_cheap
    IC 95 % bootstrap APPARIÉ (rééchantillonnage de PAIRES, pas d'énoncés)
    MDL : longueur de code en ligne et compression, géo vs bon marché
    permutation d'étiquettes (M3-A) : plancher de hasard au MÊME n
    B1 (garde-fou instrument)

Les observables Fisher d'un énoncé ne dépendent pas des autres énoncés :
un modèle n'est donc mesuré QU'UNE FOIS sur les 120 paires, et chaque rung
est un sous-ensemble ré-analysé en CPU. Le balayage ne coûte aucun GPU.

Usage :
    python analysis_sweep_v7.py --results results_v7 --out results_v7/sweep_report.json
    python analysis_sweep_v7.py --results results_v7 --null      # corpus nul M3-B
"""

import argparse
import csv
import json
import re
import string
import sys
from pathlib import Path

import numpy as np
from scipy.sparse import csr_matrix, hstack
from scipy.stats import spearmanr
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, roc_auc_score
from wordfreq import zipf_frequency

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))
from diag_v7 import CONSTRUCTION_MARKERS
from mdl import online_codelength

RX = [re.compile(p, re.I) for p in CONSTRUCTION_MARKERS.values()]
N_BOOT = 2000
BOOT_SEED = 12345
N_PERM = 200
PERM_SEED = 777
B1_MIN = 0.30


# --------------------------------------------------------------------------- #
def load_probe(path: Path) -> dict:
    d = json.loads(path.read_text(encoding="utf-8"))
    if d.get("pilot_debug_only"):
        raise SystemExit(f"{path.name} : sortie PILOTE — non analysable")
    return d


def _f(block):
    return np.array([[np.nan if v is None else float(v) for v in row]
                     for row in block], dtype=float)


def geo_matrix(probe):
    r = probe["results"]
    return np.concatenate([_f(r["o_vol"]), _f(r["o_rank"]), _f(r["o_aniso"])], axis=1)


def zscore_pool(X):
    mu = np.nanmean(X, axis=0, keepdims=True)
    sd = np.nanstd(X, axis=0, ddof=1, keepdims=True)
    sd[sd == 0] = 1.0
    return np.nan_to_num((X - mu) / sd, nan=0.0)


def cheap_dense(texts, n_tokens):
    rows = []
    for t, nt in zip(texts, n_tokens):
        w = re.findall(r"[A-Za-z']+", t.lower())
        zipf = float(np.mean([zipf_frequency(x, "en") for x in w])) if w else 0.0
        punct = sum(1 for c in t if c in string.punctuation)
        rows.append([float(nt), zipf, float(punct)]
                    + [float(len(rx.findall(t))) for rx in RX])
    X = np.asarray(rows, dtype=float)
    mu, sd = X.mean(0, keepdims=True), X.std(0, ddof=1, keepdims=True)
    sd[sd == 0] = 1.0
    return (X - mu) / sd


def lodo_pred(X, y, groups, folds):
    pred = np.zeros_like(y)
    proba = np.zeros(len(y), dtype=float)
    for f in folds:
        te = groups == f
        tr = ~te
        clf = LogisticRegression(max_iter=5000).fit(X[tr], y[tr])
        pred[te] = clf.predict(X[te])
        proba[te] = clf.predict_proba(X[te])[:, 1]
    return pred, proba


def lodo_pred_cheap(texts, Xd, y, groups, folds):
    texts = np.asarray(texts, dtype=object)
    pred = np.zeros_like(y)
    proba = np.zeros(len(y), dtype=float)
    for f in folds:
        te = groups == f
        tr = ~te
        v = TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True)
        Xtr = hstack([v.fit_transform(texts[tr]), csr_matrix(Xd[tr])]).tocsr()
        Xte = hstack([v.transform(texts[te]), csr_matrix(Xd[te])]).tocsr()
        clf = LogisticRegression(max_iter=5000).fit(Xtr, y[tr])
        pred[te] = clf.predict(Xte)
        proba[te] = clf.predict_proba(Xte)[:, 1]
    return pred, proba


def boot_margin(y, pred_a, pred_b, n_pairs, n=N_BOOT, seed=BOOT_SEED):
    """Bootstrap APPARIÉ : on rééchantillonne des PAIRES, pas des énoncés.
    Chaque paire tirée fait entrer ses deux membres — la structure du design
    est ainsi respectée."""
    rng = np.random.default_rng(seed)
    ba_a, ba_b, diff = [], [], []
    for _ in range(n):
        take_pairs = rng.integers(0, n_pairs, n_pairs)
        idx = np.concatenate([take_pairs, take_pairs + n_pairs])
        a = balanced_accuracy_score(y[idx], pred_a[idx])
        b = balanced_accuracy_score(y[idx], pred_b[idx])
        ba_a.append(a); ba_b.append(b); diff.append(a - b)
    q = lambda v, p: float(np.percentile(v, p))
    return {"BA_geo_ci95": [q(ba_a, 2.5), q(ba_a, 97.5)],
            "BA_cheap_ci95": [q(ba_b, 2.5), q(ba_b, 97.5)],
            "margin_ci95": [q(diff, 2.5), q(diff, 97.5)],
            "margin_frac_above_0": float(np.mean(np.array(diff) > 0))}


def perm_floor(X, y, groups, folds, n_pairs, n=N_PERM, seed=PERM_SEED):
    """M3-A — plancher de hasard par permutation d'étiquettes, au MÊME n,
    mêmes features, mêmes plis. Les étiquettes sont permutées ENTRE PAIRES
    (on échange les deux membres d'une paire ou non), ce qui préserve
    exactement la structure appariée."""
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(n):
        flip = rng.random(n_pairs) < 0.5
        yp = y.copy()
        yp[:n_pairs] = np.where(flip, 0.0, 1.0)
        yp[n_pairs:] = np.where(flip, 1.0, 0.0)
        pred, _ = lodo_pred(X, yp, groups, folds)
        out.append(balanced_accuracy_score(yp, pred))
    return {"mean": float(np.mean(out)), "p95": float(np.percentile(out, 95)),
            "p99": float(np.percentile(out, 99)), "max": float(np.max(out)),
            "n_perm": n}


def b1_sanity(con, cons, idx):
    o = np.concatenate([_f(con["results"]["o_rank"])[idx],
                        _f(cons["results"]["o_rank"])[idx]], axis=0)
    nl = np.concatenate([_f(con["results"]["nll"])[idx],
                         _f(cons["results"]["nll"])[idx]], axis=0)
    best = float("nan")
    for l in range(o.shape[1]):
        x, yv = o[:, l], nl[:, l]
        ok = np.isfinite(x) & np.isfinite(yv)
        if ok.sum() < 10 or np.ptp(x[ok]) == 0 or np.ptp(yv[ok]) == 0:
            continue
        r = abs(float(spearmanr(x[ok], yv[ok]).statistic))
        if not np.isfinite(best) or r > best:
            best = r
    return best



# --------------------------------------------------------------------------- #
# M3-B — corpus nul de même vivier : le plancher END-TO-END, mesure GPU comprise
# --------------------------------------------------------------------------- #
def analyze_null(R: Path, out_path: Path):
    nm = json.loads(Path("corpora/v7_sweep/null_map.json").read_text(encoding="utf-8"))
    ta = [l.strip() for l in Path("corpora/v7_sweep/null_A.txt").read_text(
        encoding="utf-8").splitlines() if l.strip()]
    tb = [l.strip() for l in Path("corpora/v7_sweep/null_B.txt").read_text(
        encoding="utf-8").splitlines() if l.strip()]
    n = len(ta)
    models = sorted({p.name.split("_nullA_fisher")[0]
                     for p in R.glob("*_nullA_fisher.json")})
    if not models:
        raise SystemExit(f"aucune mesure nulle dans {R}")
    print(f"CORPUS NUL — {n}+{n} énoncés du MÊME vivier consensuel.")
    print("Par construction il n'y a rien à trouver : ce qui sort est le plancher.\n")

    rep = {"schema_version": "sweep_v7_null.0", "n_per_arm": n, "per_model": {}}
    for m in models:
        A = load_probe(R / f"{m}_nullA_fisher.json")
        B = load_probe(R / f"{m}_nullB_fisher.json")
        y = np.concatenate([np.ones(n), np.zeros(n)])
        groups = np.array(nm["arm_A_super"] + nm["arm_B_super"])
        folds = sorted(set(groups.tolist()))
        texts = ta + tb
        nt = A["n_tokens_per_statement"] + B["n_tokens_per_statement"]
        Xg = zscore_pool(np.concatenate([geo_matrix(A), geo_matrix(B)], 0))
        Xd = cheap_dense(texts, nt)
        pg, _ = lodo_pred(Xg, y, groups, folds)
        pc, _ = lodo_pred_cheap(texts, Xd, y, groups, folds)
        ba_g = float(balanced_accuracy_score(y, pg))
        ba_c = float(balanced_accuracy_score(y, pc))
        bs = boot_margin(y, pg, pc, n)
        pf = perm_floor(Xg, y, groups, folds, n)
        rep["per_model"][m] = {
            "model_id": A["model_id"], "BA_geo_lodo": ba_g,
            "BA_cheap_lodo": ba_c, "margin": ba_g - ba_c,
            "bootstrap": bs, "perm_floor_geo": pf,
            "mdl_geo": online_codelength(Xg, y, groups)}
        print(f"  {A['model_id']:<26} geo={ba_g:.4f} cheap={ba_c:.4f} "
              f"marge={ba_g-ba_c:+.4f} [{bs['margin_ci95'][0]:+.3f},"
              f"{bs['margin_ci95'][1]:+.3f}]  perm95={pf['p95']:.3f}")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(rep, indent=2))
    print(f"\nwrote {out_path}")
    print("Lecture : toute BA_geo proche de perm95 ou en dessous = bruit. "
          "Un écart net ici serait un ARTEFACT du pipeline, à corriger avant "
          "d'interpréter quoi que ce soit du corpus réel.")


# --------------------------------------------------------------------------- #
def analyze_rung(model, rung, con, cons, con_sh, cons_sh, meta, do_perm):
    lines = rung["lines"]
    idx = np.array([l - 1 for l in lines])
    n = len(idx)
    y = np.concatenate([np.ones(n), np.zeros(n)])
    groups = np.array([meta["super"][i] for i in idx] * 2)
    folds = sorted(set(groups.tolist()))
    texts = [meta["con"][i] for i in idx] + [meta["cns"][i] for i in idx]
    nt = ([con["n_tokens_per_statement"][i] for i in idx]
          + [cons["n_tokens_per_statement"][i] for i in idx])

    Xg = zscore_pool(np.concatenate([geo_matrix(con)[idx], geo_matrix(cons)[idx]], 0))
    Xs = zscore_pool(np.concatenate([geo_matrix(con_sh)[idx],
                                     geo_matrix(cons_sh)[idx]], 0))
    Xd = cheap_dense(texts, nt)

    pg, prg = lodo_pred(Xg, y, groups, folds)
    pc, _ = lodo_pred_cheap(texts, Xd, y, groups, folds)
    ps, _ = lodo_pred(Xs, y, groups, folds)

    ba_g = float(balanced_accuracy_score(y, pg))
    ba_c = float(balanced_accuracy_score(y, pc))
    ba_s = float(balanced_accuracy_score(y, ps))

    # MDL — même structure de blocs
    ta = np.asarray(texts, dtype=object)

    def sparse_builder(mtr, mte):
        v = TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True)
        return (hstack([v.fit_transform(ta[mtr]), csr_matrix(Xd[mtr])]).tocsr(),
                hstack([v.transform(ta[mte]), csr_matrix(Xd[mte])]).tocsr())

    mdl_g = online_codelength(Xg, y, groups)
    mdl_c = online_codelength(None, y, groups, sparse_builder=sparse_builder)

    res = {
        "rung": rung["rung"], "n_pairs": n,
        "BA_geo_lodo": ba_g, "BA_cheap_lodo": ba_c, "BA_geo_shuf_lodo": ba_s,
        "AUC_geo_lodo": float(roc_auc_score(y, prg)),
        "margin_vs_cheap": ba_g - ba_c, "margin_vs_shuffle": ba_g - ba_s,
        "bootstrap": boot_margin(y, pg, pc, n),
        "mdl_geo": mdl_g, "mdl_cheap": mdl_c,
        "mdl_compression_gap": mdl_g["compression"] - mdl_c["compression"],
        "B1_max_abs_rho": b1_sanity(con, cons, idx),
    }
    res["B1_pass"] = bool(np.isfinite(res["B1_max_abs_rho"])
                          and res["B1_max_abs_rho"] >= B1_MIN)
    if do_perm:
        res["perm_floor_geo"] = perm_floor(Xg, y, groups, folds, n)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default="results_v7")
    ap.add_argument("--rungs", default="corpora/v7_sweep/rungs.json")
    ap.add_argument("--selected", default="corpora/v6_4_proposals/_selected.tsv")
    ap.add_argument("--out", default="results_v7/sweep_report.json")
    ap.add_argument("--null", action="store_true",
                    help="analyser le corpus NUL (M3-B) au lieu du balayage")
    ap.add_argument("--perm-every", type=int, default=4,
                    help="permutation d'étiquettes tous les N rungs (coût CPU)")
    args = ap.parse_args()

    R = Path(args.results)
    if args.null:
        analyze_null(R, Path(args.out).with_name('null_report.json'))
        return
    rungs = json.loads(Path(args.rungs).read_text(encoding="utf-8"))
    rows = {int(r["line"]): r for r in csv.DictReader(
        Path(args.selected).open(encoding="utf-8"), delimiter="\t")}
    meta = {"con": [rows[l]["contested_claim"] for l in range(1, 121)],
            "cns": [rows[l]["proposed_consensual"] for l in range(1, 121)],
            "super": [rows[l]["super_domain"] for l in range(1, 121)]}

    models = sorted({p.name.split("_contested_fisher")[0]
                     for p in R.glob("*_contested_fisher.json")})
    if not models:
        raise SystemExit(f"aucune mesure dans {R} — lancer la campagne GPU d'abord")
    print(f"{len(models)} modèle(s) : {', '.join(models)}")
    print(f"{rungs['n_rungs']} rungs · bootstrap {N_BOOT} · permutation tous les "
          f"{args.perm_every} rungs\n")

    report = {"schema_version": "sweep_v7.0",
              "rungs_source_sha_tsv": rungs["source_tsv_sha256"],
              "n_boot": N_BOOT, "n_perm": N_PERM, "per_model": {}}

    for m in models:
        con = load_probe(R / f"{m}_contested_fisher.json")
        cons = load_probe(R / f"{m}_consensual_fisher.json")
        con_sh = load_probe(R / f"{m}_contested_shuffle.json")
        cons_sh = load_probe(R / f"{m}_consensual_shuffle.json")
        print(f"--- {con['model_id']}")
        out = []
        for rung in rungs["rungs"]:
            r = analyze_rung(m, rung, con, cons, con_sh, cons_sh, meta,
                             do_perm=(rung["rung"] % args.perm_every == 0))
            out.append(r)
            ci = r["bootstrap"]["margin_ci95"]
            flag = "+" if ci[0] > 0 else " "
            pf = r.get("perm_floor_geo")
            pfs = f" perm95={pf['p95']:.3f}" if pf else ""
            print(f"  rung {r['rung']:>2} n={r['n_pairs']:>3}  "
                  f"geo={r['BA_geo_lodo']:.3f} cheap={r['BA_cheap_lodo']:.3f}  "
                  f"marge={r['margin_vs_cheap']:+.3f} "
                  f"[{ci[0]:+.3f},{ci[1]:+.3f}]{flag}  "
                  f"MDLgap={r['mdl_compression_gap']:+.3f}  "
                  f"B1={r['B1_max_abs_rho']:.2f}{pfs}")
        report["per_model"][m] = {"model_id": con["model_id"],
                                  "n_layers": con["n_layers"],
                                  "hidden_dim": con["hidden_dim"], "rungs": out}
        pos = sum(1 for r in out if r["bootstrap"]["margin_ci95"][0] > 0)
        print(f"  >>> marge strictement positive (IC bas > 0) sur "
              f"{pos}/{len(out)} rungs\n")

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(report, indent=2))
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
