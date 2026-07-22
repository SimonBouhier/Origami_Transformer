# Cahier des charges — bras consensuel v6.2
**Généré mécaniquement** par `build_spec_v6_2.py` depuis les fichiers gelés. Aucun chiffre n'est saisi à la main ; régénérable à l'identique.
**Sources :** [contested.txt](corpora/contested.txt) (gelé, sha `3eb7bae8…`) · [consensual_v6.txt](corpora/consensual_v6.txt) · [domain_map_v6.json](corpora/domain_map_v6.json) · [contested_anchors.tsv](corpora/contested_anchors.tsv)
**Cible :** `corpora/consensual_v6_2.txt`, 120 lignes.
**Pré-enregistrement :** [PREREGISTRATION_v6.2.md](PREREGISTRATION_v6.2.md) — à geler APRÈS que ce corpus soit construit et ait passé la porte G1.

---
## 1. Le besoin, exactement
v6 a été démenti parce qu'une description linguistique bon marché égalait la géométrie. Le diagnostic a nommé la cause : **le bras contesté compare des grandeurs, le bras consensuel décrit des mécanismes.** Huit compteurs d'expressions régulières atteignent BA = 0,762 en LODO — au-dessus de la baseline gelée et au-dessus de la géométrie sur 3 modèles sur 4.
v6.2 supprime cette asymétrie. **La ligne *i* du bras consensuel doit correspondre à la ligne *i* du bras contesté sur DEUX critères :**
1. le **domaine fin** — déjà vrai en v6, à préserver ;
2. la **classe de construction** — comparatif vs non-comparatif. C'est ce qui manque.

> Le bras contesté est **gelé**. On ne le touche pas. Tout le travail porte sur le bras consensuel.

### Ce qu'est un consensuel comparatif
Une comparaison qu'**aucun expert informé ne conteste**. Pas un énoncé contesté adouci, pas une comparaison vague.

**Oui :**
- *Light travels faster through a vacuum than through glass or water.*  (12 tokens)
- *A progressive income tax takes a larger share from higher earners.*  (12 tokens)
- *Compound interest makes unpaid debt grow faster over time.*  (11 tokens)
- *Infectious diseases spread faster in densely populated urban areas.*  (12 tokens)

**Non :**
- *Nuclear power is safer than coal power.* — vrai selon la plupart des bilans, mais **disputé** dans le débat expert : c'est un contesté.
- *Some materials conduct heat better than others.* — comparatif mais **vide** : aucun contenu empirique testable.
- *Studies suggest vitamin C may shorten colds.* — **hedge** interdit, et l'énoncé est contesté.

### Contraintes dures (reprises de v5/v6, inchangées)
| contrainte | valeur |
|---|---|
| langue | anglais, déclaratif, assertable (*truth-apt*) |
| hedges | **interdits** (`may`, `might`, `some studies suggest`, `possibly`) |
| longueur | **9 à 16 tokens gpt2**, appariée en longueur dans le domaine |
| doublons | aucun, ni dans le bras ni avec le bras contesté |
| statut | accord large et établi ; jugements de valeur **exclus** |
| registre | même famille syntaxique que le contesté apparié |

### Portes de qualité (model-free, AVANT tout gel)
- **G0** — structurelle, dure : classe de construction identique entre les deux bras sur **120/120 lignes**.
- **G1** — statistique : le classifieur sur les 8 marqueurs seuls, sous les 7 plis LODO gelés, doit tomber à **BA ≤ 0,65** (contre 0,762 en v6).
- **Plafond : 3 tours de reconstruction**, chaque valeur de G1 journalisée dans `corpora/matching_report_v6_2.json`. Au-delà, la campagne s'arrête sans verdict et l'échec est publié.

---

## 2. Récapitulatif du chantier
| catégorie | lignes | action |
|---|---|---|
| §3 — consensuel **comparatif** à écrire | **36** | rédaction neuve |
| §4 — consensuel à rendre **non-comparatif** | **5** | réécriture |
| §5 — déjà conformes | **79** | **reprise verbatim** |
| total | 120 | |

Répartition par domaine fin des lignes à écrire en §3 :

- `medicine` — 5
- `ai` — 4
- `economics` — 3
- `education` — 3
- `history` — 3
- `political_science` — 3
- `archaeology` — 2
- `physics` — 2
- `biology` — 1
- `conservation` — 1
- `cosmology` — 1
- `genomics` — 1
- `health_econ` — 1
- `linguistics` — 1
- `neuroscience` — 1
- `organizational` — 1
- `psychology` — 1
- `public_health` — 1
- `sociology` — 1

---

## 3. Lignes exigeant un consensuel COMPARATIF (36)

Le contesté apparié est comparatif ; le consensuel ne l'est pas. Il faut un consensuel comparatif dans le même domaine fin.

### Ligne 1 — `health_econ` · super `econ_policy` — **COMPARATIF requis**

**Contesté (gelé, référence)** — [contested.txt:1](corpora/contested.txt:1) · 14 tokens

> A regulated market in human kidneys would save more lives than it costs.

*Qui l'affirme :* market-in-organs economists (Becker & Elias); Iranian-model advocates  
*Qui le nie :* WHO transplant ethics; gift-economy bioethics (Titmuss-line)

