#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_sweep_v7.py — construit la FAMILLE de corpus emboîtés (M1) et le
corpus NUL de même-vivier (M3-B). Entièrement MODEL-FREE.

======================================================================
DISCIPLINE : ce script ne touche JAMAIS à la géométrie.
Le retrait des paires est piloté uniquement par le classifieur BON MARCHÉ
(TF-IDF ∪ surface ∪ 8 marqueurs). Aucune sortie Fisher n'est lue, aucun
modèle de langue n'est chargé. Il peut donc tourner et être gelé AVANT
toute mesure GPU, sans risque de fuite.
======================================================================

M1 — LE BALAYAGE DE DIFFICULTÉ
    Rung 0 = les 120 paires v6.4. À chaque rung on retire les `step` paires
    que le bon marché sépare le mieux (marge de décision out-of-fold, du
    bon côté), on refit, on recommence. La descente est donc gloutonne :
    elle produit l'axe de difficulté le plus raide possible.

    Pourquoi c'est loyal : le retrait optimise UNIQUEMENT l'échec du bon
    marché. Il ne sait rien de la géométrie. Si la géométrie suit la chute,
    le signal était partagé ; si elle résiste, il ne l'était pas. On ne
    peut pas désirer le résultat en construisant l'axe.

    Plancher : aucun pli LODO ne descend sous MIN_PER_FOLD paires, sinon
    la mesure devient du bruit.

M3-B — LE CORPUS NUL DE MÊME VIVIER
    Les 120 énoncés CONSENSUELS de v6.4 sont répartis en deux bras A/B,
    au hasard mais équilibrés PAR DOMAINE FIN. Les deux bras sortent du
    même vivier : il n'y a, par construction, aucun statut épistémique à
    trouver. Ce que le pipeline y mesure est du bruit pur — c'est le
    plancher end-to-end, mesure GPU comprise.

Sorties (toutes gelables telles quelles) :
    corpora/v7_sweep/rungs.json          — composition de chaque rung
    corpora/v7_sweep/sweep_report.md     — lisible
    corpora/v7_sweep/null_A.txt          — bras A du nul
    corpora/v7_sweep/null_B.txt          — bras B du nul
    corpora/v7_sweep/null_map.json       — domaines du nul

Usage :
    python build_sweep_v7.py
