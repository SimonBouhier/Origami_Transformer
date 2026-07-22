# Plan v6.1 — étalonnage GPU et échelle de capacité

**Date :** 2026-07-22
**Statut :** plan, **non porteur de verdict sur H-D**. v6 reste gelé et son
verdict inchangé. v6.1 ne rejuge rien : elle qualifie l'instrument sur un
nouveau support de calcul et produit le renseignement de conception qui manque
à v7.
**Matériel :** RTX 4090, 24 Go, pilote 610.74. Le `torch` du venv de mesure est
une build **CPU** (`2.12.0+cpu`) — un venv séparé `.venv-gpu` est créé pour ne
pas altérer l'environnement qui a produit v4/v5/v6.

---

## 0. Correction préalable : Q7 était mal posée — par moi

En relisant `probe_fisher.py:95-134` avant de planifier le portage, je constate
que **l'instrument ne tronque pas le vocabulaire**. Il accumule la Fisher
complète sur les |V| tokens (GEMM float32 par blocs, accumulateur float64),
symétrise, puis diagonalise la matrice **d × d entière** en float64 :

```
G = Σ_blocs (W_c ⊙ p_c)ᵀ W_c  −  m mᵀ      # vocabulaire COMPLET
lam = eigvalsh(G)                          # spectre COMPLET, float64
```

`k = 50` ne sert qu'à **O_vol** = ½ Σ_{i≤50} log λᵢ. `O_rank` (rang effectif) et
`O_aniso` sont calculés sur le spectre complet.

Conséquences, toutes à mon débit :

1. **La question « la restriction top-k = 50 reste-t-elle fidèle à grand
   vocabulaire ? » ne s'applique pas à notre instrument.** Je l'ai écrite dans
   le cahier, le rapport de littérature y a répondu consciencieusement, et la
   prémisse était fausse. L'instrument est plus rigoureux que ma description.
2. **La comparabilité inter-modèles des observables n'est pas un problème non
   plus.** `O_vol` et `O_rank` dépendent de *d* — mais nous ne comparons jamais
   les observables entre modèles : chaque modèle a son propre classifieur, et
   nous ne comparons que des **BA**, qui sont comparables. La seconde moitié de
   Q7 se dissout aussi.
3. **Ce qui reste de Q7 est réel et différent** : une diagonalisation d × d en
   float64, dont le coût croît en **O(d³)**, sur une carte grand public où le
   float64 tourne à **1/64 du débit float32**. Passer de d = 1024 à d = 4096,
   c'est ×64 de travail par diagonalisation, et il y en a *n_énoncés ×
   n_couches*. C'est la vraie contrainte, et elle se mesure — elle ne se lit pas.

Observation collatérale, à creuser un jour : `O_rank` médian vaut **1,55 chez
gpt2** (spectre quasi rang-1) contre 870 chez pythia-410m, 586 chez bloom, 408
chez opt (plafonné par `project_out`). gpt2 n'est pas un petit modèle du même
genre que les autres : c'est un régime géométrique différent. Cela explique
peut-être pourquoi il est le plus faible dans les trois campagnes.

---

## Phase A — équivalence CPU ↔ GPU (obligatoire)

**But :** établir que le nouveau support rend les mêmes nombres que l'ancien,
avant de lui faire dire quoi que ce soit de neuf.

- Mêmes 4 modèles, **corpus v6 gelé inchangé**, mêmes graine / k / dtype.
- Rejouer `probe_fisher.py` sur GPU, comparer aux sorties CPU gelées **énoncé
  par énoncé, couche par couche** : erreur relative sur `O_vol`, `O_rank`,
  `O_aniso`, et écart sur `NLL`.
- Rejouer `analysis_v6.py` sur les sorties GPU : les BA LODO doivent reproduire
  celles du verdict.
- **Critère d'acceptation, fixé maintenant :** BA_geo_lodo reproduit à ±0,005
  sur les 4 modèles, et erreur relative médiane < 1e-6 sur les observables.
  En deçà, le GPU n'est pas qualifié et v6.1 s'arrête là.

