# Corpus freeze v6.3

Protocol commit: `22aa2cb`

Round-0 candidate commit: `204f33b`

Round-0 G1 report commit: `87186b8`

Round-1 status at freeze commit `0e4bff0`: **unscored**

## Round 0 retained result

Round 0 is immutable. Its registered G1 result is:

- balanced accuracy: `0.6125`;
- effect-size ceiling: `0.60` — fail;
- one-sided paired permutation p-value: `0.00029997000299970003` — fail;
- permutations: `10000`, seed `20260722`;
- overall verdict: `G1_pass=false`.

No real-model output was read before or during corpus construction.

## Permitted round-1 adaptation

Only the eight frozen marker counts from the failed round were inspected. The
largest round-0 differences were causal attribution (`37` contested versus `18`
consensual), definitional copula (`21` versus `8`), mechanism preposition (`3`
versus `20`), and abstract/meta noun (`15` versus `4`).

Round 1 retains all 120 pair registrations, fine domains, super-domains, and
source pointers. Wording was changed without relaxing factual scope or source
criteria. The result is stricter than G0: every one of the 120 pairs has the
same full eight-marker count vector. Both arms therefore have totals, in frozen
feature order, of `[51, 5, 2, 6, 1, 1, 0, 5]`.

Mechanical checks before observing round-1 G1:

- 120 lines per arm and 120 aligned evidence rows;
- no blanks, exact duplicates, questions, semicolons, or registered hedges;
- 9–16 GPT-2 BPE tokens per sentence;
- maximum paired token gap 3;
- comparative G0 exact in every pair;
- complete eight-marker counts exact in every pair;
- seven unit tests passed before round-1 construction, then the suite expanded
  to nine tests covering pairwise equality and scored-round immutability.

The work container lacked the declared `transformers` dependency. Lengths were
therefore checked with `gpt-3-encoder`, which implements the same GPT-2
vocabulary and BPE merges. The canonical validator remains based on the
repository's declared GPT-2 tokenizer.

## Frozen round-1 hashes

| File | SHA-256 |
|---|---|
| `round1/contested.txt` | `85d795fb3d17e2d2aae8c35d72c59167b43a50f9a03abb2746823a6468b1755c` |
| `round1/consensual.txt` | `eb537ee1577134f5e77fbbcf21978ee7f17ac099d46202506d3ad4f7c6056bf1` |
| `round1/evidence.tsv` | `89250a005863b0c685e78b58c90b6a153df6ea17708ca98ada7abe06a8861770` |
| `corpora/domain_map_v6.json` | `22e93f04d907f036f5679ae8837eb29d3535653686f245c60addaa7b5091019b` |

These hashes are committed before the round-1 G1 score is observed. If round 1
fails, its files and report remain immutable and only round 2 may be constructed.

## Registered round-1 outcome

The immutable report was subsequently committed as `a9cf875`:

- balanced accuracy: `0.5000`;
- effect-size ceiling: `0.60` — pass;
- one-sided paired permutation p-value: `1.0` — pass;
- permutation quantiles (`q025`, `q50`, `q975`): all `0.5000`;
- permutations: `10000`, seed `20260722`;
- overall verdict: `G1_pass=true`.

Round 1 is therefore the first and only eligible v6.3 corpus. Under the frozen
protocol, round 2 is forbidden. This gate establishes only non-separability by
the eight registered markers; it does not certify source truth, equivalence of
the two epistemic classes, or absence of every unregistered lexical cue.