"""

import csv
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy.sparse import csr_matrix, hstack
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score
from wordfreq import zipf_frequency

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))
from diag_v7 import CONSTRUCTION_MARKERS

SEL = Path("corpora/v6_4_proposals/_selected.tsv")
OUT = Path("corpora/v7_sweep")
STEP = 2               # paires retirées par rung — le balayage est gratuit en GPU
MIN_PER_FOLD = 8       # plancher d'effectif par pli LODO
SEED = 0

RX = [re.compile(p, re.I) for p in CONSTRUCTION_MARKERS.values()]
import string as _string


def cheap_features(texts, n_tokens):
    """Bloc dense bon marché : surface v5 + 8 compteurs de construction."""
    rows = []
    for t, nt in zip(texts, n_tokens):
        words = re.findall(r"[A-Za-z']+", t.lower())
        zipf = float(np.mean([zipf_frequency(w, "en") for w in words])) if words else 0.0
        punct = sum(1 for c in t if c in _string.punctuation)
        rows.append([float(nt), zipf, float(punct)]
                    + [float(len(rx.findall(t))) for rx in RX])
    X = np.asarray(rows, dtype=float)
    mu, sd = X.mean(0, keepdims=True), X.std(0, ddof=1, keepdims=True)
    sd[sd == 0] = 1.0
    return (X - mu) / sd


def cheap_lodo(texts, Xd, y, groups, folds):
    """Renvoie (BA, marge signée out-of-fold). Marge > 0 = bien classé, confiant."""
    texts = np.asarray(texts, dtype=object)
    pred = np.zeros_like(y)
    margin = np.zeros(len(y), dtype=float)
    for f in folds:
        te = groups == f
        tr = ~te
        if tr.sum() < 4 or len(set(y[tr])) < 2:
            continue
        v = TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True)
        Xtr = hstack([v.fit_transform(texts[tr]), csr_matrix(Xd[tr])]).tocsr()
        Xte = hstack([v.transform(texts[te]), csr_matrix(Xd[te])]).tocsr()
        clf = LogisticRegression(max_iter=5000).fit(Xtr, y[tr])
        pred[te] = clf.predict(Xte)
        d = clf.decision_function(Xte)
        # marge orientée : positive quand le modèle a raison et est confiant
        margin[te] = d * np.where(y[te] == 1, 1.0, -1.0)
    return balanced_accuracy_score(y, pred), margin


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows = {int(r["line"]): r for r in csv.DictReader(
        SEL.open(encoding="utf-8"), delimiter="\t")}
    lines = list(range(1, 121))
    con = [rows[l]["contested_claim"] for l in lines]
    cns = [rows[l]["proposed_consensual"] for l in lines]
    fine = [rows[l]["fine_domain"] for l in lines]
    sup = [rows[l]["super_domain"] for l in lines]

    # longueurs en tokens gpt2 (surface v5) — chargé une seule fois
    from transformers import AutoTokenizer
    tk = AutoTokenizer.from_pretrained("gpt2")
    ntc = [len(tk(s)["input_ids"]) for s in con]
    nts = [len(tk(s)["input_ids"]) for s in cns]

    folds_all = sorted(set(sup))

    # ---------------------------------------------------------------- M1
    print(f"M1 — balayage glouton, pas={STEP}, plancher={MIN_PER_FOLD}/pli\n")
    alive = list(lines)                      # numéros de ligne encore présents
    rungs = []
    rung_id = 0
    while True:
        idx = [l - 1 for l in alive]
        texts = [con[i] for i in idx] + [cns[i] for i in idx]
        nt = [ntc[i] for i in idx] + [nts[i] for i in idx]
        y = np.concatenate([np.ones(len(idx)), np.zeros(len(idx))])
        groups = np.array([sup[i] for i in idx] * 2)
        folds = sorted(set(groups.tolist()))
        Xd = cheap_features(texts, nt)
        ba, margin = cheap_lodo(texts, Xd, y, groups, folds)

        counts = Counter(sup[i] for i in idx)
        rungs.append({"rung": rung_id, "n_pairs": len(alive),
                      "BA_cheap_lodo": float(ba),
                      "fold_counts": dict(sorted(counts.items())),
                      "lines": list(alive)})
        print(f"  rung {rung_id:>2} : {len(alive):>3} paires   BA_cheap = {ba:.4f}")

        # candidats au retrait : plus grande marge (bien classé + confiant),
        # en respectant le plancher par pli
        pair_margin = {}
        for j, l in enumerate(alive):
            pair_margin[l] = float(margin[j] + margin[j + len(alive)])
        removable = [l for l in alive
                     if counts[sup[l - 1]] > MIN_PER_FOLD]
        if len(removable) < STEP or len(alive) - STEP < MIN_PER_FOLD * len(folds_all):
            print(f"\n  plancher atteint — arrêt à {len(alive)} paires")
            break
        # retirer STEP paires, en re-vérifiant le plancher à chaque retrait
        order = sorted(removable, key=lambda l: -pair_margin[l])
        removed = 0
        for l in order:
            if removed == STEP:
                break
            if counts[sup[l - 1]] > MIN_PER_FOLD:
                alive.remove(l)
                counts[sup[l - 1]] -= 1
                removed += 1
        if removed == 0:
            print("\n  plus rien de retirable sans casser un pli — arrêt")
            break
        rung_id += 1

    # ---------------------------------------------------------------- M3-B
    print(f"\nM3-B — corpus nul de même vivier (les {len(lines)} consensuels "
          f"répartis A/B par domaine fin)")
    rng = np.random.default_rng(SEED)
    by_fine = defaultdict(list)
    for l in lines:
        by_fine[fine[l - 1]].append(l)
    arm_a, arm_b = [], []
    for d in sorted(by_fine):
        grp = list(by_fine[d])
        rng.shuffle(grp)
        half = len(grp) // 2
        arm_a.extend(grp[:half])
        arm_b.extend(grp[half:2 * half])       # taille égale, reste écarté
    arm_a.sort(); arm_b.sort()
    print(f"  bras A : {len(arm_a)} énoncés | bras B : {len(arm_b)} énoncés "
          f"| écartés (domaines impairs) : {len(lines) - len(arm_a) - len(arm_b)}")

    (OUT / "null_A.txt").write_text(
        "\n".join(cns[l - 1] for l in arm_a) + "\n", encoding="utf-8")
    (OUT / "null_B.txt").write_text(
        "\n".join(cns[l - 1] for l in arm_b) + "\n", encoding="utf-8")
    null_map = {"seed": SEED,
                "source": "corpora/v6_4_proposals/_selected.tsv (bras consensuel)",
                "arm_A_lines": arm_a, "arm_B_lines": arm_b,
                "arm_A_super": [sup[l - 1] for l in arm_a],
                "arm_B_super": [sup[l - 1] for l in arm_b],
                "arm_A_fine": [fine[l - 1] for l in arm_a],
                "arm_B_fine": [fine[l - 1] for l in arm_b]}
    (OUT / "null_map.json").write_text(json.dumps(null_map, indent=2), encoding="utf-8")

    # ---------------------------------------------------------------- gel
    payload = {"schema_version": "sweep_v7.0", "step": STEP,
               "min_per_fold": MIN_PER_FOLD, "seed": SEED,
               "source_tsv_sha256": hashlib.sha256(SEL.read_bytes()).hexdigest(),
               "n_rungs": len(rungs), "rungs": rungs}
    (OUT / "rungs.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    R = [f"# Famille de corpus v7 — {len(rungs)} rungs\n\n",
         f"Construit par `build_sweep_v7.py`, **model-free** : le retrait est "
         f"piloté par le seul classifieur bon marché, jamais par la géométrie.\n\n",
         f"- pas : **{STEP}** paires par rung · plancher : **{MIN_PER_FOLD}** "
         f"paires par pli LODO\n",
         f"- descente : **{rungs[0]['n_pairs']} → {rungs[-1]['n_pairs']}** paires\n",
         f"- BA_cheap : **{rungs[0]['BA_cheap_lodo']:.4f} → "
         f"{rungs[-1]['BA_cheap_lodo']:.4f}**\n\n",
         "| rung | paires | BA_cheap LODO |\n|---:|---:|---:|\n"]
    for r in rungs:
        R.append(f"| {r['rung']} | {r['n_pairs']} | {r['BA_cheap_lodo']:.4f} |\n")
    R.append(f"\n## Corpus nul (M3-B)\n\nLes {len(lines)} énoncés consensuels de "
             f"v6.4 répartis en deux bras de **{len(arm_a)}**, équilibrés par "
             f"domaine fin, graine {SEED}. Même vivier des deux côtés : il n'y a "
             f"rien à trouver. Ce que le pipeline y mesure est le plancher réel, "
             f"mesure GPU comprise.\n")
    (OUT / "sweep_report.md").write_text("".join(R), encoding="utf-8")

    print(f"\nwrote {OUT}/rungs.json ({len(rungs)} rungs), null_A/B.txt, "
          f"null_map.json, sweep_report.md")
    print(f"BA_cheap : {rungs[0]['BA_cheap_lodo']:.4f} → "
          f"{rungs[-1]['BA_cheap_lodo']:.4f}")


if __name__ == "__main__":
    main()
