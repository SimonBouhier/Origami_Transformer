# v6.1 — résultats des phases A et B (étalonnage de l'instrument)

**Date :** 2026-07-22
**Statut :** étalonnage. **Ne rejuge pas H-D.** Le verdict v6 (`HD_DÉMENTI`,
0/4) reste gelé et inchangé. Aucune mesure ici n'entre dans un verdict.
**Matériel :** RTX 4090 24 Go, pilote 610.74, `torch 2.12.0+cu130` dans un venv
séparé `.venv-gpu` (le venv de mesure, `torch 2.12.0+cpu`, n'a pas été touché).
**Artefacts :** `results_gpu/equivalence_v61.json`,
`results_gpu/bench_spectral_{cpu,gpu}.json`

---

## Phase A — équivalence CPU ↔ GPU : **qualifié, 4/4**

Corpus v6 gelé, mêmes graine / k / dtype, sorties écrites dans `results_gpu/`
(jamais dans `results/`).

| modèle | BA_geo LODO GPU | BA_geo LODO CPU gelé | Δ |
|---|---|---|---|
| gpt2 | 0,6292 | 0,6292 | **0,0000** |
| pythia-410m | 0,7458 | 0,7458 | **0,0000** |
| opt-350m | 0,7500 | 0,7500 | **0,0000** |
| bloom-560m | 0,8167 | 0,8167 | **0,0000** |

Critère fixé d'avance : Δ ≤ 0,005. Obtenu : égalité exacte sur les quatre.

Deux environnements indépendants — venv distinct, backend distinct, ordre de
sommation distinct — produisent le même verdict géométrique. C'est une
validation plus forte que la reproductibilité d'un seul environnement.

**Portage.** `fisher_scalars` alloue ses accumulateurs sans argument `device`
(`probe_fisher.py:107-108`) : elle **échoue** sur des tenseurs CUDA. Elle est
transcrite dans `probe_fisher_gpu.fisher_scalars_device`, seule modification
`device=W.device`, et **vérifiée contre l'originale sur CPU par `--selfcheck` :
égalité stricte**. `layer_nll` et `get_unembedding` sont agnostiques et
importées telles quelles.

**TF32 désactivé explicitement.** Sur Ampere+, laisser TF32 actif ferait tourner
les GEMM « float32 » avec une mantisse de 10 bits : le spectre serait faux et
aucune erreur ne serait levée. Trois `torch.backends` verrouillés et tracés dans
la sortie.

**Anomalie révélée par le portage — gpt2.** Erreur relative CPU/GPU sur `O_vol` :
gpt2 **4,9e-4**, contre ~1e-8 pour les trois autres. Explication : `O_rank`
médian de gpt2 vaut **1,55** (contre 870 / 408 / 586). Son spectre est
quasi rang-1, donc la 50ᵉ valeur propre — que `O_vol` fait entrer dans une somme
de logarithmes — est du bruit numérique. **`O_vol` est mal conditionné pour gpt2,
sur CPU autant que sur GPU** : ce n'est pas un défaut du portage, c'est une
propriété de l'instrument que le portage a mise en lumière. Cohérent avec le
fait que gpt2 échoue partout depuis v4. À verser au dossier v7.

**Coût.** 4 modèles × 2 bras × 120 énoncés : 325 s au total (gpt2 32 s,
pythia 83 s, opt 81 s, bloom 129 s), contre ~2 h 15 pour la campagne CPU
équivalente.

## Phase B — précision et coût de la diagonalisation

### B-0 : Q7 était mal posée (cf. `PLAN_v6.1.md` §0)

L'instrument ne tronque pas le vocabulaire : il calcule la Fisher exacte sur les
|V| tokens et diagonalise la matrice *d × d* complète. `k = 50` ne sert qu'à
`O_vol`. La question « fidélité de la troncature top-k à grand vocabulaire »,
que j'avais écrite dans le cahier, ne s'applique pas.

### B-1 : float32 contre float64 pour `eigvalsh` — sûr

Sur de vraies matrices g(h) de pythia-410m (10 tirages, couches variées) :

| observable | erreur relative médiane | max |
|---|---|---|
| `O_vol` | 6,9e-09 | 3,5e-08 |
| `O_rank` | 7,6e-08 | 5,0e-07 |
| `O_aniso` | 3,7e-07 | 9,1e-07 |

Ma crainte que le float32 corrompe les petites valeurs propres et fausse le rang
effectif **ne tient pas** : `O_rank` est une entropie du spectre *normalisé*,
dominée par le corps de la distribution, pas par la queue.

**Argument décisif :** l'écart CPU↔GPU en float32 déjà accepté en phase A vaut
~5e-4 sur `O_vol` (gpt2) — soit **cinq ordres de grandeur au-dessus** de
l'écart f32/f64 de la diagonalisation. Le bruit dominant vient de l'ordre de
sommation du GEMM, pas de la précision spectrale. Passer `eigvalsh` en float32
pour le passage à l'échelle est justifié par la mesure.

### B-2 : coût de `eigvalsh`

| d | CPU f64 | CUDA f64 | CUDA f32 |
|---|---|---|---|
| 1024 | 29 ms | 21 ms | 7,7 ms |
| 2048 | 282 ms | 54 ms | 19,9 ms |
| 2560 | 406 ms | 88 ms | 29,6 ms |
| 4096 | 1261 ms | 290 ms | **72 ms** |

**Mon hypothèse « GEMM sur GPU, diagonalisation sur CPU » est réfutée.** Le
float64 d'une GeForce est bridé à 1/64 du float32, mais cuSOLVER en f64 bat
quand même MKL d'un facteur 4,3 à d = 4096. Le GPU gagne partout ; le float32
donne encore ×4.

### B-3 : qualification bf16 — **ÉCHEC**

pythia-6.9b en float32 pèse 27,6 Go : **ne rentre pas dans 24 Go**. Atteindre ce
barreau exigerait des poids en bf16. Testé sur pythia-410m, où fp32 et bf16
tiennent tous les deux (seule la passe avant change de dtype ; W et h sont
remontés en float32 pour la Fisher) :

| | valeur |
|---|---|
| BA_geo LODO fp32 | 0,7458 |
| BA_geo LODO bf16 | 0,7542 |
| **Δ** | **0,0083** — au-dessus de notre tolérance de 0,005 |

| observable | médiane | p99 | max |
|---|---|---|---|
| `O_vol` | 2,0e-05 | 6,9e-03 | 2,5e-02 |
| `O_rank` | 1,1e-04 | **1,1e-01** | **1,9e-01** |
| `O_aniso` | 6,5e-04 | 6,8e-02 | 1,3e-01 |
| `NLL` | 7,6e-04 | 1,7e-02 | 4,8e-02 |

`O_rank` bouge de **19 % au maximum** et de 11 % au 99ᵉ centile, contre 3,9e-08
pour l'écart fp32 CPU/GPU accepté. **bf16 n'est pas le même instrument.**

**Conséquence pour l'échelle pythia :**
- **En float32 strict, l'échelle s'arrête à 2.8b** (11,2 Go) : trois barreaux,
  410m → 1.4b → 2.8b, d = 1024 → 2048 → 2560, facteur ~7 en paramètres. C'est
  déjà une expérience réelle, et elle reste comparable aux mesures gelées.
- **Un 4ᵉ barreau à 6.9b reste possible, mais seulement comme échelle bf16
  entièrement séparée** : tous les barreaux en bf16, jamais mélangés aux
  chiffres fp32. Une échelle est une comparaison *interne* — elle reste
  interprétable si la précision est constante d'un bout à l'autre. Le décalage
  est déjà calibré à 410m : **+0,0083**.

---

## Bilan

L'instrument est qualifié sur GPU (A, 4/4 exact). Le float32 spectral est
justifié par la mesure (B-1). Le coût est connu et permet une campagne d'échelle
(B-2). Le bf16 est disqualifié comme équivalent et ne peut servir que dans une
échelle homogène (B-3).

**Deux de mes prédictions ont été réfutées par la mesure** — le CPU ne bat pas
le float64 bridé du GPU, et le float32 ne corrompt pas le rang effectif — et
**une de mes questions était mal posée** (la troncature top-k). C'est le
rendement normal d'une phase d'étalonnage : elle existe pour que ces erreurs
soient découvertes avant la campagne, pas dedans.

**Ce qui n'est pas fait et attend une décision :** la phase C (échelle pythia)
avance une affirmation — « la capacité fait croître la séparabilité
géométrique » — et doit donc être **pré-enregistrée avant toute lecture de
chiffre** : seuil de monotonie, seuil de franchissement de la barre bon marché
(0,762, indépendante du modèle), traitement des VOID, et choix explicite entre
l'échelle fp32 à trois barreaux et l'échelle bf16 à quatre.
