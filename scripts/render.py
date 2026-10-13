#!/usr/bin/env python3
"""Render a daily card JSON into a PNG.

Usage: python3 scripts/render.py cards/2026-10-13.json [out.png]

The Arabic is never taken from the card file: it is looked up from
data/quran-uthmani.json (Tanzil) using the card's `verses` field, so the
verse text is always exact.
"""
import datetime as dt
import html
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
QURAN = json.loads((ROOT / "data/quran-uthmani.json").read_text(encoding="utf-8"))
CHAPTERS = json.loads((ROOT / "data/chapters.json").read_text(encoding="utf-8"))

REQUIRED = ["date", "title", "verses", "translation", "body", "question", "source_label", "source_url"]
LIMITS = {"title": 9, "translation": 45, "body": 75, "question": 26}  # max words

ICONS = {  # simple line icons, 24x24 viewBox, stroke-based
    "book": '<path d="M4 5a2 2 0 0 1 2-2h13v16H6a2 2 0 0 0-2 2z"/><path d="M4 21V5"/><path d="M9 7h6"/>',
    "scroll": '<path d="M8 21h11a2 2 0 0 0 2-2v-1H10v1a2 2 0 0 1-4 0V5a2 2 0 0 0-2-2 2 2 0 0 0-2 2v2h4"/><path d="M19 17V5a2 2 0 0 0-2-2H4"/>',
    "cloud": '<path d="M17.5 19H8a5 5 0 1 1 1.2-9.86A6 6 0 0 1 20 11.5 3.75 3.75 0 0 1 17.5 19z"/>',
    "smoke": '<path d="M4 18c2-1.5 4-1.5 6 0s4 1.5 6 0 4-1.5 4-1.5"/><path d="M4 13c2-1.5 4-1.5 6 0s4 1.5 6 0 4-1.5 4-1.5"/><path d="M6 8c2-1.5 4-1.5 6 0s4 1.5 6 0"/>',
    "water": '<path d="M12 3s6 6.5 6 11a6 6 0 0 1-12 0c0-4.5 6-11 6-11z"/>',
    "leaf": '<path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z"/><path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"/>',
    "globe": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18"/><path d="M12 3a14 14 0 0 1 0 18a14 14 0 0 1 0-18z"/>',
    "scale": '<path d="M12 3v18"/><path d="M5 21h14"/><path d="M3 7h18"/><path d="M6 7l-3 7a3 3 0 0 0 6 0z"/><path d="M18 7l-3 7a3 3 0 0 0 6 0z"/>',
    "flame": '<path d="M12 22a7 7 0 0 0 7-7c0-4-3-6-4-9-2 2-2 4-3 5-1-2-2-3-2-5-3 3-5 6-5 9a7 7 0 0 0 7 7z"/>',
    "star": '<path d="M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1L3.2 9.5l6.1-.9z"/>',
    "moon": '<path d="M20 14.5A8 8 0 1 1 9.5 4a6.5 6.5 0 0 0 10.5 10.5z"/>',
    "people": '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20a6.5 6.5 0 0 1 13 0"/><circle cx="17" cy="9" r="2.5"/><path d="M16 14.5a5 5 0 0 1 5.5 5"/>',
    "mountain": '<path d="M3 20l6-11 4 7 3-4 5 8z"/>',
    "seed": '<path d="M12 21V11"/><path d="M12 11c0-4 3-7 7-7 0 4-3 7-7 7z"/><path d="M12 14c0-3-2.5-5.5-6-5.5 0 3 2.5 5.5 6 5.5z"/>',
    "ship": '<path d="M3 17l2 4h14l2-4z"/><path d="M5 17V11h14v6"/><path d="M12 11V3l5 5h-5"/>',
}

AR_DIGITS = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")


def parse_ref(ref):
    m = re.fullmatch(r"\s*(\d{1,3}):(\d{1,3})(?:\s*[-–]\s*(\d{1,3}))?\s*", ref)
    if not m:
        raise SystemExit(f"bad verses ref {ref!r}; use e.g. '44:10' or '44:10-11'")
    s, a, b = int(m[1]), int(m[2]), int(m[3] or m[2])
    if str(s) not in QURAN or b < a or b - a > 3:
        raise SystemExit(f"verses ref {ref!r} out of range (max 4 verses)")
    if str(b) not in QURAN[str(s)]:
        raise SystemExit(f"surah {s} has no verse {b}")
    return s, a, b


def arabic_html(s, a, b):
    parts = []
    for v in range(a, b + 1):
        txt = html.escape(QURAN[str(s)][str(v)])
        parts.append(f'{txt} <span class="n">﴿{str(v).translate(AR_DIGITS)}﴾</span>')
    return " ".join(parts)


def rich(text):
    t = html.escape(text)
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)


def check(card):
    missing = [k for k in REQUIRED if not str(card.get(k, "")).strip()]
    if missing:
        raise SystemExit(f"card missing fields: {missing}")
    for k, n in LIMITS.items():
        words = len(re.sub(r"\*\*", "", card[k]).split())
        if words > n:
            raise SystemExit(f"{k} has {words} words; limit is {n}")
    if not card["source_url"].startswith("https://"):
        raise SystemExit("source_url must be https")


def render(card_path, out_path):
    card = json.loads(pathlib.Path(card_path).read_text(encoding="utf-8"))
    check(card)
    s, a, b = parse_ref(card["verses"])
    ch = CHAPTERS[str(s)]
    ref_txt = f"Qur'an {s}:{a}" + (f"–{b}" if b > a else "") + f" · {ch['name']} ({ch['meaning']})"
    date = dt.date.fromisoformat(card["date"])
    icon = ICONS.get(card.get("icon", "book"), ICONS["book"])
    data = {
        "tag": card.get("tag", "Qur'an & the news"),
        "day": date.strftime("%a").upper(),
        "icon": f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">{icon}</svg>',
        "title": html.escape(card["title"]),
        "arabic": arabic_html(s, a, b),
        "translation": "“" + html.escape(card["translation"]) + "”",
        "ref": html.escape(ref_txt),
        "body": rich(card["body"]),
        "question": html.escape(card["question"]),
        "source": html.escape(card["source_label"]),
        "date": date.strftime("%-d %b %Y"),
    }
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        br = p.chromium.launch()
        pg = br.new_page(viewport={"width": 1080, "height": 1350})
        pg.goto((ROOT / "template/card.html").as_uri())
        pg.evaluate("d => { for (const [k,v] of Object.entries(d)) document.getElementById(k).innerHTML = v; }", data)
        pg.evaluate("document.fonts.ready")
        pg.wait_for_timeout(300)
        h = pg.evaluate("document.getElementById('card').scrollHeight")
        if h > 1600:
            raise SystemExit(f"card is too tall ({h}px); shorten the text")
        pg.locator("#card").screenshot(path=str(out_path))
        br.close()
    return card, h


if __name__ == "__main__":
    src = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else str(pathlib.Path(src).with_suffix(".png"))
    _, h = render(src, out)
    print(f"rendered {out} ({h}px tall)")
