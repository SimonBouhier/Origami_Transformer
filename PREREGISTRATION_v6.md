# Pre-Registration v6 — Cross-domain transfer of the contestation signature (H-D)

> **STATUS: DRAFT — thresholds PROPOSED, awaiting researcher validation ; to be
> FROZEN at the v6 freeze (commit dance).** This is the within-domain /
> cross-domain study. It runs AFTER v5 (`PREREGISTRATION_v5.md`, freeze
> `ca588c3`, verdict `HC_CONFIRMÉ` 3/4) and exists to eliminate the LAST cheap
> explanation left standing after v5: **domain vocabulary**. v5 established the
> signature (C1), ruled out surface form (C2) and destroyed-structure artifacts
> (C3); its arms differed by domain BY CONSTRUCTION, so "the geometry reads the
> topic" remained open — flagged in `NOTE_RESULTATS_v5.md` (Limites) and
> `README_corpora.md` §8. v6 closes it or the claim dies there.

**Frozen on**: TBD
**Frozen by**: Simon Bouhier
**Git commit at freeze**: TBD

## Hypothesis

H-D: The per-layer Fisher-metric signature of epistemic contestation
**transfers across knowledge domains** within a fixed model. A classifier on
the geometric features, trained on contested-vs-consensual statements from a
set of domains, separates contested from consensual statements **in a domain
it has never seen** — above chance, above what lexical features transfer, and
collapsing under destruction of linguistic structure.

If H-D holds together with v5, the defensible claim becomes: *the Fisher
geometry captures a proxy of the epistemic status of statements, not a content
effect* (researcher's formulation, 2026-07-21). If H-D fails, the honest
reading is that the v5 signature was carried largely by domain content — a
pre-registered, publishable boundary result.

Definitions: **Contested / Consensual** exactly as frozen in v5 ((A)
expert-contested only; value judgments excluded). **Domain** = the `domain`
column of `corpora/contested_anchors.tsv` (frozen at the v6 freeze after the
consensual-by-domain arm is built), coarsened into K super-domains of
n ≥ 12 statements per arm each (coarsening map frozen with the corpus).

## Corpus (construction protocol — frozen at the v6 freeze)

- **Contested arm: UNCHANGED** — `corpora/contested.txt` as frozen in v5
  (sha256 `3eb7bae8…`). Its v5 Fisher measurements are **reused as-is**
  (deterministic instrument, same protocol; explicitly decided here, before
  any v6 analysis).
- **Consensual-by-domain arm: NEW** — `corpora/consensual_v6.txt`, 120
  well-formed truth-apt claims under broad established agreement, drawn from
  the SAME domains as the contested arm, matching its per-domain counts.
  Same hard constraints as v5 (English declaratives, no hedges, 9–16 gpt2
  tokens, no duplicates); **length-matched within domain** (greedy
  deterministic pairing, per-domain; report committed). Register matched to
  the contested arm (empirical claims, same syntax family). The arm is built
  and quarantined pre-freeze, **never observed by any model** before the
  freeze; sha256 recorded here at the freeze.
- v5's `consensual.txt` (claims.txt-derived, different domains) is NOT reused
  in v6 verdicts.

## Observables

Extraction and Fisher metric: **identical to v4/v5** (frozen instrument,
`probe_fisher.py`; shuffle control, `probe_fisher_shuffle.py`; CPU, float32,
seed 0, k = 50).

- **O1 (primary — cross-domain separability).** Per model, logistic regression
  (L2, C = 1.0, same convention as v5) on the per-layer feature vector
  [O_vol, O_rank, O_aniso], evaluated under **leave-one-domain-out (LODO)**
  cross-validation: folds = super-domains; predictions pooled out-of-fold →
  `BA_geo_lodo`, `AUC_geo_lodo`. (LODO is the field-standard protocol for this
  question — STATE_OF_ART §10.)
- **O2 (lexical-transfer baseline).** Same classifier and SAME LODO folds on a
  **bag-of-words TF-IDF** representation of the statements (unigrams+bigrams,
  min_df = 2; exact vectorizer config frozen in `analysis_v6.py` before any
  data) → `BA_lex_lodo`. This is the strong lexical baseline v5 lacked; under
  LODO, domain vocabulary does not transfer, so what remains is transferable
  lexical style — exactly the competitor to beat.
- **O3 (content-destruction under transfer).** O1 recomputed on token-shuffled
  inputs (both arms) under the same LODO folds → `BA_geo_shuf_lodo`.
- **B1 (instrument sanity — VOID gate, unchanged from v5).** Pooled-corpus
  max-layer |Spearman(O_rank, NLL)| ≥ 0.30, else the model's run is VOID.

## Falsification thresholds (PROPOSED — researcher validates, then frozen, no coussin)

- **C1** (transfer above chance): `BA_geo_lodo >= 0.60`
  *(lower than v5's 0.65: LODO is strictly harder than stratified CV; the
  nearest literature shows ~25-pt OOD drops — 0.60 keeps the bar meaningful
  without demanding what no published probe achieves)*
- **C2** (beats lexical transfer): `BA_geo_lodo - BA_lex_lodo >= 0.08`
- **C3** (content-dependent): `BA_geo_lodo - BA_geo_shuf_lodo >= 0.08`

Verdict per model: H-D confirmed iff C1 AND C2 AND C3; VOID if B1 fails.
Global: confirmed on ≥ **3 of 4** models AND fraction ≥ **0.66**.
A global denial is a pre-registered, publishable boundary result.

## Anti-confirmation clause

A denial means: the geometric signature does not survive removal of domain
identity (C1), or transfers no better than lexical style (C2), or what
transfers is not borne by linguistic structure (C3). Given STATE_OF_ART §10
(truth-probes drop ~25 pts OOD; skepticism-geometry attenuates across
domains), **the prior for H-D is LOW-to-moderate — a denial is the likely
outcome** and would bound the v5 claim honestly ("a real signature, largely
domain-carried"). A confirmation under LODO would be correspondingly strong:
together with v5's C2/C3 it would leave "proxy of epistemic status" as the
last explanation standing among those tested.

## Scope

Models: the same four as v4/v5 (`gpt2`, `EleutherAI/pythia-410m`,
`facebook/opt-350m`, `bigscience/bloom-560m`) — OPT retained as instrument
stress-test (expected VOID per v4/v5 B1 history). CPU, float32, seed 0, k=50.
New measurements required: consensual_v6 arm × {fisher, shuffle} × 4 models
(the contested-arm v5 outputs are reused; ≈ half a v5 campaign, ~2 h 15 CPU).
sha256 of `consensual_v6.txt`, the per-domain pairing report and the
domain-coarsening map recorded at the v6 freeze and re-checked at run time.

## Out-of-scope

- Any change to the Fisher instrument or to v5 definitions.
- Larger / instruction-tuned models (v7, GPU protocol frozen from the start).
- The OPT/LN-lens investigation (separate track).
- Causal/interventional claims; EPP attestation (bridge work proceeds
  separately on the already-confirmed v5 result).
