# Research Log

Append-only chronological log. Newest entries at the bottom. Do not edit
prior entries — supersede with a new one.

---

## 2026-05-30 — v3 measurement campaign

Wrote `probe.py` (TwoNN + MLE per layer, bootstrap, pre-registered verdict)
and `analysis.py` (frozen thresholds: C1 inter-estimator agreement ≥ 70%,
C2 strict interior peak, C3 strict last-below-peak).

Ran on 4 models: gpt2, EleutherAI/pythia-410m, bigscience/bloom-560m,
facebook/opt-350m. Results in `archived/v3_results/`.

Per-model:
- gpt2: H1 confirmed (peak @ 11, last 12 < 14)
- opt-350m: H1 confirmed (peak @ 22, last 13 < 16)
- pythia-410m: H1 denied (peak @ 0 — embedding layer)
- bloom-560m: H1 denied (peak @ 0 — embedding layer)

Global: 2/4 confirmed — below the 4/6 threshold even before completing the
campaign. Inter-estimator divergence on pythia and bloom (TwoNN ~10, MLE
~20) was the loudest signal.

## 2026-05-31 — Literature review (the one we should have done first)

Found four directly relevant papers, all predating our 2026-05-30 freeze:
- arxiv:2604.20276 (AISTATS 2026) — TwoNN/MLE do not measure true ID.
- arxiv:2511.20315 (NeurIPS 2025) — hunchback profile confirmed across 28 models.
- arxiv:2405.15471 — the peak has functional meaning.
- arxiv:2603.22301 — Riemannian framework with Fisher metric, density-free.

See `STATE_OF_ART.md` for digests.

**Decision**: v3 archived. `probe.py` moves to `archived/probe_v3.py`. The
inter-estimator divergence we observed is now reinterpreted as an
independent empirical confirmation of Schulte & Rügamer — that is itself a
publishable side-finding.

## 2026-05-31 — Pivot decision

Primary instrument changes from NN-based ID estimation to **Fisher
information metric restricted via logit-lens** (Mabrok §5).
Per-layer observables now available without sampling assumptions:
- volume element √det g (on a fixed top-k subspace)
- effective rank of the metric
- anisotropy ratio
- geodesic vs euclidean distance gap

`curvature.py` survives in spirit but its dependence on TwoNN/MLE-derived `d`
must be cut. Reformulate as a spectral, dimension-free residual.
`spectrum.py` (to write) — effective spectral rank — is untouched by §1's
critique because it's a covariance-spectrum measure, not an NN estimator.

## Pending — researcher decision on v4 hypothesis

Three pre-registration candidates, all measurable with the new instrument
suite and density-free:

### H-A — Volume hourglass
The Fisher volume element √det g (on fixed top-k subspace) follows a
non-monotonic profile across layers: expansion then contraction. This is
H1 re-tested with a clean instrument. Low novelty (shape established by
§3), but a clean confirmation under the new metric is itself
methodologically useful as a baseline. Lowest risk of failure.

### H-B — Curvature signature
Local extrinsic curvature (redefined dimension-free, spectral) peaks in
middle "abstraction" layers and flattens at the end. Connects `curvature.py`
to the high-dim phase of §2. Medium novelty — §4 (Mabrok) partly covers
curvature but does not isolate this functional placement. Need to read §4
carefully to confirm what is and is not already there.

### H-C — Geometry ↔ function coupling
A geometric quantity at layer ℓ (Fisher volume or curvature) **predicts**
the per-layer logit-lens NLL on next-token prediction. Not "is there a
shape" but "does the shape explain function". Highest novelty. The natural
extension of §2 and §3 with §4's machinery. Possible EPP bridge variant:
test the same coupling on contested vs consensual statements — does
geometry distinguish them?

**The researcher chooses.** This document records the candidates; the
chosen hypothesis goes into `PREREGISTRATION_v4.md` and is signed by
git commit before any v4 measurement runs.

---

## 2026-05-31 — v4 hypothesis chosen: H-C, scoped to the EPP bridge

