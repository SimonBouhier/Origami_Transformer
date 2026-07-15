#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
diag.py — diagnostic du NaN (jetable, ne pas commiter dans le pre-enreg).

Lance : python diag.py
Imprime, pour quelques couches, ce qui casse reellement TwoNN/MLE.
"""
import traceback
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from sklearn.neighbors import NearestNeighbors
from skdim import id as skid

from probe import extract_hidden_states, DEFAULT_CORPUS

MODEL = "gpt2"

corpus_path = Path("claims.txt")
corpus = ([l.strip() for l in corpus_path.read_text(encoding="utf-8").splitlines() if l.strip()]
          if corpus_path.exists() else DEFAULT_CORPUS)

device = "cpu"
tok = AutoTokenizer.from_pretrained(MODEL)
if tok.pad_token is None:
    tok.pad_token = tok.eos_token
model = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.float32).to(device).eval()

print(f"[diag] {MODEL} | corpus={len(corpus)} enonces")
layers = extract_hidden_states(corpus, model, tok, device, 128)
print(f"[diag] {len(layers)} couches, dim={layers[0].shape[1]}, tokens={layers[0].shape[0]}\n")


def probe_layer(X):
    Xf = np.ascontiguousarray(X.astype(np.float32))
    print(f"   shape={Xf.shape}  NaN_in_X={np.isnan(Xf).any()}  Inf_in_X={np.isinf(Xf).any()}")
    print(f"   norme: min={np.linalg.norm(Xf,axis=1).min():.3e} "
          f"max={np.linalg.norm(Xf,axis=1).max():.3e}")
    U = np.unique(Xf, axis=0)
    print(f"   lignes uniques (np.unique) : {U.shape[0]} / {Xf.shape[0]}")
    rng = np.random.default_rng(0)
    S = U[rng.choice(U.shape[0], min(1500, U.shape[0]), replace=False)] if U.shape[0] >= 10 else U
    d, _ = NearestNeighbors(n_neighbors=3).fit(S).kneighbors(S)
    print(f"   1er-voisin a distance EXACTE 0 : {int((d[:,1]==0).sum())} / {S.shape[0]}"
          f"   (min r1 = {d[:,1].min():.3e})")
    for m in ("twonn", "mle"):
        try:
            est = skid.TwoNN() if m == "twonn" else skid.MLE(K=20)
            est.fit(S)
            print(f"   {m:6s} -> dimension_ = {float(est.dimension_)}")
        except Exception:
            print(f"   {m:6s} -> LEVE une exception :")
            traceback.print_exc()


for i in (0, 1, 6, len(layers) - 1):
    print(f"=== couche {i} ===")
    probe_layer(layers[i])
    print()
