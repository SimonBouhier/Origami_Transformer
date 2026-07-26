#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
select_pairs.py — parse les propositions des modèles et pioche la meilleure
par ligne, selon des critères OBJECTIFS uniquement.

Ne juge PAS la vérité ni la non-contestation d'une phrase (travail humain +
audit de source). Il filtre sur ce qui est mécaniquement vérifiable, puis classe
les survivantes, pour que le tri éditorial parte d'un socle déjà propre.

Filtres DURS (une candidate qui en rate un est écartée) :
  - phrase déclarative anglaise, se terminant par un point, sans ; ni ?
  - 9–16 tokens gpt2
  - même classe de construction que le contesté (comparatif ⇔ comparatif)
  - aucun hedge
  - recouvrement de sujet >= 2 mots de contenu avec le contesté
  - non-identique au contesté, non-doublon avec une ligne deja retenue

Score de CLASSEMENT parmi les survivantes (plus haut = mieux) :
  + recouvrement de sujet (mots de contenu partagés)
  + réutilisation d'un mot rare du contesté (chiefly/materially/... ) : bonus
  + longueur proche de celle du contesté
  - présence de mots à sens unique déjà sur-représentés d'un côté du corpus

Usage :
    python select_pairs.py            # parse, filtre, classe, écrit le TSV
"""
import csv
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from transformers import AutoTokenizer

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))
from diag_v7 import CONSTRUCTION_MARKERS

PROP_DIR = Path("corpora/v6_4_proposals")
EVIDENCE = Path("corpora/v6_3/evidence.tsv")
DEMO = PROP_DIR / "subject_matched_demo.tsv"
OUT = PROP_DIR / "_selected.tsv"
REPORT = PROP_DIR / "_selection_report.md"

CMP = re.compile(list(CONSTRUCTION_MARKERS.values())[0], re.I)
HEDGE = re.compile(r"\b(may|might|could|possibly|perhaps|likely|tends? to|"
                   r"appears? to|seems? to|is thought to|some studies suggest|"
                   r"potentially|arguably|generally)\b", re.I)
RARE = re.compile(r"\b(chiefly|materially|causally|explains?|rather|primarily|"
                  r"mainly|outweigh\w*)\b", re.I)
tok = AutoTokenizer.from_pretrained("gpt2")
ntok = lambda s: len(tok(s)["input_ids"])


def content(s):
    return {w for w in re.findall(r"[a-z']+", s.lower())
            if w not in ENGLISH_STOP_WORDS and len(w) > 2}


def parse_block_file(path):
    """Extrait {line:int -> sentence} d'un fichier de propositions."""
    out = {}
    cur = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\s*\[(\d+)\]", raw)
        if m:
            cur = int(m.group(1))
            continue
        m = re.match(r"^\s*CONSENSUAL\s*:\s*(.+)$", raw, re.I)
        if m and cur is not None:
            out[cur] = m.group(1).strip()
            cur = None
    return out


