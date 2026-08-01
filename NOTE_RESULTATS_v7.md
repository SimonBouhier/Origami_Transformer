# Note de résultats — v7 : persistance de la marge géométrique (H-F)

**Date :** 2026-07-26
**Dépôt :** github.com/SimonBouhier/Origami_Transformer
**Pré-enregistrement :** `PREREGISTRATION_v7.md`, gelé le 2026-07-26,
commit `aa120bd63b462fc1f40ab5e0812db5355999c641`, estampillé `d89a45f`
**Verdict global :** **`HF_DÉMENTI` — 0/6 modèles**, δ = 0.00 et F = 2/3 gelés,
sans coussin
**Campagne :** 6 modèles × 4 bras × 2 (fisher, shuffle) = 48 mesures, 86 min de
RTX 4090, float32, TF32 désactivé. 48/48 sha256 conformes au gel.

---

## Résumé

v7 ne demandait pas « la géométrie bat-elle le bon marché sur ce corpus ? » —
question ponctuelle à laquelle v6 avait déjà répondu non — mais **une question de
forme** : quand on rend le corpus progressivement plus dur pour une description
linguistique bon marché, la marge géométrique tient-elle ?

**Réponse : non. La géométrie décroît avec le bon marché, elle ne lui survit
pas.** Les deux courbes descendent ensemble, avec une corrélation de +0,51 à
+0,95 selon les modèles. C'est un **résultat compatible avec un confond
partagé** — la covariation ne l'identifie pas causalement, et il reste possible
que deux mécanismes distincts déclinent en parallèle pour des raisons
différentes. Ce qui est établi est la non-persistance de la marge, pas sa cause.

Trois résultats convergents, obtenus par trois instruments différents :

