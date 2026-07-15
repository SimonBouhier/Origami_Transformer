# Origami of LLM Representations — Project Contract

This file is the contract between the researcher and any Claude Code session
working on this repo. It is loaded on every session start. Read it once, in full,
before doing anything else. Do not edit it without a commit that explains why.

---

## 1. What this project is

A research project on the **geometry of internal representations in transformer
language models** — how the variety of activations folds across layers, and
whether that folding has a functional signature.

The output is **measurements, pre-registered analyses, and publishable negatives**.
Not a product. Not a demo. Not an artifact for the user to admire.

This work is sister to the EPP project (epp-verdict-docs.vercel.app) and inherits
its epistemic discipline: divergence is signal, unanimity is failure mode, proofs
of process never become verdicts on truth.

---

## 2. The three commandments — broken at your peril

These are the lessons we paid for. Do not re-pay.

### 2.1 Literature before code

Before writing or modifying any measurement script, you **must** check whether
the question has already been answered. See `STATE_OF_ART.md` for current
coverage. If your work plausibly extends beyond what's catalogued there:
arxiv.org search, semantic scholar search, and a sanity check on connected
papers. Read at least the abstracts. Add new findings to `STATE_OF_ART.md`
with a one-paragraph digest.

A null search result is the only acceptable green light. "I don't think this
exists" is not a search result.

### 2.2 Pre-registration before measurement

No measurement script runs against real models without a corresponding
`PREREGISTRATION_vN.md` committed to the repo first, containing:
- the hypothesis (H1, H2, ...) in plain language
- the observable(s) — what numbers come out
- the falsification thresholds, frozen, no tolerance, no coussin
- the verdict logic (per-model and global)

See `.claude/skills/preregistration/SKILL.md`. The pre-registration is committed
to git **before** the analysis script reads any output JSON. The commit hash is
the proof.

A pre-registered negative is a publishable result. A post-hoc loosened threshold
is fraud. The line is sharp.

### 2.3 Fisher pivot — TwoNN and MLE are archived

We were burned by AISTATS 2026 (Schulte & Rügamer, arxiv 2604.20276), which
showed that nearest-neighbor intrinsic dimension estimators (TwoNN, MLE, and
relatives) do not track the true ID of neural representations. They measure
*something* — correlated with density, anisotropy, scale — but not the
geometric object we cared about.

Our `probe.py` from v3 is archived under `archived/probe_v3.py` as an
empirical confirmation of their critique (our C1 failures on Pythia and Bloom
are textbook symptoms). Do not bring TwoNN or MLE back as primary
instruments. If you need a nearest-neighbor estimator for sanity check, run
it as a **secondary** diagnostic, not as ground truth, and report the
disagreement.

The primary instrument for this project is the **Fisher information metric
restricted via logit-lens**:

  g(h) = W_uᵀ · (diag(p) − p pᵀ) · W_u

where h is the hidden state, W_u the unembedding matrix, p the softmax of the
logit-lens at that layer. This is density-free — it does not need a
neighborhood graph. It inherits its validity from the model's own output
distribution, not from sampling assumptions.

See `STATE_OF_ART.md` §4 (Mabrok 2603.22301) for the derivation and §1
(Schulte & Rügamer) for why this matters.

---

## 3. Project layout

```
.
├── CLAUDE.md                   ← this file
├── RESEARCH_LOG.md             ← living log of what was done and decided
├── STATE_OF_ART.md             ← digest of the literature
├── PREREGISTRATION_vN.md       ← one per pre-registered hypothesis
├── .claude/
│   └── skills/
│       ├── literature-first/   ← the search-before-code discipline
│       └── preregistration/    ← the pre-reg discipline
├── probe_fisher.py             ← (to write) Fisher-metric probe
├── curvature.py                ← extrinsic curvature, to be re-worked d-free
├── spectrum.py                 ← (to write) effective spectral rank, NN-free
├── analysis.py                 ← applies pre-registered verdicts
├── corpora/                    ← input statement lists, one per line
├── results/                    ← probe outputs, JSON, gitignored if large
└── archived/                   ← v3 dead code, kept for the record
```

---

## 4. State of play (snapshot — refresh from RESEARCH_LOG.md)

- v3 (probe.py with TwoNN+MLE) has been archived following AISTATS 2026.
- v4 is pending: pivot to Fisher metric + extrinsic curvature.
- Three candidate hypotheses are on the table: H-A (volume hourglass),
  H-B (curvature signature), H-C (geometry↔function coupling).
  The researcher has not yet chosen. **Do not pick for them.**

---

## 5. House style

- French is the working language with the researcher. Comments and docstrings
  can stay English; commit messages and prose either is fine.
- No emojis in code, JSON output, or commit messages.
- No "✅" / "🎯" / decorative unicode in attestations or reports — that was a
  v2 anti-pattern.
- Numbers in reports come from running code, never copy-pasted from memory.
- One canonical source of truth per fact. If two docs disagree, fix one.

---

## 6. What sessions are allowed to do without asking

- Run probe scripts on local models.
- Add to `RESEARCH_LOG.md` (append-only).
- Add new entries to `STATE_OF_ART.md` after reading a paper.
- Fix bugs in measurement code, with the test that demonstrates the fix.
- Suggest the next experiment.

## 7. What sessions must ask before doing

- Editing this `CLAUDE.md`.
- Modifying or deleting a committed `PREREGISTRATION_vN.md`.
- Choosing among H-A / H-B / H-C.
- Branching the project into a new research direction.
- Anything that touches the EPP repo.
