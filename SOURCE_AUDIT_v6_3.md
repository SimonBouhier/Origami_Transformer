# Source audit v6.3 — round 0

Date: 2026-07-22

Protocol: researcher choices 1A (strict gate) and 2A (rebuild both arms)

Scoring state during this audit: **G1 unobserved**

## Audit question

This audit asks whether every row is fit for corpus construction, not whether the
contested claim is true. A contested row passes only when its proposition is
truth-apt, specialist-facing, bounded enough to evaluate, and connected to a
source that exposes an active empirical, causal, theoretical, or historiographic
disagreement. A consensual row passes only when an authoritative source supports
the proposition at the stated scope.

The audit does **not** require the two sides of a controversy to have equal
evidential weight. It also does not turn a source pointer into an independent
replication of the underlying research.

## Method

1. Align all 120 pairs against `domain_map_v6.json` and the named specialist
   constituencies in `contested_anchors.tsv`.
2. Inspect source identity using the landing-page title and, where available,
   abstract or executive summary. DOI, PMID, PMCID, NBER, AEA, and publisher
   metadata were preferred over secondary descriptions.
3. Compare the source's population, intervention or exposure, outcome, causal
   strength, time frame, and comparator with the exact sentence.
4. Reject public-value disputes, predictions, settled falsehoods, and sources
   that support only a neighboring topic.
5. Re-run alignment, punctuation, duplicate, hedge, comparative G0, and exact
   GPT-2 token-length checks after every wording change.

## Material defects found and repaired

| Line | Defect in the pre-audit candidate | Repair in round 0 |
|---:|---|---|
| 5 | PMID 25787902 concerned radiation dose monitoring, not salt reduction. | Replaced with two sodium/CVD reviews that explicitly describe the population-wide and J-curve controversy. |
| 21 | The China-shock paper covered concentrated worker losses but not the aggregate-gain side. | Narrowed the claim to average real wages and paired aggregate/consumer-gain and local-labor-loss sources. |
| 24 | The QJE DOI was malformed and did not resolve. | Replaced it with the correct Borjas DOI and a Peri review of competing wage evidence. |
| 29 | “Most effective way” was a policy ranking not identified by Dollar and Kraay. | Replaced it with their proportionate-income-growth proposition and a Ravallion heterogeneity critique. |
| 37 | “Integrated information rather than specific circuits” did not match the preregistered adversarial predictions. | Recast as posterior cortical activity versus prefrontal broadcasting. |
| 43 | “Mostly explained by genetics” omitted age, phenotype, and variance scope. | Restricted it to adult variation in measured intelligence and added a malleability/interpretation review. |
| 51 | The original pointer covered only the new-physics interpretation. | Added an independent distance-ladder analysis that does not require new physics. |
| 64 | PMID 31554670 concerned autoimmune autonomic neuropathy, not social media. | Replaced it with adolescent high-exposure and mixed-evidence reviews; changed “major cause of mental illness” to a substantial depression risk factor. |
| 87 | “Biodiversity versus sustainable use” exceeded the protected-area studies' comparator and outcome. | Restricted the proposition to tropical forest fires in strict versus multiple-use reserves. |
| 91 | A narrative review alone could not identify a causal expectancy effect. | Restricted the claim to induced expectations and added the synthesis of 18 experiments. |
| 92 | The MTO source did not compare neighborhood and school mediation. | Recast the row around substantial adult-earnings differences, separated magnitude from the causal-existence claim at line 94, and added a critical review. |
| 109 | “Colonial rule left its territories poorer” universalized a specific institutions design. | Restricted the claim to extractive versus inclusive colonial institutions and added the published instrument critique. |
| 113 | The original archive page listed documents but did not establish causal primacy. | Paired an internal-Soviet-weakness interpretation with a leadership-and-diplomacy counterinterpretation. |
| 114 | DOI 10.1162/qjec.2008.123.1.139 is Nunn's slave-trade paper, not the asserted European-growth comparison. | Replaced it with Atlantic-trade growth estimates and O'Brien's smaller-periphery-contribution estimate. |
| 116 | DOI 10.1126/science.aag2624 concerned belief-network dynamics, not American migration. | Replaced it with the Pacific-route review and the published route-viability exchange. |
| 119 | The Larsen review documented health decline, not a live claim about total living standards. | Replaced it with the directly disputed productivity explanation for the spread of early farming. |

## Result before G1

- 120 contested rows aligned with 120 named specialist oppositions and audit
  pointers in `evidence.tsv`.
- 120 consensual rows aligned with authoritative or primary audit pointers.
- No question, hedge, exact duplicate, blank line, or missing terminal period.
- Every sentence is 9–16 GPT-2 tokens; every paired gap is at most 3 tokens.
- Comparative-marker presence is identical within every pair (G0).
- G1 remained unobserved until the source-audited candidate and its validator
  were frozen in Git.

## Residual epistemic limits

“Pass” here means source identity and claim scope are coherent enough for the
registered adversarial construction rule. It is not a 100% guarantee that every
specialist would choose the same boundary, especially for historical causation,
social-media effect magnitude, intelligence heritability, or theory-laden physics.
Those are retained precisely because the disagreement is specialist and active;
the manifest makes the chosen boundary and opposing constituencies inspectable.
