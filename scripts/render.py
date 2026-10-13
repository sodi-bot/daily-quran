#!/usr/bin/env python3
"""Render a daily Qur'an x Bible card JSON into a PNG.

Usage: python3 scripts/render.py cards/2026-10-14.json [out.png]

Scripture is never taken from the card file when it can be looked up:
- Arabic comes from data/quran-uthmani.json (Tanzil) via `verses`
- Bible text comes from data/bible-asv.json (American Standard Version, 1901,
  public domain) via `bible`
Only non-biblical parallels (Mishnah, Infancy Gospels, Syriac legends...) use
the card's own `parallel_text`, which must be a paraphrase and is labelled so.
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
BIBLE = json.loads((ROOT / "data/bible-asv.json").read_text(encoding="utf-8"))

REQUIRED = ["date", "relation", "title", "verses", "translation", "body", "question", "source_label"]
LIMITS = {"title": 9, "translation": 40, "body": 70, "question": 24, "parallel_text": 35}  # max words
RELATIONS = {
    "aligns": "Where they meet",
    "differs": "Where they part",
    "retells": "Same story, retold",
}
TAGS = {"bible": "Qur'an & the Bible", "news": "Qur'an & the news"}

ABBR = {
    "gen": "Genesis", "gn": "Genesis", "ex": "Exodus", "exod": "Exodus", "lev": "Leviticus",
    "num": "Numbers", "deut": "Deuteronomy", "dt": "Deuteronomy", "josh": "Joshua",
    "judg": "Judges", "1sam": "1 Samuel", "2sam": "2 Samuel", "1kgs": "1 Kings", "2kgs": "2 Kings",
    "1kings": "1 Kings", "2kings": "2 Kings", "1chr": "1 Chronicles", "2chr": "2 Chronicles",
    "neh": "Nehemiah", "esth": "Esther", "ps": "Psalms", "psalm": "Psalms", "psa": "Psalms",
    "prov": "Proverbs", "eccl": "Ecclesiastes", "eccles": "Ecclesiastes", "song": "Song of Solomon",
    "isa": "Isaiah", "jer": "Jeremiah", "lam": "Lamentations", "ezek": "Ezekiel", "dan": "Daniel",
    "hos": "Hosea", "obad": "Obadiah", "jon": "Jonah", "mic": "Micah", "nah": "Nahum",
    "hab": "Habakkuk", "zeph": "Zephaniah", "hag": "Haggai", "zech": "Zechariah", "mal": "Malachi",
    "matt": "Matthew", "mt": "Matthew", "mk": "Mark", "mrk": "Mark", "lk": "Luke", "jn": "John",
    "rom": "Romans", "1cor": "1 Corinthians", "2cor": "2 Corinthians", "gal": "Galatians",
    "eph": "Ephesians", "phil": "Philippians", "col": "Colossians", "1thess": "1 Thessalonians",
    "2thess": "2 Thessalonians", "1tim": "1 Timothy", "2tim": "2 Timothy", "tit": "Titus",
    "phlm": "Philemon", "philem": "Philemon", "heb": "Hebrews", "jas": "James", "1pet": "1 Peter",
    "2pet": "2 Peter", "1jn": "1 John", "2jn": "2 John", "3jn": "3 John", "rev": "Revelation",
}
for _name in BIBLE:
    ABBR[_name.lower().replace(" ", "")] = _name

AR_DIGITS = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")


def parse_quran(ref):
    m = re.fullmatch(r"\s*(\d{1,3}):(\d{1,3})(?:\s*[-–]\s*(\d{1,3}))?\s*", ref)
    if not m:
        raise SystemExit(f"bad verses ref {ref!r}; use e.g. '44:10' or '44:10-11'")
    s, a, b = int(m[1]), int(m[2]), int(m[3] or m[2])
    if str(s) not in QURAN or b < a or b - a > 3 or str(b) not in QURAN[str(s)]:
        raise SystemExit(f"verses ref {ref!r} invalid (max 4 verses)")
    return s, a, b


def parse_bible(ref):
    m = re.fullmatch(r"\s*([1-3]?\s*[A-Za-z][A-Za-z .]*?)\s*(\d{1,3}):(\d{1,3})(?:\s*[-–]\s*(\d{1,3}))?\s*", ref)
    if not m:
        raise SystemExit(f"bad bible ref {ref!r}; use e.g. 'Genesis 3:6' or 'Matt 19:23-24'")
    key = re.sub(r"[\s.]", "", m[1]).lower()
    book = ABBR.get(key)
    if not book:
        raise SystemExit(f"unknown Bible book {m[1]!r}")
    c, a, b = int(m[2]), int(m[3]), int(m[4] or m[3])
    chs = BIBLE[book]
    if c > len(chs) or b < a or b - a > 2 or b > len(chs[c - 1]):
        raise SystemExit(f"bible ref {ref!r} invalid (max 3 verses)")
    text = " ".join(chs[c - 1][v - 1] for v in range(a, b + 1))
    label = f"{book} {c}:{a}" + (f"–{b}" if b > a else "") + " · ASV"
    return text, label


def words(t):
    return len(re.sub(r"\*\*", "", t).split())


def check(card):
    missing = [k for k in REQUIRED if not str(card.get(k, "")).strip()]
    if missing:
        raise SystemExit(f"card missing fields: {missing}")
    if card["relation"] not in RELATIONS:
        raise SystemExit(f"relation must be one of {list(RELATIONS)}")
    if bool(card.get("bible")) == bool(card.get("parallel_label")):
        raise SystemExit("give exactly one of `bible` or `parallel_label` + `parallel_text`")
    if card.get("parallel_label") and not card.get("parallel_text"):
        raise SystemExit("`parallel_label` needs `parallel_text`")
    for k, n in LIMITS.items():
        if card.get(k) and words(card[k]) > n:
            raise SystemExit(f"{k} has {words(card[k])} words; limit is {n}")
    if card.get("source_url") and not card["source_url"].startswith("https://"):
        raise SystemExit("source_url must be https")


def arabic_html(s, a, b):
    parts = []
    for v in range(a, b + 1):
        txt = html.escape(QURAN[str(s)][str(v)])
        parts.append(f'{txt} <span class="n">﴿{str(v).translate(AR_DIGITS)}﴾</span>')
    return " ".join(parts)


def rich(text):
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", html.escape(text))


def render(card_path, out_path):
    card = json.loads(pathlib.Path(card_path).read_text(encoding="utf-8"))
    check(card)
    s, a, b = parse_quran(card["verses"])
    ch = CHAPTERS[str(s)]
    meaning = f" ({ch['meaning']})" if ch["meaning"].lower() != ch["name"].lower() else ""
    qref = f"Qur'an {s}:{a}" + (f"–{b}" if b > a else "") + f" · {ch['name']}{meaning}"
    if card.get("bible"):
        ptext, pref = parse_bible(card["bible"])
    else:
        ptext, pref = card["parallel_text"], card["parallel_label"] + " · paraphrase"
    date = dt.date.fromisoformat(card["date"])
    data = {
        "tag": TAGS.get(card.get("tag", "bible"), card.get("tag", TAGS["bible"])),
        "day": date.strftime("%a").upper(),
        "relation": RELATIONS[card["relation"]],
        "title": html.escape(card["title"]),
        "arabic": arabic_html(s, a, b),
        "translation": "“" + html.escape(card["translation"]) + "”",
        "ref": html.escape(qref),
        "ptext": "“" + html.escape(ptext) + "”",
        "pref": html.escape(pref),
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
        if h > 1750:
            raise SystemExit(f"card is too tall ({h}px, max 1750); shorten the text")
        pg.locator("#card").screenshot(path=str(out_path))
        br.close()
    return card, h


if __name__ == "__main__":
    src = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else str(pathlib.Path(src).with_suffix(".png"))
    _, h = render(src, out)
    print(f"rendered {out} ({h}px tall)")