**Consensuel actuel** — [consensual_v6.txt:1](corpora/consensual_v6.txt:1) · 11 tokens

> Health insurance spreads medical costs across a pool of members.

**Marqueurs du contesté :** comparatif (`more`, `than`) · modal/irréalis (`would`)

**Marqueurs du consensuel actuel :** prép. de mécanisme (`across`)

**À produire :** un énoncé consensuel **comparatif** en `health_econ`, **11–16 tokens gpt2**, respectant les contraintes dures du §1.

### Ligne 2 — `medicine` · super `medicine_health` — **COMPARATIF requis**

**Contesté (gelé, référence)** — [contested.txt:2](corpora/contested.txt:2) · 14 tokens

> Routine PSA screening reduces prostate cancer mortality more than it harms.

*Qui l'affirme :* early PSA-screening urology; some ERSPC-trial interpreters  
*Qui le nie :* USPSTF (grade C/D); Cochrane; PLCO-trial interpreters

**Consensuel actuel** — [consensual_v6.txt:2](corpora/consensual_v6.txt:2) · 13 tokens

> Anaesthesia allows surgery to proceed without the patient feeling pain.

**Marqueurs du contesté :** comparatif (`more`, `than`) · attribution causale (`reduces`)

**Marqueurs du consensuel actuel :** négation (`without`)

**À produire :** un énoncé consensuel **comparatif** en `medicine`, **11–16 tokens gpt2**, respectant les contraintes dures du §1.

### Ligne 3 — `medicine` · super `medicine_health` — **COMPARATIF requis**

**Contesté (gelé, référence)** — [contested.txt:3](corpora/contested.txt:3) · 12 tokens

> Antidepressants outperform placebo by a clinically meaningful margin.

*Qui l'affirme :* Cipriani et al. 2018 meta-analysis; NICE mainstream psychiatry  
*Qui le nie :* Kirsch-line; Moncrieff & critical-psychiatry network

**Consensuel actuel** — [consensual_v6.txt:3](corpora/consensual_v6.txt:3) · 12 tokens

> The heart pumps blood through arteries to the body's tissues.

**Marqueurs du contesté :** comparatif (`outperform`) · quantif. de portée (`meaningful`)

**Marqueurs du consensuel actuel :** prép. de mécanisme (`through`)

**À produire :** un énoncé consensuel **comparatif** en `medicine`, **9–15 tokens gpt2**, respectant les contraintes dures du §1.

### Ligne 7 — `medicine` · super `medicine_health` — **COMPARATIF requis**

**Contesté (gelé, référence)** — [contested.txt:7](corpora/contested.txt:7) · 11 tokens

> Most antibiotic courses are prescribed for longer than clinically necessary.

*Qui l'affirme :* "shorter-is-better" (Spellberg; Llewelyn BMJ 2017)  
*Qui le nie :* traditional "complete the course" clinical guidance

**Consensuel actuel** — [consensual_v6.txt:7](corpora/consensual_v6.txt:7) · 12 tokens

> Blood transfusions require compatibility between donor and recipient blood types.

**Marqueurs du contesté :** comparatif (`longer`, `than`) · quantif. de portée (`most`) · copule définitionnelle (`are`)

**Marqueurs du consensuel actuel :** prép. de mécanisme (`between`)

**À produire :** un énoncé consensuel **comparatif** en `medicine`, **9–14 tokens gpt2**, respectant les contraintes dures du §1.

### Ligne 8 — `medicine` · super `medicine_health` — **COMPARATIF requis**

**Contesté (gelé, référence)** — [contested.txt:8](corpora/contested.txt:8) · 14 tokens

> Intermittent fasting produces greater fat loss than continuous calorie restriction.

*Qui l'affirme :* intermittent-fasting proponents (some metabolic researchers)  
*Qui le nie :* isocaloric-RCT interpreters (Trepanowski 2017; Templeman)

**Consensuel actuel** — [consensual_v6.txt:8](corpora/consensual_v6.txt:8) · 13 tokens

> Antibiotics treat bacterial infections but have no effect on viruses.

**Marqueurs du contesté :** comparatif (`greater`, `than`)

**Marqueurs du consensuel actuel :** négation (`no`)

**À produire :** un énoncé consensuel **comparatif** en `medicine`, **11–16 tokens gpt2**, respectant les contraintes dures du §1.

### Ligne 10 — `medicine` · super `medicine_health` — **COMPARATIF requis**

**Contesté (gelé, référence)** — [contested.txt:10](corpora/contested.txt:10) · 14 tokens

> Screening mammography before age fifty saves more lives than it harms.

*Qui l'affirme :* American Cancer Society; radiology societies  
*Qui le nie :* USPSTF; Nordic Cochrane (Gøtzsche); Canadian task force

**Consensuel actuel** — [consensual_v6.txt:10](corpora/consensual_v6.txt:10) · 14 tokens

> Vaccines train the immune system by presenting harmless antigens.

**Marqueurs du contesté :** comparatif (`more`, `than`)

**Marqueurs du consensuel actuel :** 

**À produire :** un énoncé consensuel **comparatif** en `medicine`, **11–16 tokens gpt2**, respectant les contraintes dures du §1.

### Ligne 14 — `political_science` · super `econ_policy` — **COMPARATIF requis**

