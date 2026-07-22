# Pre-Registration v6.2 — Contestation signature under CONSTRUCTION control (H-D2)

> **STATUS: DRAFT — NOT FROZEN, NOT COMMITTED.** Two new numbers await the
> researcher's validation: the corpus quality gate **G1** and the rebuild-round
> cap. All verdict thresholds are **identical to v6** and are not re-opened.
> No model has seen `consensual_v6_2.txt`; it does not yet exist.

**Frozen on**: {pending}
**Frozen by**: {pending — Simon Bouhier}
**Git commit at freeze**: {pending}

## Hypothesis

**H-D2:** The per-layer Fisher-metric signature of epistemic contestation
separates contested from consensual statements **in unseen domains**, when the
two arms are matched **both on domain and on syntactic construction**, and it
does so **better than every cheap linguistic description of the same text**.

This is H-D with the last identified confound removed. v6 denied H-D because a
cheap baseline matched the geometry; the post-verdict diagnostic
(`NOTE_DIAGNOSTIC_v7.md`) showed **why**: 8 regex construction counters reach
BA = 0.762 in LODO, above the frozen O2 baseline and above the geometry on 3 of
4 models. The contested arm compares magnitudes; the consensual arm describes
mechanisms. v6.2 removes that asymmetry and re-asks the question.

## Why this and not its negation

The prior comes from our own data, not from the literature. On the frozen
corpus, restricting **both** arms to non-comparative statements (n = 193)
collapses the cheap baseline from 0.73 to 0.62 while the geometry **does not
move** (bloom 0.842 → 0.841, opt 0.751 → 0.772). If removing the comparative
cue destroyed the phenomenon, the geometry would have fallen with the baseline.
It did not.

That probe is **exploratory and not probative** — stratified 5-fold CV, not
LODO, so domain is uncontrolled; post-hoc subsetting on already-measured data;
an imbalanced subset. It is a reason to run v6.2, not a reason to expect a
particular answer.

Against: `STATE_OF_ART.md` §7 (Baroni, Cheng et al.) reports that intrinsic
dimension tracks *syntactic* complexity strongly and semantic contrasts weakly.
Removing syntactic variance is precisely removing what that literature says the
geometry is best at reading. **A denial is a live possibility and would be
informative.**

Honest net prior: **moderate.** Better than v6's (which was low-to-moderate and
was denied), but not comfortable.

## Multiplicity — declared

This is the **fourth** pre-registered campaign on variants of the same question:
v4 (`HA_DÉMENTI`), v5 (`HC_CONFIRMÉ` 3/4), v6 (`HD_DÉMENTI` 0/4), now v6.2.
Every one is pre-registered, committed before measurement, and published
including the negatives — nothing is hidden, and that is what keeps the record
honest.

But the multiplicity is real and must not be laundered. These are **not four
independent tests of one hypothesis**; they are tests of progressively
better-controlled versions of it, each corpus differing from the last.
**A confirmation at v6.2 must be read with this history in view, and the results
note must restate it.** A confirmation here is evidence that the signature
survives three successive controls — not evidence at the nominal strength of a
single pre-registered test.

## Corpus

- **Contested arm: UNCHANGED AND FROZEN** — `corpora/contested.txt`, sha256
  `3eb7bae8506e97e274f407cf8f6d8357cdc06555d727e71f5aa8f9bb668850f2`. Its Fisher
  measurements are **re-run** (GPU is qualified, phase A, Δ = 0.0000) but its
  text is not touched.
- **Consensual arm: NEW** — `corpora/consensual_v6_2.txt`, 120 statements, built
  by a deterministic model-free builder from `consensual_v6.txt`.
  **Line *i* must match contested line *i* on BOTH:**
  1. the **fine domain** (34 domains, as in v6), and
  2. the **construction class** — comparative vs non-comparative, per the 8-marker
     definition frozen in `diag_v7.py`.
- Measured job, from the frozen text: **36 lines need a consensual comparative**
  (medicine 5, ai 4, political_science 3, economics 3, education 3, history 3,
  physics 2, archaeology 2, and 11 domains with 1 each); **5 lines must be made
  non-comparative**; **79 lines are already correct and are kept verbatim**.
- All v5/v6 hard constraints carry over unchanged: English declaratives, no
  hedges, 9–16 gpt2 tokens, no duplicates, length-matched within domain,
  register matched, and **broad established agreement** — a consensual
  comparative is a comparison no informed party disputes
  (*"Light travels faster through a vacuum than through glass"*), never a
  softened contested claim.
- The arm is built and **quarantined pre-freeze, never observed by any model**;
  its sha256 is recorded here at the freeze.

## Corpus quality gate — model-free, applied BEFORE the freeze

