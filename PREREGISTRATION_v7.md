# Pre-Registration v7 — Persistence of the geometric margin under increasing corpus difficulty (H-F)

> **STATUS: DRAFT — NOT FROZEN, NOT COMMITTED AS FROZEN.**
> The corpus family and the null corpus are already built and are **model-free**
> (`build_sweep_v7.py`); no geometry has been computed on them. What awaits the
> researcher's validation is §5 (the shape criterion) and §6 (scope).

**Frozen on**: {pending}
**Frozen by**: {pending — Simon Bouhier}
**Git commit at freeze**: {pending}

---

## 1. Hypothesis

**H-F:** As the corpus is made progressively harder for a cheap linguistic
description — until that description falls to chance — the **geometric margin
persists**. That is: `BA_geo − BA_cheap` stays strictly positive across the
difficulty range, rather than collapsing together with the cheap baseline.

This is deliberately **not** the question of the four previous campaigns. They
asked "does the geometry beat cheap **at this corpus**?" — a single point, whose
answer depends on where that point sits. H-F asks about a **shape**: what the
geometry does while the corpus slides from easy to impossible for cheap methods.

## 2. Why the shape and not a threshold — the methodological point

The researcher's requirement (2026-07-22): *not to lock ourselves into results
desired in advance.*

The failure mode is real and we have already lived it. In v6.3 a gate was set,
a corpus was built until it passed, and the gate became a tautology
(`AUDIT_CORPUS_v6_3.md` §2). The desire does not enter through dishonesty; it
enters through **the choice of the point**. A single threshold can always land,
innocently, where the geometry happens to win.

A curve cannot be chosen that way. To fake H-F one would have to arrange the
geometry to win at *every* difficulty level of an axis built without ever
looking at the geometry. There is no knob for that.

Two outcomes, both informative:

- **the margin collapses with the cheap baseline** → the two were reading the
  same confound all along. Denial, and it depends on no threshold;
- **the margin holds or widens as cheap falls to chance** → something survives
  that no cheap description captures. That, and only that, would make the
  epistemic-geometry reading defensible.

## 3. Materials — all built model-free and frozen before any measurement

**Corpus v6.4** (`corpora/v7_sweep/{contested,consensual}.txt`) — 120 pairs
matched on **domain and subject**: the consensual member states the established
proximal fact underneath the contested distal claim (same entities, same
vocabulary, same construction class). Built from 4 independent model proposals
plus editorial selection; audit in `AUDIT_CORPUS_v6_3.md`, provenance in
`corpora/v6_4_proposals/`.

**The difficulty family (M1)** — `corpora/v7_sweep/rungs.json`, **33 rungs**,
built by `build_sweep_v7.py`. At each rung the 2 pairs the **cheap classifier**
separates most confidently (out-of-fold margin) are removed, then the classifier
is refit. Floor: no LODO fold below 8 pairs. Descent achieved:
**120 → 56 pairs, BA_cheap 0.6875 → 0.4643**.

> **The removal is blind to the geometry by construction.** It reads only
> TF-IDF ∪ surface ∪ the 8 construction markers. No Fisher output is opened by
> that script. This is what makes the axis honest.

**The null corpus (M3-B)** — `corpora/v7_sweep/null_{A,B}.txt`. The 120
**consensual** statements of v6.4 split into two arms of 50, balanced within
fine domain, seed 0. Both arms come from the same pool: there is, by
construction, no epistemic status to find. What the pipeline reports there is
the real floor — **GPU measurement included**, so it catches instrument and
pipeline artifacts that a permutation cannot.

**The label-permutation null (M3-A)** — computed at every 4th rung: pair labels
are flipped at random (both members swap together, preserving the paired
design), 200 draws. This gives the chance floor **at exactly the same n, the
same features and the same folds** as the rung it calibrates.

## 4. Observables

Frozen instrument, GPU-qualified in v6.1 phase A (Δ = 0.0000 on 4 models);
`probe_fisher_gpu.py`, CUDA, float32, TF32 explicitly disabled, seed 0, k = 50.
Shuffle control cross-checked against the frozen CPU probe.

- **O1** `BA_geo_lodo` — L2 logistic regression on the per-layer
  [O_vol, O_rank, O_aniso] vector, leave-one-domain-out, pooled out-of-fold.
- **O2** `BA_cheap_lodo` — same classifier, same folds, on
  **TF-IDF ∪ v5 surface ∪ the 8 construction markers**. This is the hardened
  baseline of the post-v6 diagnostic, not v6's weaker one.
- **O3** `BA_geo_shuf_lodo` — O1 on token-shuffled inputs. Diagnostic; no
  criterion depends on it, but a rung whose shuffle control does not collapse is
  a broken rung and must be visible.
- **O4 — MDL (new, per Q2).** Online (prequential) code length of the labels
  given the features, blocks = super-domains in random order, 20 orders
  averaged (`mdl.py`, after Voita & Titov 2020). Reported as **compression**
  for geometry and for cheap, and as their gap.
  *Why it is here:* comparing an accuracy on 39 geometric features to an
  accuracy on ~10 000 TF-IDF features is not dimension-fair, and a reviewer will
  say so. Code length charges for model capacity, so it answers the objection
  in advance. **It is a secondary observable: no verdict depends on it in this
  pre-registration**, because we have no prior experience of its scale on this
  material. It is measured now so that v8 can use it as a primary.