**Contesté (gelé, référence)** — [contested.txt:14](corpora/contested.txt:14) · 10 tokens

> Democratic peace reflects shared interests more than shared institutions.

*Qui l'affirme :* realists (Rosato; Mearsheimer; Gartzke capitalist peace)  
*Qui le nie :* democratic-peace liberals (Russett; Doyle-line)

**Consensuel actuel** — [consensual_v6.txt:14](corpora/consensual_v6.txt:14) · 10 tokens

> Federal states divide powers between national and regional governments.

**Marqueurs du contesté :** comparatif (`more`, `than`)

**Marqueurs du consensuel actuel :** prép. de mécanisme (`between`)

**À produire :** un énoncé consensuel **comparatif** en `political_science`, **9–13 tokens gpt2**, respectant les contraintes dures du §1.

### Ligne 15 — `political_science` · super `econ_policy` — **COMPARATIF requis**

**Contesté (gelé, référence)** — [contested.txt:15](corpora/contested.txt:15) · 14 tokens

> Electoral systems shape the number of parties more than social divisions do.

*Qui l'affirme :* Duverger-line institutionalists (Cox)  
*Qui le nie :* sociological cleavage theory (Lipset & Rokkan)

**Consensuel actuel** — [consensual_v6.txt:15](corpora/consensual_v6.txt:15) · 13 tokens

> Diplomatic embassies represent one state within the territory of another.

**Marqueurs du contesté :** comparatif (`more`, `than`) · nom abstrait méta (`social`)

**Marqueurs du consensuel actuel :** prép. de mécanisme (`within`)

**À produire :** un énoncé consensuel **comparatif** en `political_science`, **11–16 tokens gpt2**, respectant les contraintes dures du §1.

### Ligne 16 — `political_science` · super `econ_policy` — **COMPARATIF requis**

**Contesté (gelé, référence)** — [contested.txt:16](corpora/contested.txt:16) · 12 tokens

> Economic conditions determine incumbent re-election more than campaigns do.

*Qui l'affirme :* economic-voting models (Fair; Achen & Bartels)  
*Qui le nie :* campaign-effects scholars (Vavreck; persuasion researchers)

**Consensuel actuel** — [consensual_v6.txt:16](corpora/consensual_v6.txt:16) · 12 tokens

> Parliaments pass legislation through recorded votes of their members.

**Marqueurs du contesté :** comparatif (`more`, `than`) · nom abstrait méta (`economic`)

**Marqueurs du consensuel actuel :** prép. de mécanisme (`through`)

**À produire :** un énoncé consensuel **comparatif** en `political_science`, **9–15 tokens gpt2**, respectant les contraintes dures du §1.

### Ligne 23 — `economics` · super `econ_policy` — **COMPARATIF requis**

**Contesté (gelé, référence)** — [contested.txt:23](corpora/contested.txt:23) · 13 tokens

> Industrial policy can outperform free markets at building strategic industries.

*Qui l'affirme :* Mazzucato; Rodrik; developmental-state scholars  
*Qui le nie :* free-market neoclassical economists

**Consensuel actuel** — [consensual_v6.txt:23](corpora/consensual_v6.txt:23) · 13 tokens

> Gross domestic product measures the value of goods and services produced.

**Marqueurs du contesté :** comparatif (`outperform`) · modal/irréalis (`can`)

**Marqueurs du consensuel actuel :** 

**À produire :** un énoncé consensuel **comparatif** en `economics`, **10–16 tokens gpt2**, respectant les contraintes dures du §1.

### Ligne 33 — `economics` · super `econ_policy` — **COMPARATIF requis**

**Contesté (gelé, référence)** — [contested.txt:33](corpora/contested.txt:33) · 12 tokens

> Occupational licensing raises consumer prices more than it improves quality.

*Qui l'affirme :* Kleiner-line labor economists  
*Qui le nie :* licensing defenders (quality-signaling scholars)

**Consensuel actuel** — [consensual_v6.txt:33](corpora/consensual_v6.txt:33) · 12 tokens

> Exchange rates determine how much foreign currency a payment buys.

**Marqueurs du contesté :** comparatif (`more`, `than`) · attribution causale (`improves`, `raises`)

**Marqueurs du consensuel actuel :** 

**À produire :** un énoncé consensuel **comparatif** en `economics`, **9–15 tokens gpt2**, respectant les contraintes dures du §1.

### Ligne 37 — `neuroscience` · super `life_sciences` — **COMPARATIF requis**

**Contesté (gelé, référence)** — [contested.txt:37](corpora/contested.txt:37) · 13 tokens

> Consciousness arises from integrated information rather than specific neural circuits.

*Qui l'affirme :* Integrated Information Theory (Tononi; Koch)  
*Qui le nie :* global-workspace theorists; 2023 IIT-"pseudoscience" letter signatories

**Consensuel actuel** — [consensual_v6.txt:37](corpora/consensual_v6.txt:37) · 13 tokens

> Neurons transmit signals through electrical impulses and chemical synapses.

**Marqueurs du contesté :** comparatif (`rather than`)

**Marqueurs du consensuel actuel :** prép. de mécanisme (`through`)

**À produire :** un énoncé consensuel **comparatif** en `neuroscience`, **10–16 tokens gpt2**, respectant les contraintes dures du §1.