These are checks on **text only**. No model is involved, so running them cannot
leak anything about the geometry.

- **G0 (structural, hard):** per-line construction class identical between arms
  for **120/120 lines**. Not statistical — it either holds or the build is wrong.
- **G1 (statistical):** the classifier on the **8 construction markers alone**,
  under the same 7 LODO folds, must fall to **BA ≤ 0.65** (from 0.762 in v6).
- **Rebuild cap: at most 3 rounds.** Every round's G1 value is logged in
  `corpora/matching_report_v6_2.json`. Iterating a *model-free* corpus check
  against a criterion fixed in advance is corpus engineering, not result-fitting
  — but it is bounded and auditable so that it cannot become the latter.
- **If G1 cannot be met in 3 rounds, the campaign STOPS without a verdict** and
  the failure is written up. That outcome would mean construction cannot be
  decoupled from contestation in practice — the pessimistic branch of Q1 — and
  it is a real finding, not a setback to be engineered away.

## Observables

Frozen instrument, GPU-qualified (`probe_fisher_gpu.py`, transcription verified
by `--selfcheck`): CUDA, float32, TF32 disabled, seed 0, k = 50.

- **O1 (primary):** `BA_geo_lodo` — L2 logistic regression (C = 1.0) on the
  per-layer [O_vol, O_rank, O_aniso] vector, leave-one-domain-out over the 7
  frozen super-domains, pooled out-of-fold. Conventions identical to
  `analysis_v6.py`.
- **O2 (cheap baseline — HARDENED):** same classifier, same folds, on
  **TF-IDF (1–2 grams, min_df = 2, sublinear_tf, fitted on training folds only)
  ∪ v5 surface features ∪ the 8 construction-marker counts**. *Strictly harder
  than v6's O2, which the diagnostic showed to be too weak. Strengthening a
  baseline before a freeze is always admissible; weakening one never is.*
- **O3 (structure control):** O1 on token-shuffled inputs, same folds.
- **B1 (VOID gate):** pooled-corpus max-layer |Spearman(O_rank, NLL)| ≥ 0.30.

## Falsification thresholds — IDENTICAL TO v6, no coussin

- **C1:** `BA_geo_lodo >= 0.60`
- **C2:** `BA_geo_lodo − BA_cheap_lodo >= +0.08`
- **C3:** `BA_geo_lodo − BA_geo_shuf_lodo >= +0.08`

Not re-opened, not re-negotiated. v6.2 changes the **corpus**, not the bar.
Loosening a threshold while improving a corpus would make any confirmation
uninterpretable.

## Verdict logic

Per model: H-D2 confirmed iff C1 AND C2 AND C3; **VOID** if B1 < 0.30.
Global: confirmed iff **≥ 3 of 4** models confirmed AND fraction **≥ 0.66**.
(Identical to v6.)

## Anti-confirmation clause

A denial means the signature does not survive control of syntactic construction:
what v5 and v6 measured was carried by domain and by sentence form, and the
geometry adds nothing a cheap description of the text does not already have.
Given §7 (ID tracks syntax strongly, semantics weakly), **this is a live
outcome**, and it would effectively close the "epistemic status" reading on this
corpus family — a clean, publishable end to a line of inquiry.

A confirmation would mean the signature survives, in order: surface form (v5 C2),
destroyed structure (v5/v6 C3), domain identity (v6 C1), and now construction.
That is a serious result — read, as §Multiplicity requires, as the outcome of
three successive controls rather than of one test.

## Scope

- **Models:** the same four — `gpt2`, `EleutherAI/pythia-410m`,
  `facebook/opt-350m`, `bigscience/bloom-560m`. OPT retained as instrument
  stress-test (expected VOID; B1 = 0.197 / 0.133 / 0.143 across v4/v5/v6).
- **Compute:** GPU, ~10 min for the full campaign (4 models × 2 arms ×
  {fisher, shuffle}), versus ~2 h 15 on CPU.
- **New measurements required:** both arms × {fisher, shuffle} × 4 models. The v6
  contested measurements are **not** reused, because the GPU port is a new
  support and phase A qualified it for fresh measurement, not for mixing.
- **Seed:** 0. **k:** 50.

## Out-of-scope

- The Pythia scale ladder (`PREREGISTRATION_v6.1.md`, drafted, C-E1 = +0.05
  validated, on hold). It runs **after** v6.2, on whichever corpus survives.
- Q3 — external provenance and graded contestedness. The consensual arm here is
  still **agent-written**, which remains the standing limitation of this corpus
  family and must be restated in the results note. v6.2 fixes construction, not
  authorship.
- Any re-judgement of v4, v5 or v6. Those verdicts are frozen and stay as they
  are, whatever v6.2 returns.
