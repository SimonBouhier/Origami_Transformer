#!/bin/bash
# v6.1 phase A — rejoue le corpus v6 gele sur GPU pour controle d'equivalence.
# N'ECRIT JAMAIS dans results/ : les mesures de verdict sont intouchables.
set -e
PY=./.venv-gpu/Scripts/python.exe
for M in "gpt2:gpt2" "EleutherAI/pythia-410m:pythia410m" \
         "facebook/opt-350m:opt350m" "bigscience/bloom-560m:bloom560m"; do
  ID="${M%%:*}"; SHORT="${M##*:}"
  for ARM in "contested.txt:contested_fisher" "consensual_v6.txt:consensualv6_fisher"; do
    C="${ARM%%:*}"; O="${ARM##*:}"
    OUT="results_gpu/${SHORT}_${O}.json"
    [ -f "$OUT" ] && { echo "== $SHORT/$O deja fait"; continue; }
    echo "== $SHORT / $O"
    $PY probe_fisher_gpu.py --model "$ID" --corpus "corpora/$C" \
        --out "$OUT" --device cuda 2>&1 | grep -E "wrote|couches|ETA +0\.0" | tail -2
  done
done
echo "=== phase A : mesures terminees ==="