### Ligne 42 — `physics` · super `physical_climate` — **COMPARATIF requis**

**Contesté (gelé, référence)** — [contested.txt:42](corpora/contested.txt:42) · 12 tokens

> Dark matter consists of undiscovered particles rather than modified gravity.

*Qui l'affirme :* CDM / particle dark-matter mainstream  
*Qui le nie :* MOND (Milgrom; McGaugh)

**Consensuel actuel** — [consensual_v6.txt:42](corpora/consensual_v6.txt:42) · 10 tokens

> Energy is conserved in any closed physical system.

**Marqueurs du contesté :** comparatif (`rather than`) · copule définitionnelle (`consists of`)

**Marqueurs du consensuel actuel :** copule définitionnelle (`is`)

**À produire :** un énoncé consensuel **comparatif** en `physics`, **9–15 tokens gpt2**, respectant les contraintes dures du §1.

### Ligne 50 — `physics` · super `physical_climate` — **COMPARATIF requis**

**Contesté (gelé, référence)** — [contested.txt:50](corpora/contested.txt:50) · 12 tokens

> Information swallowed by a black hole is preserved rather than destroyed.

*Qui l'affirme :* information-preservation (Susskind; islands / holography)  
*Qui le nie :* information-loss holdouts (historical Hawking-line)

**Consensuel actuel** — [consensual_v6.txt:50](corpora/consensual_v6.txt:50) · 11 tokens

> Sound requires a material medium and cannot travel through vacuum.

**Marqueurs du contesté :** comparatif (`rather than`) · copule définitionnelle (`is`)

**Marqueurs du consensuel actuel :** négation (`cannot`) · prép. de mécanisme (`through`)

**À produire :** un énoncé consensuel **comparatif** en `physics`, **9–15 tokens gpt2**, respectant les contraintes dures du §1.

### Ligne 51 — `cosmology` · super `physical_climate` — **COMPARATIF requis**

**Contesté (gelé, référence)** — [contested.txt:51](corpora/contested.txt:51) · 11 tokens

> The Hubble tension reflects new physics rather than measurement error.

*Qui l'affirme :* new-physics interpreters of the Hubble tension (Riess / SH0ES)  
*Qui le nie :* systematics / measurement-error interpreters (some CMB-side)

**Consensuel actuel** — [consensual_v6.txt:51](corpora/consensual_v6.txt:51) · 11 tokens

> The observable universe has been expanding since the Big Bang.

**Marqueurs du contesté :** comparatif (`rather than`)

**Marqueurs du consensuel actuel :** 

**À produire :** un énoncé consensuel **comparatif** en `cosmology`, **9–14 tokens gpt2**, respectant les contraintes dures du §1.

### Ligne 53 — `genomics` · super `life_sciences` — **COMPARATIF requis**

**Contesté (gelé, référence)** — [contested.txt:53](corpora/contested.txt:53) · 14 tokens

> Most human non-coding DNA is functional rather than evolutionary residue.

*Qui l'affirme :* ENCODE consortium (Birney)  
*Qui le nie :* Graur-line ("junk DNA" defenders)

**Consensuel actuel** — [consensual_v6.txt:53](corpora/consensual_v6.txt:53) · 10 tokens

> The human genome contains roughly three billion base pairs.

**Marqueurs du contesté :** comparatif (`rather than`) · quantif. de portée (`most`) · copule définitionnelle (`is`)

**Marqueurs du consensuel actuel :** 

**À produire :** un énoncé consensuel **comparatif** en `genomics`, **11–16 tokens gpt2**, respectant les contraintes dures du §1.

### Ligne 57 — `biology` · super `life_sciences` — **COMPARATIF requis**

**Contesté (gelé, référence)** — [contested.txt:57](corpora/contested.txt:57) · 12 tokens

> Viruses belong among living organisms rather than inert chemistry.

*Qui l'affirme :* giant-virus researchers (Forterre-line)  
*Qui le nie :* mainstream "viruses are not alive" view

**Consensuel actuel** — [consensual_v6.txt:57](corpora/consensual_v6.txt:57) · 12 tokens

> DNA carries genetic information in sequences of four nucleotide bases.

**Marqueurs du contesté :** comparatif (`rather than`)

**Marqueurs du consensuel actuel :** 

**À produire :** un énoncé consensuel **comparatif** en `biology`, **9–15 tokens gpt2**, respectant les contraintes dures du §1.

### Ligne 59 — `linguistics` · super `mind_language_society` — **COMPARATIF requis**

**Contesté (gelé, référence)** — [contested.txt:59](corpora/contested.txt:59) · 12 tokens

> Human grammar rests on an innate faculty rather than general learning.

*Qui l'affirme :* generativists / universal grammar (Chomsky)  
*Qui le nie :* usage-based emergentists (Tomasello; Christiansen & Chater)

**Consensuel actuel** — [consensual_v6.txt:59](corpora/consensual_v6.txt:59) · 10 tokens

> Written scripts developed thousands of years after spoken language.

**Marqueurs du contesté :** comparatif (`rather than`)

**Marqueurs du consensuel actuel :** 

**À produire :** un énoncé consensuel **comparatif** en `linguistics`, **9–15 tokens gpt2**, respectant les contraintes dures du §1.

### Ligne 63 — `ai` · super `ai_computing` — **COMPARATIF requis**

