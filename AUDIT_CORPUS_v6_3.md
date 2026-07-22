# Audit indépendant du corpus v6.3

**Date :** 2026-07-22
**Auditeur :** agent Opus, session Origa
**Méthode :** tous les chiffres ci-dessous sont **recalculés**, jamais lus dans
`g1_report.json`, `CORPUS_FREEZE_v6_3.md` ou `SOURCE_AUDIT_v6_3.md`.
**Matériel audité :** `contested.txt`, `evidence.tsv` (qui contient les deux
bras), `g1_report.json`, `CORPUS_FREEZE_v6_3.md`, `SOURCE_AUDIT_v6_3.md`.

**Verdict : ne pas geler pour mesure en l'état.** Le travail mécanique et
documentaire est de très bonne qualité — meilleur que ce que le cahier des
charges v6.2 exigeait. Mais le corpus a **échangé un confond mesuré contre un
confond non mesuré**, et la porte censée détecter ce genre de dérive est
devenue incapable d'échouer.

---

## 1. Ce qui est vérifié et tient

Tout ce qui est déclaré est exact. Aucun chiffre du rapport ne diverge de ma
mesure.

| contrôle | résultat |
|---|---|
| `contested.txt` == colonne 4 de `evidence.tsv` | 120/120 |
| vecteur 8-marqueurs déclaré `[51,5,2,6,1,1,0,5]` | **concorde exactement** |
| longueurs gpt2 hors 9–16 | 0 sur les deux bras |
| écart de longueur maximal dans une paire | 3 |
| doublons intra-bras / croisés | 0 / 0 / 0 |
| hedges enregistrés | 0 |
| questions, points-virgules, points finaux manquants | 0 |
| `fine_domain` aligné sur `domain_map_v6.json` | 120/120 |
| super-domaines (plis LODO) | 27/22/16/15/15/13/12 — **identiques à v6** |
| lignes sans source | 0 sur les deux bras |

**L'audit de source est du vrai travail.** Seize défauts matériels trouvés et
réparés, dont plusieurs graves : PMID 25787902 portait sur la dosimétrie et non
sur le sodium (L5) ; PMID 31554670 portait sur une neuropathie autonome et non
sur les réseaux sociaux (L64) ; le DOI 10.1162/qjec.2008.123.1.139 est l'article
de Nunn sur la traite, pas la comparaison européenne alléguée (L114) ; un DOI
QJE malformé qui ne résolvait pas (L24). Ce sont exactement les erreurs qui
tuent un corpus en silence.

**Le protocole de tours a tenu.** Le tour 0 a échoué (BA 0,6125, p = 0,0003), il
a été conservé immuable, et le tour 1 a été construit sans desserrer le seuil.
C'est la bonne discipline.

**Les frontières sensibles sont bien tenues.** J'ai lu les lignes que le
chercheur signale comme fragiles. Elles sont correctement cadrées :

- **L43** — *« Genetic differences explain most adult variation in measured
  intelligence »*, Plomin contre Turkheimer. Portée restreinte à l'adulte, à
  l'intelligence *mesurée*, et à la *variation*. C'est la bonne dispute.
- **L64** — passé de « cause majeure de maladie mentale » à *« poses a material
  risk for adolescent depression »*, Twenge contre Odgers. Correction juste.
- **L51** — Hubble tension, SH0ES contre Freedman. Dispute vivante et propre.
- **L37** — activité corticale postérieure contre diffusion préfrontale : c'est
  la collaboration adversariale réelle, pas une caricature.

Sur ce plan, le corpus est meilleur que celui de v6.

---

## 2. Problème n°1 — la porte G1 ne peut plus échouer

**120 paires sur 120 ont des vecteurs de marqueurs strictement identiques.**
Les totaux des deux bras sont le même vecteur `[51,5,2,6,1,1,0,5]`.

