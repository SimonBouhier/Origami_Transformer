# Famille de corpus v7 — 33 rungs

Construit par `build_sweep_v7.py`, **model-free** : le retrait est piloté par le seul classifieur bon marché, jamais par la géométrie.

- pas : **2** paires par rung · plancher : **8** paires par pli LODO
- descente : **120 → 56** paires
- BA_cheap : **0.6875 → 0.4643**

| rung | paires | BA_cheap LODO |
|---:|---:|---:|
| 0 | 120 | 0.6875 |
| 1 | 118 | 0.6822 |
| 2 | 116 | 0.6767 |
| 3 | 114 | 0.6667 |
| 4 | 112 | 0.6562 |
| 5 | 110 | 0.6500 |
| 6 | 108 | 0.6343 |
| 7 | 106 | 0.6321 |
| 8 | 104 | 0.6346 |
| 9 | 102 | 0.6275 |
| 10 | 100 | 0.6200 |
| 11 | 98 | 0.6071 |
| 12 | 96 | 0.6042 |
| 13 | 94 | 0.5904 |
| 14 | 92 | 0.5761 |
| 15 | 90 | 0.5722 |
| 16 | 88 | 0.5625 |
| 17 | 86 | 0.5465 |
| 18 | 84 | 0.5417 |
| 19 | 82 | 0.5427 |
| 20 | 80 | 0.5688 |
| 21 | 78 | 0.5577 |
| 22 | 76 | 0.5526 |
| 23 | 74 | 0.5473 |
| 24 | 72 | 0.5278 |
| 25 | 70 | 0.5357 |
| 26 | 68 | 0.4926 |
| 27 | 66 | 0.4924 |
| 28 | 64 | 0.4844 |
| 29 | 62 | 0.4839 |
| 30 | 60 | 0.4667 |
| 31 | 58 | 0.5086 |
| 32 | 56 | 0.4643 |

## Corpus nul (M3-B)

Les 120 énoncés consensuels de v6.4 répartis en deux bras de **50**, équilibrés par domaine fin, graine 0. Même vivier des deux côtés : il n'y a rien à trouver. Ce que le pipeline y mesure est le plancher réel, mesure GPU comprise.