Resolves the "Pending — researcher decision" section above.

Decision (researcher): v4 tests **H-C**. The `literature-first` pass on this date
(three fronts, ~16 query phrasings) found:
- Front A — generic "geometry predicts per-layer logit-lens NLL" coupling: RED / saturated.
  Already published (Viswanathan et al. 2501.10573 — also the paper Mabrok miscites as
  "Ferrara [14]"; RankMe 2210.02885; Hosseini & Fedorenko 2311.04930; Skean 2502.02013)
  and confounded by training hyperparameters (Kulkarni 2602.20433).
- Front B — Fisher-metric instrument: GREEN, with one concurrent neighbour to cite and
  differentiate (FishBack 2605.17231: output-Fisher via Jacobian pullback + steering;
  we use the per-layer logit-lens form + measurement).
- Front C — contested<->consensual × metric geometry: GREEN. The conjunction is unpublished.

Scope (researcher's call, "contesté primaire + baseline"):

**H-C (scoped):** A Fisher-metric observable (volume sqrt(det g), effective rank, and/or
curvature; logit-lens-restricted, density-free) computed per layer **distinguishes contested
from consensual epistemic statements within a fixed model.** The generic geometry<->NLL
coupling is retained ONLY as a pre-registered baseline (instrument sanity-check), NOT a
claimed contribution.

Instrument: g(h) = W_u^T (diag(p) − p p^T) W_u per layer (Mabrok §5). NN-ID estimators stay
archived (§2.3).

Constraints carried into PREREGISTRATION_v4 (see STATE_OF_ART §5–§9):
- Compare WITHIN model (contested vs consensual at fixed weights) to neutralise the
  training-hyperparameter confound (2602.20433).
- Expect a possibly weak/null semantic signal (Baroni 2601.03779) — thresholds honest, a
  null is publishable.
- Operational definition of "contested" must be distinct from ambiguous / uncertain / false
  (the conceptual seam) — to be fixed with the researcher before freezing.
- Stay on Fisher / effective rank; do not regress to NN-LID (closest adjacent, Yin 2402.18048,
  uses exactly the archived family).

Next: fix the operational definition + corpus + model set with the researcher, then invoke the
preregistration skill to write PREREGISTRATION_v4.md (committed before any script reads real data).

---

## 2026-06-02 — Re-scoping: v4 = Fisher baseline (V3 repasse), H-C devient v5

Researcher decision (2026-05-31/06-01): before the EPP-bridge study, re-run the V3 campaign
under the Fisher instrument, with the same pipeline v5 will use. Direct answer to Schulte
(STATE_OF_ART §1): does the v3 hunchback survive a density-free instrument?

- PREREGISTRATION_v4.md = Fisher baseline / V3 repasse (H-A under Fisher). Thresholds frozen
  by the researcher: C1 interior peak of P_rank; C2 strict final compression; C3
  max_l |Spearman(O_rank, NLL)| >= 0.30; global >= 3/4 models.
- PREREGISTRATION_v5.md = contested vs consensual (H-C), thresholds validated (BA_geo >= 0.65;
  AUC_geo - AUC_surf >= 0.10; BA_geo - BA_geo_shuf >= 0.08; >= 3/4), frozen at the v5 freeze
  AFTER v4 completes. No contamination: v4 sees only the factual corpus marginal; the v5 test
  is the contested<->consensual CONTRAST, whose contested arm is built only at the v5 freeze.

Commit dance executed: freeze 4e9683efead2fafea26b26ce2d37611e97f69269 "preregister v4"
(2026-06-02 12:06 +0200), stamp aa9997f "stamp v4 freeze" (12:46).

## 2026-07-09 — Audit du gel v4, instrument ecrit, campagne lancee

Audit du commit dance (session Fable), tout conforme:
- Gel 4e9683ef..69269: PREREGISTRATION_v4.md seul (89 lignes). Tampon aa9997f: modifie
  uniquement la ligne du hash, qui pointe bien le commit de gel. Encodage UTF-8 intact.
  Branche synchronisee avec origin/main (github.com/SimonBouhier/Origami_Transformer).
- Ecart de dates, note pour transparence: le fichier dit "Frozen on: 2026-05-31" (jour de
  redaction), les commits datent du 2026-06-02. La date qui fait foi est celle du commit.
  Le fichier gele n'est pas edite (interdit post-tampon).
- Corpus fige par l'arbre du commit de gel (claims.txt, blob 7b8d4512). sha256(fichier) =
  91047e94f1d308c3086e7e13df6f1476a0b48f5ddfc592b1c4b668d7720fc40c ; hash "join des lignes"
  (convention probe.py v3) = ebdc64bd...adc53b — identique a la NOTE v3: corpus inchange.
- Convention d'indice C1, fixee AVANT toute donnee v4: "peak in [1, L-2]" se lit avec la
  convention v3 (L = NOMBRE de couches captees, analysis.py v3: 1 <= peak <= L-2), soit
  "exclut exactement la premiere et la derniere couche" — conforme a la glose "strictly
  interior" du texte gele. Implementation: 1 <= argmax <= n_layers - 2 (indices 0-based).

Instrument (ecrit post-tampon, comme l'exige la danse):
- probe_fisher.py — instrument pur, zero verdict. Logit-lens brut (sans LN finale), Fisher
  g = W_u^T (diag(p) - p p^T) W_u exacte sur tout le vocabulaire, spectre par eigvalsh
  float64, O_rank / O_vol(k=50) / O_aniso + NLL logit-lens par (enonce, couche).
  Gestion OPT-350m: unembedding effectif lm_head @ project_out (rang <= 512, propriete
  du modele).
- analysis_v4.py — applique les seuils geles (C1/C2/C3, >= 3/4, F=0.66). Refuse les sorties
  pilotes. analysis.py (v3) reste intact comme artefact historique jusqu'a l'archivage v3.
- Piege metrologique trouve au pilote et corrige: la queue de la softmax produit des
  probabilites SUBNORMALES (float32 < 1.2e-38) qui font tomber les GEMM de ~700 a ~80
  GFlops (assist microcode x86). Fix: torch.set_flush_denormal(True). Verification: sorties
  bit-identiques sur 39 points x 4 observables (ecart relatif max = 0.0), 6.44 -> 0.12
  s/point. C'est un correctif numerique documente, pas un changement de definition.
- Pilotes debug (gpt2, 3 enonces, scratchpad hors depot, non analyses), conformes au skill.

Campagne v4 lancee en arriere-plan: gpt2, pythia-410m, opt-350m, bloom-560m x claims.txt
-> results/*_fisher.json, puis analysis_v4.py -> results/analysis_v4_report.json.
Duree estimee ~2h15 (extrapolation pilote; bloom domine via son vocab 250k).

## 2026-07-09 (suite) — Incident OPT-350m: espaces de representation mixtes

gpt2 (10 min, 0.22 s/pt) et pythia-410m (45 min, 0.49 s/pt) termines proprement au premier
lancement. Crash sur opt-350m, AVANT toute valeur observee pour ce modele:
transformers 5.9 capture pour opt-350m les couches 0..23 en hidden_size=1024 et la DERNIERE
en word_embed_proj_dim=512 (etat post-project_out, celui que lm_head lit directement).
L'instrument supposait un espace unique.

Resolution, fixee avant toute valeur OPT observee: "the model's own unembedding" (texte gele)
se lit PAR ESPACE de representation — decode-map lm_head o project_out pour les etats 1024,
lm_head seul pour l'etat 512. C'est le chemin de decodage effectif du modele depuis chaque
espace; pas de changement pour les modeles a espace unique (gpt2, pythia, bloom — leurs runs
restent valides tels quels). probe_fisher.py enregistre desormais hidden_dims_per_layer.
Verification par mini-pilotes (2 enonces, scratchpad, non analyses): opt espaces=[512,1024]
OK a 0.50 s/pt; bloom uniforme 1024 OK a 1.99 s/pt.

Campagne relancee: opt-350m puis bloom-560m puis verdict analysis_v4.py sur les 4 JSON.
Duree estimee restante ~3h45 (bloom ~3h a ~2 s/pt, vocab 250880).

opt-350m termine proprement (220/220, 44.6 min, 0.49 s/pt, espaces [512, 1024]).
bloom-560m interrompu a 65/220 par l'arret du processus hote (pas une erreur de
l'instrument; probe_fisher.py n'ecrit son JSON qu'en fin de run, donc pas de reprise
partielle) — relance complete le 2026-07-09, verdict analysis_v4.py enchaine sur les 4 JSON.
3/4 sorties completes au moment de cette note: gpt2, pythia-410m, opt-350m.

(Deuxieme interruption machine — redemarrage Windows Update — a 10/220 de la relance
bloom. Troisieme lancement complet: 220/220 en 72.2 min a 0.79 s/pt. Aucune donnee
corrompue a aucun moment: le JSON s'ecrit atomiquement en fin de run.)

---

## 2026-07-09 — Verdict v4 : HA_DEMENTI global (1/4)

analysis_v4.py, seuils geles (commit 4e9683ef), sur les 4 sorties completes.
Duree des runs: gpt2 10.4 min / pythia 45.3 / opt 44.6 / bloom 72.2.

| modele        | L  | P_rank[0] | pic          | P_rank[fin] | C1 | C2 | C3 (rho_best)   | verdict     |
|---------------|----|-----------|--------------|-------------|----|----|-----------------|-------------|
| gpt2          | 13 | 510.24    | 0  (=510.24) | 118.87      | X  | ok | X  (+0.290@12)  | HA_DEMENTI  |
| pythia-410m   | 25 | 888.68    | 0  (=888.68) | 50.29       | X  | ok | ok (+0.335@1)   | HA_DEMENTI  |
| opt-350m      | 25 | 437.54    | 0  (=437.54) | 47.78       | X  | ok | X  (+0.197@18)  | HA_DEMENTI  |
| bloom-560m    | 25 | 580.59    | 22 (=731.15) | 103.15      | ok | ok | ok (+0.486@24)  | HA_CONFIRME |

GLOBAL: 1/4 (25%) -> HA_DEMENTI. C'est le negatif pre-enregistre prevu, publiable.

Lecture (hors verdict, a developper dans NOTE_RESULTATS_v4):
- C2 (compression finale) universelle 4/4 — comme C3 en v3. La compression finale est
  le motif qui survit au changement d'instrument (NN -> Fisher). Resultat robuste des
  deux campagnes.
- C1 echoue sur 3/4 par pic en couche 0 — echo direct du mode d'echec v3 (explosion
  MLE couche 0). Au lens de la couche 0, p est quasi uniforme -> rang de Fisher quasi
  maximal (510/768 gpt2; 889/1024 pythia; 437 pour opt dont le lens est de rang <= 512).
  Deux lectures concurrentes NON departagees par ces donnees: (a) la bosse interieure
  etait un artefact d'estimateur NN (sens Schulte, STATE_OF_ART section 1); (b) la
  couche 0 est un regime degenere du logit-lens (artefact de lens, symetrique de (a)).
  bloom, seul confirme (pic interieur 22, P_rank[0]=580 < 731), est aussi le seul dont
  les embeddings passent par une LayerNorm dediee (word_embeddings_layernorm) avant le
  stream — difference architecturale plausible, a creuser.
- C3: couplage O_rank<->NLL faible a modere, TOUJOURS POSITIF (rang plus haut <-> NLL
  plus haute, meme direction que Viswanathan 2501.10573, STATE_OF_ART section 5).
  gpt2 echoue a 0.290 pour un seuil de 0.30 — sans coussin, conformement a la
  discipline. Coherent avec le prior "signal semantique faible" (section 7).
- Toute exclusion de la couche 0 exige un pre-enregistrement NOUVEAU (jamais
  retroactif). Lecon a porter au gel v5.

## 2026-07-20 — Verdict v5 : HC_CONFIRME global (3/4, 1 VOID)

Gel v5 le 2026-07-19 (commit ca588c3, stamp fbfc2c2) : corpus purifie (A)
expert-conteste seulement (decision chercheur — jugements de valeur exclus,
esprit EPP), 120/bras, anchors 120/120 sans REVIEW, appariement 119/120 exact.
Campagne le 2026-07-20, CPU float32 seed 0 : gpt2 13 min / pythia 40 / opt 36 /
bloom 179 (~4 h 30 total). Analyse aux seuils geles, sha256 verifies au run-time.

| modele      | BA_geo | AUC_geo | AUC_surf | C2     | BA_shuf | C3     | B1        | verdict     |
|-------------|--------|---------|----------|--------|---------|--------|-----------|-------------|
| gpt2        | 0.729  | 0.792   | 0.645    | +0.147 | 0.512   | +0.217 | 0.342@12  | HC_CONFIRME |
| pythia-410m | 0.838  | 0.923   | 0.650    | +0.273 | 0.608   | +0.229 | 0.319@1   | HC_CONFIRME |
| opt-350m    | 0.821  | 0.901   | 0.645    | +0.255 | 0.575   | +0.246 | 0.133@22  | VOID        |
| bloom-560m  | 0.908  | 0.955   | 0.644    | +0.311 | 0.633   | +0.275 | 0.471@24  | HC_CONFIRME |

GLOBAL : 3/4 confirmes (75%) -> HC_CONFIRME. Premier positif pre-enregistre du
projet, apres les negatifs v3 et v4.

Lecture (details : NOTE_RESULTATS_v5.md) :
- C2 : surface quasi constante (~0.645) sur les 4 modeles, geometrie largement
  au-dessus. C3 : effondrement sous melange (0.51-0.63). Les deux controles ont
  fait leur travail.
- OPT = le signal fort : C1/C2/C3 passes avec les memes marges que les
  confirmes, mais B1 echoue (0.133) — echo direct du C3 v4 (0.197) et de
  l'incident "espaces de representation mixtes" (journal 2026-07-09). La porte
  VOID a refuse de compter une confirmation d'instrument non valide sur ce
  modele. Hypothese v6 : la projection project_out (rang<=512) casse le
  couplage rang<->NLL, pas la signature de contestation. LN-lens a departager.
- Honnete : le global tient a 3 confirmes pour 3 requis — sans marge.
- Portes ouvertes (doctrine des ponts) : conditions de degel epp_adapter
  reunies ; condition du pont Origa->Lyra (H-C confirme aux seuils geles)
  REMPLIE. Chantiers a dessiner, chacun pre-enregistre.

## 2026-07-21 — Scoping v6 (H-D) : transfert inter-domaines de la signature

Question du chercheur : apres elimination de la surface (v5-C2), de l'ordre des
tokens (v5-C3), reste le DOMAINE LEXICAL — si la signature survit, la lecture
« proxy du statut epistemique » devient defendable ; sinon, borne honnete.

Literature-first (STATE_OF_ART §10) : leave-one-domain-out = protocole standard
du champ voisin (truth-probes) ; transfert OOD typiquement faible (~-25 pts) ;
voisin le plus proche (2607.01951, geometrie x scepticisme utilisateur, juil.
2026) attenue/inverse en transfert. Conjonction Fisher x contestation x
transfert inter-domaines : NON PUBLIEE — verte.

PREREGISTRATION_v6.md redige en DRAFT : bras conteste v5 reutilise tel quel
(mesures v5 comprises — decision explicite pre-analyse), nouveau bras
consensuel PAR DOMAINE (120, memes domaines que le conteste, apparie en
longueur INTRA-domaine, quarantaine avant gel), evaluation LODO, baseline
lexicale TF-IDF (la baseline forte que v5 n'avait pas), shuffle sous LODO,
B1/VOID inchanges. Seuils PROPOSES (C1 0.60 ; C2 +0.08 ; C3 +0.08 ; global
3/4) — a valider par le chercheur avant gel. Prior assume BAS : le dementi est
l'issue probable, et publiable.

EN ATTENTE (chercheur) : validation des seuils + du protocole corpus ; puis
construction du bras consensuel_v6, gel (commit dance), campagne (~2 h 15).

## 2026-07-21 — Verdict v6 : HD_DEMENTI global (0/4, 2 VOID)

Gel v6 le 2026-07-21 (commit 10b6c89, stamp 75ea4e3). Bras conteste v5 reutilise,
nouveau bras consensuel APPARIE PAR DOMAINE ligne a ligne (34 domaines fins,
effectifs identiques), evaluation LODO sur 7 super-domaines, baseline
non-geometrique DURCIE avant gel (TF-IDF U surface). Campagne ~2 h 15.

| modele      | BA_geo | BA_lex | C2     | BA_shuf | C3     | B1    | verdict     |
|-------------|--------|--------|--------|---------|--------|-------|-------------|
| gpt2        | 0.629  | 0.738  | -0.108 | 0.500   | +0.129 | 0.255 | VOID        |
| pythia-410m | 0.746  | 0.754  | -0.008 | 0.508   | +0.238 | 0.314 | HD_DEMENTI  |
| opt-350m    | 0.750  | 0.738  | +0.012 | 0.575   | +0.175 | 0.143 | VOID        |
| bloom-560m  | 0.817  | 0.746  | +0.071 | 0.617   | +0.200 | 0.353 | HD_DEMENTI  |

GLOBAL : 0/4 -> HD_DEMENTI. C1 passe 4/4 (le transfert inter-domaines EXISTE),
C3 passe 4/4 (structure linguistique necessaire), C2 echoue 4/4 : une baseline
bon marche atteint BA ~0.74 en LODO sur les quatre modeles. Le dementi ne tient
PAS a la porte VOID (les 4 echouent C2 de toute facon) — robuste.

Lecture (details : NOTE_RESULTATS_v6.md) :
- Le vrai resultat est la baseline : il existe un STYLE du conteste qui traverse
  les domaines (comparatifs, attributions causales) — confond que v5 ne pouvait
  pas voir. C'est le prochain a eliminer.
- bloom rate de 9 millièmes (+0.071 vs +0.080). Sans coussin = echec. La
  discipline tient.
- Chute v5->v6 tres constante (~-0.09 sur les 4) mais campagnes non strictement
  comparables : regularite observee, pas decomposition.
- B1 sensible au corpus (gpt2 0.342->0.255, bascule sous la porte ; bloom
  0.471->0.353). Propriete de l'instrument, pas du modele. OPT sous la porte
  pour la 3e campagne (0.197 / 0.133 / 0.143).
- Ordre des modeles stable sur 3 campagnes : bloom > opt ~ pythia > gpt2.

CONSEQUENCE ECOSYSTEME : le pont Origa->Lyra doit etre RE-GELE. Sa condition
formelle (v5 confirme) tient, mais l'interpretation qui le justifiait — Fisher
comme tension epistemique instrumentee — n'est plus soutenable : le signal
n'est pas geometriquement specifique. Recommandation au chercheur : gel du pont
jusqu'a v7 (controle du style syntaxique). Idem pont Origa->EPP.

v7 propose : apparier sur la CONSTRUCTION SYNTAXIQUE, pas seulement le domaine.

## 2026-07-26 — Verdict v7 : HF_DEMENTI global (0/6)

Gel v7 le 2026-07-26 (commit aa120bd, stamp d89a45f). Premiere campagne a
pre-enregistrer une FORME et non un niveau : la marge geometrique tient-elle
quand on rend le corpus progressivement plus dur pour le bon marche ? 33 rungs
(120 -> 56 paires) construits MODEL-FREE, corpus v6.4 appari par domaine ET
par sujet, 6 modeles dont l'echelle Pythia controlee. 48/48 mesures conformes
au gel, 86 min de RTX 4090.

CONTROLE PREALABLE — corpus nul (deux bras du meme vivier consensuel) : toutes
les BA_geo sous leur plancher de permutation, tous les IC contenant zero. Le
pipeline ne trouve rien quand il n'y a rien, mesure GPU comprise. Etalon ~0.59.

| modele      | BA_geo r0->r32 | pente  | r(geo,cheap) | soutien | MDL gap |
|-------------|----------------|--------|--------------|---------|---------|
| bloom-560m  | 0.675 -> 0.554 | -0.102 | +0.833       | 11/33   | 0/33 >0 |
| gpt2        | 0.671 -> 0.607 | -0.058 | +0.692       | 19/33   | 0/33 >0 |
| opt-350m    | 0.688 -> 0.634 | -0.070 | +0.811       |  9/33   | 0/33 >0 |
| pythia-410m | 0.600 -> 0.589 | -0.030 | +0.511       |  4/33   | 0/33 >0 |
| pythia-1.4b | 0.683 -> 0.589 | -0.092 | +0.739       |  5/33   | 0/33 >0 |
| pythia-2.8b | 0.654 -> 0.491 | -0.152 | +0.949       |  0/33   | 0/33 >0 |

Requis : 22/33. GLOBAL 0/6 -> HF_DEMENTI.

Trois instruments independants concordent : (1) le critere gele echoue 0/6 ;
(2) la geometrie SUIT le bon marche, r = +0.51 a +0.95, les deux courbes
descendent ensemble — signature d'un confond partage ; (3) MDL, l'instrument
equitable en dimension, donne la geometrie MOINS compressive que le bon marche
sur 198/198 mesures, et les deux compressions sont sous 1.00 (hors domaine, ni
l'une ni l'autre ne paie son cout de modele).

ECHELLE PYTHIA : l'echelle n'aide pas, elle AGGRAVE. 2.8b a la pente la plus
raide (-0.152), la correlation la plus forte (+0.949), zero rung soutenante.
L'ordre inter-architectures de v4/v5/v6 ne se reproduit pas dans une famille
controlee -> confirmation directe de STATE_OF_ART §6 : notre ordre historique
etait un artefact de recette d'entrainement. La lecture "la signature croit
avec la capacite" TOMBE.

DEUX FAIBLESSES DECLAREES, toutes deux de mon fait :
 - Le retrait glouton pousse BA_cheap SOUS 0.50 (jusqu'a 0.425) aux rungs
   profonds : la marge y est un artefact du denominateur. La condition (1) du
   critere protege de ce piege et c'est elle qui fait echouer bloom et 2.8b au
   rung le plus dur. Lecon : en v8 le balayage doit s'arreter a BA_cheap = 0.50.
 - B1 echoue partout (0/33 pour 5 modeles sur 6). Sous les conventions
   v4/v5/v6 la campagne serait VOID. Mon pre-enregistrement mesure B1 mais ne
   l'a PAS inscrit comme porte : lacune de conception, non appliquee
   retroactivement. Le dementi n'en depend pas (un VOID n'est pas une
   confirmation, et les 3 instruments concordent). L'echec generalise de B1 sur
   un corpus sujet-appari est lui-meme un resultat.

CONSEQUENCE ECOSYSTEME : pont Origa->Lyra maintenu GELE, recommandation
desormais definitive. Le signal n'est geometriquement specifique a AUCUN niveau
de difficulte, sur AUCUN modele, et ne s'ameliore pas avec la capacite. Idem
Origa->EPP. Decision du chercheur.

SUITE : ne pas rejouer la meme mesure sur un corpus marginalement different.
Reste (1) Q3, la provenance externe — seule variable jamais touchee ;
(2) reparer/remplacer B1 ; (3) publier la serie des quatre negatifs
pre-enregistres, qui est probablement la vraie contribution du projet.