**Contesté (gelé, référence)** — [contested.txt:63](corpora/contested.txt:63) · 13 tokens

> Language models mostly memorize training data rather than truly generalizing.

*Qui l'affirme :* memorization researchers (Carlini extraction studies)  
*Qui le nie :* generalization / grokking proponents

**Consensuel actuel** — [consensual_v6.txt:63](corpora/consensual_v6.txt:63) · 13 tokens

> Tokenizers split text into discrete units before a model processes it.

**Marqueurs du contesté :** comparatif (`rather than`)

**Marqueurs du consensuel actuel :** prép. de mécanisme (`into`)

**À produire :** un énoncé consensuel **comparatif** en `ai`, **10–16 tokens gpt2**, respectant les contraintes dures du §1.

### Ligne 71 — `ai` · super `ai_computing` — **COMPARATIF requis**

**Contesté (gelé, référence)** — [contested.txt:71](corpora/contested.txt:71) · 17 tokens

> Retrieval-augmented systems hallucinate less than larger parametric models.

*Qui l'affirme :* RAG proponents (Lewis et al.)  
*Qui le nie :* long-context / parametric-knowledge proponents

**Consensuel actuel** — [consensual_v6.txt:71](corpora/consensual_v6.txt:71) · 16 tokens

> Transformers process input sequences using self-attention over token embeddings.

**Marqueurs du contesté :** comparatif (`larger`, `less`, `than`)

**Marqueurs du consensuel actuel :** 

**À produire :** un énoncé consensuel **comparatif** en `ai`, **14–16 tokens gpt2**, respectant les contraintes dures du §1.

### Ligne 75 — `ai` · super `ai_computing` — **COMPARATIF requis**

**Contesté (gelé, référence)** — [contested.txt:75](corpora/contested.txt:75) · 16 tokens

> Mixture-of-experts architectures outperform dense models at equal compute.

*Qui l'affirme :* MoE proponents (Fedus, Zoph & Shazeer)  
*Qui le nie :* dense-scaling proponents / MoE-cost skeptics

**Consensuel actuel** — [consensual_v6.txt:75](corpora/consensual_v6.txt:75) · 15 tokens

> Regularization constrains model parameters to improve generalization beyond training data.

**Marqueurs du contesté :** comparatif (`outperform`)

**Marqueurs du consensuel actuel :** attribution causale (`improve`)

**À produire :** un énoncé consensuel **comparatif** en `ai`, **13–16 tokens gpt2**, respectant les contraintes dures du §1.

### Ligne 76 — `ai` · super `ai_computing` — **COMPARATIF requis**

**Contesté (gelé, référence)** — [contested.txt:76](corpora/contested.txt:76) · 14 tokens

> Reinforcement learning from feedback suppresses rather than removes unwanted outputs.

*Qui l'affirme :* "shallow alignment" critics (some interpretability researchers)  
*Qui le nie :* RLHF-as-genuine-improvement proponents

**Consensuel actuel** — [consensual_v6.txt:76](corpora/consensual_v6.txt:76) · 15 tokens

> Backpropagation computes gradients by applying the chain rule backwards.

**Marqueurs du contesté :** comparatif (`rather than`)

**Marqueurs du consensuel actuel :** 

**À produire :** un énoncé consensuel **comparatif** en `ai`, **11–16 tokens gpt2**, respectant les contraintes dures du §1.

### Ligne 77 — `economics` · super `econ_policy` — **COMPARATIF requis**

**Contesté (gelé, référence)** — [contested.txt:77](corpora/contested.txt:77) · 11 tokens

> A carbon tax cuts emissions more effectively than permit trading.

*Qui l'affirme :* carbon-tax economists (Nordhaus-line; Pigouvian)  
*Qui le nie :* cap-and-trade proponents (some environmental economists)

**Consensuel actuel** — [consensual_v6.txt:77](corpora/consensual_v6.txt:77) · 11 tokens

> Stock exchanges let shareholders trade partial ownership of listed companies.

**Marqueurs du contesté :** comparatif (`more`, `than`)

**Marqueurs du consensuel actuel :** 

**À produire :** un énoncé consensuel **comparatif** en `economics`, **9–14 tokens gpt2**, respectant les contraintes dures du §1.

### Ligne 87 — `conservation` · super `life_sciences` — **COMPARATIF requis**

**Contesté (gelé, référence)** — [contested.txt:87](corpora/contested.txt:87) · 12 tokens

> Protected areas conserve biodiversity better than sustainable-use zones.

*Qui l'affirme :* fortress-conservation proponents  
*Qui le nie :* community-based / sustainable-use conservationists

**Consensuel actuel** — [consensual_v6.txt:87](corpora/consensual_v6.txt:87) · 12 tokens

> Habitat destruction is a leading cause of species extinction.

**Marqueurs du contesté :** comparatif (`better`, `than`)

**Marqueurs du consensuel actuel :** attribution causale (`cause`) · copule définitionnelle (`is`)

**À produire :** un énoncé consensuel **comparatif** en `conservation`, **9–15 tokens gpt2**, respectant les contraintes dures du §1.

### Ligne 88 — `education` · super `mind_language_society` — **COMPARATIF requis**

**Contesté (gelé, référence)** — [contested.txt:88](corpora/contested.txt:88) · 11 tokens

