#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_consensual_v6.py — bras consensuel PAR DOMAINE (v6 / H-D)
================================================================

Construit `corpora/consensual_v6.txt` : 120 enonces consensuels, un par ligne,
tels que **la ligne i porte le meme domaine fin que la ligne i du bras
conteste** (`corpora/contested.txt` + `corpora/contested_anchors.tsv`).

C'est le geste central de v6 : en appariant les domaines DANS chaque fold LODO,
le vocabulaire thematique cesse d'etre un indice exploitable — il ne reste que
le statut epistemique. (v5 opposait des domaines differents ; ce raccourci
restait ouvert, cf. NOTE_RESULTATS_v5 "Limites".)

Deterministe (aucun aleatoire) :
  - les enonces consensuels sont ecrits en dur ci-dessous, par domaine fin,
    avec EXACTEMENT les effectifs du bras conteste ;
  - dans chaque domaine, contestes et consensuels sont tries par longueur en
    tokens gpt2 puis apparies par rang (egalites : index d'origine croissant) ;
    relancer sur les memes entrees redonne le meme fichier.

Ce script est un OUTIL DE CONSTRUCTION DE CORPUS : il ne touche a aucun modele,
ne lit aucun etat cache, ne produit aucun verdict. Il tourne AVANT le gel v6.

Usage :
    python build_consensual_v6.py
"""

import json
from collections import Counter, defaultdict
from pathlib import Path

from transformers import AutoTokenizer

CONTESTED = Path("corpora/contested.txt")
ANCHORS = Path("corpora/contested_anchors.tsv")
OUT_TXT = Path("corpora/consensual_v6.txt")
OUT_REPORT = Path("corpora/matching_report_v6.json")
OUT_DOMAINS = Path("corpora/domain_map_v6.json")

TOKENIZERS = ["gpt2", "EleutherAI/pythia-410m", "facebook/opt-350m",
              "bigscience/bloom-560m"]

# --------------------------------------------------------------------------- #
# Regroupement en super-domaines (folds LODO) : chacun n >= 12 par bras.
# --------------------------------------------------------------------------- #
SUPER = {
    "econ_policy": ["economics", "health_econ", "political_science"],
    "ai_computing": ["ai", "ai_safety", "privacy"],
    "medicine_health": ["medicine", "nutrition", "public_health", "epidemiology"],
    "mind_language_society": ["psychology", "sociology", "education",
                              "organizational", "criminology", "linguistics"],
    "history_archaeology": ["history", "archaeology"],
    "physical_climate": ["physics", "cosmology", "astrobiology", "energy",
                         "climate", "geoengineering"],
    "life_sciences": ["biology", "genetics", "genomics", "evolution",
                      "neuroscience", "behavioral_genetics", "microbiome",
                      "agriculture", "environment", "conservation"],
}

# --------------------------------------------------------------------------- #
# Enonces CONSENSUELS par domaine fin (faits etablis, meme registre declaratif
# empirique que le bras conteste ; anglais, sans hedge, 9-16 tokens gpt2).
# --------------------------------------------------------------------------- #
CONSENSUAL = {
    "economics": [
        "Inflation reduces the purchasing power of money held as cash.",
        "Trade barriers raise the domestic price of imported goods.",
        "Compound interest makes unpaid debt grow faster over time.",
        "Central banks raise interest rates to slow rapid price increases.",
        "Unemployment rises during recessions in most modern economies.",
        "Insurance markets pool risk across many policyholders to reduce variance.",
        "Gross domestic product measures the value of goods and services produced.",
        "Diversifying investments across assets reduces the variance of returns.",
        "Scarcity forces every economy to allocate limited resources among competing uses.",
        "Hyperinflation destroys the value of a currency within months.",
        "A progressive income tax takes a larger share from higher earners.",
        "Supply chains connect producers and consumers across many countries.",
        "Bankruptcy law lets insolvent firms restructure or discharge their debts.",
        "Exchange rates determine how much foreign currency a payment buys.",
        "Depreciation reduces the recorded book value of capital equipment.",
        "Labor productivity measures the output produced per hour worked.",
        "Government budgets record planned public revenue and public spending.",
        "Stock exchanges let shareholders trade partial ownership of listed companies.",
        "Subsidies lower the price that buyers pay below production cost.",
        "Interest compensates lenders for postponing their own consumption.",
    ],
    "health_econ": [
        "Health insurance spreads medical costs across a pool of members.",
    ],
    "political_science": [
        "A constitution defines the basic legal structure of a state.",
        "Secret ballots let voters cast their choices without disclosing them.",
        "Federal states divide powers between national and regional governments.",
        "Universal suffrage extends voting rights to all adult citizens.",
        "Parliaments pass legislation through recorded votes of their members.",
        "Diplomatic embassies represent one state within the territory of another.",
    ],
    "ai": [
        "Transformers process input sequences using self-attention over token embeddings.",
        "Neural networks are trained by minimizing a loss with gradient descent.",
        "Tokenizers split text into discrete units before a model processes it.",
        "Backpropagation computes gradients by applying the chain rule backwards.",
        "Overfitting occurs when a model memorizes noise in its training data.",
        "Graphics processors accelerate training through massively parallel matrix operations.",
        "A softmax function converts real-valued scores into a probability distribution.",
        "Convolutional networks apply the same learned filters across spatial positions.",
        "Language models predict the next token given the preceding context.",
        "Regularization constrains model parameters to improve generalization beyond training data.",
        "Cross-validation estimates performance by holding out parts of the data.",
        "Embeddings represent discrete symbols as vectors in a continuous space.",
        "Floating-point arithmetic introduces small rounding errors into every computation.",
    ],
    "ai_safety": [
        "Software systems are tested before deployment to reduce operational failures.",
    ],
    "privacy": [
        "Encryption makes intercepted messages unreadable without the decryption key.",
    ],
    "medicine": [
        "Antibiotics treat bacterial infections but have no effect on viruses.",
        "Vaccines train the immune system by presenting harmless antigens.",
        "The heart pumps blood through arteries to the body's tissues.",
        "Insulin lowers the concentration of glucose in the bloodstream.",
        "Smoking tobacco substantially increases the risk of lung cancer.",
        "Blood transfusions require compatibility between donor and recipient blood types.",
        "Anaesthesia allows surgery to proceed without the patient feeling pain.",
        "The liver metabolizes many drugs before they reach general circulation.",
    ],
    "nutrition": [
        "The human body cannot synthesize the essential amino acids itself.",
        "Vitamin C deficiency causes the disease known as scurvy.",
    ],
    "public_health": [
        "Clean drinking water reduces the transmission of intestinal disease.",
        "Seatbelts reduce the risk of death in vehicle collisions.",
        "Handwashing lowers the spread of infectious disease in hospitals.",
    ],
    "epidemiology": [
        "Infectious diseases spread faster in densely populated urban areas.",
        "Randomized controlled trials assign participants to treatment groups by chance.",
    ],
    "psychology": [
        "Working memory holds a limited amount of information for seconds.",
        "Classical conditioning pairs a neutral stimulus with a meaningful one.",
        "Sleep deprivation impairs attention and reaction time in laboratory tasks.",
        "The retina sends visual signals to the brain through the optic nerve.",
        "Children acquire their first language without explicit formal instruction.",
        "Long-term memories consolidate over hours and days after learning.",
        "Stress activates the release of cortisol from the adrenal glands.",
        "People recall items from the start and end of lists best.",
        "Human colour vision depends on three types of retinal cone cells.",
        "Practice distributed over time produces better retention than massed practice.",
    ],
    "sociology": [
        "Urban populations have grown faster than rural ones since industrialization.",
        "Census surveys collect demographic data about a national population.",
    ],
    "education": [
        "Literacy rates rose across the world during the twentieth century.",
        "Spaced repetition improves long-term retention of memorized material.",
        "Compulsory schooling laws set a minimum age for leaving education.",
        "Learning to read requires mapping written symbols onto spoken sounds.",
        "Universities award degrees after students complete the required coursework.",
    ],
    "organizational": [
        "Large organizations divide labour into specialized roles and departments.",
    ],
    "criminology": [
        "Police forces record reported offences in official crime statistics.",
    ],
    "linguistics": [
        "Every known human language has both consonants and vowels.",
        "Written scripts developed thousands of years after spoken language.",
        "Languages change across generations in pronunciation and in vocabulary.",
    ],
    "history": [
        "The Roman Republic preceded the Roman Empire in political order.",
        "The printing press spread through Europe during the fifteenth century.",
        "The French Revolution began in seventeen eighty-nine.",
        "The Second World War ended in nineteen forty-five.",
        "Ancient Egypt built monumental pyramids as tombs for its rulers.",
        "The Berlin Wall divided the city for twenty-eight years.",
        "Christopher Columbus crossed the Atlantic under the Spanish crown.",
        "The Ottoman Empire captured Constantinople in fourteen fifty-three.",
        "Napoleon was finally defeated at the battle of Waterloo.",
        "The Industrial Revolution introduced steam power to manufacturing.",
    ],
    "archaeology": [
        "Radiocarbon dating estimates the age of once-living organic material.",
        "Stone tools appear in the archaeological record before metal ones.",
        "Pompeii was buried by the eruption of Mount Vesuvius.",
    ],
    "physics": [
        "Light travels faster through a vacuum than through glass or water.",
        "Energy is conserved in any closed physical system.",
        "Objects in free fall accelerate at the same rate regardless of mass.",
        "Electric current flows when charge carriers move through a conductor.",
        "The entropy of an isolated system does not decrease over time.",
        "Sound requires a material medium and cannot travel through vacuum.",
    ],
    "cosmology": [
        "The observable universe has been expanding since the Big Bang.",
        "Stars generate energy by fusing hydrogen nuclei into helium.",
    ],
    "astrobiology": [
        "Liquid water is required by all known forms of life.",
    ],
    "energy": [
        "Solar panels convert sunlight into electricity through the photovoltaic effect.",
        "Hydroelectric dams generate power from the movement of falling water.",
    ],
    "climate": [
        "Carbon dioxide absorbs and re-emits infrared radiation in the atmosphere.",
        "Global average surface temperatures have risen since the industrial era.",
        "Melting land ice raises the global mean sea level.",
        "Burning fossil fuels releases carbon dioxide into the atmosphere.",
    ],
    "geoengineering": [
        "Large volcanic eruptions can lower global temperatures for several years.",
    ],
    "biology": [
        "DNA carries genetic information in sequences of four nucleotide bases.",
        "Photosynthesis converts light energy into chemical energy in plants.",
    ],
    "genetics": [
        "Offspring inherit one copy of each chromosome from each parent.",
    ],
    "genomics": [
        "The human genome contains roughly three billion base pairs.",
    ],
    "evolution": [
        "Natural selection favours heritable traits that improve reproductive success.",
    ],
    "neuroscience": [
        "Neurons transmit signals through electrical impulses and chemical synapses.",
        "The cerebellum contributes to the coordination of voluntary movement.",
    ],
    "behavioral_genetics": [
        "Identical twins share nearly all of their nuclear DNA.",
    ],
    "microbiome": [
        "The human gut hosts trillions of bacterial cells.",
    ],
    "agriculture": [
        "Crop rotation helps maintain the fertility of farmland soil.",
    ],
    "environment": [
        "Plastic waste decomposes very slowly in the natural environment.",
    ],
    "conservation": [
        "Habitat destruction is a leading cause of species extinction.",
    ],
}


def main():
    contested = [l.strip() for l in CONTESTED.read_text(encoding="utf-8").splitlines()
                 if l.strip()]
    rows = [l.split("\t") for l in ANCHORS.read_text(encoding="utf-8").splitlines()[1:]]
    domains = [r[1] for r in rows]
    assert len(contested) == len(domains) == 120, "corpus/anchors desalignes"

    # 1) effectifs identiques par domaine fin
    need, have = Counter(domains), {d: len(v) for d, v in CONSENSUAL.items()}
    for d, n in need.items():
        if have.get(d, 0) != n:
            raise SystemExit(f"domaine '{d}': {have.get(d,0)} consensuels ecrits, {n} attendus")
    extra = set(CONSENSUAL) - set(need)
    if extra:
        raise SystemExit(f"domaines consensuels sans contrepartie contestee: {sorted(extra)}")

    # 2) super-domaines : couverture et n >= 12
    fine2super = {f: s for s, fs in SUPER.items() for f in fs}
    missing = sorted(set(domains) - set(fine2super))
    if missing:
        raise SystemExit(f"domaines fins non ranges en super-domaine: {missing}")
    super_counts = Counter(fine2super[d] for d in domains)
    for s, n in super_counts.items():
        if n < 12:
            raise SystemExit(f"super-domaine '{s}': n={n} < 12 (fold LODO trop petit)")

    tok = AutoTokenizer.from_pretrained("gpt2")
    n_tok = lambda s: len(tok.encode(s))

    # 3) appariement par rang de longueur, DANS chaque domaine fin (deterministe)
    by_domain = defaultdict(list)
    for i, d in enumerate(domains):
        by_domain[d].append(i)
    out = [None] * 120
    for d, idxs in by_domain.items():
        c_sorted = sorted(idxs, key=lambda i: (n_tok(contested[i]), i))
        s_sorted = sorted(CONSENSUAL[d], key=lambda s: (n_tok(s), s))
        for slot, claim in zip(c_sorted, s_sorted):
            out[slot] = claim
    assert all(out), "trous dans l'appariement"

    OUT_TXT.write_text("\n".join(out) + "\n", encoding="utf-8")

    # 4) rapport : deltas par paire, par domaine, et controle multi-tokenizers
    deltas = [n_tok(out[i]) - n_tok(contested[i]) for i in range(120)]
    lens_c = [n_tok(c) for c in contested]
    lens_s = [n_tok(s) for s in out]
    out_of_range = [i + 1 for i, l in enumerate(lens_s) if not (9 <= l <= 16)]
    per_super = {}
    for s in SUPER:
        idx = [i for i, d in enumerate(domains) if fine2super[d] == s]
        per_super[s] = {
            "n": len(idx),
            "mean_delta_tokens": round(sum(deltas[i] for i in idx) / len(idx), 3),
            "max_abs_delta": max(abs(deltas[i]) for i in idx),
        }
    cross = {}
    for name in TOKENIZERS:
        t = AutoTokenizer.from_pretrained(name)
        dc = [len(t.encode(contested[i])) for i in range(120)]
        ds = [len(t.encode(out[i])) for i in range(120)]
        d = sorted(ds[i] - dc[i] for i in range(120))
        cross[name] = {"median_gap": d[60], "mean_gap": round(sum(d) / 120, 3)}

    report = {
        "schema_version": "matching_report_v6.0",
        "purpose": "bras consensuel apparie PAR DOMAINE au bras conteste (ligne a ligne)",
        "method": "meme domaine fin ligne par ligne ; appariement par rang de longueur "
                  "gpt2 dans chaque domaine ; egalites par index/texte croissant",
        "n_per_arm": 120,
        "n_fine_domains": len(need),
        "n_super_domains": len(SUPER),
        "pair_delta_tokens": {
            "mean": round(sum(deltas) / 120, 3),
            "max_abs": max(abs(d) for d in deltas),
            "n_exact": sum(1 for d in deltas if d == 0),
        },
        "gpt2_lengths": {
            "contested": {"min": min(lens_c), "median": sorted(lens_c)[60], "max": max(lens_c)},
            "consensual": {"min": min(lens_s), "median": sorted(lens_s)[60], "max": max(lens_s)},
        },
        "out_of_range_9_16": out_of_range,
        "per_super_domain": per_super,
        "cross_tokenizer_gap": cross,
    }
    OUT_REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")

    OUT_DOMAINS.write_text(json.dumps({
        "schema_version": "domain_map_v6.0",
        "note": "la ligne i des DEUX bras porte le meme domaine fin ; folds LODO = super-domaines",
        "fine_to_super": fine2super,
        "per_line_fine_domain": domains,
        "super_domain_counts_per_arm": dict(super_counts),
    }, indent=2), encoding="utf-8")

    print(f"[v6] ecrit {OUT_TXT} ({len(out)} enonces)")
    print(f"[v6] delta longueur par paire: moyenne={report['pair_delta_tokens']['mean']} "
          f"max|d|={report['pair_delta_tokens']['max_abs']} "
          f"exactes={report['pair_delta_tokens']['n_exact']}/120")
    print(f"[v6] hors 9-16 tokens: {out_of_range or 'aucun'}")
    print(f"[v6] super-domaines: { {s: v['n'] for s, v in per_super.items()} }")
    for name, v in cross.items():
        print(f"[v6] {name:<28} ecart median={v['median_gap']:+} moyen={v['mean_gap']:+}")


if __name__ == "__main__":
    main()
