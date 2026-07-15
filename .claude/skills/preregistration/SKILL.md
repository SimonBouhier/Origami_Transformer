---
name: preregistration
description: Use whenever the researcher is about to commit to a new hypothesis or measurement campaign. Produces a PREREGISTRATION_vN.md file with frozen thresholds, hypothesis statement, observables, and verdict logic — committed to git before any measurement script reads real data. Trigger on phrases like "let's pre-register", "freeze the criteria", "before running v4", or whenever the literature-first skill has returned green light and a new hypothesis is ready to be tested.
---

# Pre-Registration Discipline

## Why this exists

A pre-registered negative is a publishable result. A post-hoc loosened
threshold is fraud. The discipline turns the second into the impossible.

This project treats the line between them as sharp. The skill produces
the artifact that proves which side a result lives on.

## When to invoke

After `literature-first` has returned green and the researcher has stated
a hypothesis they want to test. Before any script that produces the
measurement reads real-model output.

## The template

Create a file at the project root named `PREREGISTRATION_v{N}.md` where N
is the next integer (v4 if v3 exists archived). Use exactly this
structure:

```markdown
# Pre-Registration v{N}

**Frozen on**: {YYYY-MM-DD}
**Frozen by**: {researcher name}
**Git commit at freeze**: {to be filled by `git rev-parse HEAD` after commit}

## Hypothesis

H{N}: One sentence, plain language. What is the world supposed to look
like if this is true? Avoid hedges. The hypothesis must be capable of
being denied by the data.

## Why this and not its negation

One paragraph stating the prior reason to believe H{N} over its negation.
Cite at least one entry from `STATE_OF_ART.md`. If the prior is purely
the researcher's intuition, say so — that is a legitimate prior but it
should be named as such.

## Observables

The exact numerical quantities to be computed, with their definitions.
No ambiguity. A second researcher reading this should produce the same
script.

- O1: ...
- O2: ...

## Falsification thresholds

The numbers that distinguish confirmation from denial. Frozen. No coussin.
No tolerance margin added later because "it was close".

- C1: {observable} {operator} {value}
- C2: ...

## Verdict logic

Per-model: H{N} is confirmed for a model iff C1 AND C2 AND ... .
Global: H{N} is confirmed iff confirmed on at least M models out of N
        AND fraction confirmed >= F.

Fill M, N, F here, frozen.

## Anti-confirmation clause

State explicitly what a denial would *mean*. A denial is publishable iff
it surprises the prior in §2. If the prior was weak, a denial is less
informative. Say so.

## Scope

Models to be tested: {list, with HuggingFace IDs}.
Corpus: {file path under corpora/, with sha256 to be computed at run time}.
Estimator(s): {primary and any secondary diagnostics}.
Seed: {single integer}.

## Out-of-scope

What this pre-registration deliberately does NOT cover. Future
hypotheses go in v{N+1}.
```

## Commit dance

1. Researcher writes the pre-registration. Session may help with phrasing
   but must not relax any threshold.
2. Researcher runs `git add PREREGISTRATION_v{N}.md && git commit -m "preregister v{N}"`.
3. The session then fills the `Git commit at freeze` line with the output
   of `git rev-parse HEAD`, and makes a second commit "stamp v{N} freeze".
4. Only after this is the v{N} measurement code allowed to run on real
   models.

## What is forbidden

- Editing the pre-registration after stamping. If the plan was wrong, write
  v{N+1} that supersedes v{N}. The old one stays in git history.
- Computing the observables before the stamp. Pilot runs on synthetic data
  or on a tiny throwaway model (gpt2) are allowed to debug code, but their
  output JSON is gitignored and not analyzed.
- Choosing thresholds after seeing any v{N} output.

The asymmetry is the point. A loose ex-ante threshold that survives the
test is fine. A tightened ex-post threshold is not.
