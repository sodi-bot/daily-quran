#!/usr/bin/env python3
"""Show the next (or a given) reading from the Nöldeke plan.

Usage:
  python3 scripts/passage.py              # next unused reading
  python3 scripts/passage.py 12           # reading #12
  python3 scripts/passage.py 12 96:1-5    # reading #12, with words numbered for that range

Whole-surah readings print every word numbered. For long surahs it prints the
whole surah (verse numbers and length) so you can choose a key passage of at
most 5 verses / 450 Arabic characters; then run again with that range to get
word numbers for root.verse / root.index.
Also lists roots already taught.
"""
import json
import pathlib
import re
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
s = str(p["surah"])
print(f"Reading {n} of {len(PLAN)} · {p['period']} · Surah {s} {p['name']} ({p['meaning']}), {p['verses_total']} verses")

if p["whole"]:
    a, b = p["from"], p["to"]
    print("Whole surah on one card.\n")
elif len(sys.argv) > 2:
    m = re.fullmatch(r"(\d+):(\d+)(?:-(\d+))?", sys.argv[2])
    a, b = int(m[2]), int(m[3] or m[2])
    print(f"Key passage {s}:{a}-{b} (set `verses` to this on the card).\n")
else:
    print("Long surah: choose a key passage (max 5 verses, 450 chars), then rerun with the range.\n")
    for v in range(1, p["verses_total"] + 1):
        t = QURAN[s][str(v)]
        print(f"{v} ({len(t)}): {t}")
    a = b = None

if a:
    for v in range(a, b + 1):
        toks = QURAN[s][str(v)].split(" ")
        print(f"verse {v}: " + "  ".join(f"[{i}]{t}" for i, t in enumerate(toks, 1)))
    print(f"\nTotal Arabic characters: {sum(len(QURAN[s][str(v)]) for v in range(a, b + 1))}")

print("\nRoots taught so far (date · translit · meaning):")
for c in cards:
    r = c.get("root", {})
    print(f"  {c['date']} · {r.get('translit')} · {r.get('meaning')}")
if not cards:
    print("  (none yet)")
