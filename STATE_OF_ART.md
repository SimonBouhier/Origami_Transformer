# State of the Art — Geometry of LLM Representations

Last updated: 2026-05-31. Add to the bottom when new papers enter the picture.
Do not edit prior entries — append a follow-up entry instead.

---

## §1 — Schulte & Rügamer (AISTATS 2026, arxiv:2604.20276)

**"Rethinking Intrinsic Dimension Estimation in Neural Representations"**, 22 Apr 2026.

> "common ID estimators are, in fact, not tracking the true underlying ID of
> the representation."

Theoretical and empirical demonstration that TwoNN, MLE, and related
nearest-neighbor ID estimators fail to recover the true intrinsic dimension
of neural representations. They identify the latent factors (density,
anisotropy, scale) that actually drive the published "ID profiles" we all
trusted. They propose a new estimation approach (read the paper for the
constructive part — it should be the next deep-read once one of H-A/B/C is
chosen).

**Direct consequence for this project**: probe.py v3 is archived. NN-based
ID estimators do not return as primary instruments. The pivot to
Fisher-metric-based observables is the rigorous response.

---

## §2 — Cheng et al. (May 2024, arxiv:2405.15471)

**"A central high-dimensionality phase underlies core linguistic processing"**.

Across 5 LMs and 3 datasets, a distinct **high-dimensionality phase** appears
in the middle layers. In that phase, representations: (1) correspond to the
first full linguistic abstraction; (2) are the first to transfer downstream;
(3) predict each other across LMs. An earlier onset of the phase predicts
better language modelling.

**Consequence**: the "hunchback" profile is not just a shape — its peak has a
functional meaning. Whatever we measure with Fisher should be checked
against this phase.

---

## §3 — Joshi, Bhatt, Modi (NeurIPS 2025, arxiv:2511.20315)

**"Geometry of Decision Making in Language Models"**, 25 Nov 2025.

28 open-weight transformers, multiple ID estimators, plus per-layer MCQA
performance. Result: consistent low → expansion → compression ID pattern
across all 28 models, with the compressed late layers being decision-relevant.

**Consequence**: H1 (the hunchback) was confirmed at scale six months before
our pre-registration. Re-confirming it on 6 models is not a contribution.
The novel direction lies elsewhere — geometry↔function coupling beyond
MCQA, on contested vs consensual epistemic content (the EPP bridge), with
instruments that survive §1's critique.

Note: this paper still uses NN-based estimators. Its conclusions about the
*shape* may survive §1's critique by averaging effects, but the *numerical
values* of ID it reports should be read with §1 in mind.

---

## §4 — Mabrok (Mar 2026, arxiv:2603.22301)

**"Latent Semantic Manifolds in LLMs"**, 17 Mar 2026.

Full Riemannian framework: representation space as a semantic manifold with
**Fisher information metric**, tokens as Voronoi regions, generation as
projection. Validated on 6 architectures (124M to 1.5B). Reports the ID
profile as an established prior fact and analyzes curvature. The Fisher
metric is computed via the logit-lens:

  g(h) = W_uᵀ · (diag(p) − p pᵀ) · W_u

This is the instrument the project pivots to. **Method §5 (restricted
Fisher metric) and recipe §13 are the relevant sections.**

**Consequence**: the geometry-via-Fisher pipeline is empirically validated
and density-free. Curvature analysis is partly done in §4 — read it
carefully before designing H-B, to avoid re-deriving what's there and to
find what's *not* there.

---

## §5 — Viswanathan et al. (Jan 2025, arxiv:2501.10573)

**"The Geometry of Tokens in Internal Representations of LLMs"**. (Abstract-level; not yet deep-read.)

Per-prompt, per-layer intrinsic dimension of the token point cloud correlates with that
prompt's next-token cross-entropy loss (higher loss <-> higher-dimensional cloud), strongest
near the ID peak; shuffle-token control; Llama-3-8B, Mistral-7B, Pythia-6.9B. NB: this is the
paper Mabrok (§4) miscites as "Ferrara et al. [14]" — there is no "Ferrara" author; do not
chase a separate reference.

**Consequence**: the GENERIC "geometry predicts per-layer next-token loss" coupling — the
non-EPP form of H-C — is already published. Re-demonstrating geometry<->loss is not a
contribution. Per the researcher's 2026-05-31 decision, the generic coupling is DEMOTED to a
baseline sanity-check; H-C's contribution lives on the contested<->consensual axis (§9).

---

## §6 — Kulkarni et al. (Feb 2026, arxiv:2602.20433)

**"Disentangling Geometry, Performance, and Training in Language Models"**. (Abstract-level.)

The geometry<->performance correlation is largely a confound of training hyperparameters
(batch size, weight decay), not causal; counterexamples in both directions.

**Consequence**: any raw geometry<->function correlation read ACROSS models is presumptively
spurious. v4 must compare WITHIN a fixed model (contested vs consensual at constant weights),
which neutralises this confound — an argument for the EPP design over the generic cross-model
coupling. To be frozen into PREREGISTRATION_v4.

---

## §7 — Baroni, Cheng et al. (2026, arxiv:2601.03779)

**ID complexity profiles of linguistic phenomena**. (Abstract-level.)

Intrinsic dimension tracks SYNTACTIC complexity strongly but functional/semantic contrasts much
more weakly.

**Consequence**: a contested<->consensual contrast is semantic/epistemic, so its geometric signal
may be weak or null. Honest prior: the v4 pre-registered effect size should be modest, and a
pre-registered null is a real, publishable outcome — not a failure.

---