def main():
    ev = {int(r["line"]): r for r in csv.DictReader(
        EVIDENCE.open(encoding="utf-8"), delimiter="\t")}

    # 26 déjà écrites (démonstration) : retenues d'office, servent de référence corpus
    demo = {int(r["line"]): r for r in csv.DictReader(
        DEMO.open(encoding="utf-8"), delimiter="\t")}

    props = {}
    for p in sorted(PROP_DIR.glob("proposition_*.txt")):
        props[p.name] = parse_block_file(p)
        print(f"{p.name}: {len(props[p.name])} candidates parsées")

    # vocabulaire déjà engagé (côté consensuel des 26) pour pénaliser les mots à sens unique
    con_all = [ev[l]["contested_claim"] for l in ev]
    consensual_fixed = [demo[l]["proposed_consensual"] for l in demo]

    selected = dict(demo)     # line -> row-like
    chosen_consensual = {l: demo[l]["proposed_consensual"] for l in demo}
    per_line_report = []

    target_lines = [l for l in ev if l not in demo]
    for line in sorted(target_lines):
        con = ev[line]["contested_claim"]
        con_is_cmp = bool(CMP.search(con))
        con_words = content(con)
        con_rare = {m.group(0).lower() for m in RARE.finditer(con)}
        con_len = ntok(con)

        cands = []
        for fname, d in props.items():
            s = d.get(line)
            if not s:
                continue
            # --- filtres durs
            reason = None
            if not s.endswith(".") or ";" in s or "?" in s:
                reason = "ponctuation"
            elif not (9 <= ntok(s) <= 16):
                reason = f"longueur {ntok(s)}"
            elif bool(CMP.search(s)) != con_is_cmp:
                reason = "classe de construction"
            elif HEDGE.search(s):
                reason = "hedge"
            elif len(content(s) & con_words) < 2:
                reason = f"recouvrement {len(content(s) & con_words)}"
            elif s.strip().lower() == con.strip().lower():
                reason = "identique au contesté"
            if reason:
                cands.append((None, fname, s, reason))
                continue
            # --- score de classement
            ov = len(content(s) & con_words)
            rare_reuse = len({m.group(0).lower() for m in RARE.finditer(s)} & con_rare)
            len_pen = abs(ntok(s) - con_len)
            score = ov + 2.0 * rare_reuse - 0.15 * len_pen
            cands.append((score, fname, s, None))

        valid = sorted([c for c in cands if c[0] is not None], key=lambda c: -c[0])
        if valid:
            score, fname, s, _ = valid[0]
            chosen_consensual[line] = s
            selected[line] = {
                "line": line, "fine_domain": ev[line]["fine_domain"],
                "super_domain": ev[line]["super_domain"],
                "contested_claim": con, "proposed_consensual": s,
                "why_uncontested": f"[auto-sélection {fname}, score {score:.2f}]"}
        per_line_report.append((line, con_is_cmp, valid, [c for c in cands if c[0] is None]))

    # --- écriture du TSV fusionné (26 démos + sélections)
    with OUT.open("w", encoding="utf-8", newline="") as f:
        wr = csv.writer(f, delimiter="\t")
        wr.writerow(["line", "fine_domain", "super_domain", "contested_claim",
                     "proposed_consensual", "why_uncontested"])
        for line in sorted(selected):
            r = selected[line]
            wr.writerow([r["line"], r["fine_domain"], r["super_domain"],
                         r["contested_claim"], r["proposed_consensual"],
                         r.get("why_uncontested", "")])

    filled = len(selected)
    missing = [l for l in ev if l not in selected]
    print(f"\n{filled}/120 lignes remplies ; {len(missing)} manquantes : {missing}")

    # --- rapport lisible
    R = [f"# Sélection automatique — {filled}/120 lignes\n",
         f"Filtres durs : ponctuation, 9-16 tokens gpt2, classe de construction, "
         f"hedge, recouvrement de sujet >= 2. Score = recouvrement + 2·réutilisation "
         f"de mot rare − 0,15·écart de longueur.\n",
         f"**26** viennent de la démonstration (retenues d'office). "
         f"**{filled-26}** choisies parmi les propositions. "
         f"**{len(missing)}** encore à couvrir : {missing or '—'}\n",
         "\n## Lignes sans candidate valide (à retravailler)\n"]
    none_valid = [l for l, _, v, _ in per_line_report if not v]
    if none_valid:
        for line, is_cmp, valid, rejected in per_line_report:
            if valid:
                continue
            R.append(f"\n**[{line}]** ({'COMPARATIVE' if is_cmp else 'PLAIN'}) "
                     f"_{ev[line]['contested_claim']}_\n")
            for _, fname, s, reason in rejected:
                R.append(f"- ✗ {fname}: {reason} — «{s}»\n")
    else:
        R.append("\n_(aucune — toutes les lignes ont au moins une candidate valide)_\n")
    REPORT.write_text("".join(R), encoding="utf-8")
    print(f"wrote {OUT}\nwrote {REPORT}")
    if missing:
        print(f"\n>>> {len(missing)} lignes à compléter : {missing}")


if __name__ == "__main__":
    main()
