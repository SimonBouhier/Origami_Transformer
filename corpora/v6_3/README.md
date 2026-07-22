# Corpus v6.3 — les deux bras réécrits

**⚠️ Ne pas confondre avec `corpora/contested.txt`.** Le fichier à la racine de
`corpora/` est le bras contesté **gelé de v5 et v6** (sha
`3eb7bae8506e97e274f407cf…`), sur lequel portent les verdicts `HC_CONFIRMÉ` et
`HD_DÉMENTI`. Il est intouchable. Le `contested.txt` **de ce dossier** est un
bras différent : 93 de ses 120 lignes ont été réécrites.

## Contenu

| fichier | sha256 | provenance |
|---|---|---|
| `contested.txt` | `85d795fb3d17e2d2aae8c35d…` | déposé tel quel ; **conforme** au hash de `CORPUS_FREEZE_v6_3.md` |
| `consensual.txt` | `eb537ee1577134f5e77fbbcf…` | **reconstruit** depuis la colonne 9 de `evidence.tsv` (jointure LF + saut de ligne final) ; sha **vérifié identique** à celui déclaré au gel |
| `evidence.tsv` | — | 120 paires, 12 colonnes : claims, ancres, URL de sources, rationales, provenance |
| `g1_report.json` | — | rapport G1 du tour 1 produit par les auteurs |

Le corpus correspond au `round1/` du protocole des auteurs (tour 0 échoué et
conservé immuable, cf. `CORPUS_FREEZE_v6_3.md`).

## Deux hashes qui semblaient diverger — résolus

- **`consensual.txt` n'avait pas été déposé.** Il est intégralement récupérable
  depuis `evidence.tsv` : la colonne 9, jointe par `\n` avec saut de ligne final,
  donne exactement le sha déclaré. Rien n'est perdu.
- **`domain_map_v6.json` déclaré `22e93f04d907f036…` contre `5a8abe901f09bb8e…`
  sur disque.** Ce n'est pas une divergence de contenu : le hash déclaré est
  celui de `json.dumps(contenu, indent=2)` (sans saut de ligne final), c'est-à-dire
  une **re-sérialisation canonique** du même objet. Les domaines fins s'alignent
  120/120 avec le fichier gelé. La piste d'audit tient.

## Statut

**Non gelé pour mesure.** Voir `AUDIT_CORPUS_v6_3.md` à la racine : le corpus
passe tous les contrôles mécaniques et l'audit de source, mais la porte G1 est
devenue non falsifiable (les 120 paires ont des vecteurs de marqueurs
identiques, donc BA = 0,5000 par construction) et le raccourci lexical s'est
déplacé vers des mots non enregistrés (BA = 0,6208 sur six mots ; TF-IDF 0,6292).

Aucune mesure de modèle n'a été lancée sur ce corpus.
