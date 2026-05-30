#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
epp_adapter.py — Origami DI -> EPP attestation (STUB)
=====================================================

CE MODULE EST UN STUB DELIBERE.

Principe :
----------
EPP consomme un instrument valide. Jamais l'inverse. Cristalliser une
attestation EPP a partir d'une sonde non encore validee revient a faire
confiance a un oracle qui ne s'est pas encore mefié de lui-meme. C'est
exactement l'anti-pattern que tout EPP combat.

Condition de degel :
--------------------
1. probe.py a tourne sur >= 4 modeles d'architectures distinctes.
2. analysis.py renvoie GLOBAL = H1_CONFIRME avec ses seuils preenregistres.
3. Le pre-enregistrement ET les seuils sont commits sur git AVANT de
   regarder les resultats (pas de p-hacking retroactif sur les thresholds).

Tant que ces trois conditions ne sont pas remplies, importer ce module
leve une erreur. C'est volontaire.

Quand le moment vient :
-----------------------
- build_attestation(probe_outputs, analysis_report) -> dict
- metrological_frame = "origami_di_v1.0"
- source_anchor = sha256( corpus_hash || model_ids || thresholds_json )
- L'attestation passe par la pipeline EPP normale (VERIFY ou
  DETERMINISTIC selon le cadre). Elle n'est PAS produite ici en bypass.

Note epistemique :
------------------
Un dementi global (H1_DEMENTI) est aussi un resultat publiable. Dans ce
cas, ce module restera un stub permanent et le frame "origami_di_v1.0"
ne sera jamais ajoute a EPP. C'est la forme correcte du non-resultat.
"""

raise NotImplementedError(
    "epp_adapter.py est un stub. Le probe doit etre valide sur >= 4 "
    "familles d'architecture avec H1_CONFIRME global avant integration "
    "EPP. Voir docstring pour les conditions de degel."
)
