# Instructions à soumettre aux modèles — bras consensuel apparié par sujet

## Pour toi, Simon (mode d'emploi — ne pas envoyer aux modèles)

1. Copie **tout le bloc entre les deux lignes `═══`** ci-dessous, puis colle à la
   fin la liste des phrases contestées (fichier
   `_remaining_contested.txt`, dans ce même dossier). Le prompt est autonome :
   il ne suppose aucun contexte.
2. Soumets-le tel quel à **plusieurs modèles différents** (3 à 5 : un Claude, un
   GPT, un Gemini, un Llama… la diversité est le but). **Une liste par modèle.**
3. Récupère chaque sortie brute — copie-colle dans un fichier texte, un par
   modèle, peu importe le format exact tant que les blocs `[numéro]` sont
   lisibles. Dépose-les dans ce dossier.
4. Je passerai **chaque candidate au crible mécanique** (recouvrement de sujet,
   longueur en tokens gpt2, classe de construction, absence de hedge, réalité de
   la non-contestation) et je **piocherai la meilleure par ligne**. Les lignes où
   rien ne passe partiront pour un second tour.

Tu n'as **rien à vérifier toi-même** — soumets, récupère, dépose. Le tri est mon
travail.

> Note de méthode : le prompt demande **une** partenaire par phrase. La variété
> vient des différents modèles, pas de variantes multiples — ça garde les
> sorties propres à parser. Chaque ligne est déjà étiquetée `[COMPARATIVE]` ou
> `[PLAIN]` : le modèle n'a pas à deviner la forme requise.

---

═══════════════════════════════════════════════════════════════════════════════

# TASK: write one "consensual" partner sentence for each "contested" sentence

You are helping assemble a set of matched sentence pairs. Every pair has:

- a **CONTESTED** sentence — a factual claim that domain specialists **actively
  disagree about** (given to you, do not change it);
- a **CONSENSUAL** sentence — a plain statement that essentially **no specialist
  disputes** (you write it).

The two sentences of a pair must be **about the same subject** and differ **only**
in whether experts disagree. Your job: for each contested sentence in the list at
the end, write exactly one consensual partner.

## The pattern to follow

The consensual sentence states the **established fact right next to** the
contested claim — usually the accepted step *underneath* the disputed conclusion,
about the very same things. Same subject, same vocabulary, same sentence shape.

Worked examples (contested → consensual):

- *Population-wide salt reduction lowers cardiovascular risk.*
  → *Population-wide salt reduction lowers average measured blood pressure.*
  (the blood-pressure effect is settled; the cardiovascular outcome is disputed)

- *Genetic differences explain most adult variation in measured intelligence.*
  → *Genetic differences explain most adult variation in measured human height.*
  (height heritability is undisputed; intelligence heritability is the live dispute)

- *Undiscovered particles explain dark matter rather than modified gravity.*
  → *Galaxy rotation curves stay flatter than visible mass alone would predict.*
  (the rotation-curve observation is settled; its explanation is disputed)

- *The Roman Empire fell chiefly from internal decay.*
  → *The Western Roman Empire ended while the Eastern Roman Empire endured.*
  (the chronology is settled; the cause of the fall is disputed)

## Rules — every one is mandatory

**R1. Same subject (most important).** The consensual sentence must be about the
same topic and the same entities as its contested sentence, and must **reuse at
least two important content words** from it (a key noun, a named thing, a field
term). A sentence about a different topic is rejected, even if true.

**R2. Reuse a distinctive word when present.** If the contested sentence uses an
unusual word (for example *chiefly, materially, causally, explains, rather,
primarily, outweighing*), reuse **that same word** in your consensual sentence
whenever it fits naturally. This keeps the two sides sharing vocabulary.

**R3. Genuinely uncontested.** The consensual sentence must state something
established that essentially no informed specialist disputes. It must be a
**different, adjacent fact — NOT the contested claim softened.** Adding a hedge to
the contested claim is the most common mistake and is always rejected.

**R4. Same shape.** Each contested sentence is tagged **[COMPARATIVE]** or
**[PLAIN]**.
- `[COMPARATIVE]` → your sentence must make a comparison (use *more, less, faster,
  larger, better, worse, longer, "…-er than", "rather than", "than"*).
- `[PLAIN]` → your sentence must make **no** comparison.

**R5. Length.** Between **9 and 16 words**. Try to stay within 3 words of the
contested sentence.

**R6. No hedging, ever.** Never use *may, might, could, possibly, perhaps, likely,
tends to, appears to, seems to, is thought to, some studies suggest*. State the
fact flatly.

**R7. Facts only.** No value judgments, no predictions of the future, no political
opinion. Plain empirical or definitional statements. English, one declarative
sentence, ending in a period. No questions, no semicolons.

## Rejected examples — learn the traps

- Contested: *Salt reduction lowers cardiovascular risk.*
  ✗ *Salt reduction may lower cardiovascular risk.* — softened claim + hedge (R3, R6).
- Contested: *Heavy platform use is a risk for adolescent depression.*
  ✗ *Human colour vision depends on three cone types.* — different subject (R1).
- ✗ *Some materials conduct heat better than others.* — empty comparison, no real content.
- ✗ *Nuclear power is safer than coal power.* — this is itself disputed, not consensual.
- ✗ *Free markets are the fairest economic system.* — value judgment (R7).

## Output format — one block per contested sentence

```
[<line number>]
CONSENSUAL: <your single sentence>
SHARED: <the content words you reused from the contested sentence>
WHY: <one short clause — the established fact this is, and why it is not the contested claim>
```

Do not echo the contested sentence back. Keep the same order as the list. If you
truly cannot write a valid partner for a line, output `[<number>] SKIP` and move
on — do not force a bad one.

## The contested sentences

*(Simon: colle ici le contenu de `_remaining_contested.txt`.)*

═══════════════════════════════════════════════════════════════════════════════

---

## Rappel de la décision en attente (pour toi, pas pour les modèles)

Ces 94 phrases contestées viennent du bras **v6.3** (celui de la nuit dernière,
dont les sources ont été auditées). C'est cohérent avec les 26 paires que j'ai
déjà écrites. Si tu préfères ancrer plutôt sur le bras **contesté gelé v5/v6**,
dis-le-moi et je régénère la liste — c'est une ligne de commande, pas un
chantier. En l'état, on continue sur v6.3.
