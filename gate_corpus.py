#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gate_corpus.py — porte qualité de corpus FALSIFIABLE, model-free
================================================================

Remplace la porte G1 de v6.3, devenue non falsifiable.

**La leçon de v6.3.** Sa porte portait sur 8 marqueurs enregistrés. Le tour 1 a
rendu ces 8 compteurs *identiques paire par paire* : le classifieur n'a plus
aucune information, BA = 0,5000 devient une identité arithmétique, p = 1,0, et
tous les quantiles de permutation valent 0,5000. Une porte qui ne peut plus
échouer ne mesure plus rien — la mesure était devenue la cible.

**Le principe retenu ici.** Une porte doit s'appuyer sur des traits que la
construction n'a PAS optimisés, et doit **détecter sa propre dégénérescence**.

Quatre contrôles, aucun ne peut être satisfait par construction sans que le
corpus soit réellement meilleur :

  A — TF-IDF seul en LODO. Le vocabulaire complet, pas une liste de marqueurs :
      on ne peut pas l'équilibrer mot à mot sans détruire le sens.
  B — mots à sens unique. Part des énoncés portant au moins un mot fréquent
      dans son bras et TOTALEMENT absent de l'autre. C'est ce qui a attrapé
      `chiefly` 7/0 et `exceed*` 0/15 dans v6.3.
  C — recouvrement de sujet par paire. Les deux membres d'une paire doivent
      parler de la MÊME chose ; sinon on a fermé un confond de forme en
      rouvrant un confond de contenu.
  D — détecteur de marqueurs, avec **alarme de dégénérescence** : si les
      vecteurs de marqueurs sont identiques dans plus de 95 % des paires, le
      résultat est déclaré VACUOUS et ne compte pas comme un succès.

Aucun seuil n'est gelé dans ce fichier : ils s'affichent avec la distance à des
valeurs *proposées*, que le chercheur valide ou corrige avant tout gel.

Usage :
    python gate_corpus.py --contested corpora/v6_3/contested.txt \
                          --consensual corpora/v6_3/consensual.txt
    python gate_corpus.py --evidence corpora/v6_3/evidence.tsv
    python gate_corpus.py --contested corpora/contested.txt \
                          --consensual corpora/consensual_v6.txt   # reference v6
