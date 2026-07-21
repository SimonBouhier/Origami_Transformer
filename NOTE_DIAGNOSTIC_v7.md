# Note de diagnostic — préparation v7

**Date :** 2026-07-21
**Statut :** **descriptif, HORS VERDICT.** Ne modifie aucun seuil, aucun gel,
aucun verdict. Répond aux points 2 et 3 des « Prochaines marches » de
`NOTE_RESULTATS_v6.md`, en réutilisant les mesures v6 : aucune nouvelle passe
modèle n'a été faite.
**Script :** `diag_v7.py` → `results/diag_v7_report.json`

---

## D1 — Décomposition de la baseline : le confond est la construction

Sous les **mêmes plis LODO** que le verdict v6, quatre blocs bon marché :

| bloc | gpt2 | pythia | opt | bloom |
|---|---|---|---|---|
| surface seule (v5) | 0,583 | 0,579 | 0,583 | 0,554 |
| TF-IDF seul | 0,725 | 0,725 | 0,725 | 0,725 |
| union = **O2 gelé v6** | 0,738 | 0,754 | 0,738 | 0,746 |
| **construction seule (8 regex)** | **0,762** | **0,762** | **0,762** | **0,762** |
| *géométrie (rappel)* | *0,629* | *0,746* | *0,750* | *0,817* |

Les 8 marqueurs : comparatif, attribution causale, modal/irréalis, quantificateur
de portée, copule définitionnelle, négation, préposition de mécanisme, nom
abstrait méta. Comptages regex, rien d'autre.

**Trois choses, toutes importantes.**

1. **La surface ne portait presque rien** (0,55–0,58). Le durcissement pré-gel de
   O2 (TF-IDF ∪ surface) n'a ajouté que ~1,5 point au TF-IDF seul. Ce n'est pas
   là que se jouait le démenti.

2. **Huit compteurs regex battent la baseline gelée entière** (0,762 > 0,738–0,754),
   et battent la géométrie sur trois modèles sur quatre. Le confond n'est ni le
   vocabulaire de domaine — v6 l'avait apparié — ni la forme de surface. C'est la
   **construction syntaxique**, et elle est capturée par un modèle jouet.

3. **La baseline v6 n'était donc pas assez dure.** Contre la baseline correcte,
   la marge de bloom tombe de +0,071 à **+0,055**, et celle d'opt de +0,012 à
   −0,012. Le démenti v6 ne s'affaiblit pas : il se **renforce**. C'est le bon
   sens de l'erreur — nous avons sous-estimé le bon marché, pas surestimé.

Contrôle de cohérence : TF-IDF et construction donnent le même chiffre sur les
quatre modèles, ce qui est attendu — ces blocs ne dépendent pas du modèle. Seule
la surface varie légèrement (le `n_tokens` vient du tokenizer de chaque modèle).

Mesure textuelle directe sur les deux bras v6 (fréquence d'occurrence) :

| trait | contesté | consensuel | écart |
|---|---|---|---|
| comparatif | 32 % | 7 % | **+26 pts** |
| copule définitionnelle | 20 % | 8 % | +12 pts |
| modal / irréalis | 8 % | 1 % | +8 pts |
| quantificateur de portée | 15 % | 8 % | +8 pts |
| attribution causale | 27 % | 19 % | +7 pts |

Tokens les plus déséquilibrés : `than` 33/3, `more` 13/0, `rather` 12/0,
`would` 5/0 côté contesté ; `through` 0/11, `into` 0/8, `across` 0/7 côté
consensuel. Le bras contesté **compare des grandeurs** ; le bras consensuel
**décrit des mécanismes**. Deux registres, pas deux statuts épistémiques.

À noter aussi : `social` 7/0, `economic` 7/0 **malgré l'appariement par domaine
fin**. L'appariement de domaine n'a pas neutralisé le registre abstrait.

## D2 — Barres d'erreur (bootstrap apparié, 2000 tirages)

| modèle | BA_geo [IC95] | marge C2 [IC95] | P(marge ≥ 0,08) |
|---|---|---|---|
| gpt2 | 0,629 [0,567 – 0,692] | −0,108 [−0,188 – −0,029] | 0 % |
| pythia | 0,746 [0,688 – 0,800] | −0,008 [−0,079 – +0,067] | 1 % |
| opt | 0,750 [0,696 – 0,804] | +0,012 [−0,067 – +0,092] | 5 % |
| bloom | 0,817 [0,767 – 0,867] | +0,071 [+0,004 – +0,137] | **38 %** |

**Avertissement méthodologique :** ces IC sont calculés à modèles ajustés fixes
(rééchantillonnage des prédictions out-of-fold poolées). Ils n'intègrent ni le
réajustement du classifieur ni la variabilité du découpage en plis. Ils sont
donc **optimistes**, c'est-à-dire trop étroits. À lire comme un ordre de
grandeur, jamais comme un test.

Lecture : pour trois modèles sur quatre, l'échec de C2 n'est pas un accident
d'échantillonnage. Pour bloom, le quasi-succès à neuf millièmes est réellement
indéterminé — 38 % de chances de passer sur un tirage voisin. C'est exactement
le statut qu'il faut lui donner : **ni confirmé, ni écarté, sous-alimenté en
données.** Contre la baseline « construction », cette probabilité tombe encore.

## D3 — Dispersion par pli

`BA_geo` par super-domaine :

- **bloom** 0,73 – 0,93 (ai_computing 0,93 ; econ 0,87 ; medicine 0,87) — force
  **large**, pas portée par un pli unique. C'est le seul modèle dont la
  géométrie dépasse les 8 regex, et il le fait partout.
- **opt** 0,54 – 0,81 — très dispersé, history_archaeology au hasard.
- **pythia** 0,63 – 0,83 ; **gpt2** 0,56 – 0,77, plat et faible.

## Ce que cela impose au design v7

1. **La cible est nommée.** v7 doit apparier sur la **construction**, et le
   critère d'appariement est désormais *mesurable sans aucun modèle* : un
   classifieur sur les 8 marqueurs, en LODO, doit tomber près du hasard sur le
   corpus v7. Cela transforme l'appariement en **contrôle qualité pré-gel**,
   vérifiable avant toute mesure.

2. **Le risque s'inverse.** v6 risquait une baseline trop faible ; v7 risquera
   une baseline **trop bien neutralisée** — si `BA_lex` tombe à ~0,55, alors
   `C2 ≥ +0,08` devient franchissable par n'importe quelle géométrie à 0,63, ce
   qui ne prouverait rien. Le pré-enregistrement v7 doit donc être **à deux
   côtés** : un plancher de qualité corpus (model-free, pré-gel) *et* une barre
   C1 relevée, pour que le poids de la preuve retombe sur la séparabilité
   absolue.

3. **La puissance est insuffisante.** À n = 120/bras, la demi-largeur d'IC est
   ~±0,055 pour une marge exigée à 0,08. On teste une différence plus petite que
   notre barre d'erreur. v7 doit augmenter n, sans quoi il reproduira
   l'indétermination de bloom.

4. **L'hypothèse survivante est étroite et précise** : *chez un modèle
   suffisamment capable, la géométrie de Fisher sépare contesté/consensuel
   au-delà de ce que capte toute description linguistique bon marché.* bloom est
   le seul témoin. C'est ça, et rien de plus, que v7 doit mettre à l'épreuve —
   avec la puissance de le faire.

---

*Aucune de ces mesures n'a servi à choisir un seuil v6 : le verdict v6 était
rendu, gelé et commité (`9a1aa42`) avant que ce diagnostic ne soit écrit.*
