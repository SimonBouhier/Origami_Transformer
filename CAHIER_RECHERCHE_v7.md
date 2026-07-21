# Cahier des charges de recherche — v7

**Pour :** Simon Bouhier
**De :** l'agent, 2026-07-21
**Objet :** les points où j'hésite réellement pour concevoir v7, et ce qu'une
lecture ciblée résoudrait.

Chaque entrée dit : **la question**, **pourquoi j'hésite** (pas de fausse
modestie : ce sont de vraies incertitudes qui changeraient le design), **quoi
chercher**, et **ce que ta réponse change concrètement**. Les entrées sont
classées par ce qu'elles bloquent, pas par intérêt intellectuel.

Ce qui suit ne demande pas que tu deviennes exhaustif. Une seule bonne référence
sur Q1 ou Q3 vaut mieux que dix sur le reste. Si tu ne dois en ouvrir qu'un :
**Q1**, puis **Q3**.

---

## Rang 1 — bloquant : sans réponse, je ne peux pas figer v7

### Q1. Peut-on découpler « contesté » de « comparatif » ?

**La question.** Le diagnostic montre que le contesté est massivement comparatif
et causal, le consensuel définitionnel et mécaniste (`NOTE_DIAGNOSTIC_v7.md`,
D1). v7 veut apparier là-dessus. Mais une possibilité m'inquiète sérieusement :
**et si être contesté impliquait quasi-analytiquement d'être comparatif ?** Une
affirmation contestée porte typiquement sur un effet net, un arbitrage, une
magnitude relative — parce que c'est précisément là que des gens informés
peuvent diverger. Si c'est structurel et non accidentel, alors apparier sur la
construction ne retire pas un confond : **cela retire le phénomène**, et v7
mesurera un corpus artificiel qui ne parle plus de contestation.

**Pourquoi j'hésite.** Je n'arrive pas à trancher par le raisonnement seul. Il
existe des contre-exemples (« Le tabac cause le cancer du poumon » est causal et
consensuel ; « La conscience est un phénomène purement physique » est
définitionnel et contesté), donc les catégories ne sont pas coextensives. Mais
« pas coextensives » ne veut pas dire « suffisamment indépendantes pour bâtir
120 paires équilibrées et naturelles ». C'est empirique, et je n'ai pas la
donnée.

**Quoi chercher.**
- Philosophie/sociologie des sciences sur ce qui rend un énoncé *contestable* :
  contestation portant sur des magnitudes/effets nets vs sur des définitions et
  des cadres. Mots-clés : *scientific controversy taxonomy*, *epistemic
  disagreement types*, *expert disagreement taxonomy*, *evidential vs conceptual
  disputes*.
- Côté linguistique : travaux sur les **paires minimales** qui font varier la
  sémantique en tenant la syntaxe constante — BLiMP (Warstadt et al. 2020) pour
  la méthode ; *counterfactually-augmented data* (Kaushik, Hovy & Lipton 2020)
  pour la façon dont on réécrit un item en ne changeant qu'un facteur sans
  détruire le naturel.