> Standardized tests predict university success better than school grades.

*Qui l'affirme :* SAT predictive-validity psychometricians  
*Qui le nie :* test-optional advocates (Hiss-line)

**Consensuel actuel** — [consensual_v6.txt:88](corpora/consensual_v6.txt:88) · 11 tokens

> Learning to read requires mapping written symbols onto spoken sounds.

**Marqueurs du contesté :** comparatif (`better`, `than`)

**Marqueurs du consensuel actuel :** prép. de mécanisme (`onto`)

**À produire :** un énoncé consensuel **comparatif** en `education`, **9–14 tokens gpt2**, respectant les contraintes dures du §1.

### Ligne 92 — `sociology` · super `mind_language_society` — **COMPARATIF requis**

**Contesté (gelé, référence)** — [contested.txt:92](corpora/contested.txt:92) · 11 tokens

> Social class matters more than race in shaping life outcomes.

*Qui l'affirme :* class-primacy (W. J. Wilson, "declining significance of race")  
*Qui le nie :* structural-racism sociologists

**Consensuel actuel** — [consensual_v6.txt:92](corpora/consensual_v6.txt:92) · 11 tokens

> Census surveys collect demographic data about a national population.

**Marqueurs du contesté :** comparatif (`more`, `than`) · nom abstrait méta (`social`)

**Marqueurs du consensuel actuel :** 

**À produire :** un énoncé consensuel **comparatif** en `sociology`, **9–14 tokens gpt2**, respectant les contraintes dures du §1.

### Ligne 93 — `education` · super `mind_language_society` — **COMPARATIF requis**

**Contesté (gelé, référence)** — [contested.txt:93](corpora/contested.txt:93) · 13 tokens

> Smaller class sizes improve students' long-run academic outcomes.

*Qui l'affirme :* STAR-experiment interpreters (Krueger)  
*Qui le nie :* class-size skeptics (Hanushek)

**Consensuel actuel** — [consensual_v6.txt:93](corpora/consensual_v6.txt:93) · 13 tokens

> Universities award degrees after students complete the required coursework.

**Marqueurs du contesté :** comparatif (`smaller`) · attribution causale (`improve`)

**Marqueurs du consensuel actuel :** 

**À produire :** un énoncé consensuel **comparatif** en `education`, **10–16 tokens gpt2**, respectant les contraintes dures du §1.

### Ligne 95 — `organizational` · super `mind_language_society` — **COMPARATIF requis**

**Contesté (gelé, référence)** — [contested.txt:95](corpora/contested.txt:95) · 16 tokens

> Diverse teams outperform homogeneous ones on complex problem-solving tasks.

*Qui l'affirme :* diversity-bonus proponents (Page-line)  
*Qui le nie :* mixed-evidence skeptics (van Dijk et al. meta)

**Consensuel actuel** — [consensual_v6.txt:95](corpora/consensual_v6.txt:95) · 10 tokens

> Large organizations divide labour into specialized roles and departments.

**Marqueurs du contesté :** comparatif (`outperform`)

**Marqueurs du consensuel actuel :** prép. de mécanisme (`into`)

**À produire :** un énoncé consensuel **comparatif** en `organizational`, **13–16 tokens gpt2**, respectant les contraintes dures du §1.

### Ligne 99 — `public_health` · super `medicine_health` — **COMPARATIF requis**

**Contesté (gelé, référence)** — [contested.txt:99](corpora/contested.txt:99) · 13 tokens

> Cannabis legalization has produced more benefit than harm where adopted.

*Qui l'affirme :* cannabis-legalization proponents (some health economists)  
*Qui le nie :* harm-emphasis researchers

**Consensuel actuel** — [consensual_v6.txt:99](corpora/consensual_v6.txt:99) · 13 tokens

> Seatbelts reduce the risk of death in vehicle collisions.

**Marqueurs du contesté :** comparatif (`more`, `than`)

**Marqueurs du consensuel actuel :** attribution causale (`reduce`)

**À produire :** un énoncé consensuel **comparatif** en `public_health`, **10–16 tokens gpt2**, respectant les contraintes dures du §1.

### Ligne 105 — `psychology` · super `mind_language_society` — **COMPARATIF requis**

**Contesté (gelé, référence)** — [contested.txt:105](corpora/contested.txt:105) · 10 tokens

> Grit predicts achievement better than measured cognitive ability.

*Qui l'affirme :* Duckworth-line grit researchers  
*Qui le nie :* Credé et al. 2017 meta (grit ≈ conscientiousness)

**Consensuel actuel** — [consensual_v6.txt:105](corpora/consensual_v6.txt:105) · 12 tokens

> People recall items from the start and end of lists best.

**Marqueurs du contesté :** comparatif (`better`, `than`) · nom abstrait méta (`cognitive`)

**Marqueurs du consensuel actuel :** 

**À produire :** un énoncé consensuel **comparatif** en `psychology`, **9–13 tokens gpt2**, respectant les contraintes dures du §1.

### Ligne 109 — `history` · super `history_archaeology` — **COMPARATIF requis**

**Contesté (gelé, référence)** — [contested.txt:109](corpora/contested.txt:109) · 13 tokens

> Colonial rule left its territories poorer than they would otherwise be.

