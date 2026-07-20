# État des lieux formel — Origami of LLM Representations

> **Date :** 2026-07-18 · **Auteur :** revue externe (Fable, session lyra_reborn) ·
> **Méthode :** lecture intégrale de PREREGISTRATION_v5, CLAUDE.md, RESEARCH_LOG,
> NOTE_RESULTATS_v4 ; inventaire git ; vérifications factuelles sur corpora/ et
> results/. **Fichier volontairement non commité** — le dépôt suit sa propre
> discipline de commit ; à intégrer (ou pas) à ta main.
> **But :** préparer la bascule de demain — tout ce qu'il faut savoir, vérifier
> et trancher avant le gel v5.

---

## 1. Identité

Projet de recherche sur la **géométrie des représentations internes des
transformers** — comment la variété des activations se *plie* à travers les
couches, et si ce pliage a une signature fonctionnelle. Production visée :
**mesures, analyses pré-enregistrées, négatifs publiables**. Pas un produit.
Sœur d'EPP_Verdict, dont il hérite la discipline épistémique (« divergence is
signal, unanimity is failure mode »).

Place dans l'écosystème (cf. `lyra_reborn/docs/ORGANES_ET_PONTS.md`) :
**l'instrument métrologique** des trois organes. Si H-C confirme, il irrigue
EPP (lecture de la contestation) ET Lyra (tension épistémique instrumentée,
successeur légitime de la topologie κ/ρ abandonnée).

## 2. Verdict de la revue : discipline exemplaire, prête pour v5

C'est le dépôt le plus rigoureux de tout l'écosystème audité. Le « commit
dance » est réel et vérifiable dans l'historique git (`preregister v4` →
`stamp v4 freeze` → instrument → verdict), les seuils sont gelés sans coussin,
les négatifs sont assumés publiables, et la règle « toute exclusion exige un
pré-enregistrement nouveau, jamais rétroactif » est écrite ET appliquée.
La charte de lyra_reborn a ici son étalon.

## 3. Historique et acquis

| Campagne | Instrument | Verdict | Ce qui reste |
|---|---|---|---|
| v1/v3 | ID par plus proches voisins (TwoNN/MLE) | H1_DÉMENTI (métrologique : explosion MLE couche 0) | estimateurs NN **archivés** après Schulte & Rügamer (AISTATS 2026) |
| v4 | **Rang effectif de la métrique de Fisher** via logit-lens brut | HA_DÉMENTI global (1/4 ; seuil ≥3/4) — bloom seul confirmé | l'instrument Fisher est **validé comme baseline** (B1 le re-teste en v5) |

**Acquis robustes (deux campagnes, deux instruments incompatibles) :**
- La **compression finale est universelle** (4/4 modèles, deux instruments) — le
  seul motif qui survit à tout. C'est LE résultat solide du projet à ce jour.
