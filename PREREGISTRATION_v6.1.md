# Pre-Registration v6.1 — Controlled scale ladder within one model family (H-E)

> **STATUS: DRAFT — NOT FROZEN, NOT COMMITTED.**
>
> Threshold **C-E1 = +0.05 is validated** by the researcher (2026-07-22).
>
> The **framing of the corpus is NOT settled**: the researcher's first answer was
> a misclick and he has withdrawn it. Until he decides, this whole campaign is on
> hold — he has indicated he may prefer to redo v6 instead of running a scale
> ladder on a corpus known to be confounded. Nothing here may be measured, and
> nothing here records his agreement.
>
> Phases A and B — instrument calibration, no claim — are done and reported in
> `NOTE_v61_PHASES_A_B.md`. Neither new rung has been measured.

**Frozen on**: {pending}
**Frozen by**: {pending}
**Git commit at freeze**: {pending}

## Hypothesis

**H-E:** Within a **single model family** — same training data, same tokenizer,
same architecture, only parameter count varying — the cross-domain (LODO)
separability of contested from consensual statements in the Fisher geometry
**increases with model scale**.

## Why this and not its negation

Our most robust surviving finding across v4/v5/v6 is an ordering:
bloom-560m > opt-350m ≈ pythia-410m > gpt2, stable across three campaigns and
two corpora. We have been reading it as "the signature grows with model
capability".

**`STATE_OF_ART.md` §6 (Kulkarni et al., arXiv:2602.20433) says that reading is
presumptively invalid.** Geometry↔performance correlations read *across* models
are largely a confound of training hyperparameters, with counterexamples in both
directions. Our four models differ in data, tokenizer, architecture and training
recipe — every one of §6's confounds is live.

The Pythia suite is the standard instrument for removing exactly this confound.
If the capacity reading survives within one family, it is a real effect and §6
is answered. If it does not, our ordering was a §6 artifact and we will have
found that out ourselves.

§2 (Cheng et al.) and §3 (Joshi et al.) give a weak positive prior — richer
linguistic abstraction and decision-relevant compression appear with capability.
§6 gives a specific negative prior. **Honest net prior: genuinely uncertain,
which is the right condition for a pre-registration.**

## Pre-existing datum — declared

The anchor rung, **pythia-410m, is already measured**: BA_geo_lodo = 0.7458
(frozen v6 CPU value, reproduced exactly on GPU in phase A, Δ = 0.0000). It is
not an output of this campaign; it predates the campaign's conception.

**The two new rungs (1.4b, 2.8b) have never been measured.** All thresholds
below are fixed before those measurements exist. The anchor's known value is
used only to express C-E1 as a gain relative to it — which is what a ladder
requires.

## Observables

Extraction and Fisher metric: the **frozen instrument**, qualified on GPU in
phase A (`probe_fisher_gpu.py`; transcription verified against the original by
`--selfcheck`, strict equality). CUDA, **float32 weights and forward pass**,
TF32 explicitly disabled, seed 0, k = 50. Corpus: v6 frozen, unchanged.

- **O1 (primary).** Per rung, `BA_geo_lodo` — logistic regression (L2, C = 1.0)
  on the per-layer [O_vol, O_rank, O_aniso] vector, evaluated leave-one-domain-out
  over the 7 frozen super-domains, pooled out-of-fold. Conventions identical to
  `analysis_v6.py`.