*Qui l'affirme :* dependency theory; Acemoglu extractive-institutions  
*Qui le nie :* colonial-legacy revisionists (some economic historians)

**Consensuel actuel** — [consensual_v6.txt:109](corpora/consensual_v6.txt:109) · 12 tokens

> The Berlin Wall divided the city for twenty-eight years.

**Marqueurs du contesté :** comparatif (`poorer than`) · modal/irréalis (`would`)

**Marqueurs du consensuel actuel :** 

**À produire :** un énoncé consensuel **comparatif** en `history`, **10–16 tokens gpt2**, respectant les contraintes dures du §1.

### Ligne 112 — `history` · super `history_archaeology` — **COMPARATIF requis**

**Contesté (gelé, référence)** — [contested.txt:112](corpora/contested.txt:112) · 11 tokens

> Great individuals shape history more than impersonal social forces.

*Qui l'affirme :* "great man" / contingency historians  
*Qui le nie :* structuralists / Annales school (Braudel)

**Consensuel actuel** — [consensual_v6.txt:112](corpora/consensual_v6.txt:112) · 11 tokens

> The Ottoman Empire captured Constantinople in fourteen fifty-three.

**Marqueurs du contesté :** comparatif (`more`, `than`) · nom abstrait méta (`social`)

**Marqueurs du consensuel actuel :** 

**À produire :** un énoncé consensuel **comparatif** en `history`, **9–14 tokens gpt2**, respectant les contraintes dures du §1.

### Ligne 116 — `archaeology` · super `history_archaeology` — **COMPARATIF requis**

**Contesté (gelé, référence)** — [contested.txt:116](corpora/contested.txt:116) · 14 tokens

> Agriculture arose independently in several regions rather than spreading from one.

*Qui l'affirme :* multiple-independent-origins mainstream  
*Qui le nie :* diffusionist holdouts

**Consensuel actuel** — [consensual_v6.txt:116](corpora/consensual_v6.txt:116) · 15 tokens

> Radiocarbon dating estimates the age of once-living organic material.

**Marqueurs du contesté :** comparatif (`rather than`)

**Marqueurs du consensuel actuel :** 

**À produire :** un énoncé consensuel **comparatif** en `archaeology`, **11–16 tokens gpt2**, respectant les contraintes dures du §1.

### Ligne 118 — `history` · super `history_archaeology` — **COMPARATIF requis**

**Contesté (gelé, référence)** — [contested.txt:118](corpora/contested.txt:118) · 14 tokens

> Pre-Columbian America was far more populous than early estimates held.

*Qui l'affirme :* high-counters (Dobyns; Mann, "1491")  
*Qui le nie :* low-counters (Ubelaker-line)

**Consensuel actuel** — [consensual_v6.txt:118](corpora/consensual_v6.txt:118) · 13 tokens

> Ancient Egypt built monumental pyramids as tombs for its rulers.

**Marqueurs du contesté :** comparatif (`more`, `than`) · copule définitionnelle (`was`)

**Marqueurs du consensuel actuel :** 

**À produire :** un énoncé consensuel **comparatif** en `history`, **11–16 tokens gpt2**, respectant les contraintes dures du §1.

### Ligne 119 — `archaeology` · super `history_archaeology` — **COMPARATIF requis**

**Contesté (gelé, référence)** — [contested.txt:119](corpora/contested.txt:119) · 12 tokens

> The Neolithic transition lowered rather than raised human living standards.

*Qui l'affirme :* "worst mistake" bioarchaeology (Diamond-line)  
*Qui le nie :* neutral / positive interpreters of the Neolithic

**Consensuel actuel** — [consensual_v6.txt:119](corpora/consensual_v6.txt:119) · 15 tokens

> Pompeii was buried by the eruption of Mount Vesuvius.

**Marqueurs du contesté :** comparatif (`rather than`) · attribution causale (`raised`)

**Marqueurs du consensuel actuel :** copule définitionnelle (`was`)

**À produire :** un énoncé consensuel **comparatif** en `archaeology`, **9–15 tokens gpt2**, respectant les contraintes dures du §1.

### Ligne 120 — `education` · super `mind_language_society` — **COMPARATIF requis**

**Contesté (gelé, référence)** — [contested.txt:120](corpora/contested.txt:120) · 11 tokens

> Handwriting instruction improves reading acquisition more than typing does.

*Qui l'affirme :* handwriting-benefit researchers (James; Longcamp)  
*Qui le nie :* keyboard-equivalence proponents

**Consensuel actuel** — [consensual_v6.txt:120](corpora/consensual_v6.txt:120) · 13 tokens

> Compulsory schooling laws set a minimum age for leaving education.

**Marqueurs du contesté :** comparatif (`more`, `than`) · attribution causale (`improves`)

**Marqueurs du consensuel actuel :** 

**À produire :** un énoncé consensuel **comparatif** en `education`, **9–14 tokens gpt2**, respectant les contraintes dures du §1.

---

## 4. Lignes exigeant un consensuel NON-COMPARATIF (5)

Le contesté apparié n'est pas comparatif ; le consensuel l'est. Retirer la comparaison sans rendre l'énoncé vide ni changer de domaine.

### Ligne 26 — `economics` · super `econ_policy` — **NON-COMPARATIF requis**

