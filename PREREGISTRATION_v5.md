# Pre-Registration v5 — Contested vs consensual (H-C)

> **STATUS: DRAFT — thresholds VALIDATED by the researcher (2026-05-31), to be FROZEN at
> the v5 freeze.** This is the contested-vs-consensual study (H-C). It runs AFTER the v4
> Fisher baseline (`PREREGISTRATION_v4.md`), on the instrument validated there. The
> consensual arm's marginal Fisher profile is known from v4; the v5 hypothesis concerns the
> contested-vs-consensual CONTRAST, whose contested arm is not built or observed until this
> v5 freeze — so v4 does not contaminate v5. No measurement script reads real-model output
> for v5 until this file is frozen and committed (commit dance).

**Frozen on**: TBD (set at the v5 freeze, after v4 completes)
**Frozen by**: Simon Bouhier
**Git commit at freeze**: TBD

## Hypothesis

H-C: Within a fixed language model, the per-layer Fisher-information-metric geometry of the
hidden state carries a signature of epistemic contestation — a contested statement and a
consensual one are separable from that geometry alone, that separability is not reducible to
surface form, and it collapses when linguistic structure is destroyed.

Definitions (the axis, frozen):
- **Contested** = a well-formed, truth-apt declarative claim on which currently informed
  parties disagree (ethics, politics, unsettled science, value judgments).
- **Consensual** = a well-formed, truth-apt claim under broad established agreement (settled
  science, mathematics, uncontroversial fact).
- Contestedness is the axis. NOT truth-vs-falsehood, NOT referential ambiguity, NOT model
  uncertainty. A contested claim may be true; a consensual one may be false.

The generic coupling "a per-layer geometric quantity tracks per-layer logit-lens NLL" is NOT a
contribution (published — `STATE_OF_ART.md` §5, and validated as the v4 baseline). It appears
here only as B1, an instrument sanity check.

## Why this and not its negation

The central high-dimensionality / abstraction phase is functional (`STATE_OF_ART.md` §2, §3),
and epistemic contestation is a semantic property that plausibly engages that abstraction
differently from settled content. The Fisher metric reads geometry through the model's own
output distribution (§4); if contested content yields locally higher-rank / more anisotropic
output-distinguishability, it should appear in g(h). The conjunction "Fisher/metric geometry ×
contested-vs-consensual" is unpublished (§9). Honest counter-prior: ID/geometry tracks syntax
strongly but semantics weakly (§7), so the effect may be small or absent. The prior is MODERATE
and mixed — part researcher intuition (recurrent geometric perception during contested exchanges,
named as intuition), part the §2/§3 functional result. A denial surprises the intuition but is
only weakly informative against the field.

## Observables

**Extraction and Fisher metric: identical to v4** (`PREREGISTRATION_v4.md` §Observables) —
last-token h(s,l); raw logit-lens `W_u h + b_u` (no final LayerNorm); g(h) =
`W_u^T (diag(p) - p p^T) W_u`; per-(statement, layer) scalars O_vol (k=50), O_rank, O_aniso,
z-scored per layer across the pooled corpus.

- **O1 (primary — separability).** Per model, a logistic-regression classifier
  contested-vs-consensual on the per-layer feature vector [O_vol(l), O_rank(l), O_aniso(l)] for
  l = 0..L, stratified 5-fold CV (frozen; L2, C = 1.0). Report balanced accuracy `BA_geo` and
  ROC-AUC `AUC_geo`.
- **O2 (surface baseline).** Same classifier on surface features only [n_tokens, mean unigram
  log-frequency (wordfreq, en), punctuation count] -> `BA_surf`, `AUC_surf`.
- **O3 (content-destruction control).** O1 recomputed on token-SHUFFLED inputs
  (`control_probe.py` shuffle): `BA_geo_shuf`.
- **B1 (instrument sanity — NOT a confirmation condition).** Per layer, Spearman rho between
  O_rank(s,l) and per-statement logit-lens NLL. (Validated in v4.)

## Falsification thresholds

VALIDATED by the researcher 2026-05-31; FROZEN at the v5 freeze. No coussin.

- **C1** (separation above chance): `BA_geo >= 0.65`
- **C2** (not a surface artifact): `AUC_geo - AUC_surf >= 0.10`
- **C3** (content-dependent): `BA_geo - BA_geo_shuf >= 0.08`

B1 is reported but is not a confirmation condition; if B1 fails (the instrument does not even
reproduce the known geometry-NLL coupling validated in v4), the run is VOID, not a denial.

## Verdict logic

Per-model: H-C confirmed iff **C1 AND C2 AND C3**.
Global: H-C confirmed iff confirmed on at least **M = 3** of **N = 4** models (fraction
>= **F = 0.66**).
A global denial is a pre-registered, publishable negative.

## Anti-confirmation clause

A denial means: the per-layer Fisher geometry does not separate contested from consensual beyond
chance (C1), or any separation is explained by surface form (C2), or it survives destruction of
linguistic structure and is therefore not about content (C3). Given the MODERATE, partly-intuition
prior and Baroni's weak-semantic-signal caution (§7), a denial surprises the researcher's geometric
intuition but is only weakly informative against the field — state this plainly in any writeup. A
confirmation is strong precisely because C2 and C3 rule out the two cheap explanations (surface
features; structure-without-content).

## Scope

Models: the same four families as the v4 baseline (`gpt2`, `EleutherAI/pythia-410m`,
`facebook/opt-350m`, `bigscience/bloom-560m`). CPU, float32. Seed = 0. k = 50.
Corpus: `corpora/consensual.txt` and `corpora/contested.txt`, one statement per line, curated by
the researcher per the definitions above. Construction protocol (frozen at v5 freeze): each arm
n >= 100; arms matched as far as feasible on token-length distribution, domain spread, and surface
register; `claims.txt` seeds the consensual arm. sha256 of each committed corpus file recorded at
the v5 freeze and re-checked at run time. The statement lists are frozen by their commit before
measurement; this document fixes the selection protocol. The contested arm is not observed before
the v5 freeze.
Estimator: Fisher metric via the logit lens (primary); secondary diagnostic `spectrum.py`. NN-ID
estimators not used (§2.3).

## Out-of-scope

- Curvature as a primary observable (was H-B; deferred — `STATE_OF_ART.md` §4 follow-up).
- Cross-model coupling / scaling laws (confounded — §6).
- Any EPP attestation (`epp_adapter.py` stays a stub until a confirmed result).
- Causal / interventional claims: v5 is observational geometry only.
- LayerNorm-variant of the logit lens (raw `W_u h` is frozen for v5; an LN-corrected metric is a
  v6 question).
- Larger / instruction-tuned models (a possible v6 extension).
