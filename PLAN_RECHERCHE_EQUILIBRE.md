# Plan — chercher l'équilibre sans le désirer d'avance

**Date :** 2026-07-22
**Statut :** plan de méthode, **non gelé**. Il répond à une exigence du
chercheur : *« ne pas s'enfermer dans des résultats trop désirés d'avance,
élargir la recherche d'équilibre dès maintenant, quitte à coûter du compute
GPU. »* Rien ici ne mesure encore ; c'est le protocole à valider avant de figer.

---

## 1. Le piège, nommé

Le schéma habituel — choisir **un** seuil (« BA_cheap ≤ 0,60 »), construire **un**
corpus qui le passe, mesurer la géométrie **une fois** — a un vice caché : le
seuil peut être choisi, même sans mauvaise foi, là où la géométrie gagne. C'est
exactement ce qui s'est passé en v6.3 : la porte a été satisfaite *par
construction*, et le résultat est devenu une tautologie.

Le désir se glisse dans **le choix du point**. La parade est de ne plus choisir
un point.

## 2. Le principe : cartographier la courbe, pas pointer un endroit

On transforme la **difficulté du corpus** en un axe **continu**, et on mesure la
géométrie tout le long de cet axe. La question cesse d'être binaire — « la
géométrie bat-elle le bon marché à ce seuil ? » — et devient une **forme** :

> Quand on rend le corpus progressivement plus dur pour le bon marché
> (BA_cheap glisse de ~0,64 vers 0,50), que fait la géométrie ?

Deux issues, discriminantes :

- **La géométrie décroche avec le bon marché** → le signal était partagé, porté
  par le même confond. Démenti, et il ne dépend d'aucun seuil.
- **La marge géométrique (BA_geo − BA_cheap) tient ou s'ouvre** quand le bon
  marché s'effondre → il reste quelque chose que la description bon marché ne
  capte pas. C'est ça, et seulement ça, qui rendrait la thèse défendable.

Un point de croisement isolé ne compte pas. Une **persistance sur la plage**
compte. On ne peut pas désirer une courbe entière au seuil près.

## 3. Trois mécanismes concrets

### M1 — Le balayage de difficulté (model-free, aveugle à la géométrie)

À partir du corpus v6.4, produire une **famille** de corpus emboîtés en retirant
progressivement les paires que le **classifieur bon marché** sépare avec le plus
de confiance. La confiance est calculée par le bon marché seul, **jamais par la
géométrie** — celle-ci ne touche jamais la sélection.

- Rung 0 : les 120 paires (BA_cheap ≈ 0,64).
- Rung *k* : on retire les *m* paires les plus « bon-marché-évidentes »
  (out-of-fold, pour ne pas tricher), jusqu'à approcher BA_cheap ≈ 0,52.
- **Plancher d'effectif** : on s'arrête avant que le plus petit pli LODO passe
  sous 8 paires par bras (sinon la mesure devient bruit). Cela borne la
  profondeur du balayage.

À chaque rung, on mesure **le bon marché ET la géométrie** (GPU, instrument
gelé). On obtient deux courbes en fonction de la taille du corpus, et surtout la
courbe **marge = BA_geo − BA_cheap**.

### M2 — Des barres d'erreur partout

À chaque rung : **bootstrap apparié** (≥ 2000 tirages, stratifié par classe) de
BA_geo, BA_cheap et de leur marge. Un point chanceux ne peut plus se faire
passer pour un signal. La marge est reportée avec son IC 95 % à chaque rung ; la
**forme de la courbe des IC** est le résultat, pas un chiffre isolé.

*Rappel de la limite déjà connue* (diag_v7) : ces IC, à modèles ajustés fixes,
sont optimistes. On les lit comme ordre de grandeur, et on le redit dans la note.

### M3 — Le plancher par corpus nul (calibrer le seuil AILLEURS)

Le seuil ne doit pas venir du corpus qu'il juge. On construit un **corpus nul**
sans aucun signe épistémique : deux bras tirés **du même vivier consensuel**,
étiquetés au hasard en « A »/« B », appariés par domaine. Par construction, il
n'y a rien à trouver.