"""

import argparse
import collections
import csv
import json
import re
import sys
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))
from diag_v7 import CONSTRUCTION_MARKERS

# Seuils PROPOSÉS — non gelés, à valider par le chercheur.
PROPOSED = {
    "A_tfidf_lodo_max": 0.60,
    "B_onesided_coverage_max": 0.15,   # part d'énoncés portant un mot à sens unique
    "C_median_subject_overlap_min": 2,  # mots de contenu partagés, médiane par paire
    "D_degeneracy_max_identical": 0.95,
}
MIN_COUNT_ONESIDED = 3   # un mot doit apparaître au moins 3 fois pour compter


def load(args):
    if args.evidence:
        rows = list(csv.DictReader(open(args.evidence, encoding="utf-8"),
                                   delimiter="\t"))
        con = [r["contested_claim"].strip() for r in rows]
        cns = [r["consensual_claim"].strip() for r in rows]
        sup = [r["super_domain"].strip() for r in rows]
        return con, cns, sup
    con = [l.strip() for l in Path(args.contested).read_text(
        encoding="utf-8").splitlines() if l.strip()]
    cns = [l.strip() for l in Path(args.consensual).read_text(
        encoding="utf-8").splitlines() if l.strip()]
    dm = json.loads(Path(args.domain_map).read_text(encoding="utf-8"))
    sup = [dm["fine_to_super"][d] for d in dm["per_line_fine_domain"]]
    return con, cns, sup


def content_words(s):
    return {w for w in re.findall(r"[a-z']+", s.lower())
            if w not in ENGLISH_STOP_WORDS and len(w) > 2}


def lodo_ba(X_builder, y, groups, folds, texts):
    pred = np.zeros_like(y)
    for f in folds:
        te = groups == f
        Xtr, Xte = X_builder(texts[~te], texts[te])
        pred[te] = LogisticRegression(max_iter=5000).fit(Xtr, y[~te]).predict(Xte)
    return balanced_accuracy_score(y, pred)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--contested")
    ap.add_argument("--consensual")
    ap.add_argument("--evidence")
    ap.add_argument("--domain-map", default="corpora/domain_map_v6.json")
    ap.add_argument("--out")
    args = ap.parse_args()

    con, cns, sup = load(args)
    n = len(con)
    assert len(cns) == n == len(sup), "bras désalignés"
    y = np.concatenate([np.ones(n), np.zeros(n)])
    groups = np.array(sup + sup)
    folds = sorted(set(sup))
    texts = np.array(con + cns, dtype=object)
    rep = {"n_pairs": n, "proposed_thresholds": PROPOSED, "checks": {}}

    print(f"Porte qualité de corpus — {n} paires, {len(folds)} plis LODO")
    print("Seuils PROPOSÉS, non gelés. Aucun modèle de langue n'est chargé.\n")

    # --- A : TF-IDF seul
    def tfidf(a, b):
        v = TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True)
        return v.fit_transform(a), v.transform(b)
    ba_tfidf = lodo_ba(tfidf, y, groups, folds, texts)
    okA = ba_tfidf <= PROPOSED["A_tfidf_lodo_max"]
    rep["checks"]["A_tfidf_lodo"] = {"value": ba_tfidf, "pass": bool(okA)}
    print(f"[{'OK' if okA else '--'}] A  TF-IDF seul, LODO      BA = {ba_tfidf:.4f}"
          f"   (seuil proposé <= {PROPOSED['A_tfidf_lodo_max']}, "
          f"écart {ba_tfidf - PROPOSED['A_tfidf_lodo_max']:+.4f})")

    # --- B : mots à sens unique
    ca = collections.Counter(w for s in con for w in re.findall(r"[a-z']+", s.lower()))
    cb = collections.Counter(w for s in cns for w in re.findall(r"[a-z']+", s.lower()))
    one_con = {w for w, c in ca.items() if c >= MIN_COUNT_ONESIDED and cb[w] == 0}
    one_cns = {w for w, c in cb.items() if c >= MIN_COUNT_ONESIDED and ca[w] == 0}
    carried = sum(1 for s in con if set(re.findall(r"[a-z']+", s.lower())) & one_con)
    carried += sum(1 for s in cns if set(re.findall(r"[a-z']+", s.lower())) & one_cns)
    cov = carried / (2 * n)
    okB = cov <= PROPOSED["B_onesided_coverage_max"]
    rep["checks"]["B_onesided_coverage"] = {
        "value": cov, "pass": bool(okB),
        "words_contested_only": sorted(one_con, key=lambda w: -ca[w]),
        "words_consensual_only": sorted(one_cns, key=lambda w: -cb[w])}
    print(f"[{'OK' if okB else '--'}] B  mots à sens unique     {cov:.1%} des énoncés"
          f"   (seuil proposé <= {PROPOSED['B_onesided_coverage_max']:.0%})")
    if one_con:
        print("       contesté seul   : " + ", ".join(
            f"{w}({ca[w]})" for w in sorted(one_con, key=lambda w: -ca[w])[:10]))
    if one_cns:
        print("       consensuel seul : " + ", ".join(
            f"{w}({cb[w]})" for w in sorted(one_cns, key=lambda w: -cb[w])[:10]))

    # --- C : recouvrement de sujet par paire
    ov = [len(content_words(a) & content_words(b)) for a, b in zip(con, cns)]
    med = float(np.median(ov))
    zero = int(sum(1 for x in ov if x == 0))
    okC = med >= PROPOSED["C_median_subject_overlap_min"]
    rep["checks"]["C_subject_overlap"] = {
        "median": med, "n_zero_overlap": zero, "pass": bool(okC),
        "lines_zero_overlap": [i + 1 for i, x in enumerate(ov) if x == 0]}
    print(f"[{'OK' if okC else '--'}] C  recouvrement de sujet  médiane = {med:.1f} mots"
          f"   ({zero}/{n} paires à recouvrement NUL)"
          f"   (seuil proposé >= {PROPOSED['C_median_subject_overlap_min']})")

    # --- D : détecteur de marqueurs + alarme de dégénérescence
    RX = [re.compile(p, re.I) for p in CONSTRUCTION_MARKERS.values()]
    vec = lambda s: tuple(len(rx.findall(s)) for rx in RX)
    identical = sum(1 for a, b in zip(con, cns) if vec(a) == vec(b)) / n
    Xm = np.array([vec(s) for s in con] + [vec(s) for s in cns], float)
    pred = np.zeros_like(y)
    for f in folds:
        te = groups == f
        pred[te] = LogisticRegression(max_iter=5000).fit(Xm[~te], y[~te]).predict(Xm[te])
    ba_mark = balanced_accuracy_score(y, pred)
    vacuous = identical > PROPOSED["D_degeneracy_max_identical"]
    rep["checks"]["D_markers"] = {"value": ba_mark, "identical_fraction": identical,
                                  "vacuous": bool(vacuous)}
    tag = "!!" if vacuous else "OK"
    print(f"[{tag}] D  marqueurs enregistrés  BA = {ba_mark:.4f}"
          f"   ({identical:.0%} de paires à vecteur identique)")
    if vacuous:
        print("       >>> VACUOUS : les vecteurs sont identiques par construction.")
        print("       >>> BA = 0,5 est une identité arithmétique, PAS un succès.")
        print("       >>> Ce contrôle ne compte pas comme passé.")

    passed = okA and okB and okC and not vacuous
    rep["overall_pass_proposed"] = bool(passed)
    print(f"\n=== {'PASSE' if passed else 'NE PASSE PAS'} les seuils proposés ===")
    print("Rappel : ces seuils ne sont pas gelés. Ils doivent être validés par le")
    print("chercheur AVANT construction du corpus qu'ils jugeront.")

    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(rep, indent=2))
        print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
