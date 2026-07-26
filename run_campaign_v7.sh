#!/bin/bash
# =============================================================================
# run_campaign_v7.sh — campagne GPU v7 : difficulté × capacité
# =============================================================================
# Mesure les 4 bras (corpus v6.4 + corpus NUL) sur 6 modèles, fisher + shuffle.
#
# Le BALAYAGE NE COÛTE RIEN ICI : les observables Fisher d'un énoncé ne
# dépendent pas des autres énoncés du corpus. On mesure donc chaque modèle UNE
# FOIS sur les 120 paires, et les 33 rungs sont des sous-ensembles ré-analysés
# en CPU par analysis_sweep_v7.py.
#
# REPRENABLE : toute sortie déjà présente est sautée. Coupez et relancez sans
# rien perdre.
#
# Usage :   bash run_campaign_v7.sh
#           bash run_campaign_v7.sh --small     # seulement les 4 petits modèles
# =============================================================================
set -e
PY=./.venv-gpu/Scripts/python.exe
OUT=results_v7
mkdir -p "$OUT"

# --- échelle de capacité : Pythia (même corpus, même tokenizer, même archi) ---
LADDER=(
  "EleutherAI/pythia-410m:pythia410m"
  "EleutherAI/pythia-1.4b:pythia1400m"
  "EleutherAI/pythia-2.8b:pythia2800m"
)
# --- continuité historique avec v4/v5/v6 ---
LEGACY=(
  "gpt2:gpt2"
  "facebook/opt-350m:opt350m"
  "bigscience/bloom-560m:bloom560m"
)
# --- les 4 bras : corpus réel + corpus nul (M3-B) ---
ARMS=(
  "corpora/v7_sweep/contested.txt:contested"
  "corpora/v7_sweep/consensual.txt:consensual"
  "corpora/v7_sweep/null_A.txt:nullA"
  "corpora/v7_sweep/null_B.txt:nullB"
)

MODELS=("${LADDER[@]}" "${LEGACY[@]}")
if [ "$1" = "--small" ]; then
  MODELS=("EleutherAI/pythia-410m:pythia410m" "gpt2:gpt2"
          "facebook/opt-350m:opt350m" "bigscience/bloom-560m:bloom560m")
fi

echo "=== campagne v7 : ${#MODELS[@]} modèles × ${#ARMS[@]} bras × 2 (fisher+shuffle)"
echo "=== sorties dans $OUT/ — relançable à tout moment"
START=$(date +%s)

for M in "${MODELS[@]}"; do
  ID="${M%%:*}"; SHORT="${M##*:}"
  for A in "${ARMS[@]}"; do
    CORPUS="${A%%:*}"; ARM="${A##*:}"
    for KIND in fisher shuffle; do
      DEST="$OUT/${SHORT}_${ARM}_${KIND}.json"
      if [ -f "$DEST" ]; then echo "  = $SHORT/$ARM/$KIND déjà fait"; continue; fi
      SCRIPT=probe_fisher_gpu.py
      EXTRA=""
      [ "$KIND" = "shuffle" ] && EXTRA="--shuffle"
      echo "  > $SHORT / $ARM / $KIND"
      $PY $SCRIPT --model "$ID" --corpus "$CORPUS" --out "$DEST" \
          --device cuda $EXTRA 2>&1 | grep -E "wrote|couches|ERROR" || true
    done
  done
  echo "--- $SHORT terminé  (écoulé : $((($(date +%s)-START)/60)) min)"
done

echo
echo "=== campagne terminée en $((($(date +%s)-START)/60)) min ==="
echo "Analyse :  ./.venv/Scripts/python.exe analysis_sweep_v7.py --results $OUT"