Ce n'est pas une formalité : deux environnements indépendants (venv distinct,
backend distinct, ordre de sommation distinct) qui tombent sur les mêmes
chiffres, c'est une validation bien plus forte que la reproductibilité d'un
seul.

## Phase B — coût et précision (la vraie Q7)

1. **float64 contre float32 pour `eigvalsh`.** Sur un échantillon de matrices
   G réelles, mesurer la divergence induite sur les trois observables. Si
   float32 suffit, le 4090 cesse d'être bridé et le budget change d'ordre de
   grandeur. Si non, on le sait avant de lancer.
2. **Où placer la diagonalisation.** Hypothèse à tester : le partage optimal sur
   cette carte est **GEMM sur GPU** (accumulation sur |V| = 50 k lignes, où le
   GPU écrase le CPU) et **`eigvalsh` sur CPU** (où MKL multithreadé peut battre
   un float64 bridé à 1/64). À mesurer, pas à supposer.
3. **Courbe de coût** à d = 1024 / 2048 / 2560 / 4096, pour extrapoler le budget
   d'une campagne **avant** de s'y engager.

## Phase C — l'échelle pythia (l'apport scientifique)

**Pourquoi cette échelle et pas des modèles assortis.** `STATE_OF_ART.md` §6
(Kulkarni et al.) établit qu'une corrélation géométrie ↔ performance lue **entre
modèles** est présumée fallacieuse : elle reflète les hyperparamètres
d'entraînement. Or « la signature croît avec la capacité » est notre résultat le
plus robuste (ordre stable sur trois campagnes) — et il est actuellement lu
entre architectures, donc exposé de plein fouet à §6.

La suite pythia est la réponse standard à cette objection : **mêmes données,
même tokenizer, même architecture, seule l'échelle varie.**

- pythia-410m (d = 1024, déjà mesuré) → 1.4b (2048) → 2.8b (2560) → 6.9b (4096).
- Corpus v6 gelé, protocole LODO inchangé.
- **La barre est déjà fixée et indépendante du modèle** : la baseline bon marché
  vaut 0,738–0,754 (O2 gelé) et 0,762 (marqueurs de construction). Elle ne
  dépend d'aucun modèle : elle ne bougera pas d'un millième quand nous
  changerons de GPU ou de taille.

**La question, nette :** `BA_geo_lodo` croît-elle avec l'échelle, et franchit-elle
la barre bon marché quelque part sur l'échelle ?

Si oui — v7 vaut d'être construit à grande échelle, et nous saurons à partir de
quelle taille. Si la courbe plafonne sous 0,762 — l'histoire géométrique est en
difficulté sérieuse, et il vaut mieux l'apprendre sur un corpus que nous avons
déjà que sur un corpus que nous aurions payé cher à écrire.

**Discipline :** Phases A et B sont de l'étalonnage d'instrument — pas de
pré-enregistrement, ce sont des mesures de conformité. **Phase C avance une
affirmation** (« la capacité fait croître la séparabilité géométrique »), donc
elle doit être **pré-enregistrée** avant de lire le moindre chiffre : seuil de
monotonie, seuil de franchissement, gestion des VOID. Sinon elle n'est que du
renseignement de conception, et devra être présentée comme tel — jamais comme un
résultat.

---

## Ce que v6.1 ne fait pas

- **Elle ne rejuge pas H-D.** Le verdict v6 (`HD_DÉMENTI`, 0/4) est gelé,
  commité, publié. Aucune mesure v6.1 ne le modifie.
- **Elle ne durcit pas rétroactivement la baseline de v6.** Que les marqueurs de
  construction atteignent 0,762 est un diagnostic post-hoc consigné dans
  `NOTE_DIAGNOSTIC_v7.md` ; il informe v7, il ne réécrit pas v6.
- **Elle ne touche pas au corpus.** Le corpus construction-apparié est le
  chantier v7, et il attend la résolution de Q3 (provenance).
