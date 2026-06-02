# Pre-Registration v4 — Fisher baseline (V3 repasse)

> **Thresholds FROZEN 2026-05-31** (researcher: Simon Bouhier). No coussin, no post-hoc
> tolerance. The `Git commit at freeze` hash is stamped in a second commit immediately after
> the freeze commit; no measurement script (`probe_fisher.py`) reads real-model output before
> that stamp.

**Frozen on**: 2026-05-31
**Frozen by**: Simon Bouhier
**Git commit at freeze**: TBD (filled by `git rev-parse HEAD` after the freeze commit)

## Hypothesis

H-A (under the Fisher instrument): On the factual corpus, the per-layer profile of the
Fisher-metric effective rank rises to a strictly interior peak and then compresses (final layer
below the peak), AND the per-layer Fisher geometry couples to the model's logit-lens next-token
loss. In plain words: the v3 "hunchback" reproduces under a density-free instrument — the shape
is a real property of the representations, not an artifact of nearest-neighbour ID estimators.

This is a baseline / instrument-validation study: it establishes that `probe_fisher.py` behaves
and that the known phenomena (hourglass shape; geometry-loss coupling) survive the pivot to
Fisher, on the same corpus and models as v3. The contested-vs-consensual contrast is NOT in
scope here — that is v5, built on the instrument validated here.

## Why this and not its negation

Schulte & Rügamer (`STATE_OF_ART.md` §1) prove NN-ID estimators cannot track true ID and that
reported layer-wise "ID patterns" reflect variance-distribution / effective-rank effects. If so,
the v3 hunchback should REPRODUCE when measured directly as a density-free effective rank of the
Fisher metric — and Mabrok (§4) reports an hourglass under the Fisher framework on overlapping
models. The prior for H-A is therefore STRONG (two independent literature anchors) — which is
exactly why this is a baseline, not a novelty claim. A denial would mean the shape v3 saw was an
NN-estimator artifact that does not survive a density-free instrument: surprising against §1/§4,
and itself a strong methodological result that would force a rethink before v5.

## Observables

**Extraction (shared with v5).** For each statement s and layer l (l = 0..L), h(s,l) =
last-token hidden state. Logit-lens at layer l: logits = `W_u h(s,l) + b_u` using the model's
own unembedding (raw, NO final LayerNorm — matches Mabrok Prop. 5.2 so the closed form holds
exactly). p = softmax(logits).

**Fisher metric (per point).** g(h) = `W_u^T (diag(p) - p p^T) W_u`, a d x d PSD matrix;
eigenvalues λ_1 >= ... >= λ_d >= 0.

**Per-(statement, layer) scalars.**
- O_rank = `exp(- sum_i q_i log q_i)`, q_i = λ_i / sum_j λ_j — Fisher effective rank.
- O_vol  = `0.5 * sum_{i=1..k} log λ_i` — log top-k Fisher volume (k = 50).
- O_aniso = `λ_1 / sum_j λ_j`.

**Profiles (the baseline observables).**
- P_rank(l) = mean over the corpus of O_rank(s,l), l = 0..L (also report P_vol, P_aniso).
- peak = argmax_l P_rank(l).
- B1(l) = Spearman rho between O_rank(s,l) and per-statement logit-lens NLL(s,l), per layer.

## Falsification thresholds

FROZEN 2026-05-31. No coussin.

- **C1** (interior peak): `peak in [1, L-2]` (strictly interior).
- **C2** (final compression): `P_rank(L) < P_rank(peak)` (strict).
- **C3** (coupling reproduced): `max_l |B1(l)| >= 0.30`.

## Verdict logic

Per-model: H-A confirmed for a model iff **C1 AND C2 AND C3**.
Global: H-A confirmed iff confirmed on at least **M = 3** of **N = 4** models (fraction
>= **F = 0.66**).

A global denial (the hunchback or the coupling does NOT survive the density-free instrument) is a
pre-registered, publishable methodological result, and would force a rethink before v5.

## Scope

Models: `gpt2` (124M), `EleutherAI/pythia-410m`, `facebook/opt-350m`, `bigscience/bloom-560m`.
CPU, float32. Seed = 0. All layers including embeddings (l = 0). k = 50 for O_vol.
Corpus: `claims.txt` (repo root; the v3 factual corpus, 220 statements). Its sha256 is recorded at
freeze and re-checked at run time.
Estimator: Fisher metric via the logit lens (primary). Secondary diagnostic permitted: linear
effective rank (`spectrum.py`). NN-ID estimators (TwoNN/MLE) are NOT used (CLAUDE.md §2.3).
Instrument script: `probe_fisher.py`, written AFTER this freeze is stamped.

## Out-of-scope

- The contested-vs-consensual contrast (that is v5).
- Curvature as an observable (deferred — `STATE_OF_ART.md` §4 follow-up).
- LayerNorm-corrected logit lens (raw `W_u h` is frozen; the LN-variant is a later question).
- Any EPP attestation (`epp_adapter.py` stays a stub).
- Cross-model / scaling comparisons (confounded — §6).
