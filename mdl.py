#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mdl.py — longueur de description minimale (Voita & Titov 2020, codage en ligne)

POURQUOI. Comparer une exactitude sur 39 features géométriques à une exactitude
sur ~10 000 features TF-IDF est bancal : un relecteur objectera que les deux
espaces n'ont pas la même capacité. Le codage prequentiel répond à l'objection
en mesurant, non la justesse, mais **le coût de transmettre les étiquettes quand
on connaît déjà les features**. Un espace qui « sait » vraiment quelque chose
comprime ; un espace qui mémorise ne comprime pas.

VARIANTE RETENUE — codage en ligne PAR BLOCS DE DOMAINE.
Voita & Titov ordonnent les données au hasard. Ici les blocs sont les
**super-domaines** : chaque bloc est prédit par un modèle entraîné sur les blocs
précédents uniquement. La mesure est donc à la fois équitable en dimension ET
hors-domaine, comme le reste du protocole. On moyenne sur plusieurs ordres de
domaines tirés au sort, l'ordre étant arbitraire.

    L_online = n_1·log2(K)  +  Σ_{b≥2} [ −Σ_{i∈b} log2 p_θ(b−1)(y_i | x_i) ]

    compression = L_uniforme / L_online ,  L_uniforme = n·log2(K)

    compression > 1 : les features informent sur l'étiquette.
    compression ≈ 1 : elles n'apprennent rien de transmissible.

Les probabilités sont bornées à [eps, 1−eps] : sans cela une seule prédiction
sûre et fausse enverrait la longueur de code à l'infini.
"""

import numpy as np
from sklearn.linear_model import LogisticRegression

EPS = 1e-6
N_ORDERS = 20          # ordres de domaines tirés au sort, puis moyennés
SEED = 0


def _codelength_one_order(fit_predict_proba, y, groups, order):
    """Longueur de code en ligne pour un ordre de blocs donné, en bits."""
    n_classes = 2
    first = groups == order[0]
    bits = float(first.sum()) * np.log2(n_classes)      # 1er bloc : code uniforme
    seen = first.copy()
    for g in order[1:]:
        cur = groups == g
        if seen.sum() < 4 or len(np.unique(y[seen])) < 2:
            bits += float(cur.sum()) * np.log2(n_classes)   # repli : uniforme
            seen |= cur
            continue
        p = fit_predict_proba(seen, cur)                # p(classe 1) sur le bloc
        p = np.clip(p, EPS, 1.0 - EPS)
        py = np.where(y[cur] == 1, p, 1.0 - p)
        bits += float(-np.log2(py).sum())
        seen |= cur
    return bits


def online_codelength(X, y, groups, n_orders=N_ORDERS, seed=SEED, sparse_builder=None):
    """Longueur de code en ligne moyenne (bits) et taux de compression.

    X / sparse_builder :
      - X dense fourni  -> le classifieur est ajusté sur X[train] ;
      - sparse_builder  -> callable(mask_train, mask_test) -> (Xtr, Xte),
        pour les blocs qui doivent être RÉAJUSTÉS par pli (TF-IDF).
    """
    y = np.asarray(y)
    groups = np.asarray(groups)
    uniq = sorted(set(groups.tolist()))
    rng = np.random.default_rng(seed)

    def fit_predict_proba(mask_tr, mask_te):
        if sparse_builder is not None:
            Xtr, Xte = sparse_builder(mask_tr, mask_te)
        else:
            Xtr, Xte = X[mask_tr], X[mask_te]
        clf = LogisticRegression(max_iter=5000).fit(Xtr, y[mask_tr])
        return clf.predict_proba(Xte)[:, 1]

    lengths = []
    for _ in range(n_orders):
        order = list(uniq)
        rng.shuffle(order)
        lengths.append(_codelength_one_order(fit_predict_proba, y, groups, order))

    L = float(np.mean(lengths))
    L_uniform = float(len(y)) * np.log2(2)
    return {"codelength_bits": L,
            "codelength_std": float(np.std(lengths)),
            "uniform_bits": L_uniform,
            "compression": L_uniform / L if L > 0 else float("nan"),
            "n_orders": n_orders}
