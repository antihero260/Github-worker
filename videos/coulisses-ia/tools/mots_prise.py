#!/usr/bin/env python3
"""Affiche les mots d'une prise avec leurs temps : python3 tools/mots_prise.py PRISE DEBUT FIN"""
import json, sys
p, a, b = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
m = json.load(open(f"assets/transcripts/20261116_{p}.json"))
print(" ".join(f"{w['text'].strip()}@{w['start']:.2f}" for w in m if a <= w["start"] <= b))
