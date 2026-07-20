# Corpus specification — v5 (contested vs consensual)

**Status: PRE-FREEZE. Nothing here is committed as frozen yet.** This document is the
self-contained brief for anyone (human or agent) writing or correcting this corpus. Read it
in full before editing a single line.

> **UPDATE 2026-07-19 — corpus PURIFIED to (A) expert-contested only (researcher's decision).**
> All pure value-judgment / "ought" lines were rewritten as empirical expert-contested claims;
> the §4 (A)/(B)/(C) scope decision is now settled to **(A)** and reflected in
> `PREREGISTRATION_v5.md`. Rematch re-run (delta max = 1, 119/120 exact, median gap 0.0 on all
> four tokenizers). `contested_anchors.tsv` rebuilt and aligned 1..120 with named constituencies.
> **The mix note in §4 and the specific line numbers in §10 below refer to the OLD mixed draft**
> (archived at `../archived/contested_v5draft1_mixed_normative.txt` and
> `../archived/contested_anchors_v5draft1_normative.tsv`) — read them as history, not as the
> current file.
> **Still open (researcher's call before freeze):** 5 lines the anchor rebuild could not anchor
> as genuine (A) — flagged `REVIEW` in `contested_anchors.tsv`: lines **60, 83, 89, 91, 98**
> (weak-evidence or expert-settled/(C)/near-False). Replacement candidates proposed to the
> researcher; not applied unilaterally (scope is reserved, `CLAUDE.md` §7 / this file §9).

---

## 1. What this corpus is for

It is the input to a **pre-registered** study (`PREREGISTRATION_v5.md`, hypothesis H-C) asking
whether the **per-layer Fisher-information-metric geometry** of a language model's hidden
states separates **contested** from **consensual** statements — within a fixed model, on
frozen thresholds, across four models (`gpt2`, `EleutherAI/pythia-410m`,
`facebook/opt-350m`, `bigscience/bloom-560m`).

You are building the ground truth of a falsifiable experiment. A sloppy line does not make the
result "a bit worse" — it makes a pre-registered null uninterpretable. **A pre-registered
negative is a publishable result; a corpus that quietly smuggles in a confound is not.**

## 2. Files, and the hard dependency

| File | Role | Editable? |
|---|---|---|
| `contested.txt` | 120 contested statements, one per line | **Yes — this is the work** |
| `consensual.txt` | 120 statements from `claims.txt`, length-matched | **NO — derived, regenerate it** |
| `contested_anchors.tsv` | `line / domain / affirmed_by / denied_by` — the audit trail | **Yes — keep in lockstep** |
| `matching_report.json` | matching method + stats | **NO — derived** |
| `../build_consensual_subset.py` | the matcher | Only with reason |
| `../claims.txt` | **REQUIRED INPUT** — 220 factual statements, 11 domains × 20 | **NO — v3/v4 corpus, frozen by history** |

**`claims.txt` (repo root) is mandatory.** The script asserts exactly 220 lines. It also needs
`numpy`, `transformers`, and network access (it downloads four tokenizers). Handing over
`corpora/` alone is not enough.

`consensual.txt` and `matching_report.json` are **outputs**. Editing them by hand silently
breaks the length matching that condition C2 depends on. If you touch `contested.txt`, rerun:

```
python build_consensual_subset.py     # from the repo root
```

## 3. The operational definition (this is the whole game)

- **Contested** = a well-formed, **truth-apt** declarative claim on which **currently informed
  parties disagree**.
- **Consensual** = a well-formed, truth-apt claim under **broad established agreement**.

Contestedness is the axis. It is **not** truth-vs-falsehood, **not** ambiguity, **not** model
uncertainty. A contested claim may be true; a consensual one may be false.

### The three exclusions — each is a distinct failure mode

| Exclusion | Why it fails | Example to reject |
|---|---|---|
| **False** (settled against) | informed parties agree — that it's wrong | "Vaccines cause autism." |
| **Ambiguous** | under-specified referent; nothing would settle it | "Digital privacy has been irreversibly lost." |
| **Uncertain / predictive** | nobody knows yet; that is not disagreement | "AGI will arrive before 2050." |

The line to hold: an **ambiguous** item has an under-specified referent. An **uncertain** item
has a well-specified referent and no evidence yet. A **contested** item has a well-specified
referent, evidence on the table, and informed people who read that evidence differently.

## 4. "Contested" is at least three things — and one of them is a defect

This is the most important finding of the review pass, and the easiest trap to fall into:

- **(A) Expert-contested** — specialists are genuinely split. Metaphysics, historiography, dark
  matter vs modified gravity, string theory's status, quantum interpretations, saturated fat,
  the replication crisis. **The gold standard.**
- **(B) Normatively contested** — no fact of the matter; values divide. Bioethics, political
  philosophy, criminal justice. **Legitimate.** Note carefully: "most bioethicists think X"
  does **not** settle a normative question — moral disagreement among informed parties *is* the
  phenomenon. Do not reject a (B) line just because a majority holds one side.
- **(C) Publicly contested but expert-settled** — the political/public debate rages while the
  specialists agree. **This FAILS the definition** and must be rejected: informed parties do
  *not* disagree. Rent control's supply effects (~93% of the IGM panel agree), the phonics
  "reading wars" (settled in cognitive science; the dissent is practitioner, not scientific).

**Why (C) is not a cosmetic flaw:** from the model's point of view, the expert sources in its
training data *agree* on (C) items. They therefore look **consensual** to the model, dilute the
contrast, and bias the study toward a null. (C) items also risk turning the classifier into a
detector of "publicly controversial topic vocabulary" rather than of epistemic contestation.

**(A) vs (B) is a live design decision, not a defect** — it belongs to the researcher and must
be settled in `PREREGISTRATION_v5.md` before the freeze. Normative and empirical contestation
have no reason to share a geometric signature; mixing them may average two different signals
toward nothing. Current mix: roughly 30 lines (A), ~60 (B), ~12 (C), rest borderline.

## 5. Hard constraints on every line

1. **English**, single **declarative** sentence, ends with a period.
2. **No hedges** (`might`, `maybe`, `perhaps`, `possibly`, `arguably`, `seems`) — hedging
   signals *uncertainty*, which is an excluded category. Assert the claim.
3. **No questions**, no lists, no semicolons-as-clauses. Match the register of `claims.txt`.
4. **Length: 9–16 gpt2 tokens, target median 12** (~10 words).
5. **No duplicates**, no near-duplicate propositions.

### Length budget — respect the pool or the matching degrades

`consensual.txt` is drawn from `claims.txt` by **exact** length matching (currently 120/120 at
delta 0). Replacing a line **at the same token length is free**. Changing the length
distribution spends from a finite pool:

| gpt2 tokens | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| available in `claims.txt` | 1 | 7 | 15 | 36 | 46 | 43 | 37 | 13 | 13 | 6 | 2 | 1 |
| **spare (unused)** | 1 | 4 | **2** | **5** | 13 | 15 | 28 | 12 | 11 | 6 | 2 | 1 |

**Prefer 12–16 tokens** for new lines (ample slack). **Avoid adding lines at 10–11 tokens** —
only 2 and 5 spare. A `DOMAIN_CAP = 12` per `claims.txt` domain also applies (11 domains × 12 =
132 capacity for 120 needed); shifting the distribution can make it bind.

Verify after every edit — the matcher prints `delta max` and per-model gaps. **`delta max` must
stay 0**, and the median gap must stay 0.0 for all four tokenizers.

## 6. The anchor rule (`contested_anchors.tsv`)

Every contested line needs **nameable informed constituencies on both sides**.

> **If you cannot name who affirms it and who denies it, the line does not belong in the corpus.**

Name real schools, traditions, professional bodies, or researchers ("Card-line immigration
economists", "Catholic bioethics", "MOND researchers (Milgrom, McGaugh)") — never "some people"
or "critics". The TSV is tab-separated, one row per contested line, `line` strictly 1..120 and
aligned with `contested.txt`. **It is never shown to any model** — it exists to make the
operational definition auditable.

Self-check for free: if one side's description reads like a *consensus* ("most X", "mainstream
X", "near-consensus") **and the other does not**, you probably have a **(C)** item or a
minority-side assertion. Investigate — do not auto-delete. This screen over-flags on (B)
normative lines, where a majority view is compatible with genuine contestation.

## 7. Balance

The corpus must not argue a thesis. Across the whole file, statements asserting positions
associated with the political left and right should be **roughly balanced** (currently ~14 vs
~12, the remainder orthogonal: science, AI, metaphysics, method). Asserting the **minority** side
of a genuinely expert-contested question is **fine** (Borjas is informed and dissents).
Asserting what informed parties have settled **against** is not — that is the *False* exclusion.

## 8. What matching does and does not cover

**Matched:** n per arm (120), token-length distribution (exact on gpt2; median gap 0.0 on all
four tokenizers), surface register, `claims.txt` domain spread of the consensual arm (9–12
across all 11 domains).

**Not matched, and unmatchable by construction:** the **domains**. The contested arm is
ethics/politics/open science; the consensual arm is settled fact. That is the axis under test,
not a matching defect. The resulting **vocabulary confound is real and expected** — it is
precisely what the pre-registered guards are for:

- **O2 (surface baseline)** — a classifier on `[n_tokens, mean unigram log-frequency,
  punctuation count]`. Geometry must beat it by a frozen margin (C2). This is why length
  matching is not cosmetic.
- **O3 (shuffle control)** — the same geometry on token-shuffled inputs. If the separation is
  merely bag-of-words, it survives shuffling and C3 fails, correctly.

## 9. What you must not do

- **Do not touch the thresholds** in `PREREGISTRATION_v5.md` (BA_geo ≥ 0.65; AUC_geo − AUC_surf
  ≥ 0.10; BA_geo − BA_geo_shuf ≥ 0.08; ≥ 3 of 4 models). They are the researcher's, already
  validated, and may never be loosened.
- **Do not run any measurement** on this corpus. The corpus and the pre-registration are
  committed **before** any script reads real-model output. That commit hash is the proof.
- **Do not hand-edit** `consensual.txt` or `matching_report.json`.
- **Do not choose (A)/(B)/(C) scope** yourself — that is a hypothesis-shaping decision reserved
  to the researcher (`CLAUDE.md` §7).

## 10. Known open defects (as of 2026-07-16, not yet fixed)

Flagged by review; **the researcher has not yet ruled on them**. Do not silently fix — propose.

- **Category (C), fail the bar:** `31` rent control (the anchor itself says "near-consensus"),
  `95` phonics, and weakly `37` central-bank independence, `41` cryptocurrencies, `42` growth
  and poverty.
- **Assert what informed parties settled against (→ False):** `101` single-sex education
  (Halpern-line meta-analyses find ~no effect; the anchor admits "most … researchers" deny),
  `107` longer sentences deter (certainty-over-severity dominates criminology).
- **Predictive → Uncertain, not contested:** `64` AGI timing, `65` self-driving cars, weakly
  `60` automation.
- **Not crisply truth-apt → Ambiguous:** `67` digital privacy irreversibly lost; borderline
  `54` rarity of intelligent life.

Roughly 10–12 lines of 120. Replacements must keep the same gpt2 token length where possible
(free), carry a full anchor row, and preserve balance.

---

*Corpus written 2026-07-16 for `PREREGISTRATION_v5.md` (H-C). Instrument and frozen v4 baseline:
`probe_fisher.py`, `PREREGISTRATION_v4.md` (freeze `4e9683ef`). Project contract: `CLAUDE.md`.
Literature: `STATE_OF_ART.md` §5–§9.*
