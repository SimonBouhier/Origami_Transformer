# Origami DI Probe — v3

Trois fichiers, frontieres nettes :

- `probe.py`     — instrument pur. Mesure, ne juge pas.
- `analysis.py`  — applique le verdict preenregistre.
- `epp_adapter.py` — stub. Refuse de tourner tant que le probe n'est pas valide.

## Install

```bash
pip install torch transformers scikit-dimension numpy
```

## Run (un modele a la fois)

```bash
python probe.py --model gpt2 --out results/gpt2.json
python probe.py --model EleutherAI/pythia-410m --out results/pythia410m.json
python probe.py --model mistralai/Mistral-7B-v0.1 --out results/mistral7b.json \
                --n-subsample 2000 --n-boot 20
```

Modeles "gated" (Llama, Gemma) : `huggingface-cli login` au prealable.

## Verdict

```bash
python analysis.py results/*.json --out analysis_report.json
```

## Pre-enregistrement (FIGE, ne pas editer apres premier run)

```
date              : 2026-05-30
hypothese H1      : profil de DI en bosse, derniere couche < pic
estimateurs       : TwoNN + MLE (hypotheses orthogonales)
C1 accord         : >= 70% des couches avec ecart relatif <= 20%
C2 pic            : strictement dans [1, L-2]
C3 compression    : DI[derniere] < DI[pic], sans tolerance
verdict global    : H1 confirme sur >= 4 modeles ET >= 66% du total
```

Commit ce README AVANT de regarder le premier `analysis_report.json`.
Un dementi est un negatif publiable et arrete proprement le chantier.

## Ce que ce code NE fait PAS

- Pas d'attestation EPP. Voir `epp_adapter.py`.
- Pas de signature epistemique a 5 dimensions. Pas son role.
- Pas de "tolerance legere" sur les seuils. La potence est seche.
- Pas d'agregation multi-claims dans un meme nuage : si tu veux comparer
  claims contestes vs consensuels (sonde #3), tu fais tourner probe.py
  DEUX fois avec deux corpus distincts, puis tu compares les profils.
