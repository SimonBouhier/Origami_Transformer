#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_consensual_subset.py — appariement du bras consensuel (v5)
================================================================

Selectionne un sous-ensemble de claims.txt (220 enonces factuels, 11 domaines
x 20) apparie en LONGUEUR au bras conteste (corpora/contested.txt), avec un
plafond par domaine pour garantir l'etalement.

Deterministe (aucun aleatoire) : appariement glouton, les longueurs les plus
extremes d'abord, egalites tranchees par l'index d'origine le plus bas. Relancer
le script sur les memes entrees redonne exactement le meme fichier.

Ce script est un OUTIL DE CONSTRUCTION DE CORPUS, pas un instrument de mesure :
il ne touche a aucun modele, ne lit aucun etat cache, ne produit aucun verdict.
Il tourne AVANT le gel v5 ; ses sorties (corpora/consensual.txt + le rapport)
sont committees avec PREREGISTRATION_v5.md au moment du gel.

Note sur le tokenizer : l'appariement se fait sur les tokens gpt2 (un des quatre
modeles). Le rapport verifie que l'appariement tient aussi pour les tokenizers
des trois autres modeles — c'est le controle qui compte, gpt2 n'etant qu'un proxy.

Usage :
    python build_consensual_subset.py
"""

import json
from pathlib import Path

import numpy as np
from transformers import AutoTokenizer

CLAIMS = Path("claims.txt")
CONTESTED = Path("corpora/contested.txt")
OUT_TXT = Path("corpora/consensual.txt")
OUT_REPORT = Path("corpora/matching_report.json")

# claims.txt : 11 domaines x 20 enonces, dans cet ordre (lignes 1-based).
DOMAINS = ["physics", "chemistry", "biology", "mathematics", "computer_science",
           "astronomy", "earth_science", "history", "economics", "arts", "everyday"]
DOMAIN_CAP = 12          # plafond par domaine (11 x 12 = 132 >= 120 : de la marge)

MODELS = ["gpt2", "EleutherAI/pythia-410m", "facebook/opt-350m",
          "bigscience/bloom-560m"]


def read_lines(p: Path) -> list[str]:
    return [l.strip() for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


def token_lengths(tok, lines: list[str]) -> np.ndarray:
    return np.array([len(tok(l)["input_ids"]) for l in lines], dtype=int)


def describe(x: np.ndarray) -> dict:
    return {"n": int(x.size), "min": int(x.min()), "p10": float(np.percentile(x, 10)),
            "median": float(np.median(x)), "mean": round(float(x.mean()), 2),
            "p90": float(np.percentile(x, 90)), "max": int(x.max())}


def main():
    claims = read_lines(CLAIMS)
    contested = read_lines(CONTESTED)
    assert len(claims) == 220, f"claims.txt: {len(claims)} lignes, attendu 220"
    n_target = len(contested)

    tok = AutoTokenizer.from_pretrained("gpt2")
    len_claims = token_lengths(tok, claims)
    len_cont = token_lengths(tok, contested)

    domain_of = [DOMAINS[i // 20] for i in range(len(claims))]

    # --- appariement glouton, deterministe -------------------------------- #
    # On traite les enonces contestes du plus atypique au plus median : les
    # longueurs extremes ont le moins de partenaires disponibles.
    med = np.median(len_cont)
    order = sorted(range(n_target),
                   key=lambda i: (-abs(len_cont[i] - med), i))

    used = set()
    per_domain: dict[str, int] = {d: 0 for d in DOMAINS}
    pairs = []
    for ci in order:
        target = len_cont[ci]
        best, best_key = None, None
        for j in range(len(claims)):
            if j in used or per_domain[domain_of[j]] >= DOMAIN_CAP:
                continue
            key = (abs(int(len_claims[j]) - int(target)), per_domain[domain_of[j]], j)
            if best_key is None or key < best_key:
                best, best_key = j, key
        if best is None:
            raise RuntimeError("plus de candidat disponible sous le plafond de domaine")
        used.add(best)
        per_domain[domain_of[best]] += 1
        pairs.append({"contested_line": ci + 1, "consensual_claims_line": best + 1,
                      "len_contested": int(target), "len_consensual": int(len_claims[best]),
                      "delta": int(abs(int(len_claims[best]) - int(target))),
                      "domain": domain_of[best]})

    sel = sorted(used)                     # ordre d'origine de claims.txt
    OUT_TXT.parent.mkdir(parents=True, exist_ok=True)
    OUT_TXT.write_text("\n".join(claims[j] for j in sel) + "\n", encoding="utf-8")

    # --- rapport ---------------------------------------------------------- #
    len_sel = len_claims[sel]
    deltas = np.array([p["delta"] for p in pairs])

    per_model = {}
    for m in MODELS:
        t = AutoTokenizer.from_pretrained(m)
        lc = token_lengths(t, contested)
        ls = token_lengths(t, [claims[j] for j in sel])
        per_model[m] = {
            "contested": describe(lc),
            "consensual": describe(ls),
            "median_gap": float(np.median(lc) - np.median(ls)),
            "mean_gap": round(float(lc.mean() - ls.mean()), 3),
        }

    report = {
        "schema_version": "matching_report_v5.0",
        "purpose": "appariement en longueur du bras consensuel sur le bras conteste",
        "method": "glouton deterministe sur tokens gpt2, extremes d'abord, "
                  f"plafond {DOMAIN_CAP}/domaine, egalites par index d'origine",
        "n_per_arm": n_target,
        "matching_tokenizer": "gpt2",
        "pair_delta_tokens": {"mean": round(float(deltas.mean()), 3),
                              "max": int(deltas.max()),
                              "n_exact": int((deltas == 0).sum())},
        "gpt2_lengths": {"contested": describe(len_cont), "consensual": describe(len_sel)},
        "per_model_lengths": per_model,
        "consensual_domain_spread": per_domain,
        "consensual_claims_lines": [j + 1 for j in sel],
        "pairs": sorted(pairs, key=lambda p: p["contested_line"]),
        "known_limitation": "les DOMAINES ne sont pas apparies et ne peuvent pas l'etre: "
                            "le bras conteste porte sur l'ethique/politique/science non "
                            "tranchee, le consensuel sur des faits etablis. C'est l'axe "
                            "teste, pas un defaut d'appariement. Le confound de vocabulaire "
                            "qui en decoule est precisement ce que O2 (surface) et O3 "
                            "(shuffle) sont la pour attraper.",
    }
    OUT_REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"[match] ecrit {OUT_TXT} ({len(sel)} enonces)")
    print(f"[match] delta de longueur par paire: moyenne={deltas.mean():.3f} "
          f"max={deltas.max()} exactes={int((deltas == 0).sum())}/{n_target}")
    print(f"[match] gpt2  conteste : {describe(len_cont)}")
    print(f"[match] gpt2  consensuel: {describe(len_sel)}")
    print(f"[match] etalement domaines: {per_domain}")
    for m, d in per_model.items():
        print(f"[match] {m:<26} ecart median={d['median_gap']:+.1f} "
              f"moyen={d['mean_gap']:+.2f} tokens")
    print(f"[match] ecrit {OUT_REPORT}")


if __name__ == "__main__":
    main()