- **B1** — pooled max-layer |Spearman(O_rank, NLL)| ≥ 0.30, per rung.

Uncertainty: **paired bootstrap resampling PAIRS, not statements** (2000 draws),
at every rung, for BA_geo, BA_cheap and the margin. Known and restated limit:
these intervals are computed at fixed fitted models, so they are optimistic —
read as an order of magnitude, never as a test.

## 5. Falsification criterion — a shape, calibrated on the null

*(The numbers δ and F await the researcher's validation; the FORM is fixed here.)*

Let `floor(n)` be the chance ceiling from the label-permutation null at the
rung's own n — the **95th percentile** of permuted `BA_geo`. Let the margin
`M(r) = BA_geo(r) − BA_cheap(r)` with its 95% bootstrap interval.

A rung **supports** H-F iff, at that rung:

1. `BA_geo > floor(n)` — the geometry is above its own chance ceiling at that
   sample size, **and**
2. the lower bound of the bootstrap interval on `M(r)` is `> δ`.

**H-F is confirmed for a model iff the supporting rungs are at least a fraction
`F` of all rungs, AND include the hardest rung reached** (the one with the
lowest `BA_cheap`). The last clause is what makes the criterion a shape rather
than an average: a margin that exists only where the corpus is easy is exactly
the confound we are trying to eliminate.

Proposed: **δ = 0.00** (the interval must simply exclude zero) and **F = 2/3**.

> **Why δ is not chosen by hand.** Setting δ from intuition would reintroduce
> the very arbitrariness this design removes. δ = 0 defers all the strictness to
> the bootstrap interval and to condition (1), whose scale comes from the
> permutation null — that is, from a corpus **where we know there is nothing**.
> If the researcher prefers a stricter δ, the honest way to pick it is
> `δ = floor(n) − 0.50` at the median rung, i.e. the estimator's own noise
> amplitude, computed on signal-free data. Either choice must be made **now**.

Global across models: reported per model; no cross-model aggregation, because
`STATE_OF_ART.md` §6 rules that out. The Pythia ladder (§6) handles capacity.

## 6. Scope — difficulty × capacity in one campaign

**Capacity ladder (Pythia, controlled family)**: `pythia-410m` (d=1024),
`pythia-1.4b` (d=2048), `pythia-2.8b` (d=2560). Same training data, same
tokenizer, same architecture — this is what answers §6 (Kulkarni et al.), which
holds that cross-architecture geometry↔performance readings are presumptively
confounded by training recipe.

**Historical continuity**: `gpt2`, `facebook/opt-350m`, `bigscience/bloom-560m`,
so the v4/v5/v6 ordering remains readable.

**The ladder stops at 2.8b**: `pythia-6.9b` in float32 needs 27.6 GB and does
not fit in 24 GB; bf16 was tested and **disqualified** in v6.1 phase B-3
(ΔBA = 0.0083, O_rank moving up to 19%). A 6.9b rung would require a separate
homogeneous bf16 ladder and is out of scope.

**Capacity reading (secondary, pre-registered as such):** if H-F holds, does the
supporting-rung fraction increase with scale across 410m → 1.4b → 2.8b? Stated
now so it cannot be discovered later and reported as if planned.

**Cost**: 6 models × 4 arms × 2 (fisher, shuffle). The 33 rungs cost **no GPU at
all** — a statement's Fisher observables do not depend on the other statements,
so each model is measured once and the rungs are CPU subsets.

## 7. Multiplicity — declared, and it is now serious

This is the **fifth** pre-registered campaign on variants of one question:
v4 `HA_DÉMENTI`, v5 `HC_CONFIRMÉ` 3/4, v6 `HD_DÉMENTI` 0/4, v6.1 (calibration,
no claim), now v7. Every one is pre-registered, committed before measurement,
and published including the negatives.

But five campaigns is five chances. What limits the damage here is that each
campaign changed the **corpus and the control**, not the threshold — and that
v7 in particular tests a *shape across 33 rungs*, which is far harder to hit by
chance than a single point. **A confirmation must be reported as the outcome of
four successive controls (surface, structure, domain, construction+subject),
not at the nominal strength of one test.** The results note must restate this.

## 8. Anti-confirmation clause

A denial means: the geometric advantage is not separable from what cheap
linguistic description already captures — it lives and dies with it. Given
`STATE_OF_ART.md` §7 (intrinsic dimension tracks syntax strongly, semantics
weakly) and given that v6 already denied the point version of this question,
**a denial is the more likely outcome**. It would close the "epistemic status"
reading on this corpus family cleanly and publishably, and it would be the
strongest form of that closure we have produced.

## 9. Out of scope

- Any change to the Fisher instrument, or to the frozen v4/v5/v6 verdicts.
- The bf16 ladder to 6.9b.
- Q3 — external provenance and graded contestedness. The consensual arm remains
  **agent-written**; that is the standing limitation of this corpus family and
  must be restated in the results note. v7 controls subject and construction,
  not authorship.
- Using MDL as a verdict criterion (see §4 — it is measured, not decisive).