- Le bon marché et la géométrie y donnent le **plancher de hasard réel** (pas le
  0,50 théorique : le vrai, avec les biais de l'estimateur et du découpage).
- Tout seuil de la porte (A, B) est **calibré sur ce plancher**, pas sur v6.4.
  Exemple : « BA_cheap acceptable = plancher nul + marge de bruit du bootstrap »,
  et non un 0,60 choisi à la main.

C'est le mécanisme le plus fort contre le désir : le seuil vient d'un corpus où
l'on **sait** qu'il n'y a rien.

## 4. Ce qu'on pré-enregistrera (la relation, pas le niveau)

Avant de lire le moindre chiffre géométrique :

1. La famille de corpus (schéma de retrait, plancher d'effectif) est **figée**.
2. Le corpus nul est **figé**.
3. Le critère est une **forme**, pas un seuil ponctuel. Formulation candidate :
   *la marge BA_geo − BA_cheap reste ≥ δ (IC 95 % bas > 0) sur au moins les deux
   tiers des rungs, y compris le rung le plus dur atteint.* δ et la fraction se
   fixent **sur le plancher nul** (M3), pas à la main.
4. L'analyse (régression marge ~ difficulté, ou simple monotonie) est écrite
   **avant** la mesure.

Un démenti reste publiable, et le devient même *davantage* : montrer que la marge
s'effondre dès qu'on serre le bon marché est un résultat propre et fort.

## 5. Le coût GPU, assumé

Le chercheur autorise explicitement la dépense. Ordre de grandeur, instrument
déjà qualifié (phase A, ~10 min pour un corpus complet de 120 sur les 4 modèles,
fisher + shuffle) :

| élément | passes | coût GPU estimé |
|---|---|---|
| balayage M1, ~8 rungs | 8 × (4 modèles × 2 bras × 2) | ~1 h 20 |
| corpus nul M3 | 1 corpus complet | ~10 min |
| marge de sécurité / reruns | — | ~30 min |
| **total** | | **~2 h de 4090** |

Le bootstrap (M2) est du CPU, négligeable. C'est très en dessous du budget d'une
seule campagne CPU historique (2 h 15 pour **un** corpus). Le GPU rend la
cartographie **moins chère qu'un point unique ne l'était avant.**

## 6. Ce que ça remplace, et ce que ça n'empêche pas

- Ça **remplace** la logique « un seuil, un corpus, un verdict » de v4–v6 par une
  logique de courbe. Les seuils de la porte (`gate_corpus.py`) deviennent des
  **sorties** du corpus nul, plus des entrées choisies.
- Ça **n'empêche pas** l'échelle Pythia (`PREREGISTRATION_v6.1`, C-E1 = +0,05,
  en attente) : au contraire, chaque rung du balayage peut être mesuré sur les
  trois tailles, ce qui croise capacité × difficulté en une seule campagne.
- Ça **ne touche pas** aux verdicts gelés v4/v5/v6.

## 7. Décisions qui te reviennent (aucune urgente)

1. **Profondeur du balayage** : ~8 rungs jusqu'à BA_cheap ≈ 0,52, ou plus fin /
   plus profond ? Plus de rungs = courbe plus lisible = plus de GPU.
2. **Le corpus nul** : deux bras du même vivier consensuel (ma proposition), ou
   une autre construction de « rien » que tu jugerais plus convaincante ?
3. **L'ajout de MDL** (Q2, Voita & Titov) comme comparateur **équitable en
   dimension** à côté de la BA. Il répond d'avance à l'objection « 39 features
   géométriques contre 10 000 TF-IDF, la comparaison est biaisée ». Je le
   recommande : c'est le bon moment pour l'intégrer, une fois pour toutes.
4. **Croiser avec l'échelle Pythia** dès maintenant (difficulté × capacité) ou
   séparément ?

Rien à décider ce soir. Quand tu veux, on fige la famille et le corpus nul —
model-free, donc sans risque de fuite — puis on lâche le GPU.
