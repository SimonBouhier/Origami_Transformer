---
name: literature-first
description: Use before writing or significantly modifying any measurement, estimator, or analysis script in this research project. Forces a literature check to avoid re-implementing or rediscovering published work, and to catch methodological critiques that may have already invalidated the planned approach. Trigger whenever the session is about to begin coding a new probe, a new metric, a new estimator, or a new visualization — and whenever the researcher proposes a "novel" angle that has not yet been searched.
---

# Literature-First Discipline

## Why this exists

The v3 campaign of this project was a fully rigorous pre-registered study
that arrived six months late and used an instrument that had been
discredited six weeks earlier by an AISTATS paper. The rigor was real. The
literature gap was the failure. This skill exists to make sure that gap
does not reopen.

## When to invoke

Invoke before:
- Writing a new measurement script (probe, estimator, metric).
- Adopting a new geometric or statistical observable.
- Pre-registering a new hypothesis.
- Telling the researcher "this angle looks novel."

Do **not** invoke for: bug fixes, refactors, plotting changes, prose edits,
or running an already-written script.

## The check

1. **Read `STATE_OF_ART.md` in full** before searching the web. The four
   foundational papers and any subsequent additions are catalogued there.
   Many "novel" ideas will fail the check at this step.

2. **Search arxiv** with two queries minimum:
   - The exact phenomenon (e.g. "intrinsic dimension transformer layers")
   - The proposed instrument (e.g. "Fisher information metric language model")

3. **Search Google Scholar / Semantic Scholar** for the most cited recent
   work on the topic. The goal is not exhaustive review — it is to
   surface anything that would change the plan.

4. **Read at least the abstracts** of the top 5 results from each query.
   For any paper that looks directly relevant, fetch and read the methods
   section.

5. **Update `STATE_OF_ART.md`** with new entries for any paper that
   changes the project's stance. Use the entry format documented at the
   bottom of that file.

## Outputs

The skill is complete when one of these is true:

- **Green light**: the search returned nothing that supersedes or
  invalidates the plan. Write a one-paragraph summary of what was
  searched and what was found in the researcher's chat, and proceed.

- **Yellow light**: a paper extends or complicates the plan but does not
  kill it. Update `STATE_OF_ART.md`, summarize the impact, and ask the
  researcher whether to adjust the plan.

- **Red light**: a paper preempts the plan or invalidates the instrument.
  Update `STATE_OF_ART.md`, archive the planned work as a known dead end,
  and propose alternatives that survive the new finding.

A null search result is the only green light. "I don't think this exists"
is not a search result.

## Honesty clause

A red light is not a failure of the session — it is the skill working. A
publishable negative or a saved month of work is the success state.
