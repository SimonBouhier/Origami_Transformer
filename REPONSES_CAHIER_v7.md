# Lecture critique du retour de littérature — cahier v7

**Date :** 2026-07-22
**Sources :** 7 PDF déposés dans `docs/Q7/` par le chercheur, texte extrait dans
`docs/_txt/`. Le chercheur signale explicitement n'avoir influencé que la
qualité des sources : **aucune décision ni idée du rapport ne vient de lui.**
Le rapport est donc traité ici comme une pièce à évaluer, pas comme une
consigne.
**Statut :** analyse. Aucune décision prise, aucun seuil touché, aucun gel.

---

## 0. Vérification des sources

Les sept PDF sont correctement identifiés et correspondent aux citations :

| fichier | identification vérifiée |
|---|---|
| `1909.03368` | Hewitt & Liang, *Designing and Interpreting Probes with Control Tasks*, 11 p. |
| `2003.12298` | Voita & Titov, *Information-Theoretic Probing with MDL*, 14 p. |
| `2010.02114` | Kaushik, Setlur, Hovy & Lipton, *Explaining the Efficacy of Counterfactually Augmented Data*, ICLR 2021 |
| `23003260` | Wojatzki, Zesch, Mohammad & Kiritchenko, **NAoCI**, LREC 2018 (archive CNRC) |
| `2406.13805` | Hou et al. (IBM Research), **WikiContradict**, 46 p. |
| `7690D24E…` | Deroover, Knight, Burke & Bucher, *Why do experts disagree? The development of a taxonomy*, **Public Understanding of Science, 2022** (le rapport date de 2023 — corriger) |
| `N18-2017` | Gururangan et al., *Annotation Artifacts in NLI*, NAACL 2018 |

Aucune référence fantôme. Le rapport ne cite rien qu'il n'ait lu.

---

## 1. Ce qui est juste et directement actionnable

### Q2 — sélectivité et MDL : diagnostic correct

Le rapport a raison sur le fond : comparer deux exactitudes entre un espace à 39
dimensions et un espace à ~10 000 est méthodologiquement bancal, et un relecteur
le dira. **Voita & Titov (MDL) est la bonne réponse** — la longueur de
description compare équitablement des espaces de dimensions très différentes,
ce qui est exactement notre problème.

**Nuance que le rapport ne fait pas :** la *selectivity* de Hewitt & Liang est
conçue pour des sondes à forte capacité qui peuvent mémoriser (MLP sur des
milliers de types de mots). Notre sonde est une régression logistique L2 sur 39
features évaluée hors-domaine : sa capacité de mémorisation est quasi nulle, et
l'accuracy sur tâche-contrôle devrait tomber à ~0,50 mécaniquement. La
sélectivité serait donc **presque vacue chez nous** — bon marché à calculer, à
faire par acquit de conscience, mais ce n'est pas elle qui répond à l'objection.
MDL, si.

### Q4/Q5 — méthodes correctement nommées

*Corrected resampled t-test* (Nadeau & Bengio), bootstrap de groupe, tests de
permutation respectant la structure des plis : c'est le bon inventaire. Et la
recommandation centrale est la bonne : **une simulation de puissance Monte-Carlo
utilisant notre propre structure de plis**, plutôt qu'une formule i.i.d. Ce
n'est pas une question de littérature, c'est un calcul que nous pouvons faire
avec les données v6.

### Q8 — cohérent avec notre propre veille

« Aucun corpus apparié sur domaine *et* forme, différant par le seul statut
épistémique » : c'est exactement la conclusion de `STATE_OF_ART.md` §10. Rien
de neuf, mais confirmation indépendante que la niche est vide.

---

## 2. Q1 — la conclusion est juste, l'argument ne l'est pas, et la vraie preuve était chez nous

### L'argument du rapport ne tient pas

Le rapport conclut « découplage viable → v7 comme prévu » en s'appuyant sur la
taxonomie de Deroover. Or **Deroover classe les *causes* du désaccord entre
experts** — trois dimensions (informant / information / incertitude), dix types :
compétence, intérêts concurrents, type de preuve, méthodologie, ambiguïté
d'entrée, ambiguïté de sortie, caractère provisoire du savoir, incertitude
inhérente, etc. Le travail est issu du **domaine nutrition/alimentation**,
construit par revue de littérature + entretiens d'experts, à destination de la
**communication scientifique**.

C'est une taxonomie du *pourquoi les experts divergent*. Q1 demande tout autre
chose : **quelle est la forme grammaticale des énoncés contestés ?** Deux
experts peuvent diverger pour cause de « compétence » ou d'« intérêts
concurrents » à propos d'un énoncé parfaitement comparatif. Le passage de
« les causes sont variées » à « les constructions sont découplées » est un
non-sequitur. Deroover reste une lecture utile pour penser la contestation ;
elle ne répond simplement pas à la question posée.