Conséquence arithmétique : un classifieur sur ces 8 features ne dispose
d'**aucune** information — les deux classes ont, ligne à ligne, exactement le
même vecteur. BA = 0,5000 n'est pas un résultat empirique, c'est une identité.
La p-value de 1,0 et les quantiles de permutation tous égaux à 0,5000 le
confirment : la statistique est dégénérée.

**Une porte qui ne peut pas échouer ne mesure rien.** Le document de gel dit
« this gate establishes only non-separability by the eight registered markers » —
c'est honnête, mais en dessous de la vérité : elle l'établit *par stipulation*.
Le tour 0 testait quelque chose (et a échoué, à 0,6125) ; le tour 1 a transformé
le test en contrainte de construction. C'est le mécanisme de Goodhart : la mesure
est devenue la cible, et a cessé d'être une mesure.

---

## 3. Problème n°2 — le raccourci a déménagé, il n'a pas disparu

C'est le point décisif, et c'est exactement ce que le chercheur pressentait.

| classifieur, LODO, mêmes plis | BA |
|---|---|
| détecteur **enregistré** (8 marqueurs) | **0,5000** — par construction |
| **six mots non enregistrés** (voir ci-dessous) | **0,6208** |
| TF-IDF seul | **0,6292** (v6 : 0,7250) |

Les six mots, repérés par log-odds, aucun présent dans le détecteur :

| mot | contesté | consensuel |
|---|---|---|
| `rather` | 9 | 0 |
| `chiefly` | 7 | 0 |
| `explains` | 7 | 0 |
| `materially` | 5 | 0 |
| `causally` | 5 | 0 |
| `exceed*` | 0 | 15 |

`chiefly`, `materially`, `causally` ne sont pas de l'anglais courant à cette
densité. Ce sont des **substituts des marqueurs interdits** : `primarily` →
`chiefly`, `substantially` → `materially`, `significantly` → `causally`. Le
détecteur a été satisfait en remplaçant les mots qu'il connaît par des synonymes
qu'il ignore. Symétriquement, `exceed` porte 15 occurrences du seul côté
consensuel.

Six mots suffisent donc à faire 0,62 là où le détecteur officiel fait 0,50.

**Note de nuance, et elle compte :** TF-IDF est passé de 0,725 à 0,629. Le
raccourci est réellement plus faible qu'en v6. Le travail n'a pas été vain — mais
il est incomplet, et la porte ne peut pas le dire.

---

## 4. Problème n°3 — la dérive topique du bras consensuel

En v6, les deux bras partageaient le vocabulaire de leur domaine. En v6.3, le
bras consensuel a glissé vers des **faits de manuel** d'un champ voisin :

| ligne | contesté | consensuel |
|---|---|---|
| 43 | héritabilité de l'intelligence adulte | *Identical twins share nearly all of their nuclear DNA.* |
| 64 | plateformes et dépression adolescente | *Human colour vision depends on three types of retinal cone cells.* |
| 113 | fin de la guerre froide | *The Roman Republic preceded the Roman Empire.* |
| 114 | commerce atlantique et essor européen | *The French Revolution began ... in seventeen eighty-nine.* |

Le `fine_domain` est nominalement le même, le **sujet** ne l'est pas. Or c'est le
recouvrement de vocabulaire qui neutralisait TF-IDF. En l'éloignant, on a
réintroduit un confond de **contenu**, à un étage au-dessus de celui qu'on
fermait — et c'est ce qui explique `blood`, `water`, `energy`, `reading` d'un
côté contre `inflation`, `academic` de l'autre.

---

## 5. Problème n°4 — la langue est forcée

Sur 120 énoncés déclaratifs anglais : **1 seule copule définitionnelle**
(`is/are/was/were`), **0 préposition de mécanisme** (`through/into/across/…`),
5 attributions causales. Ce n'est pas de la prose : c'est une solution à un
problème de satisfaction de contraintes. Le corpus cesse d'être représentatif de
la langue dont on prétend mesurer la géométrie, ce qui affaiblit toute conclusion
qu'on en tirerait.

