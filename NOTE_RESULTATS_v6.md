# Note de résultats — v6 Transfert inter-domaines (H-D)

**Date :** 2026-07-21
**Dépôt :** github.com/SimonBouhier/Origami_Transformer
**Pré-enregistrement :** `PREREGISTRATION_v6.md`, gelé le 2026-07-21, commit `10b6c89895403be0df2731a2953870f80a26c6a2` (stamp `75ea4e3`)
**Verdict global :** `HD_DÉMENTI` — **0/4 modèles confirmés**, 2 VOID ; seuils C1 ≥ 0,60 / C2 ≥ +0,08 / C3 ≥ +0,08, sans coussin
**Statut :** négatif pré-enregistré — **il borne le résultat v5**, il ne l'annule pas

---

## Résumé

v5 avait établi une séparation contesté/consensuel dans la géométrie de Fisher,
après élimination de la forme de surface (C2 v5) et de la structure détruite
(C3 v5). Restait une explication concurrente : **le domaine lexical**, les deux
bras différant par construction. v6 la teste en appariant les domaines ligne à
ligne et en évaluant en **leave-one-domain-out** contre une baseline
non-géométrique renforcée (TF-IDF ∪ features de surface).

**Résultat : la signature transfère, mais elle n'est pas géométriquement
spécifique.**

- **C1 passe 4/4** : le classifieur géométrique sépare contesté/consensuel dans
  des domaines **jamais vus à l'entraînement** (BA 0,629 à 0,817). Le transfert
  inter-domaines existe.
- **C3 passe 4/4** : détruire l'ordre des tokens ramène la séparation au hasard
  (0,50–0,62). Ce qui transfère est bien porté par la structure linguistique.
- **C2 échoue 4/4** : une baseline **bon marché** (TF-IDF + longueur + fréquence
  lexicale + ponctuation) atteint **BA ≈ 0,74 sur les quatre modèles** en LODO.
  La géométrie ne la bat pas de la marge exigée — elle fait moins bien sur gpt2.

Conclusion honnête : après suppression de l'identité de domaine, ce que lit la
géométrie de Fisher est **largement récupérable par des traits lexicaux et de
surface transférables**. La lecture « proxy du statut épistémique, plutôt qu'un
effet de contenu » **n'est pas défendable sur ces données**.

## Chiffres (seuils gelés : C1 ≥ 0,60 ; C2 ≥ +0,08 ; C3 ≥ +0,08 ; B1 ≥ 0,30)

| modèle | BA_geo LODO | BA_lex LODO | marge C2 | BA_shuffle | marge C3 | B1 \|ρ\|max | verdict |
|---|---|---|---|---|---|---|---|
| gpt2 | 0,629 ✓ | 0,738 | **−0,108** ✗ | 0,500 | +0,129 ✓ | 0,255 ✗ | **VOID** |
| pythia-410m | 0,746 ✓ | 0,754 | **−0,008** ✗ | 0,508 | +0,238 ✓ | 0,314 ✓ | **HD_DÉMENTI** |
| opt-350m | 0,750 ✓ | 0,738 | **+0,012** ✗ | 0,575 | +0,175 ✓ | 0,143 ✗ | **VOID** |
| bloom-560m | 0,817 ✓ | 0,746 | **+0,071** ✗ | 0,617 | +0,200 ✓ | 0,353 ✓ | **HD_DÉMENTI** |

Corpus : bras contesté v5 inchangé (sha `3eb7bae8…`, mesures v5 réutilisées) +
`consensual_v6.txt` (sha `71170920…`) apparié **par domaine fin, ligne à ligne**.
7 folds LODO (super-domaines, n ≥ 12 par bras). CPU, float32, seed 0, k = 50.
Campagne ≈ 2 h 15 (horodatages 11:00 → 13:15), aucun NaN imputé.

## Lectures

1. **Le démenti ne tient pas à la porte VOID.** Les quatre modèles échouent C2,
   VOID ou non. Retirer entièrement le garde-fou B1 ne changerait rien au
   verdict : `HD_DÉMENTI` 0/4 dans tous les cas. C'est un démenti robuste.

2. **La baseline bon marché est le vrai résultat de cette campagne.**
   BA_lex ≈ 0,74 — et quasi identique sur les quatre modèles (0,738 / 0,754 /
   0,738 / 0,746), ce qui est attendu puisqu'elle ne dépend presque pas du
   modèle. Autrement dit : **il existe un style linguistique du contesté qui
   traverse les domaines**, indépendamment de toute géométrie interne. Les
   énoncés contestés de notre corpus sont massivement comparatifs et
   attributifs de causalité (« more than », « primarily caused by », « rather
   than »), les consensuels plutôt définitionnels. Cette régularité de surface
   est un confond que v5 ne pouvait pas voir, et que v6 met au jour.

3. **bloom rate de neuf millièmes.** Marge C2 = +0,071 pour un seuil à +0,080.
   Sans coussin, c'est un échec — et c'est exactement la discipline qui
   fonctionne : un seuil qu'on desserre après coup n'est plus un seuil. À
   noter tout de même : bloom est le seul modèle dont la géométrie dépasse
   nettement le bon marché, et il était déjà le plus net en v4 et v5.

4. **Le durcissement pré-gel de la baseline a mordu.** O2 avait été renforcé
   avant le gel (TF-IDF **∪** surface, au lieu de TF-IDF seul). On ne peut pas
   savoir, sans recalcul descriptif, si bloom aurait passé C2 contre la version
   faible — mais la décision de durcir avant de voir les données est ce qui
   donne au démenti sa valeur. Décomposer la baseline (lexical seul vs surface
   seul) est un diagnostic **hors verdict** proposé pour v7.