## §8 — Wang & Zhao (May 2026, arxiv:2605.17231)

**"FishBack: Pullback Fisher Geometry for Optimal Activation Steering in Transformers"**.
(Abstract-level; deep-read §3 before pre-registration.)

Builds the softmax-output Fisher metric on transformer activations via Jacobian pullback from the
output (G = J^T H J), reporting effective rank (2–17% of ambient) and anisotropy (condition number
~1e7) as diagnostics, in service of an activation-steering intervention.

**Consequence**: CONCURRENT near-neighbour of our instrument — same underlying object
(output-distribution Fisher on activations) and two shared observables. Differs on two axes:
(a) Jacobian pullback from the final layer, NOT the per-layer logit-lens form
g(h) = W_u^T (diag(p) − p p^T) W_u evaluated at each layer; (b) telos = steering (engineering),
not measuring how volume/curvature fold across layers. Must cite and differentiate; we may claim
the per-layer logit-lens MEASUREMENT use, not "Fisher-on-activations" as such.

---

## §9 — Contested<->consensual × metric geometry: the gap H-C occupies (search pass, 2026-05-31)

Three-front lit pass, ~16 phrasings. The "truth/honesty direction" cluster — Marks & Tegmark
2310.06824, Azaria & Mitchell 2304.13734, Burns et al. (CCS) 2212.03827, Zou et al. (RepE)
2310.01405 — is ADJACENT on BOTH axes: true-vs-false (not contestedness) and linear probes (not
metric geometry). Closest single adjacents:
- Wang et al. 2510.08389 — effective rank of hidden states for hallucination detection: our exact
  observable, but on the truth/correctness axis, not contestedness.
- Rair et al. 2510.17548 — Mapper topology of annotator disagreement: only disagreement×geometry
  work, but on static input embeddings, topological not metric, annotation-noise not contestation.
- Yin et al. 2402.18048 — local-ID for truthfulness: uses the NN-ID family §2.3 archived; staying
  on Fisher/effective-rank is both the novelty lever and the methodological high ground.

**Consequence**: the CONJUNCTION "Fisher/metric geometry × contested-vs-consensual, per layer" is
unpublished — GREEN. Make-or-break design point: the operational definition of "contested" as
distinct from ambiguous / uncertain / false (a well-formed, truth-apt claim on which informed
parties currently disagree). This seam must be pinned in PREREGISTRATION_v4.

---

## §1 / §4 follow-ups (from the 2026-05-31 deep read of the foundational PDFs)

- §1 (Schulte & Rügamer): the constructive half — estimated ID patterns are better read as von
  Neumann entropy / effective rank ("how variance is distributed across linear directions and how
  that changes over layers"), and a recevable estimator must be NON-INCREASING across Lipschitz
  layers. This elevates effective rank (spectrum.py) from secondary diagnostic to a primary-grade,
  critique-proof observable.
- §4 (Mabrok): his ID "hourglass" is measured with TwoNN/MLE — under §1's critique, like Joshi
  (§3). We adopt Mabrok's Fisher METRIC, never his ID numbers as if exempt. His curvature (§13.3,
  local-PCA + ||II||) is uniformly tiny, stable/decaying, weakly tied to entropy (Spearman ~0.12) —
  the empirical reason H-B (a mid-layer curvature peak) was not chosen.

---

## How to add an entry

When a new relevant paper appears, append a §N section with:

1. Full citation and arxiv link.
2. One-sentence summary.
3. The exact quote that matters (under 15 words).
4. The block "**Consequence**:" — what this changes for our project,
   concretely.

If a new paper invalidates an earlier entry, do not delete the earlier
section — add a follow-up §N+1 that explains the supersession.

---

## §10 — Cross-domain transfer of epistemic probes: the gap H-D occupies (search pass, 2026-07-21)

Two-front pass (phenomenon: probe generalization across topics/domains for
epistemic axes; instrument: metric geometry under domain transfer). Landscape:

- **Universal Truthfulness Hyperplane** (2407.08582) and **Testing the Limits of
  Truth Directions** (2604.03754): the truth-axis cluster now tests cross-topic
  generalization explicitly, with **leave-one-topic-out** as the standard
  protocol; truth directions generalize partially (five "truth types", failures
  on sycophantic/expectation-inverted cases).
- Hallucination-probe OOD results: ~**25-point average drops** when probes
  trained on one dataset transfer to others — transfer is the hard test, not an
  afterthought.
- **Robust for the Wrong Reasons** (2607.01951, Jul 2026): representational
  geometry of robustness to *user-expressed science skepticism* — linear probes
  + activation patching, 3 domains, transfer "attenuates across domains and can
  reverse". ADJACENT but distinct on both axes: input-stance (not claim
  contestedness) and linear probes (not Fisher metric).
- "Deep Minds and Shallow Probes" (2605.11448) and the correctness-probe
  confound literature (2607.16799): high probe accuracy may reflect surface or
  benchmark-template correlates — the general form of our lexical-shortcut worry.

**Consequence**: (1) the conjunction "Fisher/metric geometry x contested-vs-
consensual x CROSS-DOMAIN TRANSFER" is unpublished — GREEN for v6 (H-D).
(2) Adopt **leave-one-domain-out** as the frozen evaluation protocol: it is the
field's standard instrument for exactly this question — we import it, not
invent it. (3) Honest prior: LOW-to-moderate. The nearest literatures show
partial-to-poor transfer; a pre-registered denial (signature does not transfer
= it was largely domain content) is the LIKELY outcome and is publishable.
A confirmation under LODO would be correspondingly strong.
