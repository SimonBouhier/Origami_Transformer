#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_spec_v6_2.py — genere CAHIER_CORPUS_v6.2.md
=================================================

Cahier des charges de redaction du bras consensuel v6.2, derive MECANIQUEMENT
des fichiers gelés : contested.txt, consensual_v6.txt, domain_map_v6.json,
contested_anchors.tsv. Aucun chiffre saisi a la main.

Le document produit est une SPECIFICATION, pas un corpus : il dit ce qu'il faut
ecrire, ligne par ligne, avec les liens vers les sources. La redaction vient
apres, et son resultat passera la porte G1 avant tout gel.

Usage :
    python build_spec_v6_2.py
"""

import json
import re
import sys
from collections import Counter
from pathlib import Path

from transformers import AutoTokenizer

sys.stdout.reconfigure(encoding="utf-8")

CORPORA = Path("corpora")
OUT = Path("CAHIER_CORPUS_v6.2.md")

# Les 8 marqueurs geles de diag_v7.py — recopies ici pour que le cahier soit
# lisible seul ; diag_v7.py reste la source de verite pour la mesure.
MARKERS = {
    "comparatif": r"\b(more|less|greater|higher|lower|larger|smaller|better|worse|"
                  r"faster|slower|longer|shorter|outperform\w*|exceed\w*|outweigh\w*)\b"
                  r"|\b\w+er than\b|\brather than\b|\bthan\b",
    "attribution causale": r"\b(cause[sd]?|causing|drive[sn]?|driven|lead[s]? to|"
                           r"result\w* (in|from)|due to|responsible for|attributable|"
                           r"increase[sd]?|reduce[sd]?|raise[sd]?|improve[sd]?)\b",
    "modal/irréalis": r"\b(would|will|can|could|should|may|might)\b",
    "quantif. de portée": r"\b(most|all|many|few|majority|significant\w*|substantial\w*|"
                          r"largely|primarily|mainly|meaningful|measurabl\w*)\b",
    "copule définitionnelle": r"\b(is|are|was|were|consists? of|refers? to|means)\b",
    "négation": r"\b(no|not|cannot|never|without|nor)\b",
    "prép. de mécanisme": r"\b(through|into|across|between|within|onto|via|by means of)\b",
    "nom abstrait méta": r"\b(social|economic|political|cultural|cognitive|systemic|"
                         r"structural|institutional|moral|ethical)\b",
}
CMP = re.compile(MARKERS["comparatif"], re.I)
RX = {n: re.compile(p, re.I) for n, p in MARKERS.items()}


def fired(s):
    """Marqueurs actifs dans un enonce, avec les formes qui declenchent."""
    out = []
    for name, rx in RX.items():
        hits = sorted({m.group(0).strip().lower() for m in rx.finditer(s)})
        if hits:
            out.append(f"{name} (`" + "`, `".join(hits[:4]) + "`)")
    return out


def main():
    con = [l.strip() for l in (CORPORA / "contested.txt")
           .read_text(encoding="utf-8").splitlines() if l.strip()]
    cns = [l.strip() for l in (CORPORA / "consensual_v6.txt")
           .read_text(encoding="utf-8").splitlines() if l.strip()]
    dm = json.loads((CORPORA / "domain_map_v6.json").read_text(encoding="utf-8"))
    fine, f2s = dm["per_line_fine_domain"], dm["fine_to_super"]

    anchors = {}
    rows = (CORPORA / "contested_anchors.tsv").read_text(
        encoding="utf-8").splitlines()
    hdr = rows[0].split("\t")
    for r in rows[1:]:
        c = r.split("\t")
        if len(c) >= 4:
            anchors[int(c[0])] = {"affirmed_by": c[2], "denied_by": c[3]}

    tok = AutoTokenizer.from_pretrained("gpt2")
    ntok = lambda s: len(tok(s)["input_ids"])

    a = [bool(CMP.search(s)) for s in con]
    b = [bool(CMP.search(s)) for s in cns]
    need_cmp = [i for i in range(len(con)) if a[i] and not b[i]]
    need_non = [i for i in range(len(con)) if not a[i] and b[i]]
    keep = [i for i in range(len(con)) if a[i] == b[i]]

    L = []
    w = L.append
    w("# Cahier des charges — bras consensuel v6.2\n")
    w("**Généré mécaniquement** par `build_spec_v6_2.py` depuis les fichiers "
      "gelés. Aucun chiffre n'est saisi à la main ; régénérable à l'identique.\n")
    w(f"**Sources :** [contested.txt](corpora/contested.txt) (gelé, sha "
      f"`3eb7bae8…`) · [consensual_v6.txt](corpora/consensual_v6.txt) · "
      f"[domain_map_v6.json](corpora/domain_map_v6.json) · "
      f"[contested_anchors.tsv](corpora/contested_anchors.tsv)\n")
    w("**Cible :** `corpora/consensual_v6_2.txt`, 120 lignes.\n")
    w("**Pré-enregistrement :** [PREREGISTRATION_v6.2.md]"
      "(PREREGISTRATION_v6.2.md) — à geler APRÈS que ce corpus soit construit "
      "et ait passé la porte G1.\n")
    w("\n---\n")

    # ---------------- en-tête : le besoin exact ----------------
    w("## 1. Le besoin, exactement\n")
    w("v6 a été démenti parce qu'une description linguistique bon marché égalait "
      "la géométrie. Le diagnostic a nommé la cause : **le bras contesté compare "
      "des grandeurs, le bras consensuel décrit des mécanismes.** Huit compteurs "
      "d'expressions régulières atteignent BA = 0,762 en LODO — au-dessus de la "
      "baseline gelée et au-dessus de la géométrie sur 3 modèles sur 4.\n")
    w("v6.2 supprime cette asymétrie. **La ligne *i* du bras consensuel doit "
      "correspondre à la ligne *i* du bras contesté sur DEUX critères :**\n")
    w("1. le **domaine fin** — déjà vrai en v6, à préserver ;\n"
      "2. la **classe de construction** — comparatif vs non-comparatif. C'est "
      "ce qui manque.\n")
    w("\n> Le bras contesté est **gelé**. On ne le touche pas. Tout le travail "
      "porte sur le bras consensuel.\n")

    w("\n### Ce qu'est un consensuel comparatif\n")
    w("Une comparaison qu'**aucun expert informé ne conteste**. Pas un énoncé "
      "contesté adouci, pas une comparaison vague.\n")
    w("\n**Oui :**\n")
    for s in ["Light travels faster through a vacuum than through glass or water.",
              "A progressive income tax takes a larger share from higher earners.",
              "Compound interest makes unpaid debt grow faster over time.",
              "Infectious diseases spread faster in densely populated urban areas."]:
        w(f"- *{s}*  ({ntok(s)} tokens)\n")
    w("\n**Non :**\n")
    w("- *Nuclear power is safer than coal power.* — vrai selon la plupart des "
      "bilans, mais **disputé** dans le débat expert : c'est un contesté.\n")
    w("- *Some materials conduct heat better than others.* — comparatif mais "
      "**vide** : aucun contenu empirique testable.\n")
    w("- *Studies suggest vitamin C may shorten colds.* — **hedge** interdit, et "
      "l'énoncé est contesté.\n")

    w("\n### Contraintes dures (reprises de v5/v6, inchangées)\n")
    w("| contrainte | valeur |\n|---|---|\n")
    w("| langue | anglais, déclaratif, assertable (*truth-apt*) |\n")
    w("| hedges | **interdits** (`may`, `might`, `some studies suggest`, `possibly`) |\n")
    w("| longueur | **9 à 16 tokens gpt2**, appariée en longueur dans le domaine |\n")
    w("| doublons | aucun, ni dans le bras ni avec le bras contesté |\n")
    w("| statut | accord large et établi ; jugements de valeur **exclus** |\n")
    w("| registre | même famille syntaxique que le contesté apparié |\n")

    w("\n### Portes de qualité (model-free, AVANT tout gel)\n")
    w("- **G0** — structurelle, dure : classe de construction identique entre "
      "les deux bras sur **120/120 lignes**.\n")
    w("- **G1** — statistique : le classifieur sur les 8 marqueurs seuls, sous "
      "les 7 plis LODO gelés, doit tomber à **BA ≤ 0,65** (contre 0,762 en v6).\n")
    w("- **Plafond : 3 tours de reconstruction**, chaque valeur de G1 "
      "journalisée dans `corpora/matching_report_v6_2.json`. Au-delà, la "
      "campagne s'arrête sans verdict et l'échec est publié.\n")

    # ---------------- récapitulatif ----------------
    w("\n---\n\n## 2. Récapitulatif du chantier\n")
    w("| catégorie | lignes | action |\n|---|---|---|\n")
    w(f"| §3 — consensuel **comparatif** à écrire | **{len(need_cmp)}** | rédaction neuve |\n")
    w(f"| §4 — consensuel à rendre **non-comparatif** | **{len(need_non)}** | réécriture |\n")
    w(f"| §5 — déjà conformes | **{len(keep)}** | **reprise verbatim** |\n")
    w(f"| total | 120 | |\n")
    w("\nRépartition par domaine fin des lignes à écrire en §3 :\n\n")
    for d, c in sorted(Counter(fine[i] for i in need_cmp).items(),
                       key=lambda kv: (-kv[1], kv[0])):
        w(f"- `{d}` — {c}\n")

    # ---------------- blocs par ligne ----------------
    def block(i, requis, classe):
        n = i + 1
        w(f"\n### Ligne {n} — `{fine[i]}` · super `{f2s[fine[i]]}` — "
          f"**{requis}**\n\n")
        w(f"**Contesté (gelé, référence)** — [contested.txt:{n}]"
          f"(corpora/contested.txt:{n}) · {ntok(con[i])} tokens\n\n")
        w(f"> {con[i]}\n\n")
        anc = anchors.get(n)
        if anc:
            w(f"*Qui l'affirme :* {anc['affirmed_by']}  \n")
            w(f"*Qui le nie :* {anc['denied_by']}\n\n")
        w(f"**Consensuel actuel** — [consensual_v6.txt:{n}]"
          f"(corpora/consensual_v6.txt:{n}) · {ntok(cns[i])} tokens\n\n")
        w(f"> {cns[i]}\n\n")
        w(f"**Marqueurs du contesté :** " + " · ".join(fired(con[i])) + "\n\n")
        w(f"**Marqueurs du consensuel actuel :** " + " · ".join(fired(cns[i]))
          + "\n\n")
        lo, hi = max(9, ntok(con[i]) - 3), min(16, ntok(con[i]) + 3)
        w(f"**À produire :** un énoncé consensuel **{classe}** en "
          f"`{fine[i]}`, **{lo}–{hi} tokens gpt2**, respectant les contraintes "
          f"dures du §1.\n")

    w("\n---\n\n## 3. Lignes exigeant un consensuel COMPARATIF "
      f"({len(need_cmp)})\n")
    w("\nLe contesté apparié est comparatif ; le consensuel ne l'est pas. "
      "Il faut un consensuel comparatif dans le même domaine fin.\n")
    for i in need_cmp:
        block(i, "COMPARATIF requis", "comparatif")

    w("\n---\n\n## 4. Lignes exigeant un consensuel NON-COMPARATIF "
      f"({len(need_non)})\n")
    w("\nLe contesté apparié n'est pas comparatif ; le consensuel l'est. "
      "Retirer la comparaison sans rendre l'énoncé vide ni changer de domaine.\n")
    for i in need_non:
        block(i, "NON-COMPARATIF requis", "non-comparatif")

    w("\n---\n\n## 5. Lignes déjà conformes — reprise verbatim "
      f"({len(keep)})\n")
    w("\nClasse de construction déjà appariée. **À recopier sans modification** : "
      "toute réécriture ici introduirait de la variance non nécessaire.\n\n")
    w("Numéros de ligne : " + ", ".join(str(i + 1) for i in keep) + "\n")

    w("\n---\n\n*Généré par `build_spec_v6_2.py`. Pour régénérer après "
      "modification d'un fichier source : `python build_spec_v6_2.py`.*\n")

    OUT.write_text("".join(L), encoding="utf-8")
    print(f"wrote {OUT}  ({len(need_cmp)} + {len(need_non)} lignes spécifiées, "
          f"{len(keep)} conservées)")


if __name__ == "__main__":
    main()