5. **Chute v5 → v6 remarquablement constante.** BA_geo : gpt2 0,729 → 0,629
   (−0,100) ; pythia 0,838 → 0,746 (−0,092) ; opt 0,821 → 0,750 (−0,071) ;
   bloom 0,908 → 0,817 (−0,091). Moyenne ≈ −0,089. Tentant d'y lire « la part
   du domaine », mais **les deux campagnes ne sont pas strictement comparables**
   (corpus consensuel différent, protocole de validation différent : CV
   stratifiée vs LODO). À traiter comme une régularité observée, pas comme une
   décomposition.

6. **L'ordre des modèles survit intégralement** : bloom > opt ≈ pythia > gpt2,
   identique à v5. La capacité du modèle module l'ampleur de la signature, quel
   que soit le protocole.

7. **Le garde-fou B1 est sensible au corpus.** gpt2 passe de 0,342 (v5) à 0,255
   (v6) et bascule sous la porte ; bloom de 0,471 à 0,353. Or B1 se calcule sur
   le corpus poolé, et le bras consensuel a changé. Le couplage rang↔NLL n'est
   donc pas une propriété stable du modèle seul : il dépend du matériel mesuré.
   OPT reste sous la porte pour la troisième campagne consécutive (0,197 en v4,
   0,133 en v5, 0,143 en v6) — cohérent avec son lens tronqué (`project_out`,
   rang ≤ 512).

## Ce qui reste debout, ce qui tombe

**Tombe :** l'idée que la géométrie de Fisher capte un proxy du statut
épistémique *indépendamment du contenu et de la forme*. Sur ces données, elle ne
bat pas ce qui est bon marché.

**Reste debout :**
- il existe une séparation contesté/consensuel qui **transfère à des domaines
  non vus** (C1, 4/4) ;
- elle **dépend de la structure linguistique** (C3, 4/4, effondrement au
  hasard sous mélange) ;
- elle **croît avec la capacité du modèle** (ordre stable sur trois campagnes) ;
- et le résultat v5 lui-même **n'est pas invalidé** : il est *borné*. La
  séparation qu'il mesurait était réelle ; v6 montre qu'elle était largement
  portée par le domaine et le style, non par une spécificité géométrique.

## Limites

- **n = 120 par bras, 4 petits modèles (124M–560M), anglais.** Inchangé
  depuis v5.
- **Deux modèles sur quatre n'ont pas voix interprétable** (VOID). Le démenti
  reste robuste (cf. Lecture 1), mais l'information utile vient de 2 modèles.
- **Pas d'intervalle de confiance** : graine unique, découpage LODO unique.
  Les marges C2 de pythia (−0,008) et bloom (+0,071) sont dans un régime où un
  bootstrap changerait probablement la lecture qualitative — à faire, hors
  verdict.
- **Le corpus consensuel v6 est écrit par un agent** (déterministe, ancré,
  apparié, vérifiable) et non tiré d'une source externe indépendante. Un biais
  systématique de rédaction reste possible ; c'est précisément ce que la
  baseline lexicale semble détecter.
- **Le style comparatif du bras contesté n'est pas contrôlé.** C'est le
  confond suivant, et il est maintenant identifié.

## Conséquences dans l'écosystème

⚠️ **Le pont Origa → Lyra doit être réexaminé.** Sa condition de dégel (« verdict
v5 `HC_CONFIRMÉ` aux seuils gelés ») reste formellement remplie — v5 est
inchangé. Mais l'interprétation qui justifiait le pont (« la géométrie de Fisher
comme *tension épistémique instrumentée* ») **n'est plus soutenable en l'état** :
v6 montre que le signal n'est pas géométriquement spécifique. Importer cette
mesure dans `lyra_reborn` comme signal épistémique reviendrait à survendre.

**Recommandation :** maintenir le pont **gelé** jusqu'à ce qu'une campagne
contrôle le style linguistique (v7). La doctrine des ponts dit qu'un pont ne se
dégèle que sur validation — elle ne dit pas qu'il ne peut pas se re-geler quand
la validation se révèle plus étroite qu'espéré. Décision du chercheur.

Le pont Origa → EPP est dans la même situation : conditions formelles réunies,
interprétation à réviser.

## Prochaines marches (v7, chacune à pré-enregistrer)

1. **Contrôler le style, pas seulement le domaine.** Apparier les deux bras sur
   la **construction syntaxique** (comparatifs contre comparatifs, attributions
   causales contre attributions causales). Si la géométrie bat encore le bon
   marché après ça, la thèse redevient défendable — et sérieusement.
2. **Décomposer la baseline** (hors verdict) : TF-IDF seul vs surface seule vs
   union, pour identifier quels traits transfèrent. Cela guide la conception
   du corpus v7.
3. **Bootstrap descriptif** des BA/AUC (hors verdict) : les marges serrées de
   pythia et bloom méritent une barre d'erreur.
4. **Stabilité de B1** : comprendre la sensibilité du couplage rang↔NLL au
   corpus mesuré ; c'est une propriété de l'instrument, pas du modèle.
5. Toujours ouvert : LN-lens pour l'anomalie OPT ; modèles plus grands (GPU,
   protocole gelé dès le départ).

---

*Analyse : `analysis_v6.py` (seuils gelés, folds LODO, vérification sha256,
refus des pilotes). Rapport brut : `results/analysis_v6_report.json`
(non versionné, régénérable). Le bras contesté n'a pas été re-mesuré ; le bras
consensuel v6 n'avait jamais été observé avant le gel.*
