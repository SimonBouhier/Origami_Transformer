# Note de résultats — Fisher Baseline v4 (v1)

**Date :** 2026-07-09
**Dépôt :** github.com/SimonBouhier/Origami_Transformer
**Statut :** négatif publiable — condition d'arrêt prévue atteinte pour H-A telle que gelée
**Verdict global :** `HA_DÉMENTI` (1/4 modèles confirmés ; seuil : ≥ 3/4)
**Portée :** v4 est la baseline de l'instrument Fisher (repasse de la campagne v3). Le chantier
v5 (contesté vs consensuel, H-C) n'est pas conditionné à la confirmation de H-A.

---

## Résumé

Nous avons re-testé l'hypothèse de la « bosse » — un profil par couche qui monte vers un pic
strictement intérieur puis se comprime — sous un instrument **density-free** : le rang effectif
de la métrique de Fisher restreinte via logit-lens, à la place des estimateurs de dimension
intrinsèque par plus proches voisins (TwoNN/MLE) archivés après Schulte & Rügamer (AISTATS
2026). Quatre architectures, seuils gelés avant toute donnée, corpus identique à v3.

Le verdict global est `HA_DÉMENTI` : un seul modèle (bloom-560m) satisfait les trois conditions.
Le démenti est porté par le **pic en couche 0** (trois modèles sur quatre) — un écho direct du
mode d'échec de v3, où l'estimateur MLE explosait sur la même couche — et, pour deux modèles,
par un couplage géométrie↔fonction sous le seuil. La **compression finale est de nouveau
universelle (4/4)** : c'est, à travers deux campagnes et deux instruments incompatibles, le seul
motif qui survit à tout.

---

## Pré-enregistrement (gelé, commits à l'appui)

- Fichier : `PREREGISTRATION_v4.md`. Commit de gel `4e9683ef` (« preregister v4 »,
  2026-06-02 12:06 +0200), tampon `aa9997f` (« stamp v4 freeze », 12:46). L'instrument
  (`probe_fisher.py`) a été écrit **après** le tampon, conformément à la discipline.
  (La ligne « Frozen on: 2026-05-31 » du fichier date de sa rédaction ; la date qui fait foi
  est celle du commit.)

Conditions cumulatives par modèle, sur P_rank(l) = moyenne corpus du rang effectif de Fisher :

- **C1 — pic intérieur :** `argmax_l P_rank(l)` exclut strictement la première et la dernière
  couche (convention v3, fixée par écrit avant toute donnée).
- **C2 — compression finale :** `P_rank(dernière) < P_rank(pic)`, strict.
- **C3 — couplage reproduit :** `max_l |Spearman(O_rank(·,l), NLL(·,l))| ≥ 0.30`.

Verdict par modèle : `HA_CONFIRMÉ` si C1 ∧ C2 ∧ C3. Global : confirmé sur ≥ 3 modèles et ≥ 66 %.

---

## Méthode

Instrument : `probe_fisher.py`. Pour chaque énoncé et chaque couche l (embeddings incluses),
au dernier token :

- logit-lens **brut** : `logits = W_u·h + b_u` avec l'unembedding du modèle, **sans** LayerNorm
  finale (gelé ; c'est la condition d'exactitude de la forme close de Mabrok, Prop. 5.2) ;
- métrique de Fisher `g(h) = W_uᵀ (diag(p) − p pᵀ) W_u`, exacte sur tout le vocabulaire,
  spectre par `eigvalsh` float64 ;
- observables : `O_rank` (rang effectif spectral de g), `O_vol` (0.5·Σ log λ, top-50),
  `O_aniso` (λ₁/Σλ), plus `NLL(s,l)` du logit-lens par couche.

Corpus : `claims.txt`, 220 énoncés factuels, **identique à v3** (hash de corpus
`ebdc64bd…`, inchangé). Paramètres gelés : seed 0, k = 50, max_length 128, CPU float32.

| Modèle | Famille | Couches captées | Espaces de représentation | Durée du run |
|---|---|---:|---|---:|
| `gpt2` | GPT-2 | 13 | 768 | 10,4 min |
| `EleutherAI/pythia-410m` | GPT-NeoX | 25 | 1024 | 45,3 min |
| `facebook/opt-350m` | OPT | 25 | 1024 (couches 0–23), 512 (dernière) | 44,6 min |
| `bigscience/bloom-560m` | BLOOM | 25 | 1024 | 72,2 min |

### Intégrité du protocole

Trois faits d'exécution, tous antérieurs à toute valeur observée pour le modèle concerné et
consignés au `RESEARCH_LOG` :

1. **Dénormaux.** La queue de la softmax produit des probabilités subnormales (< 1.2e-38) qui
   faisaient tomber les GEMM de ~700 à ~80 GFlops (assist microcode x86). Correctif :
   `torch.set_flush_denormal(True)`. Vérification : sorties **bit-identiques** sur 39 points ×
   4 observables (écart relatif max = 0.0). Correctif numérique, pas un changement de définition.