### La vraie réponse : notre corpus la contenait déjà

Mesure directe sur les deux bras v6, marqueur comparatif, aucun modèle
impliqué :

|  | comparatif | non-comparatif |
|---|---|---|
| **contesté** | 39 | **81** |
| **consensuel** | **8** | 112 |

**81 de nos 120 énoncés contestés ne sont pas comparatifs du tout.** Le scénario
pessimiste de Q1 — « être contesté implique quasi-analytiquement être
comparatif » — est **empiriquement faux sur notre propre matériel**. Deux tiers
du bras contesté sont déjà des attributions d'effet non comparatives :

> *Dietary cholesterol has a negligible effect on blood cholesterol levels.*
> *Vitamin D supplementation reduces the rate of respiratory infections.*
> *Term limits shift real legislative power toward unelected staff.*

C'est une preuve bien plus forte que n'importe quelle taxonomie, parce qu'elle
porte sur le matériel que nous allons effectivement mesurer.

### Le goulot est l'autre case, et il est facile à remplir

La cellule rare n'est pas « contesté non-comparatif » (81 disponibles) mais
**« consensuel comparatif » : 8 seulement**. Ce n'est pas une difficulté de
fond — le monde en regorge — c'est que `build_consensual_v6.py` n'a pas été
chargé d'en produire :

> *Light travels faster through a vacuum than through glass or water.*
> *A progressive income tax takes a larger share from higher earners.*
> *Compound interest makes unpaid debt grow faster over time.*

Parfaitement naturels, parfaitement consensuels, parfaitement comparatifs.
**Le travail de corpus v7 est donc bien plus léger que je ne le craignais** : il
s'agit surtout d'équilibrer la case consensuel-comparatif, pas de réécrire le
bras contesté.

### Sonde exploratoire — à lire avec les réserves qui suivent

En restreignant les DEUX bras aux énoncés non-comparatifs (n = 193), sur les
mesures v6 déjà acquises :

| modèle | corpus complet (geo / cheap / marge) | sous-corpus non-comparatif |
|---|---|---|
| gpt2 | 0,610 / 0,727 / **−0,117** | 0,607 / 0,626 / **−0,020** |
| pythia | 0,766 / 0,728 / **+0,038** | 0,735 / 0,617 / **+0,118** |
| opt | 0,751 / 0,727 / **+0,024** | 0,772 / 0,626 / **+0,145** |
| bloom | 0,842 / 0,728 / **+0,113** | 0,841 / 0,626 / **+0,215** |

Le bon marché s'effondre (0,73 → 0,62) ; **la géométrie ne bouge pas** (bloom
0,842 → 0,841, opt monte). Les marges triplent ou quadruplent.

**Réserves, sérieuses et non négociables :**
1. **CV stratifiée 5 plis, PAS du LODO** (effectifs insuffisants pour 7 plis).
   **Le confond de domaine n'est donc pas contrôlé** — c'est pourquoi les
   chiffres « corpus complet » ici (bloom 0,842) dépassent ceux du verdict LODO
   (0,817). Ces deux colonnes ne sont pas comparables au verdict v6.
2. **Sous-échantillonnage post-hoc sur données déjà mesurées.** C'est de
   l'exploration génératrice d'hypothèse, jamais un test. Aucun de ces chiffres
   ne peut entrer dans un verdict.
3. Retirer les comparatifs retire mécaniquement le meilleur indice bon marché :
   que la baseline chute est attendu. L'information est ailleurs — **la
   géométrie, elle, ne chute pas avec elle**. C'est ça qui est encourageant.
4. Sous-corpus déséquilibré (81 contre 112).

Conclusion prudente : rien ici ne prouve quoi que ce soit, mais **rien
n'indique que retirer le comparatif détruise le phénomène**, et plusieurs
indices suggèrent l'inverse. v7 vaut d'être construit.

---

## 3. Q3 — là où je suis en désaccord avec la recommandation la plus forte du rapport

Le rapport recommande « fortement » de basculer le bras contesté vers **NAoCI**
ou **WikiContradict**. J'ai lu les deux. **Aucun des deux ne convient**, et
adopter le premier reviendrait à défaire v5.

### NAoCI — c'est exactement ce que nous avons purgé en v5