| | résultat |
|---|---|
| **critère gelé** | 0/6 modèles confirment H-F |
| **corrélation géo↔bon marché** | +0,51 à **+0,95** — elles descendent ensemble (compatible avec un confond partagé, sans l'établir) |
| **MDL (compression)** | la géométrie comprime moins bien que le bon marché sur **198/198** mesures |

## Le contrôle qui valide la lecture

Avant tout le reste : **le corpus nul**. Deux bras tirés du même vivier
consensuel, étiquetés arbitrairement, mesurés par la chaîne complète.

| modèle | BA_geo | plancher perm95 | marge [IC 95 %] |
|---|---|---|---|
| bloom-560m | 0,520 | 0,590 | +0,020 [−0,110, +0,160] |
| gpt2 | 0,550 | 0,590 | +0,050 [−0,060, +0,170] |
| opt-350m | 0,580 | 0,600 | +0,080 [−0,030, +0,200] |
| pythia-410m | 0,520 | 0,590 | +0,070 [−0,050, +0,200] |
| pythia-1.4b | 0,470 | 0,590 | +0,020 [−0,110, +0,160] |
| pythia-2.8b | 0,440 | 0,580 | −0,010 [−0,150, +0,130] |

**Toutes les BA_geo sont sous leur propre plancher ; tous les intervalles
contiennent zéro.** Le pipeline ne trouve rien quand il n'y a rien — mesure GPU
comprise. C'est ce qui autorise à lire le reste, et c'est ce qui fournit
l'étalon (~0,59) sans qu'aucun seuil ait été choisi à la main.

## La forme, modèle par modèle

L'axe de difficulté : 33 rungs, 120 → 56 paires, construits **model-free** en
retirant à chaque cran les paires que le bon marché sépare le mieux. Le script
de construction n'ouvre aucune sortie Fisher.

| modèle | BA_geo début → fin | pente | pente bon marché | r(géo, bon marché) | rungs soutenantes |
|---|---|---|---|---|---|
| bloom-560m | 0,675 → 0,554 | −0,102 | −0,254 | +0,833 | 11/33 |
| gpt2 | 0,671 → 0,607 | −0,058 | −0,221 | +0,692 | 19/33 |
| opt-350m | 0,688 → 0,634 | −0,070 | −0,221 | +0,811 | 9/33 |
| pythia-410m | 0,600 → 0,589 | −0,030 | −0,247 | +0,511 | 4/33 |
| pythia-1.4b | 0,683 → 0,589 | −0,092 | −0,247 | +0,739 | 5/33 |
| pythia-2.8b | 0,654 → 0,491 | −0,152 | −0,247 | **+0,949** | 0/33 |

Seuil requis : 22/33. Aucun modèle n'y arrive. Le maximum est gpt2 à 19/33 — et
c'est le modèle dont le spectre est quasi rang-1 (`O_rank` médian 1,55) et dont
`O_vol` est mal conditionné, comme établi en v6.1 phase A.

## Un piège de mon propre design, qu'il faut nommer

**Le retrait glouton pousse le bon marché SOUS le hasard** — jusqu'à 0,425. Ce
n'est plus « au niveau de la chance » : c'est de l'anti-corrélation, l'effet
mécanique d'avoir retiré toutes les paires qu'il classait bien.

Conséquence : aux rungs profonds, la marge `BA_geo − BA_cheap` devient
fortement positive (+0,15) **non parce que la géométrie tient, mais parce que le
dénominateur est descendu sous 0,50**. La marge y est un artefact.

C'est exactement pourquoi le critère gelé exigeait **deux** conditions et pas
une. La condition (1) — `BA_geo > plancher(n)` — protège de ce piège, et c'est
elle qui fait échouer bloom et pythia-2.8b au rung le plus dur : leur géométrie
y est retombée *sous* son propre plancher de hasard (0,554 contre 0,589 ;
0,491 contre 0,562).

**Leçon de conception pour la suite : le balayage doit s'arrêter quand
BA_cheap atteint 0,50, pas continuer en dessous.** Les rungs concernés sont à
traiter comme un régime dégénéré.

**Ce que cela fait au verdict — dit précisément.** Le critère gelé compte les
**33** rungs et exige la plus dure ; les dernières sont dégénérées. Le
dénominateur entre donc bien dans le verdict, et il serait faux d'écrire que le
démenti « ne repose pas » sur elles. Ce qu'on peut dire, et qui est vérifié :

| modèle | gelé | requis | hors régime dégénéré | requis | bascule ? |
|---|---|---|---|---|---|
| bloom-560m | 11/33 | 22 | 7/25 | 17 | non |
| gpt2 | 19/33 | 22 | **13/27** | 18 | non |
| opt-350m | 9/33 | 22 | 4/27 | 18 | non |
| pythia-410m | 4/33 | 22 | 0/29 | 20 | non |
| pythia-1.4b | 5/33 | 22 | 2/29 | 20 | non |
| pythia-2.8b | 0/33 | 22 | 0/29 | 20 | non |

**Analyse de sensibilité NON pré-enregistrée, qui ne change et ne peut changer
aucun verdict** — elle est publiée parce que la taire serait pire. Résultat :
aucun modèle ne bascule, et gpt2 — le seul cas serré — **empire** (19/33 → 13/27
pour 18 requises), parce que ses six rungs dégénérées étaient *toutes*
soutenantes. Le régime dégénéré gonflait le décompte, il ne le pénalisait pas.

Formulation exacte à retenir : **démenti selon le design gelé, avec
dégénérescence déclarée, renforcé par des observables secondaires convergents
et par une sensibilité qui ne le renverse pas.**

## MDL — le résultat le plus net de la campagne

Longueur de code en ligne (Voita & Titov 2020), blocs = domaines, 20 ordres
moyennés. Observable **secondaire** au pré-enregistrement : aucun verdict n'en
dépend. Mais elle parle sans ambiguïté.

| modèle | compression géométrie | compression bon marché | écart médian | écarts > 0 |
|---|---|---|---|---|
| bloom-560m | 0,803 | 0,896 | −0,111 | **0/33** |
| gpt2 | 0,864 | 0,931 | −0,076 | **0/33** |
| opt-350m | 0,770 | 0,931 | −0,166 | **0/33** |
| pythia-410m | 0,778 | 0,914 | −0,145 | **0/33** |
| pythia-1.4b | 0,800 | 0,914 | −0,117 | **0/33** |
| pythia-2.8b | 0,692 | 0,914 | −0,241 | **0/33** |

Deux lectures, toutes deux importantes.

1. **La géométrie comprime moins bien que le bon marché sur 198 mesures sur
   198.** Pas une exception, aucun modèle, aucun niveau de difficulté. C'était
   l'instrument censé être *équitable en dimension* — celui qui devait laver
   la géométrie du reproche « 39 features contre 10 000 ». Il l'enfonce.
2. **Les deux compressions sont sous 1,00.** Un taux < 1 signifie que connaître
   les features rend les étiquettes *plus* coûteuses à transmettre qu'un code
   uniforme. Hors domaine, ni la géométrie ni la description bon marché ne
   paient leur propre coût de modèle. C'est une information nouvelle sur le
   corpus autant que sur la géométrie.

## L'échelle de capacité — la réponse à §6

Suite Pythia : mêmes données d'entraînement, même tokenizer, même architecture,
seule la taille varie. C'est le dispositif qui répond à `STATE_OF_ART.md` §6
(Kulkarni et al. : les corrélations géométrie↔performance lues *entre* modèles
sont présumées confondues par la recette d'entraînement).

| modèle | d | BA_geo rung 0 | pente | r(géo, cheap) | soutien |
|---|---|---|---|---|---|
| pythia-410m | 1024 | 0,600 | −0,030 | +0,511 | 4/33 |
| pythia-1.4b | 2048 | 0,683 | −0,092 | +0,739 | 5/33 |
| pythia-2.8b | 2560 | 0,654 | **−0,152** | **+0,949** | **0/33** |

**L'échelle n'aide pas — elle aggrave.** Le plus gros modèle a la pente la plus
raide, la corrélation la plus forte avec le bon marché, et zéro rung soutenante.
La lecture « la signature croît avec la capacité », que nous portions depuis v4
et qui était load-bearing dans trois documents, **ne se reproduit pas dans une
famille contrôlée**.

Et l'ordre inter-architectures ne tient pas non plus : à difficulté nulle,
opt (0,688) > bloom (0,675) > gpt2 (0,671) > pythia-410m (0,600) — ce n'est plus
bloom > opt ≈ pythia > gpt2. **C'est une confirmation directe de §6 : notre
ordre historique était bien un artefact de recette d'entraînement.**

## Le garde-fou B1 échoue — et c'est une lacune de mon pré-enregistrement

| modèle | B1 médian | rungs ≥ 0,30 |
|---|---|---|
| bloom-560m | 0,225 | 0/33 |
| gpt2 | 0,206 | 0/33 |
| opt-350m | 0,131 | 0/33 |
| pythia-410m | 0,211 | 0/33 |
| pythia-1.4b | 0,248 | 0/33 |
| pythia-2.8b | 0,240 | 6/33 |

**Sous les conventions v4/v5/v6, toute cette campagne serait VOID.**

Mon pré-enregistrement v7 mesure B1 (§4) mais **ne l'a pas inscrit comme porte
VOID dans le critère (§5)**. C'est une lacune de conception, pas un choix
opportuniste — mais je ne peux pas l'appliquer rétroactivement : ce serait
exactement le durcissement post-hoc que la discipline interdit.

Deux choses limitent les dégâts. D'abord, **le démenti ne dépend pas de B1** :
un VOID n'est pas une confirmation, et les trois instruments (critère,
corrélation, MDL) concordent indépendamment. Ensuite, l'échec généralisé de B1
sur le corpus v6.4 **est lui-même un résultat** : il confirme ce que v6 avait
signalé — le couplage rang↔NLL est une propriété du **matériel mesuré**, pas du
modèle. Un corpus dont les deux bras parlent du même sujet fait chuter B1
partout.

Pour v8 : B1 doit redevenir une porte explicite, ou être remplacé. En l'état il
signale que l'instrument est hors de son régime de validité sur ce corpus, et
cela mérite mieux qu'une note de bas de page.

---

## Ce que v7 autorise à conclure — trois niveaux distincts

*(Cadrage du chercheur, 2026-07-26, adopté tel quel : les trois niveaux ne
s'impliquent pas l'un l'autre et confondre le premier avec le troisième serait
la faute la plus facile à commettre ici.)*

### 1. Conclusion opérationnelle — solide

Sous le protocole gelé, H-F échoue sur **6/6** modèles ; géométrie et baseline
bon marché déclinent ensemble ; MDL préfère le bon marché sur **198/198**
points ; le corpus nul ne produit rien. Ce niveau est établi, avec les réserves
de dégénérescence déclarées ci-dessus.

### 2. Décision d'ingénierie — solide

**Ne pas importer Fisher comme signal épistémique dans `lyra_reborn` ni dans
EPP.** Le bénéfice n'est pas démontré ; le pont reste gelé. Pour décider de ne
PAS intégrer une dépendance, ces métriques suffisent largement — une décision
négative d'architecture n'a pas besoin du même niveau de preuve qu'une
affirmation scientifique.

### 3. Conclusion ontologique — NON AUTORISÉE

Ceci **ne prouve pas** qu'aucune géométrie épistémique n'existe, ni même que la
métrique de Fisher ne pourrait jamais en capter une.

La raison est dans nos propres chiffres : **B1 échoue presque partout**.
L'instrument ne valide plus son propre lien fonctionnel rang↔NLL sur ce
matériel. Un instrument hors de son régime de validité peut réfuter un usage
particulier ; il ne peut pas prononcer une impossibilité générale.

v7 réfute proprement **le pont actuel**. Elle ne réfute pas **l'objet possible**.
Toute rédaction ultérieure — note, article, README — doit tenir cette
distinction.

---

## Ce qui tombe, ce qui reste

**Tombe** — au sens du niveau 1 (ce protocole, ce corpus, ces modèles), jamais
au sens du niveau 3.
- H-F : la marge géométrique ne persiste pas. Elle suit le bon marché
  (r jusqu'à +0,95) et s'effondre avec lui.
- « La signature croît avec la capacité » : réfuté dans une famille contrôlée.
  L'ordre inter-modèles de v4/v5/v6 était un artefact §6.
- La défense dimensionnelle : MDL, l'instrument équitable, donne raison au bon
  marché 198 fois sur 198.

**Reste debout.**
- La séparabilité brute existe encore à difficulté nulle (BA_geo 0,60–0,69) —
  mais le bon marché est au même niveau (0,67–0,70), donc elle n'est pas
  géométriquement spécifique. C'est la borne v6, reconfirmée sur un corpus
  bien meilleur.
- Le corpus v6.4 lui-même : apparié par domaine **et par sujet**, il est le
  meilleur matériel que ce projet ait produit. Le démenti obtenu dessus est
  d'autant plus solide.
- La méthode : cartographier une courbe plutôt que pointer un seuil a
  fonctionné. Elle a produit un démenti qui ne dépend d'aucun choix de niveau.

## Limites

- **B1 échoue partout** (voir plus haut). Limite majeure, déclarée.
- **Le régime dégénéré** des rungs profonds (BA_cheap < 0,50) contamine la marge
  et doit être exclu par construction en v8.
- **Bras consensuel écrit par des agents** — Q3 reste entière et intacte depuis
  v6. v7 contrôle le sujet et la construction, pas l'auteur.
- **Intervalles bootstrap optimistes** (modèles ajustés fixes), comme déclaré
  au gel.
- **n modeste** : 120 paires au départ, 56 à l'arrivée.
- **Le plancher de permutation n'a été calculé qu'une rung sur quatre.** Le gel
  ne disait pas comment traiter les rungs intermédiaires — lacune. Les deux
  résolutions (interpolée, conservatrice) ont été calculées : **elles donnent le
  même verdict sur les six modèles**, donc rien ne se joue là.

## Conséquences dans l'écosystème

**Le pont Origa → Lyra reste gelé — décision prise par le chercheur le
2026-07-26**, au niveau 2 (ingénierie). v6 avait montré que le signal n'était pas
géométriquement spécifique ; v7 montre qu'il ne le devient à aucun niveau de
difficulté, sur aucun modèle, et qu'il ne s'améliore pas avec la capacité.
Importer la géométrie de Fisher dans `lyra_reborn` comme signal épistémique
n'est pas défendable. Idem pour Origa → EPP.

**Et le gel du pont n'est PAS une dette.** C'est le second volet de la décision,
et il compte autant que le premier : `lyra_reborn` et EPP avancent **sans**
attendre quoi que ce soit d'Origa. Un pont gelé sur une condition non remplie
est un état stable et documenté, pas un chantier en souffrance. La doctrine des
organes le prévoyait — chaque organe doit fonctionner seul — et c'est
exactement le cas de figure qu'elle anticipait.

## Décision : clore la branche

**Décision du chercheur, 2026-07-26 : pas de v8 corrective. La branche est
close, la série est publiée, les ressources se déplacent.**

Quatre campagnes ont convergé vers la même borne, chacune sur un corpus mieux
contrôlé que la précédente. Une v8 qui rejouerait la même mesure sur un corpus
marginalement différent n'ajouterait rien : ce design a dit ce qu'il pouvait
dire.

**Ce qui est publié :** la série complète des campagnes pré-enregistrées —
v4 `HA_DÉMENTI`, v5 `HC_CONFIRMÉ` 3/4, v6 `HD_DÉMENTI` 0/4, v7 `HF_DÉMENTI`
0/6 — avec leurs instruments qualifiés, leurs corpus, leurs gels horodatés et
leurs négatifs intacts. C'est probablement la vraie contribution de ce projet :
non pas une géométrie épistémique, mais **une méthode qui a su ne pas se
convaincre elle-même**, sur quatre tentatives, y compris quand elle s'était
trompée elle-même (v6.3, le durcissement rétrospectif, les rungs dégénérés).

**Ce qui reste ouvert, sans bloquer personne :**

- **Q3 — la provenance externe.** Seule variable jamais touchée : un corpus dont
  les deux bras viennent du monde (désaccord d'experts documenté et gradué)
  plutôt que d'agents. **Expérience future indépendante, pas une dette.** Si elle
  se fait un jour, elle repart du corpus v6.4 et de cette machinerie, qui sont
  en état.
- **B1 — réparer ou remplacer.** Le couplage rang↔NLL s'effondre sur un corpus
  sujet-apparié ; comprendre pourquoi est un travail d'instrumentation à part
  entière, et un préalable à toute réutilisation de la sonde. C'est aussi ce qui
  interdit la conclusion de niveau 3.

Aucun des deux n'empêche `lyra_reborn` ni EPP d'avancer.

---

*Analyse : `analysis_sweep_v7.py` (33 rungs × 6 modèles, bootstrap apparié 2000,
permutation 200, MDL 20 ordres), verdict par `verdict_v7.py` aux seuils gelés.
Rapports bruts : `results_v7/{sweep_report,null_report,verdict_v7}.json`
(non versionnés, régénérables). Le corpus nul a été analysé AVANT le corpus réel.*