- Le **pic en couche 0** est le mode d'échec récurrent (v3 : explosion MLE ;
  v4 : rang de Fisher quasi maximal). Deux lectures concurrentes non départagées
  (artefact d'estimateur vs régime dégénéré du lens en couche 0). Piste : bloom,
  seul confirmé, est le seul avec LayerNorm dédiée sur les embeddings.
- Couplage O_rank↔NLL **toujours positif** (cohérent avec Viswanathan
  2501.10573) — devenu le sanity-check B1 de v5.

## 4. État exact du dépôt (vérifié ce jour)

- **Git :** propre, v4 close et fusionnée (PR #1 `v4-fisher-instrument`,
  HEAD `6d0cca0`). Aucune modification non commitée sur le suivi.
- **Non suivi (⚠️ à commettre AU gel v5, pas avant ni après) :**
  `build_consensual_subset.py` + `corpora/` (consensual.txt, contested.txt,
  contested_anchors.tsv, matching_report.json).
- **Corpus v5 : construit et d'excellente facture.** 120 énoncés par bras
  (min. pré-enregistré : 100) ; **appariement en longueur PARFAIT** (report :
  delta tokens gpt2 moyen 0.0, 120/120 exacts, glouton déterministe, plafond
  12/domaine). C'est une force pour C2.
- **✅ Vérification de non-contamination :** grep exhaustif de `results/` —
  **aucune trace du bras contesté**. Seuls les runs v4 (consensuel) existent.
  La contrainte « le bras contesté n'est pas observé avant le gel » est
  RESPECTÉE : construction et QA d'appariement uniquement, aucun modèle ne
  l'a lu.

## 5. La v5 en une page (H-C)

**Hypothèse :** la géométrie de Fisher par couche porte une **signature de la
contestation épistématique** — énoncé contesté vs consensuel séparables par la
géométrie seule, non réductible à la forme de surface, effondrée si la
structure linguistique est détruite. L'axe est la contestation, PAS la vérité.
La conjonction « géométrie de Fisher × contesté-vs-consensuel » est inédite
(STATE_OF_ART §9). Prior modéré et mixte, contre-prior honnête (signal
sémantique faible, §7).

**Observables :** O1 = classifieur logistique (5-fold stratifié gelé, L2,
C=1.0) sur [O_vol, O_rank, O_aniso] par couche → BA_geo/AUC_geo ; O2 =
baseline de surface (n_tokens, log-fréquence unigramme wordfreq, ponctuation) ;
O3 = contrôle par mélange de tokens ; B1 = sanity (couplage rang↔NLL validé v4
— s'il échoue, run **VOID**, pas un démenti : excellente clause).

**Seuils (validés 2026-05-31, gel à venir, sans coussin) :** C1 `BA_geo ≥ 0.65`
∧ C2 `AUC_geo − AUC_surf ≥ 0.10` ∧ C3 `BA_geo − BA_geo_shuf ≥ 0.08` ;
global ≥ 3/4 modèles. Démenti = négatif publiable.

**Hors-périmètre propre :** courbure (H-B différée), attestation EPP (stub
gelé), causal, lens-LN (v6), gros modèles (v6).

## 6. ⚠️ Points relevés par la revue — à trancher AVANT le gel

Le pré-enregistrement est encore DRAFT : les amendements sont légitimes
aujourd'hui, ils ne le seront plus après le gel. Quatre points, par ordre
d'importance :

1. **Le raccourci lexical-thématique n'est pas contrôlé par C2.** La baseline
   de surface (longueur, fréquence, ponctuation) ne teste PAS le vocabulaire
   thématique : les énoncés contestés (éthique, politique) ont un lexique
   distinctif, et un classifieur pourrait « lire le thème » plutôt que la
   contestation — la géométrie aussi. Options : (a) ajouter à O2 une baseline
   lexicale (ex. logistique sur sac-de-mots/TF-IDF) — amendement pré-gel
   légitime ; (b) accepter et l'inscrire explicitement comme limite dans la
   clause d'anti-confirmation (le contraste intra-domaine devient une v6).
   **Décision : la tienne.** Ne rien faire serait le seul mauvais choix : une
   confirmation serait attaquable sur ce flanc au premier regard externe.
2. **Incohérence de formulation dans l'en-tête du prereg :** « contested arm is
   not *built* or observed until this v5 freeze » — or le bras est **construit**
   (non observé ✓, cf. §4). Le §Scope dit correctement « not *observed* ».
   Harmoniser l'en-tête au gel (« built, quarantined, never observed ») pour
   qu'aucun relecteur ne puisse y voir une entorse.
3. **Menues précisions de gel :** (a) la graine du découpage 5-fold — Seed=0
   global est déclaré, le fixer explicitement dans le script d'analyse ;
   (b) `wordfreq` (dépendance d'O2) à épingler dans requirements au gel ;
   (c) sha256 des deux corpus consignés dans le prereg au moment du commit
   (déjà prévu §Scope — le faire).
4. **Le stub `epp_adapter.py` date de l'ère v3** : ses conditions de dégel
   parlent de `H1_CONFIRME`, `probe.py`, `analysis.py`. À rafraîchir (H-C,
   `probe_fisher.py`, `analysis_v5`) — après le gel, ce n'est pas bloquant.

## 7. Coût estimé de la campagne v5

Référence v4 (CPU, float32, ~220 énoncés) : gpt2 10 min, pythia 45, opt 45,
bloom 72 — **~2 h 50 total**. v5 : 240 énoncés × (mesure + contrôle mélangé O3)
≈ **~6-7 h CPU au total**, parallélisable par modèle, **zéro GPU, zéro API
payante**. La contrainte de crédit ne s'applique qu'au temps de session Claude
Code : le gel + lancement tient en une session courte ; l'analyse dans une
seconde.

## 8. Checklist de la bascule (demain)

1. Trancher le point §6.1 (baseline lexicale : ajout ou limite assumée).
2. Harmoniser l'en-tête (§6.2) + précisions §6.3 dans PREREGISTRATION_v5.
3. **Le gel** : renseigner Frozen on/by, committer prereg + corpora/ +
   build_consensual_subset.py + matching_report + sha256 — en un commit dédié.
4. Étendre `probe_fisher.py` au double-bras + O3 (mélange via control_probe) ;
   écrire `analysis_v5.py` (logistique 5-fold gelée) — SANS lire de sortie
   modèle avant le gel (commit dance).
5. Lancer les 4 modèles (~6-7 h CPU, en tâche de fond).
6. Verdict aux seuils gelés → NOTE_RESULTATS_v5 + RESEARCH_LOG, quel que soit
   le sens du verdict.
7. Si H-C_CONFIRMÉ : dégel epp_adapter (§6.4) et ouverture du chantier pont
   Origa→Lyra (tension épistémique réelle) — cf. ORGANES_ET_PONTS.

---

*Revue en lecture seule : aucun fichier du dépôt modifié, rien commité, aucun
modèle n'a lu le bras contesté pendant cette revue.*
