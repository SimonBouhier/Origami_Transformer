# Bootstrap — How to start

This directory is a kit to drop at the root of a fresh git repo. It contains
the contract, the state of the literature, the research log, and two skills.
It contains **no measurement code yet** — that is intentional. The v4 code
gets written inside the first Claude Code session, *after* a pre-registration
is committed.

## Step 1 — Create the repo

```bash
mkdir origami-llm && cd origami-llm
git init
```

Copy the contents of this bootstrap directory in:

```
CLAUDE.md
RESEARCH_LOG.md
STATE_OF_ART.md
.claude/skills/literature-first/SKILL.md
.claude/skills/preregistration/SKILL.md
archived/                  (empty for now, will receive probe_v3.py)
results/                   (empty, gitignored)
corpora/                   (empty for now)
```

Add a `.gitignore`:

```
results/
__pycache__/
*.pyc
.venv/
```

First commit:

```bash
git add CLAUDE.md RESEARCH_LOG.md STATE_OF_ART.md .claude/ .gitignore
git commit -m "bootstrap: contract, log, lit, skills"
```

## Step 2 — Archive the v3 code

Copy the v3 files (probe.py, analysis.py, curvature.py, epp_adapter.py, the
old README) into `archived/v3/` with their old names. The `archived/` directory
is referenced in `CLAUDE.md` as the v3 graveyard. Don't delete them — they are
the evidence trail.

```bash
mkdir archived/v3
# (copy your v3 files in here)
git add archived/
git commit -m "archive v3 NN-based probe (preempted by AISTATS 2026)"
```

## Step 3 — First Claude Code session

Install Claude Code if needed (npm package `@anthropic-ai/claude-code`,
requires Node.js). At the project root, run `claude`.

First message to send:

> Read CLAUDE.md, STATE_OF_ART.md, and RESEARCH_LOG.md in full before
> answering. Then summarize back to me, in five lines or fewer, what this
> project is, what the three commandments are, and what the open decision is.
> Do not propose code.

If the summary is correct, the session has loaded the contract. If it isn't,
fix whichever file failed to communicate before moving on.

## Step 4 — Choose H-A, H-B, or H-C

This is the only thing the kit does not decide for you. The three candidates
are described at the bottom of `RESEARCH_LOG.md`. The right one is the one
*you* want to spend three months on, knowing that a denial is also a win.

Once chosen, invoke the `preregistration` skill in the Claude Code session
to write `PREREGISTRATION_v4.md`. Commit it. Then and only then, ask the
session to write the measurement code.

## What this kit deliberately does not include

- **A v4 measurement script.** Writing one before pre-registration is the
  exact mistake we just paid for.
- **An EPP adapter.** EPP consumes a validated instrument. Until v4 is
  pre-registered and produces a confirmed result, the EPP bridge stays a
  thought, not a module.
- **A visualization script.** Coloring projections of activations is
  tempting but it is the wrong place to start. After the Fisher metric is
  measured, *then* a `visualize.py` colors per-point Fisher volume on a
  UMAP — and never the other way round.
- **An MCP server config.** For local HuggingFace work, vanilla Claude Code
  with file and bash access is sufficient. Add MCP only if a specific need
  appears (e.g. arxiv access via an MCP if you want it scripted, or a
  paper-management MCP). Don't add complexity prophylactically.

## A note on tooling

Claude Code is the right tool for this project (terminal-native, runs
scripts, reads files, version-controlled context). Claude Cowork is for
non-developer file/task orchestration and is a poor fit for measurement
science. The `CLAUDE.md` and skills do load in both, but the workflow
assumes Code.

For VS Code or JetBrains users, Claude Code has matching extensions that
read the same `CLAUDE.md` file. Pick one and stick with it per session —
mixing them adds context drift without benefit.