2. **Espaces mixtes d'OPT-350m.** transformers capture les couches 0–23 en 1024 et la dernière
   en 512 (post-`project_out`). Résolution, fixée avant toute valeur OPT : la decode-map se lit
   **par espace** — `lm_head ∘ project_out` pour les états 1024, `lm_head` seul pour l'état 512.
   Les trois autres modèles (espace unique) ne sont pas concernés.
3. **Interruptions machine.** Deux arrêts du processus hôte (fermeture de session, redémarrage
   Windows Update) ont tué des runs bloom en cours, sans corruption : le JSON s'écrit
   atomiquement en fin de run ; relances complètes.

La convention d'indice de C1 (« intérieur » = exclut exactement première et dernière couche,
convention de la v3) a été fixée par écrit avant l'arrivée de toute donnée v4.

---

## Résultats

| Modèle | L | P_rank[0] | Pic (C1) | P_rank[fin] | C1 | C2 | C3 (ρ_best) | Verdict |
|---|---:|---:|---|---:|:---:|:---:|---|---|
| `gpt2` | 13 | 510,2 | 0 (= 510,2) | 118,9 | ✗ | ✓ | ✗ (+0,290 @ 12) | `HA_DÉMENTI` |
| `EleutherAI/pythia-410m` | 25 | 888,7 | 0 (= 888,7) | 50,3 | ✗ | ✓ | ✓ (+0,335 @ 1) | `HA_DÉMENTI` |
| `facebook/opt-350m` | 25 | 437,5 | 0 (= 437,5) | 47,8 | ✗ | ✓ | ✗ (+0,197 @ 18) | `HA_DÉMENTI` |
| `bigscience/bloom-560m` | 25 | 580,6 | 22 (= 731,2) | 103,2 | ✓ | ✓ | ✓ (+0,486 @ 24) | `HA_CONFIRMÉ` |

**Global : 1/4 confirmé (25 %) → `HA_DÉMENTI`.** (Seuil : ≥ 3 modèles et ≥ 66 %.)

Toutes les corrélations C3 sont **positives** : un rang de Fisher plus élevé s'accompagne d'une
NLL plus élevée — même direction que Viswanathan et al. (2501.10573) pour la DI par prompt.

---

## Lecture

**1. La compression finale (C2) est universelle — et c'est maintenant un invariant
inter-instruments.** En v3 (TwoNN/MLE) comme en v4 (rang effectif de Fisher), sur les quatre
architectures, la dernière couche est très en dessous du maximum du profil. Deux familles
d'instruments aux hypothèses incompatibles (voisinages/densité contre spectre de la métrique
de sortie) voient la même chose. C'est le résultat positif solide de ce programme.

**2. Le pic intérieur ne se reproduit pas ; la couche 0 domine (3/4).** Le profil du rang
effectif part de son maximum en couche 0 et descend, pour gpt2, pythia et opt. La mécanique est
lisible : au lens de la couche 0, les logits sont quasi plats, p est quasi uniforme, g est quasi
isotrope (P_aniso[0] entre 0,021 et 0,078 — aucune direction ne domine), donc le rang effectif
est énorme (437–889, à comparer aux dimensions ambiantes 768/1024, et au rang ≤ 512 du lens
d'opt). Deux lectures concurrentes, **non départagées par ces données** :

- *(a)* la bosse intérieure rapportée par la littérature NN était un artefact d'estimateur
  (le sens de la critique de Schulte & Rügamer) ;
- *(b)* la couche 0 est un régime dégénéré **du lens** : décoder des embeddings bruts avec la
  tête de sortie est une opération que le modèle n'a jamais apprise ; le rang quasi maximal
  mesure l'uniformité du décodage, pas une géométrie interne. C'est l'artefact symétrique de
  celui de v3 (où MLE explosait sur la même couche pour des raisons de densité/duplicatas).

L'exception bloom rend *(b)* plausible sans le prouver : seul modèle confirmé (pic intérieur à
22, P_rank[0] = 580 < 731), il est aussi le seul dont les embeddings passent par une LayerNorm
dédiée (`word_embeddings_layernorm`) avant d'entrer dans le stream — son lens de couche 0 n'est
pas dans le même régime que celui des trois autres.

**3. Le couplage géométrie↔fonction (C3) est réel, positif, mais faible à modéré (0,20–0,49).**
Cohérent avec le prior « signal sémantique faible » (Baroni, `STATE_OF_ART` §7). gpt2 échoue à
0,290 pour un seuil de 0,30 : sans coussin, conformément au pré-enregistrement — le seuil ne
bouge pas après coup. On note que pour bloom le couplage maximal est à la **dernière** couche
(+0,486), là où le lens coïncide presque avec la vraie tête de sortie.

