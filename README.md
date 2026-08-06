<p align="center">
  <img src="assets/banner.svg" alt="Origami Transformer — pre-registered geometry of LLM representations" width="100%">
</p>

<p align="center">
  <img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-0ea5e9">
  <img alt="Pre-registered" src="https://img.shields.io/badge/protocol-pre--registered-2dd4bf">
  <img alt="v7 verdict" src="https://img.shields.io/badge/v7%20H--F-DENIED%200%2F6-red">
  <img alt="Reproducible" src="https://img.shields.io/badge/CPU%2FGPU%20float32-reproducible-64748b">
</p>

<p align="center"><em>How do transformer representations fold across layers — and what does that folding know?</em></p>

---

A research program on the **geometry of internal representations in transformer
language models**, run under a strict pre-registration discipline: **frozen
thresholds committed to git before any measurement**, honest negatives treated
as publishable results, and no retroactive exclusions — ever.

## Headline result — v7 (July 2026)

> **The measured Fisher geometry does not retain an epistemic margin once the
> linguistic baseline is made progressively harder.** Geometry and cheap
> features decline together; the current Fisher bridge is therefore not a
> defensible epistemic signal for downstream systems.

**Global verdict: `HF_DENIED` — 0/6 models**, under thresholds frozen before
measurement (commit [`aa120bd`](../../commit/aa120bd63b462fc1f40ab5e0812db5355999c641),
stamped by [`d89a45f`](../../commit/d89a45f)). The 48/48 GPU measurements match
their frozen corpus hashes.

| frozen/secondary observation | result |
|---|---|
| H-F frozen criterion | **0/6** models confirm |
| geometry ↔ cheap-feature correlation | **+0.51 to +0.95** across models |
| online MDL comparison | cheap features compress better on **198/198** measurements |
| controlled Pythia scale ladder | increased capacity does not rescue the margin |
| null corpus | every geometric BA stays below its own permutation floor |

This closes an apparent success rather than erasing it. v5 found raw
separability on its frozen corpus (`HC_CONFIRMED`, 3/4); v6 showed that the
signal did not transfer beyond stronger linguistic controls; v7 showed that
the geometric margin does not persist along a model-free difficulty sweep.

The conclusion has three deliberately separate levels:

1. **Operational — established.** Under the frozen protocol, geometry does not
   outlive the cheap baseline.
2. **Engineering — established.** Do not import Fisher geometry as an epistemic
   signal into [lyra_reborn](https://github.com/SimonBouhier/lyra_reborn) or EPP
   Verdict. The bridge is frozen, and that freeze is not technical debt.
3. **Ontological — not licensed.** v7 does not prove that epistemic geometry is
   impossible. The B1 rank↔NLL sanity relation fails on most of this material,
   so the experiment rejects the current bridge, not every possible object.

Full numbers, caveats and sensitivity analysis:
[`NOTE_RESULTATS_v7.md`](NOTE_RESULTATS_v7.md). Historical v5 result:
[`NOTE_RESULTATS_v5.md`](NOTE_RESULTATS_v5.md).

## The discipline

1. **Literature first** — no probe is written before checking whether the
   question is already answered ([`STATE_OF_ART.md`](STATE_OF_ART.md)).
2. **Pre-registration before measurement** — hypothesis, observables, frozen
   falsification thresholds and verdict logic are committed *before* any script
   reads model output. The freeze commit hash is then stamped into the document:
   **the hash proves the thresholds preceded the data.**
3. **Negatives are results** — every denial, failed sanity gate and design flaw
   is documented with the same care as a confirmation. No post-hoc exclusion
   changes a frozen verdict.
4. **Claims stay scoped** — operational evidence, engineering decisions and
   ontological claims are reported separately.

| campaign | instrument | hypothesis | verdict |
|---|---|---|---|
| v3 | NN intrinsic-dimension estimators (TwoNN/MLE) | layer-wise "bump" | `DENIED` — estimator failure mode found, estimators archived |
| v4 | **Fisher metric via logit-lens** (density-free) | bump, re-tested | `DENIED` 1/4 — but *final compression universal 4/4*, instrument validated |
| v5 | Fisher metric (frozen v4 protocol) | **H-C: geometry of contestation** | **`CONFIRMED` 3/4** |
| v6 | Fisher + leave-one-domain-out + strong linguistic baseline | **H-D: cross-domain specificity** | **`DENIED` 0/4** (2 VOID) |
| v7 | difficulty × controlled model capacity + null + MDL | **H-F: persistence of the geometric margin** | **`DENIED` 0/6** |

The one robust motif across *all* instruments and campaigns: **final-layer
compression, 4/4 models, twice**. It is a geometric observation, not an
epistemic classifier.

## Reproduce

```bash
# corpus integrity is re-checked against the frozen sha256 at run time
./run_campaign_v7.sh       # 6 models x 4 arms x 2 modes = 48 GPU measurements
python analysis_sweep_v7.py --null
python analysis_sweep_v7.py
python verdict_v7.py       # applies only the frozen v7 decision rule
```

CUDA float32, TF32 disabled, seed 0 (frozen). The recorded campaign took 86
minutes on an RTX 4090. Raw outputs live under `results_v7/`, are regenerable,
and are intentionally not versioned.

## Repo map

| File | Role |
|---|---|
| `PREREGISTRATION_v7.md` | frozen H-F contract, thresholds, gates and corpus hashes |
| `NOTE_RESULTATS_v7.md` | canonical results, caveats and three-level conclusion |
| `run_campaign_v7.sh` | frozen 48-measurement GPU campaign |
| `analysis_sweep_v7.py` | 33-rung paired bootstrap, permutation and MDL analysis |
| `verdict_v7.py` | frozen-threshold verdict only |
| `corpora/v7_sweep/` | domain- and subject-matched corpus, null arms and difficulty rungs |
| `RESEARCH_LOG.md` | the dated journal, including the failures |
| `CLAUDE.md` | the project contract any agent session must obey |
| `BOOTSTRAP.md` | the original kit this repo grew from |

## Status and open questions

The v4–v7 branch is closed. There is no corrective v8 whose purpose is to save
the current Fisher bridge. Two questions remain legitimate as independent,
newly pre-registered studies:

1. **External provenance (Q3)** — both arms drawn from documented real-world
   expert agreement/disagreement rather than researcher-written statements.
2. **Instrument validity** — repair or replace B1 before asking Fisher geometry
   to support any broader claim on subject-matched material.

Sister projects: [lyra_reborn](https://github.com/SimonBouhier/lyra_reborn)
(cognitive OS) · EPP Verdict (epistemic attestation —
[docs](https://epp-verdict-docs.vercel.app)).

## License

Code and corpus: **MIT** (© 2026 Simon Bouhier). Third-party papers are linked,
never redistributed.