Le résumé du papier est sans ambiguïté. NAoCI porte sur *« public opinion on
complex controversial issues such as “Legalization of Marijuana” and “Gun
Rights” »*. Les « assertions » y sont définies comme *« opinions, beliefs,
claims, arguments, points of view »*. Les 100 000 jugements d'accord viennent de
**crowdworkers**, pas d'experts.

Or la définition (A) gelée en v5 — sur ta consigne explicite — est
*« expert-contesté seulement, divergence entre gens informés »*, jugements de
valeur exclus. NAoCI est la catégorie **(B)/(C)** : controverse publique et
valeurs, précisément ce que la purification v5 a retiré du corpus. Le désaccord
mesuré n'y est pas épistémique, il est politique.

Adopter NAoCI, ce n'est pas améliorer le corpus : c'est **revenir avant v5**.

### WikiContradict — erreur de catégorie, deux fois

C'est un banc d'essai **RAG** : 253 instances où deux passages de Wikipédia se
contredisent, pour tester si un LLM remarque le conflit. Les exemples du papier :

> *« Combien de survivants au naufrage du Lusitania ? »* (deux passages donnent
> des comptes incompatibles)
> *« Combien de moines connaissent la recette de la Chartreuse ? »* (trois
> contre deux)

Ce ne sont pas des contestations épistémiques : ce sont des **incohérences
éditoriales** — une page périmée, un chiffre mal recopié. Personne d'informé ne
« diverge » sur le nombre de moines. Et le format est un triplet
question + passages, pas un énoncé déclaratif assertable : il faudrait le
transformer lourdement, en réintroduisant exactement l'artefact de rédaction
que la manœuvre était censée éliminer.

### Ce qui survit de la recommandation

**L'intuition est juste, les jeux de données ne le sont pas.** Provenance
externe + contestation graduée resterait le levier le plus puissant dont nous
disposons : cela supprimerait l'artefact d'auteur, permettrait de la régression
au lieu de la classification, et constituerait notre meilleur argument de
publication.

Les candidats qui pourraient vraiment convenir n'ont **pas** été vérifiés par le
rapport (il les mentionne sans les documenter) : enquêtes d'*expert elicitation*
avec dispersion mesurée, discordance entre revues systématiques sur une même
question, plateformes de prévision. Aucun n'a été lu. **Q3 reste ouverte**, et
c'est la question la plus importante du cahier.

---

## 4. Q6 et Q7 — le rapport reformule mon incertitude sans la lever

Sur Q7 (fidélité de la Fisher restreinte à k = 50 à grand vocabulaire, stabilité
spectrale en fp16), le rapport dit que la littérature « existe surtout dans
l'optimisation » et « montre souvent une dégradation pour les petites valeurs
propres » — **sans citer une seule référence**, et aucun PDF correspondant n'a
été fourni. Sa recommandation (« validez numériquement avant d'échelonner ») est
la bonne, mais c'est ce que je disais déjà.

Bonne nouvelle : **c'est une expérience, pas une question de littérature.** Nous
pouvons y répondre sur nos modèles actuels, sans GPU : recalculer les
observables à k = 50, 200 et sans troncature sur un sous-ensemble d'énoncés, et
mesurer l'écart sur `O_vol`, `O_rank`, `O_aniso` ; puis fp32 contre fp16 sur le
même sous-ensemble. Une demi-heure de CPU répond à la question mieux que
n'importe quelle recherche bibliographique.

Sur Q6 (tuned lens pour OPT), le rapport confirme le dilemme sans le trancher et
conclut comme moi : à défaut de variante non entraînée fiable, **retirer OPT du
panel et le justifier** plutôt que d'introduire un composant appris dans un
instrument gelé.

---

## 5. Bilan

**Acquis :** MDL est le bon upgrade d'instrument (Q2). La simulation de puissance
est faisable et nécessaire (Q4/Q5). La niche est vide (Q8). **Q1 est réglée, mais
par notre corpus, pas par la littérature** — et elle est réglée dans le bon sens,
avec un coût de rédaction bien inférieur au budget que j'annonçais.

**Non acquis :** Q3 reste entière. Les deux jeux de données recommandés sont
inadaptés, l'un dangereusement (NAoCI défait v5). Q6 et Q7 attendent des
mesures, pas des lectures.

**Ce qui a changé dans mon estimation :** je pensais que v7 exigeait ~250
énoncés contestés supplémentaires avec ancres. C'est faux. Le bras contesté
actuel fournit déjà 81 non-comparatifs et 39 comparatifs ; **l'essentiel du
travail est d'écrire des consensuels comparatifs**, qui ne demandent aucune
ancre d'expert puisqu'ils ne sont pas contestés. Le budget humain s'effondre.
Reste la question de puissance (n global), qui est indépendante et que la
simulation tranchera.