**Conclusion.** Au sens strict du pré-enregistrement, H-A est démentie : la « bosse » vue par
TwoNN/MLE ne se transporte pas en pic intérieur du rang effectif de Fisher sur 3 modèles sur 4.
Au sens morphologique, le démenti est porté par une couche unique — la couche 0 — dont le statut
(artefact d'estimateur v3 contre artefact de lens v4) est précisément la question que la
prochaine campagne doit trancher par pré-enregistrement, pas par exclusion rétroactive.

---

## Ce que nous ne concluons pas (menaces à la validité)

- **Le rang effectif de Fisher n'est pas la dimension intrinsèque.** Vocabulaire volontairement
  distinct (discipline Schulte) : nous mesurons comment la variance de distinguabilité de sortie
  se répartit sur les directions, pas une dimension de variété.
- **Régime du lens en couche 0.** Voir Lecture §2 : le pic à 0 peut être un artefact de lens.
  Symétriquement, l'exclure sans nouveau gel serait du p-hacking ; nous ne l'avons pas fait.
- **Lens brut sans LayerNorm finale.** Choix gelé (exactitude de la forme close). Coût : pour
  gpt2/pythia/bloom, le lens de la dernière couche diffère de la vraie tête (qui applique la LN
  finale) ; la NLL(dernière) n'est donc pas exactement la loss du modèle. opt-350m, sans LN
  finale, est le seul où le lens terminal coïncide avec la tête réelle.
- **Géométrie au dernier token, NLL sur tout l'énoncé.** Les deux observables de C3 ne portent
  pas sur le même support ; lecture documentée dans le code avant les runs.
- **Échantillon.** 220 énoncés par corrélation de Spearman par couche ; float32 (accumulation
  float64) ; graine unique (pipeline déterministe).
- **Quatre modèles de petite taille (124M–560M).** Rien ici ne parle des modèles à l'échelle,
  ni des modèles instruits.

---

## Conséquences

1. **v5 (H-C, contesté vs consensuel) va de l'avant.** H-C ne présuppose pas la bosse : le test
   est la séparabilité intra-modèle des features Fisher par couche. L'instrument sort de v4
   mécaniquement validé (exact, stable, 0,2–0,8 s/point, deux pièges instrumentaux purgés et
   documentés).
2. **La leçon « couche 0 » se règle au gel v5, pas avant, pas rétroactivement** : inclure ou
   exclure la couche 0 des features est une décision à écrire dans `PREREGISTRATION_v5.md`
   avant toute mesure v5.
3. **Le motif robuste à défendre publiquement est la compression finale**, désormais établie
   sur deux campagnes et deux familles d'instruments.
4. `epp_adapter.py` reste un stub. Aucun frame EPP n'est créé sur la base d'une baseline.

---

## Pistes pour une v4.1 (re-pré-enregistrées — à NE PAS appliquer rétroactivement)

- Exclure la couche 0 du calcul du pic (avec justification lens-régime, cf. Lecture §2).
- Variante LN-corrigée du lens (tuned-lens-like) pour tester la sensibilité du profil au choix
  du lens brut.
- C3 par forme de profil (corrélation de rang entre profils moyens) plutôt que par maximum.
- Stratification par classe de tokens ; corpus élargi.
- Comparaison directe bloom vs pythia sur le rôle de la LayerNorm d'embedding (seule différence
  architecturale alignée avec l'exception observée).

---

## Reproductibilité

- Pré-enregistrement : `PREREGISTRATION_v4.md`, gel `4e9683ef`, tampon `aa9997f`.
- Instrument : `probe_fisher.py`, verdict : `analysis_v4.py` (commit `aa22b8e`) ; verdict
  consigné au `RESEARCH_LOG` (commit `1963698`).
- Corpus : `claims.txt`, 220 énoncés, sha256(fichier) `91047e94…`, hash de corpus (join)
  `ebdc64bd…` — identique à v3.
- Paramètres : seed 0, k = 50, max_length 128, CPU float32, FTZ actif, chunk 65536.
- Sorties brutes : `results/*_fisher.json` ; rapport : `results/analysis_v4_report.json`
  (gitignorés, régénérables par les deux commandes ci-dessous).

```
python probe_fisher.py --model <hf_id> --corpus claims.txt --out results/<nom>_fisher.json
python analysis_v4.py results/*_fisher.json --out results/analysis_v4_report.json
```

---

*Instrument : métrique de Fisher restreinte via logit-lens (Mabrok, arxiv:2603.22301, §5) ;
critique fondatrice : Schulte & Rügamer (AISTATS 2026, arxiv:2604.20276). Cette note documente
un résultat négatif obtenu selon un protocole pré-enregistré.*
