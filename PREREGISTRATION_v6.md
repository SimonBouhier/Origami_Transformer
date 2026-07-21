# Pre-Registration v6 — Cross-domain transfer of the contestation signature (H-D)

> **STATUS: FROZEN 2026-07-21** (thresholds validated by the researcher
> 2026-07-21 — C1 lowered to 0.60 for LODO on his decision; no coussin). This is the within-domain /
> cross-domain study. It runs AFTER v5 (`PREREGISTRATION_v5.md`, freeze
> `ca588c3`, verdict `HC_CONFIRMÉ` 3/4) and exists to eliminate the LAST cheap
> explanation left standing after v5: **domain vocabulary**. v5 established the
> signature (C1), ruled out surface form (C2) and destroyed-structure artifacts
> (C3); its arms differed by domain BY CONSTRUCTION, so "the geometry reads the
> topic" remained open — flagged in `NOTE_RESULTATS_v5.md` (Limites) and
> `README_corpora.md` §8. v6 closes it or the claim dies there.

**Frozen on**: 2026-07-21
**Frozen by**: Simon Bouhier
**Git commit at freeze**: 10b6c89895403be0df2731a2953870f80a26c6a2

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

**Corpus as built (2026-07-21, pre-freeze — quarantined, never observed):**
`corpora/consensual_v6.txt`, 120 statements, built by
`build_consensual_v6.py` (deterministic, model-free). Line *i* of both arms
carries the **same fine domain** (34 fine domains, identical per-domain counts);
within each fine domain, pairing is by token-length rank. All statements within
9–16 gpt2 tokens. Length distributions: contested min/p25/med/p75/max =
7/11/12/13/17 (mean 12.07) vs consensual 9/11/12/13/16 (mean 11.93); **median
cross-tokenizer gap 0 on all four models**; only 2 pairs with |Δ| ≥ 4.

**LODO folds — the 7 frozen super-domains** (coarsening map in
`corpora/domain_map_v6.json`), per arm: `econ_policy` 27, `mind_language_society`
22, `physical_climate` 16, `ai_computing` 15, `medicine_health` 15,
`history_archaeology` 13, `life_sciences` 12. Seven folds; every fold ≥ 12 per
arm as required.

**SHA-256 at freeze** (re-checked at run time):
- `corpora/consensual_v6.txt`      : `711709204cfc64b5969c2b71706803c5d12a0201530672425ac67c634fbe7f04`
- `corpora/domain_map_v6.json`     : `5a8abe901f09bb8e18d8a5ba2cf8e87be68e49f1602185a43683510e74fc2b78`
- `corpora/matching_report_v6.json`: `d78cd60f7fc6cd81463b44720daaf4ce61ce91426fbcdc73ad50c36bbb0131cc`
- `corpora/contested.txt` (from v5, unchanged): `3eb7bae8506e97e274f407cf8f6d8357cdc06555d727e71f5aa8f9bb668850f2`

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
- **O2 (non-geometric baseline — everything cheap).** Same classifier and SAME
  LODO folds on the concatenation of **(a) bag-of-words TF-IDF** (word
  unigrams+bigrams, min_df = 2, sublinear_tf, fitted on the training folds
  only) **and (b) the v5 surface features** (n_tokens from the model's own
  tokenizer, mean unigram zipf frequency, punctuation count) → `BA_lex_lodo`.
  *Strengthened relative to the first draft (2026-07-21, pre-freeze): the
  baseline now unions lexical AND surface, so C2 asks the geometry to beat
  **everything cheap at once**, not lexical alone. Strengthening a baseline
  before the freeze is always admissible; weakening one never is.*
- **O3 (content-destruction under transfer).** O1 recomputed on token-shuffled
  inputs (both arms) under the same LODO folds → `BA_geo_shuf_lodo`.
- **B1 (instrument sanity — VOID gate, unchanged from v5).** Pooled-corpus
  max-layer |Spearman(O_rank, NLL)| ≥ 0.30, else the model's run is VOID.

## Falsification thresholds (validated by the researcher 2026-07-21; FROZEN, no coussin)

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