**Ce que ça change.** Si le découplage est possible : v7 part comme prévu. S'il
ne l'est pas — si le comparatif est constitutif du contesté — alors v7 doit
changer d'angle : au lieu d'apparier, **stratifier** (comparer contesté et
consensuel *à l'intérieur* de la classe des énoncés comparatifs, puis à
l'intérieur des définitionnels), ce qui est un design différent et coûte encore
plus en effectifs. C'est la décision structurante.

### Q3. L'artefact d'auteur — mesure-t-on la contestation ou le rédacteur ?

**La question.** Notre bras contesté est *curé* avec ancres d'experts ; le bras
consensuel v6 est *écrit par un agent* de façon déterministe. Le texte produit
par LLM est notoirement détectable. Une partie du 0,74 de la baseline
pourrait n'être que la signature du rédacteur, pas celle du statut épistémique.

**Pourquoi j'hésite.** C'est la menace que je sais nommer sans savoir la
neutraliser. Symétriser (faire écrire les deux bras par le même agent)
supprimerait l'asymétrie mais introduirait la question « un agent peut-il écrire
un énoncé authentiquement contesté ? ». Sourcer les deux bras à l'extérieur
serait idéal mais je ne sais pas où.

**Quoi chercher — deux pistes, la seconde est la plus prometteuse.**
- *Artefacts de jeux de données de sondage* : Gururangan et al. 2018 (annotation
  artifacts in NLI) est le classique ; chercher ensuite ce que la littérature de
  *probing* fait aujourd'hui de la **symétrie de provenance** entre classes.
  Mots-clés : *probing dataset artifacts*, *spurious cues probing*, *shortcut
  learning benchmark construction*.
- **Sources externes de désaccord informé, avec désaccord quantifié.** C'est la
  piste que je te recommande le plus fortement : les plateformes de prévision
  (Metaculus, Good Judgment / GJP) et les *expert elicitation surveys*
  fournissent des énoncés sur lesquels des gens informés divergent
  *mesurablement*, avec la dispersion comme grandeur. Idem pour les corpus de
  désaccord d'annotateurs experts. Mots-clés : *forecasting question banks*,
  *expert elicitation disagreement*, *controversial claims dataset*, *NPOV
  dispute corpus*, *human label variation*.

**Ce que ça change.** Énorme. Si une source externe existe : (a) l'artefact
d'auteur disparaît, (b) la contestation devient **graduée** au lieu de binaire,
donc on peut faire de la régression au lieu de la classification — instrument
bien plus sensible et bien moins piégeable —, (c) le corpus cesse d'être notre
production, ce qui est le meilleur argument de publication qu'on puisse avoir.
Si aucune source n'existe, il faut au minimum symétriser la rédaction et le dire
comme une limite majeure.

---

## Rang 2 — structurel : ça change l'instrument, pas la faisabilité

### Q2. Faut-il remplacer « BA géo vs BA lexicale » par une mesure de sélectivité ?

**La question.** Comparer deux exactitudes de classifieurs est un instrument
grossier : il ne dit rien de la *capacité* qu'il a fallu dépenser pour extraire
l'information. La littérature de probing a réglé ce problème il y a des années.

**Pourquoi j'hésite.** Trois cadres candidats, et je ne sais pas lequel se
compose proprement avec des features de **géométrie métrique** plutôt qu'avec
des représentations brutes :
- *Control tasks* et **sélectivité** (Hewitt & Liang 2019) : on ré-entraîne la
  sonde sur des étiquettes aléatoires ; la sélectivité = accuracy réelle −
  accuracy contrôle. Simple, robuste, adapté à notre cas.
- *Probing par longueur de description minimale* (Voita & Titov 2020) : compare
  le coût de codage plutôt que l'exactitude. Plus élégant, comparable entre
  espaces de features de dimensions différentes — ce qui est exactement notre
  problème (39 features géométriques contre des milliers de TF-IDF, comparaison
  actuellement bancale).
- *Amnesic probing* (Elazar et al. 2021) : on retire l'information et on regarde
  si le comportement change. Passe du corrélationnel au causal, mais je ne sais
  pas comment « retirer » une propriété d'une métrique de Fisher.

**Ce que ça change.** Si MDL se transpose : c'est probablement l'upgrade le plus
sérieux disponible, et il répond d'avance à l'objection « votre baseline a 10 000
dimensions et la géométrie 39, la comparaison est inéquitable » — objection
qu'un relecteur posera. Si seule la sélectivité se transpose, on l'ajoute comme
garde-fou et on garde BA.

### Q4. Quelle barre d'erreur est défendable pour du LODO à 7 plis ?

**La question.** Mes IC actuels sont explicitement optimistes (rééchantillonnage
à modèles ajustés fixes). Quelle est la procédure correcte ?

**Pourquoi j'hésite.** Les plis sont des groupes, pas des tirages i.i.d. ; les
prédictions à l'intérieur d'un pli sont corrélées ; et à 7 plis les
approximations asymptotiques ne valent pas. Je connais le problème sans
connaître le consensus actuel.

**Quoi chercher.** *Corrected resampled t-test* (Nadeau & Bengio 2003) et ce qui
l'a remplacé ; *cluster bootstrap* / *group bootstrap for cross-validation* ;
tests de permutation respectant la structure de groupe. Mots-clés :
*confidence intervals cross-validation dependent folds*, *nested CV variance
estimation*, *permutation test grouped cross-validation*.

**Ce que ça change.** Détermine si on peut publier des IC ou si on doit s'en
tenir à des marges brutes et à la discipline pré-enregistrée. Détermine aussi
Q5.

### Q5. Quelle taille d'échantillon pour détecter une marge de +0,08 ?

**La question.** À n = 120/bras, la demi-largeur d'IC vaut ~±0,055 pour une
barre à 0,08 : on teste plus petit que notre bruit. Combien faut-il ?

**Pourquoi j'hésite.** Je peux faire un calcul de puissance naïf (il donne
~250–300 par bras), mais je ne sais pas comment il se corrige sous validation
groupée, où la variance inter-plis domine souvent.

**Quoi chercher.** *Sample size determination classifier comparison*, *power
analysis paired classifier accuracy*, et surtout tout travail donnant des
effectifs pour du *leave-one-group-out*.

**Ce que ça change.** Directement le budget de rédaction du corpus et le temps
de campagne. C'est un chiffre que j'aimerais avoir avant de te demander d'écrire
250 énoncés ancrés.

---

## Rang 3 — opportuniste : la 4090 ouvre des portes

### Q6. Le tuned lens réparerait-il OPT — et a-t-on le droit de s'en servir ?

**La question.** OPT échoue B1 pour la troisième campagne (ρ = 0,197 / 0,133 /
0,143), ce qui est cohérent avec un logit-lens cassé sur cette architecture
(`project_out`, rang ≤ 512). Le *tuned lens* (Belrose et al. 2023,
arXiv:2303.08112) est le correctif connu.