- **O2 (cheap baseline — HARDENED before freeze).** Same classifier, same folds,
  on **TF-IDF (1-2 grams, min_df = 2, sublinear_tf, fitted on training folds
  only) ∪ v5 surface features ∪ the 8 construction-marker counts** of
  `diag_v7.py`. *This is strictly harder than v6's frozen O2, which the post-v6
  diagnostic showed to be too weak (construction markers alone reach 0.762,
  above the frozen O2's 0.738–0.754). Strengthening a baseline before a freeze is
  always admissible; weakening one never is.*
- **O3 (structure control — DIAGNOSTIC, not verdict-bearing).** O1 recomputed on
  token-shuffled inputs, same folds. No criterion depends on it; it is measured
  because a new rung whose shuffle control does *not* collapse toward chance is
  a broken rung, and we want that visible before interpreting anything. Reported
  descriptively alongside the verdict.
- **B1 (VOID gate, unchanged).** Pooled-corpus max-layer
  |Spearman(O_rank, NLL)| ≥ 0.30, else that rung is VOID.

## Falsification thresholds (PROPOSED — frozen on validation, no coussin)

- **C-E1 (growth across the ladder):**
  `BA_geo_lodo(pythia-2.8b) − BA_geo_lodo(pythia-410m) >= +0.05`
- **C-E2 (no reversal):** no rung falls more than **0.02** below the rung beneath
  it, i.e. `BA(1.4b) >= BA(410m) − 0.02` and `BA(2.8b) >= BA(1.4b) − 0.02`.
- **C-E3 (strong form — beats everything cheap, reported separately):**
  `BA_geo_lodo(2.8b) − BA_cheap_lodo(2.8b) >= +0.08`

The +0.08 of C-E3 is v6's C2 margin, reused unchanged. Using a laxer margin here
than in the campaign that produced a denial would be exactly the drift this
discipline forbids.

**Declared weakness of C-E1.** The bootstrap of `diag_v7.py` puts the (optimistic)
half-width of a single BA at ≈ ±0.055 at n = 240. +0.05 therefore sits near the
noise floor. It is proposed anyway because a 7× parameter increase should
produce more than a noise-sized gain if the capacity story is real, and because
a higher bar would risk a denial that is merely underpowered. A **paired
bootstrap of the 410m→2.8b difference will be reported descriptively, outside
the verdict.**

## Verdict logic

This is a **ladder**, not a set of independent models; the verdict is on the
ladder as a whole. Deviation from the usual per-model/global template is
deliberate and stated here rather than improvised later.

- **H-E confirmed iff C-E1 AND C-E2**, with all three rungs non-VOID.
- **C-E3 is reported separately** as the strong form. H-E may be confirmed while
  C-E3 fails; that outcome means "scale helps, but not enough to beat cheap".
- **If either new rung is VOID (B1 < 0.30), the ladder verdict is VOID** and no
  claim is made. A VOID rung is not silently dropped.

## Anti-confirmation clause

A denial means: **within a controlled family, scale does not increase the
geometric separability of contested from consensual statements.** It would imply
that our cross-architecture ordering (bloom > opt ≈ pythia > gpt2) was largely a
§6 artifact — a confound of training recipes rather than a capacity effect — and
it would remove the last comfortable reading left standing after v6's denial.

This denial is **informative**, because §6 predicts it specifically and because
the capacity reading is currently load-bearing in three of our documents. It is
publishable as a negative.

A confirmation is correspondingly strong: it would answer §6 on §6's own terms,
using the instrument the field uses for that purpose.

## Known limitation of the corpus — OPEN QUESTION, not settled

The v6 corpus is **confounded by syntactic construction**: 8 regex counters
reach BA = 0.762 in LODO, above the frozen O2 baseline and above the geometry on
3 of 4 models (`NOTE_DIAGNOSTIC_v7.md`). Running the ladder on that corpus is a
choice the researcher has **not** made — see the status banner.

The argument *for* running it anyway would be that **H-E asks a different
question**: not "is the signal
geometrically specific?" — v6 already answered no — but "does scale increase
separability, within a controlled family?" The cheap bar (O2 hardened, including
the construction markers) is **fixed and identical across all three rungs**,
because the Pythia suite shares one tokenizer: the comparison is therefore fair
within the ladder.

**What H-E can never establish on this corpus:** that the geometry reads
epistemic status rather than construction. Whatever the ladder returns, that
claim stays where v6 left it. This limitation is to be restated in the results
note, not quietly dropped.

## Scope

- **Models:** `EleutherAI/pythia-410m` (anchor, already measured),
  `EleutherAI/pythia-1.4b`, `EleutherAI/pythia-2.8b`. All float32.
- **Why the ladder stops at 2.8b:** `pythia-6.9b` in float32 needs 27.6 GB and
  does not fit in 24 GB. bf16 was tested in phase B-3 and **disqualified** as
  non-equivalent (ΔBA = 0.0083, O_rank moving up to 19 %). A 6.9b rung would
  require a separate, homogeneous bf16 ladder and is out of scope here.
- **Corpus:** `corpora/contested.txt` (sha256 `3eb7bae8…`) and
  `corpora/consensual_v6.txt` (sha256 `71170920…`), folds from
  `corpora/domain_map_v6.json` — all re-verified at run time.
- **Runtime integrity check, pre-registered:** the Pythia suite shares one
  tokenizer, so `n_tokens_per_statement` **must be identical across the three
  rungs**. If it is not, the ladder is not controlled and the campaign stops
  without a verdict.
- **Seed:** 0. **k:** 50. **Estimators:** as above; no new estimator.

## Out-of-scope

- Any change to the Fisher instrument, to the corpus, or to v5/v6 definitions.
- The construction-matched corpus (that is v7, and it awaits Q3 — provenance).
- The bf16 ladder to 6.9b.
- Any re-judgement of H-D. **The v6 verdict `HD_DÉMENTI` is frozen and is not
  touched by this campaign, whatever H-E returns.**