**Contesté (gelé, référence)** — [contested.txt:26](corpora/contested.txt:26) · 11 tokens

> Government deficits crowd out private investment over the long run.

*Qui l'affirme :* neoclassical loanable-funds view  
*Qui le nie :* Keynesians; MMT; Blanchard (r < g)

**Consensuel actuel** — [consensual_v6.txt:26](corpora/consensual_v6.txt:26) · 11 tokens

> Compound interest makes unpaid debt grow faster over time.

**Marqueurs du contesté :** 

**Marqueurs du consensuel actuel :** comparatif (`faster`)

**À produire :** un énoncé consensuel **non-comparatif** en `economics`, **9–14 tokens gpt2**, respectant les contraintes dures du §1.

### Ligne 44 — `epidemiology` · super `medicine_health` — **NON-COMPARATIF requis**

**Contesté (gelé, référence)** — [contested.txt:44](corpora/contested.txt:44) · 12 tokens

> Moderate alcohol consumption provides no health benefit at any dose.

*Qui l'affirme :* Mendelian-randomization / GBD 2018 ("no safe level")  
*Qui le nie :* J-curve epidemiologists (older cardioprotection studies)

**Consensuel actuel** — [consensual_v6.txt:44](corpora/consensual_v6.txt:44) · 12 tokens

> Infectious diseases spread faster in densely populated urban areas.

**Marqueurs du contesté :** négation (`no`)

**Marqueurs du consensuel actuel :** comparatif (`faster`)

**À produire :** un énoncé consensuel **non-comparatif** en `epidemiology`, **9–15 tokens gpt2**, respectant les contraintes dures du §1.

### Ligne 86 — `geoengineering` · super `physical_climate` — **NON-COMPARATIF requis**

**Contesté (gelé, référence)** — [contested.txt:86](corpora/contested.txt:86) · 13 tokens

> Ocean iron fertilization would sequester carbon at a meaningful scale.

*Qui l'affirme :* ocean iron-fertilization proponents  
*Qui le nie :* OIF efficacy skeptics (most ocean scientists)

**Consensuel actuel** — [consensual_v6.txt:86](corpora/consensual_v6.txt:86) · 12 tokens

> Large volcanic eruptions can lower global temperatures for several years.

**Marqueurs du contesté :** modal/irréalis (`would`) · quantif. de portée (`meaningful`)

**Marqueurs du consensuel actuel :** comparatif (`lower`) · modal/irréalis (`can`)

**À produire :** un énoncé consensuel **non-comparatif** en `geoengineering`, **10–16 tokens gpt2**, respectant les contraintes dures du §1.

### Ligne 91 — `psychology` · super `mind_language_society` — **NON-COMPARATIF requis**

**Contesté (gelé, référence)** — [contested.txt:91](corpora/contested.txt:91) · 12 tokens

> Teacher expectations causally shape students' later academic achievement.

*Qui l'affirme :* Pygmalion / expectancy researchers (Rosenthal-line)  
*Qui le nie :* skeptics (Jussim & Harber; expectancy-effect minimizers)

**Consensuel actuel** — [consensual_v6.txt:91](corpora/consensual_v6.txt:91) · 13 tokens

> Practice distributed over time produces better retention than massed practice.

**Marqueurs du contesté :** 

**Marqueurs du consensuel actuel :** comparatif (`better`, `than`)

**À produire :** un énoncé consensuel **non-comparatif** en `psychology`, **9–15 tokens gpt2**, respectant les contraintes dures du §1.

### Ligne 94 — `sociology` · super `mind_language_society` — **NON-COMPARATIF requis**

**Contesté (gelé, référence)** — [contested.txt:94](corpora/contested.txt:94) · 13 tokens

> The neighborhood a child grows up in causally affects adult income.

*Qui l'affirme :* Chetty et al. (Moving to Opportunity; Opportunity Atlas)  
*Qui le nie :* selection-effect skeptics

**Consensuel actuel** — [consensual_v6.txt:94](corpora/consensual_v6.txt:94) · 12 tokens

> Urban populations have grown faster than rural ones since industrialization.

**Marqueurs du contesté :** 

**Marqueurs du consensuel actuel :** comparatif (`faster`, `than`)

**À produire :** un énoncé consensuel **non-comparatif** en `sociology`, **10–16 tokens gpt2**, respectant les contraintes dures du §1.

---

## 5. Lignes déjà conformes — reprise verbatim (79)

Classe de construction déjà appariée. **À recopier sans modification** : toute réécriture ici introduirait de la variance non nécessaire.

Numéros de ligne : 4, 5, 6, 9, 11, 12, 13, 17, 18, 19, 20, 21, 22, 24, 25, 27, 28, 29, 30, 31, 32, 34, 35, 36, 38, 39, 40, 41, 43, 45, 46, 47, 48, 49, 52, 54, 55, 56, 58, 60, 61, 62, 64, 65, 66, 67, 68, 69, 70, 72, 73, 74, 78, 79, 80, 81, 82, 83, 84, 85, 89, 90, 96, 97, 98, 100, 101, 102, 103, 104, 106, 107, 108, 110, 111, 113, 114, 115, 117

---

*Généré par `build_spec_v6_2.py`. Pour régénérer après modification d'un fichier source : `python build_spec_v6_2.py`.*