**Pourquoi j'hésite.** Le tuned lens **s'entraîne**. Introduire un composant
appris dans un instrument dont toute la valeur vient d'être gelé et
déterministe, c'est un problème de discipline autant que de méthode : sur quoi
l'entraîner, et comment garantir que l'entraînement n'a pas vu le corpus ?

**Quoi chercher.** Les usages du tuned lens comme *instrument de mesure* (et non
comme outil d'interprétabilité ponctuel) ; existe-t-il une variante analytique
non entraînée (correction LayerNorm seule) qui suffirait ? Mots-clés : *tuned
lens as measurement*, *logit lens failure OPT*, *LayerNorm correction logit lens*.

**Ce que ça change.** Récupérer OPT ferait passer l'échantillon informatif de 2
à 3 modèles. Mais si la seule voie est un composant entraîné, je préfère
probablement **retirer OPT du panel** et le dire, plutôt que dégeler
l'instrument.

### Q7. La Fisher restreinte à k = 50 tient-elle à grand vocabulaire, en fp16 ?

**La question.** Ta 4090 (24 Go) permettrait des modèles 7–8B. Deux inquiétudes
numériques : (a) la restriction top-k = 50 approxime g(h) = Wᵤᵀ(diag(p) − ppᵀ)Wᵤ ;
est-elle encore fidèle quand |V| passe de 50 k à 128–256 k ? (b) le **rang
effectif est une grandeur spectrale**, sensible aux petites valeurs propres —
le fp16 pourrait les corrompre silencieusement.

**Pourquoi j'hésite.** Ce sont des questions de validité numérique où une erreur
ne se voit pas : le calcul aboutit, les nombres sont plausibles, et ils sont
faux. Je ne veux pas monter en échelle sans savoir.

**Quoi chercher.** Approximations top-k / low-rank de la Fisher softmax à grand
vocabulaire ; précision requise pour l'estimation de rang effectif et d'entropie
de von Neumann ; pratiques de *mixed precision* dans les mesures spectrales.
Mots-clés : *top-k approximation softmax Fisher*, *effective rank numerical
precision*, *fp16 spectral estimation stability*.

**Ce que ça change.** Si k = 50 tient et que fp32 est nécessaire : on planifie
la VRAM en conséquence (un 7B en fp32 ne tient pas sur 24 Go → il faudra du
fp16 pour les poids et du fp32 pour l'accumulation spectrale, à valider). Si
k = 50 ne tient pas : il faut re-choisir k **avant** de figer, et donc pas au
milieu d'une campagne.

### Q8. Y a-t-il déjà un corpus contesté/consensuel apparié quelque part ?

Question courte et à fort rendement : quelqu'un a-t-il déjà publié un jeu
d'énoncés appariés sur le domaine *et* la forme, différant par le statut
épistémique ? Si oui, on l'utilise et on cesse de fabriquer notre matériel.
Mots-clés : *paired controversial consensus statements dataset*, *matched
stimuli epistemic status*, *scientific consensus claims benchmark*.

---

## Ce dont j'ai besoin de toi, hors littérature

Trois décisions, aucune urgente — elles conditionnent le design, pas la
poursuite du travail :

1. **La 4090.** Si v7 doit monter en taille de modèle, le protocole GPU doit
   être gelé **dès le départ** (précision, k, seed, versions). Dis-moi si tu
   veux que je prépare v7 en CPU sur les mêmes 4 petits modèles (sûr, comparable
   à v4/v5/v6) ou en GPU avec un panel élargi (plus fort, mais rupture de
   comparabilité avec l'historique).

2. **La provenance du corpus** (Q3). Si tu as accès à une source externe
   d'énoncés à désaccord d'experts documenté, c'est le levier le plus puissant
   dont on dispose.

3. **Le budget de rédaction.** Si Q5 confirme ~250/bras, il faudra environ 130
   énoncés contestés supplémentaires **avec ancres** (`affirmed_by` /
   `denied_by`). C'est la partie que je ne peux pas fabriquer seul sans
   dégrader la qualité épistémique du bras : les ancres sont ce qui distingue
   notre corpus d'une liste d'opinions.

Rien de tout cela ne bloque le pont, qui reste ta décision et peut décanter
aussi longtemps qu'il faut.

---

*Références citées de mémoire : Hewitt & Liang 2019 ; Voita & Titov 2020 ;
Elazar et al. 2021 ; Belrose et al. 2023 (arXiv:2303.08112) ; Gururangan et al.
2018 ; Nadeau & Bengio 2003 ; Warstadt et al. 2020 (BLiMP) ; Kaushik, Hovy &
Lipton 2020. Vérifie les identifiants avant de les citer dans un écrit —
je les donne comme points d'entrée de recherche, pas comme citations validées.
Ce qui est déjà consigné dans `STATE_OF_ART.md` (§1–§10) n'est pas répété ici.*
