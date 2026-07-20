# Note de résultats — v5 Contested vs Consensual (H-C)

**Date :** 2026-07-20
**Dépôt :** github.com/SimonBouhier/Origami_Transformer
**Pré-enregistrement :** `PREREGISTRATION_v5.md`, gelé le 2026-07-19, commit `ca588c38618325b2c54d0d78ab1c61baff379dc1` (stamp `fbfc2c2`)
**Verdict global :** `HC_CONFIRMÉ` — **3/4 modèles confirmés (75 %), 1 VOID** ; seuils : ≥ 3/4 et fraction ≥ 0,66, sans coussin
**Statut :** premier résultat POSITIF pré-enregistré du projet (après deux négatifs publiables, v3 et v4)

---

## Résumé

Sur quatre familles de modèles, la géométrie de la métrique de Fisher par couche
(O_vol, O_rank, O_aniso via logit-lens brut, protocole identique à la baseline
v4) **sépare les énoncés expert-contestés des énoncés consensuels** : C1 passé
sur 4/4, avec des équilibres de classe de 0,73 à 0,91. Cette séparation **n'est
pas réductible à la forme de surface** (C2 : la géométrie bat la baseline
[longueur, fréquence lexicale, ponctuation] de +0,15 à +0,31 d'AUC, 4/4) et
**s'effondre quand la structure linguistique est détruite** (C3 : −0,20 à −0,28
de BA sous mélange de tokens, 4/4). Les deux explications bon marché écartées
par construction, la confirmation est forte au sens de la clause
d'anti-confirmation du prereg.

Le quatrième modèle (OPT-350m) est **VOID, pas démenti** : il passe C1, C2 et C3
avec les mêmes marges que les confirmés, mais échoue la porte de validité B1
(couplage O_rank↔NLL : |ρ|max = 0,133 < 0,30). L'instrument n'ayant pas
reproduit sa baseline sur ce modèle, sa confirmation n'est pas comptée — le
garde-fou a fonctionné exactement comme gelé.

## Chiffres (seuils gelés : C1 ≥ 0,65 ; C2 ≥ +0,10 ; C3 ≥ +0,08 ; B1 ≥ 0,30)

| modèle | BA_geo | AUC_geo | AUC_surf | marge C2 | BA_shuf | marge C3 | B1 \|ρ\|max | verdict |
|---|---|---|---|---|---|---|---|---|
| gpt2 | 0,729 | 0,792 | 0,645 | +0,147 | 0,512 | +0,217 | 0,342@12 | HC_CONFIRMÉ |
| pythia-410m | 0,838 | 0,923 | 0,650 | +0,273 | 0,608 | +0,229 | 0,319@1 | HC_CONFIRMÉ |
| opt-350m | 0,821 | 0,901 | 0,645 | +0,255 | 0,575 | +0,246 | **0,133@22** | **VOID** |
| bloom-560m | 0,908 | 0,955 | 0,644 | +0,311 | 0,633 | +0,275 | 0,471@24 | HC_CONFIRMÉ |

Corpus : 120 énoncés par bras, tous (A) expert-contestés (purification du
2026-07-19), appariés en longueur (119/120 exacts, écart médian 0,0 sur les 4
tokenizers), sha256 revérifiés au run-time contre les constantes du gel.
Aucun NaN imputé. Durées (CPU, float32, seed 0) : gpt2 13 min, pythia 40,
opt 36, bloom 179 — campagne totale ≈ 4 h 30.

## Lectures (au-delà du verdict)

1. **La baseline de surface est quasi constante (AUC ≈ 0,645) sur les quatre
   modèles** — un signal de surface résiduel existe (l'appariement ne peut pas
   tout matcher), mais il est identique partout et la géométrie le domine
   largement. C'est exactement le rôle que C2 devait jouer.
2. **Le mélange de tokens ramène la séparation près du hasard** (0,51-0,63) :
   la signature est portée par la structure linguistique, pas par le sac de
   mots. C3 a mordu.
3. **OPT : le signal fort.** Ses conditions de confirmation passent toutes —
   la séparation contested/consensual est là, aussi nette qu'ailleurs — mais
   B1 échoue, en écho direct de v4 (C3 échoué à 0,197@18) et de l'incident
   documenté au journal (2026-07-09 : espaces de représentation mixtes). OPT
   est le seul modèle au lens structurellement tronqué (`project_out`
   1024→512, rang de g ≤ 512). Hypothèse pour v6 : c'est le couplage
   rang↔NLL qui casse sous cette projection, pas la géométrie de la
   contestation. Une variante de lens (LN-lens, hors périmètre v5 explicite)
   pourrait le départager.
4. **Gradient de taille ?** bloom (560m) > pythia (410m) > gpt2 (124m) sur
   toutes les métriques — compatible avec « plus de capacité → signature plus
   nette », mais n = 3 confirmés : simple observation, pas une conclusion
   (le couplage inter-modèles est explicitement hors périmètre, §6 du
   STATE_OF_ART).

## Limites (à dire dans tout écrit public)

- **n = 120 par bras, 4 petits modèles (124m-560m)**, anglais uniquement.
- **Le raccourci lexical-thématique n'est pas totalement exclu** : C2 contrôle
  longueur/fréquence/ponctuation, pas le vocabulaire de domaine. La
  purification (A) a rapproché les registres mais les domaines diffèrent par
  construction (c'est l'axe testé). Le contraste intra-domaine est la
  prochaine marche (v6) — assumé dès le gel (README_corpora §8).
- La graine unique (seed 0) et le découpage 5-fold unique : pas d'intervalle
  de confiance sur BA/AUC — les marges sont larges mais non bootstrappées
  (choix gelé ; un bootstrap descriptif hors verdict est possible a
  posteriori).
- VOID ≠ démenti : OPT ne compte ni pour ni contre. Le verdict global tient à
  3 confirmés sur 4 requis min. 3 — sans marge. Honnêteté : un seul B1 de
  moins et le global était indécidable de fait.

## Conséquences dans l'écosystème (portes qui s'ouvrent)

Conformément à la doctrine des ponts (« un pont ne se dégèle que sur
validation ») :
- **Origa → EPP** : les trois conditions de dégel du stub `epp_adapter.py`
  sont réunies (≥ 4 architectures ; GLOBAL confirmé aux seuils
  pré-enregistrés ; prereg + seuils committés avant les résultats). Le stub
  peut être mis à jour (il parle encore H1/probe.py, ère v3) et dégelé —
  décision du chercheur.
- **Origa → Lyra** : la condition du pont (« verdict v5 H-C_CONFIRMÉ aux
  seuils gelés », `lyra_reborn/docs/ORGANES_ET_PONTS.md`) est **remplie** :
  la géométrie de Fisher devient un signal épistémique instrumenté candidat
  pour le pont P2 de lyra_reborn — chantier ouvert, à dessiner.

## Prochaines marches proposées (v6, à pré-enregistrer chacune)

1. **Contraste intra-domaine** (fermer le raccourci thématique).
2. **L'anomalie OPT** : LN-lens / effet de la projection de rang sur B1.
3. **Généralisation** : modèles plus grands / instruction-tunés (la RTX 4090
   rend cela faisable ; le prereg v6 gèlera le device dès le départ).

---

*Analyse : `analysis_v5.py` (seuils gelés, conventions fixées avant données,
pilotes refusés, sha256 vérifiés). Rapport brut : `results/analysis_v5_report.json`
(non versionné, régénérable : `python analysis_v5.py`).*
