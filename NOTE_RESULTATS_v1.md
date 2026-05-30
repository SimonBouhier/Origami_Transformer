# Note de résultats — Origami DI Probe v3 (v1)

**Date :** 2026-05-30
**Dépôt :** github.com/SimonBouhier/Origami_Transformer
**Statut :** négatif publiable — condition d'arrêt atteinte
**Verdict global :** `H1_DÉMENTI` (0/4 modèles confirmés)
**Frame EPP :** `origami_di_v1.0` non intégré ; `epp_adapter.py` reste un stub permanent pour ce frame.

---

## Résumé

Nous avons testé l'hypothèse H1 — un profil de dimension intrinsèque (DI) « en bosse »
le long des couches d'un transformeur, avec compression de la dernière couche sous le
pic (Ansuini et al., 2019) — sur quatre architectures distinctes, selon des seuils figés
avant tout regard sur les données. Le verdict global est `H1_DÉMENTI` : aucun des quatre
modèles ne satisfait les trois conditions pré-enregistrées.

Le point central de cette note est que **ce démenti est métrologique, pas morphologique**.
Il est entièrement porté par le critère d'accord inter-estimateur (C1), jamais atteint, et
par l'instabilité de l'estimateur MLE sur la couche d'embeddings — et non par l'absence de
la bosse. La composante « compression finale » de l'hypothèse (C3) est, elle, **universelle :
vérifiée sur les quatre modèles**.

---

## Pré-enregistrement (figé le 2026-05-30, avant tout regard sur les données)

Hypothèse H1 (Ansuini et al.) : la DI suit un profil en bosse — expansion dans les premières
couches, puis compression, dernière couche strictement sous le pic.

Conditions cumulatives par modèle :

- **C1 — accord inter-estimateur :** sur ≥ 70 % des couches, l'écart relatif entre TwoNN et
  MLE est ≤ 20 %.
- **C2 — pic intérieur :** `argmax(DI)` strictement dans `[1, L-2]`.
- **C3 — compression finale :** `DI[dernière] < DI[pic]`, strict, sans tolérance.

Verdict par modèle : `H1_CONFIRME` si C1 ∧ C2 ∧ C3, sinon `H1_DÉMENTI`.
Verdict global : `H1_CONFIRME` si confirmé sur ≥ 4 modèles **et** ≥ 66 % du total.

Un démenti global n'est pas un échec : c'est la condition d'arrêt prévue, et un négatif
publiable.

---

## Méthode

Instrument : `probe.py`. Pour chaque modèle, extraction des états cachés par couche sur un
corpus fixe, puis estimation de la DI globale par couche avec **deux estimateurs aux
hypothèses orthogonales** :

- **TwoNN** (Facco et al., 2017) — ratios des premier/deuxième voisins, densité localement
  uniforme.
- **MLE** (Levina & Bickel, 2004) — maximum de vraisemblance sur les k plus proches voisins
  (K = 20), processus de Poisson local.

La convergence de deux méthodes à hypothèses distinctes vaut signal ; leur divergence est
précisément ce que C1 mesure. Estimation accompagnée d'une déduplication des lignes exactes
(les estimateurs par plus proches voisins divisent par la distance au premier voisin) et
d'un sous-échantillonnage sans remise (m = 0,9 n) pour l'écart-type.

Corpus : 220 énoncés déclaratifs factuels en anglais, diversifiés sur 11 domaines
(`claims.txt`, `sha256 ebdc64bd…`). Tokens réels par modèle : ~2 780 à 3 026.