---

## 6. Deux hashes qui semblaient diverger — RÉSOLUS, rien à corriger

*Signalés comme défauts dans la première version de cette note ; vérification
faite, les deux sont bénins et la piste d'audit tient.*

- **`consensual.txt` n'avait pas été déposé** (sha annoncé `eb537ee1…`). Il est
  **intégralement récupérable** : la colonne 9 de `evidence.tsv`, jointe par
  `\n` avec saut de ligne final, donne **exactement** le sha déclaré. Le fichier
  est reconstruit et vérifié dans `corpora/v6_3/consensual.txt`. Rien n'est perdu.
- **`domain_map_v6.json` déclaré `22e93f04d907f036…` contre `5a8abe901f09bb8e…`
  sur disque.** Ce n'est pas une divergence de contenu : le hash déclaré est
  celui de `json.dumps(contenu, indent=2)` sans saut de ligne final — une
  **re-sérialisation canonique du même objet**. Les domaines fins s'alignent
  120/120 avec le fichier gelé.

Aucun des deux ne bloque quoi que ce soit. Les objections de fond des §2 à §5
sont, elles, inchangées.

Point mineur et correctement signalé par les auteurs : `transformers` manquait
dans leur conteneur, les longueurs ont été validées avec `gpt-3-encoder`. Je les
ai revérifiées avec le vrai tokenizer gpt2 — **0 violation**, le substitut était
fidèle.

---

## 7. Ce que ça change pour le protocole

**93 des 120 lignes contestées ont été réécrites** (27 seulement viennent de
l'arm v6-audité ; la colonne `author_provenance` le dit franchement). Ce n'est
plus le bras contesté gelé de v5/v6.

Conséquence à assumer explicitement : **v6.3 n'est comparable ni à v5 ni à v6.**
Les verdicts `HC_CONFIRMÉ` et `HD_DÉMENTI` portaient sur un autre matériel. v6.3
est un redémarrage, pas une itération — ce que le changement de numéro reconnaît
déjà, mais qui doit être écrit dans la note de résultats.

---

## 8. Recommandation

Ne pas mesurer. Trois corrections, toutes ciblées :

1. **Rendre la porte falsifiable à nouveau.** Garder l'égalité des marqueurs
   comme *règle de construction* — elle est bonne — mais faire porter le **gate**
   sur des features **non utilisées à la construction** : TF-IDF en LODO, et un
   log-odds mot à mot avec un plafond. Une porte doit pouvoir dire non.
   Proposition concrète : `BA(TF-IDF, LODO) ≤ 0,60` et aucun mot au-delà d'un
   ratio de log-odds fixé sans être présent des deux côtés.

2. **Ré-apparier sur le SUJET, pas sur l'étiquette de champ.** C'est la
   correction la plus rentable, et elle est faisable. Le bon modèle de paire :

   > contesté : *Genetic differences explain most adult variation in measured intelligence.*
   > consensuel : *Genetic differences explain most variation in adult human height.*

   Même construction, même vocabulaire, même domaine, même registre — et l'un est
   disputé quand l'autre ne l'est pas. C'est ça qui neutralise TF-IDF, et c'est ce
   que v6 faisait mieux que v6.3.

3. **Supprimer les substituts.** `chiefly`, `materially`, `causally`, `explains`,
   `exceed` doivent être équilibrés entre les bras ou retirés. Tant qu'ils sont à
   9/0 et 0/15, six mots portent le tiers du signal bon marché.

Les deux hashes qui semblaient diverger sont résolus (§6) et ne bloquent rien.

---

*Tous les chiffres de cette note sont reproductibles depuis `evidence.tsv` et
`corpora/domain_map_v6.json` ; le script d'audit est en scratchpad et peut être
versionné sur demande.*
