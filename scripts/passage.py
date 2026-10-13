#!/usr/bin/env python3
"""Show the next (or a given) reading from the plan, with each Arabic word numbered.

Usage:
  python3 scripts/passage.py          # next unused reading
  python3 scripts/passage.py 12       # reading #12
Use the verse and word numbers for the card's root.verse / root.index.
Also lists roots already taught, so you can choose a new one or a review.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
QURAN = json.loads((ROOT / "data/quran-uthmani.json").read_text(encoding="utf-8"))
PLAN = json.loads((ROOT / "data/plan.json").read_text(encoding="utf-8"))

cards = []
for f in sorted((ROOT / "cards").glob("*.json")):
    try:
        c = json.loads(f.read_text(encoding="utf-8"))
    except Exception:
        continue
    if c.get("type") == "reading":
        cards.append(c)

used = {int(c["plan"]) for c in cards}
n = int(sys.argv[1]) if len(sys.argv) > 1 else next((i for i in range(1, len(PLAN) + 1) if i not in used), None)
if n is None:
    sys.exit("plan finished")
p = PLAN[n - 1]
print(f"Reading {n} of {len(PLAN)}: Surah {p['surah']} {p['name']} ({p['meaning']}), verses {p['from']}-{p['to']}\n")
for v in range(p["from"], p["to"] + 1):
    toks = QURAN[str(p["surah"])][str(v)].split(" ")
    print(f"verse {v}: " + "  ".join(f"[{i}]{t}" for i, t in enumerate(toks, 1)))
print("\nRoots taught so far (date · translit · meaning):")
for c in cards:
    r = c.get("root", {})
    print(f"  {c['date']} · {r.get('translit')} · {r.get('meaning')}")
if not cards:
    print("  (none yet)")