Modèles (4 familles d'architecture) :

| Modèle | Famille | Couches captées (L) |
|---|---|---|
| `gpt2` | GPT-2 | 13 |
| `EleutherAI/pythia-410m` | GPT-NeoX | 25 |
| `facebook/opt-350m` | OPT | 25 |
| `bigscience/bloom-560m` | BLOOM | 25 |

Paramètres figés : `seed=0`, `n_subsample=2000`, `n_bootstrap=20`, `max_seq_length=128`,
CPU `float32`.

### Intégrité du protocole

Deux corrections ont été apportées à l'instrument **avant toute observation d'une valeur de
DI réelle** (tous les essais antérieurs ne produisaient que des `NaN`), donc sans biais de
sélection sur les résultats :

1. Un bloc `except` trop large masquait une dépendance transitive manquante (`pandas`, requise
   par `scikit-dimension`) : chaque appel à l'estimateur levait silencieusement une
   `ImportError`, et toutes les couches sortaient `NaN`. Corrigé en installant `pandas` et en
   hissant l'import au niveau module (échec bruyant au démarrage plutôt que silencieux).
2. Le bootstrap initial échantillonnait **avec** remise, ce qui est incompatible avec des
   estimateurs par plus proches voisins (les doublons créent des distances nulles). Remplacé
   par un sous-échantillonnage **sans** remise, complété par la déduplication des lignes
   exactes (utile notamment pour la couche d'embeddings, où des tokens répétés produisent des
   vecteurs identiques).

Ces corrections touchent la mécanique de mesure, **jamais les seuils du verdict** (restés
figés), et sont antérieures à la première valeur de DI observée.

---

## Résultats

| Modèle | L | Accord C1 | C1 | Pic (C2) | C3 | Verdict |
|---|---:|---:|:---:|:---:|:---:|---|
| `gpt2` | 13 | 23 % | ✗ | 11 ✓ | ✓ | `H1_DÉMENTI` |
| `EleutherAI/pythia-410m` | 25 | 0 % | ✗ | 0 ✗ | ✓ | `H1_DÉMENTI` |
| `facebook/opt-350m` | 25 | 44 % | ✗ | 22 ✓ | ✓ | `H1_DÉMENTI` |
| `bigscience/bloom-560m` | 25 | 16 % | ✗ | 0 ✗ | ✓ | `H1_DÉMENTI` |

**Global : 0/4 confirmés (0 %) → `H1_DÉMENTI`.** (Seuil de confirmation : ≥ 4 modèles et
≥ 66 %.)

Figures : profils par modèle et superposition en profondeur normalisée dans
`results/figures/` (`_overlay_di.png` et `<modèle>_di.png`), régénérables par
`plot_results.py`.

---

## Lecture

Trois constats structurent l'interprétation.

**1. La compression finale (C3) est universelle.** Sur les quatre modèles, la dernière
couche est strictement sous le pic. La partie « ça redescend à la fin » du profil en bosse
est présente partout.

**2. L'accord inter-estimateur (C1) n'est jamais atteint.** TwoNN et MLE divergent de
manière systématique, MLE lisant constamment plus haut que TwoNN. L'écart entre les deux
courbes vaut 10 à 30 fois les écarts-types de bootstrap : il s'agit donc d'un **biais
systématique, pas de bruit**. Ce désaccord est une constante de l'instrument sur les quatre
architectures (accord de 0 % à 44 %, toujours sous le seuil de 70 %). C'est lui qui dicte le
démenti global.

**3. Le pic intérieur (C2) est corrompu pour deux modèles par la couche d'embeddings.** Pour
`bloom-560m` et `pythia-410m`, l'estimateur MLE explose sur la couche 0 (embeddings bruts) :
MLE[0] ≈ 36,3 (bloom) et 22,0 (pythia), contre 9,1 (gpt2) et 4,5 (opt). Cette valeur aberrante
tire l'`argmax` du profil primaire sur la couche 0, donc le pic n'est pas intérieur et C2
échoue. Là où la couche 0 n'explose pas (`gpt2`, `opt`), C2 passe (pics aux couches 11 et 22).

**Conclusion.** Le démenti est porté par la métrologie — désaccord systématique des deux
estimateurs et instabilité de la couche d'embeddings — et non par l'absence de la forme en
bosse. Au sens strict du pré-enregistrement, H1 est démenti ; au sens morphologique, la bosse
n'est pas réfutée. Cette distinction est le résultat principal de cette campagne.

---

## Ce que nous ne concluons pas (menaces à la validité)

- **Régime d'échantillon fini.** À ~2 000 points uniques par couche et une DI réelle de
  l'ordre de 12–20, TwoNN et MLE opèrent tous deux dans leur régime de sous-estimation, mais
  de quantités différentes — explication la plus probable de l'échec de C1.
- **Couche d'embeddings.** La couche 0 est un nuage atypique (DI MLE très élevée) ; son
  inclusion dans le calcul du pic corrompt C2 pour deux modèles.
- **Hétérogénéité du nuage.** Mots-outils, ponctuation et tokens de contenu sont agrégés dans
  un même nuage, ce qui crée des sous-densités très différentes et viole l'hypothèse de densité
  localement uniforme de TwoNN.
- **Tokens spéciaux.** `opt` et `bloom` préfixent automatiquement un token BOS ; le token de
  position 0 se comporte en puits d'attention. Inclus tels quels, conformément à la règle
  uniforme figée.
- **LayerNorm — vérifié pour gpt2.** Dans le `modeling_gpt2.py` installé,
  `_can_record_outputs = {"hidden_states": GPT2Block}` : les 13 états captés sont les
  embeddings plus les 12 sorties de blocs, **tous pré-`ln_f`**. La normalisation finale ne
  s'applique qu'à `last_hidden_state`, non capté. La compression finale (C3) n'est donc **pas**
  un artefact de LayerNorm pour gpt2. Cette vérification reste à reproduire pour pythia, opt et
  bloom, dont les classes de modèle sont distinctes.

---

## Conséquences

Le chantier s'arrête proprement, comme le pré-enregistrement le prévoit. Le frame
`origami_di_v1.0` n'est pas ajouté à EPP, et `epp_adapter.py` demeure un stub permanent pour
ce frame. Cristalliser une attestation EPP à partir d'une sonde non validée est précisément
l'anti-pattern que l'on cherchait à éviter ; le non-résultat prend ici sa forme correcte.

---

## Pistes pour une v3.1 (re-pré-enregistrée — à NE PAS appliquer rétroactivement)

Les éléments ci-dessous sont des hypothèses d'amélioration. Toute v3.1 exige un **nouveau
pré-enregistrement committé avant de regarder ses résultats** ; les appliquer aux données
actuelles serait du p-hacking.

- Exclure la couche 0 (embeddings) du calcul du pic.
- Remplacer C1 (écart absolu) par un critère d'accord de **forme** — corrélation de rang de
  Spearman entre les profils TwoNN et MLE — qui teste la cohérence morphologique plutôt que la
  coïncidence en valeur absolue de deux estimateurs aux biais connus.
- Hygiène de tokens : exclure tokens spéciaux, ponctuation et token de position 0.
- Augmenter le corpus (50 k–200 k tokens) et relever `n_subsample` pour réduire le biais
  d'échantillon fini.
- Stratifier la mesure par classe de token (fréquents, rares, ponctuation, contenu) au lieu
  d'agréger un nuage hétérogène.
- Intégrer les diagnostics additifs déjà codés : `spectrum.py` (rang effectif linéaire par
  couche) et `control_probe.py` (contrôles nuls — ordre mélangé, tokens aléatoires) pour
  distinguer une bosse linguistique d'une bosse purement architecturale.

---

## Reproductibilité

- Corpus : `claims.txt`, `sha256 ebdc64bd…`, 220 énoncés.
- Graines et paramètres : `seed=0`, `n_subsample=2000`, `n_bootstrap=20`,
  `max_seq_length=128`, CPU `float32`.
- Versions épinglées : `requirements.lock.txt` (transformers inclus).
- Sorties brutes : `results/*.json`. Figures : `results/figures/` (régénérables via
  `plot_results.py`).
- Pré-enregistrement (`README.md`), seuils (`analysis.py`) et instrument (`probe.py`) commités
  sur git avant la première analyse.

---

*Estimateurs et hypothèse : Levina & Bickel (2004) ; Facco et al. (2017) ; Ansuini, Laio,
Macke & Zoccolan (2019). Cette note documente un résultat négatif obtenu selon un protocole
pré-enregistré.*
