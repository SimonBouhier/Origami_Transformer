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
