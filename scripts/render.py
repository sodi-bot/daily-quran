#!/usr/bin/env python3
"""Render a daily card (type "reading") or a weekly recap (type "recap") into a PNG.

Usage: python3 scripts/render.py cards/2026-10-14.json [out.png]

Scripture is never typed into the card file:
- the passage comes from data/plan.json via `plan`, and its Arabic from
  data/quran-uthmani.json (Tanzil)
- the root word is chosen by position (`root.verse`, `root.index`) and highlighted
- Bible text comes from data/bible-asv.json (ASV 1901) via `bible`
Only non-biblical parallels use the card's own `parallel_text` (a paraphrase).
"""
import datetime as dt
import html
import json
import pathlib
import re
import sys
import unicodedata

ROOT = pathlib.Path(__file__).resolve().parent.parent
QURAN = json.loads((ROOT / "data/quran-uthmani.json").read_text(encoding="utf-8"))
BIBLE = json.loads((ROOT / "data/bible-asv.json").read_text(encoding="utf-8"))
PLAN = json.loads((ROOT / "data/plan.json").read_text(encoding="utf-8"))
CARDS = ROOT / "cards"

LIMITS = {"title": 9, "translation": 60, "body": 60, "question": 24, "parallel_text": 35, "news_text": 22}
RELATIONS = {"aligns": "Bible parallel · where they meet", "differs": "Bible parallel · where they part",
             "retells": "Bible parallel · same story, retold", "echo": "Bible parallel · an echo"}
OTHER_REL = {"aligns": "Parallel · where they meet", "differs": "Parallel · where they part",
             "retells": "Parallel · same story, retold", "echo": "Parallel · an echo"}
MAX_HEIGHT = 1900

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


def fail(msg):
    raise SystemExit(msg)


def words(t):
    return len(re.sub(r"\*\*", "", t or "").split())


def passage(n):
    if not 1 <= n <= len(PLAN):
        fail(f"plan must be 1..{len(PLAN)}")
    return PLAN[n - 1]


def ref_text(p):
    r = f"{p['surah']}:{p['from']}" + (f"–{p['to']}" if p["to"] > p["from"] else "")
    meaning = f" ({p['meaning']})" if p["meaning"].lower() != p["name"].lower() else ""
    return r, f"Qur'an {r} · {p['name']}{meaning}"


def parse_bible(ref):
    m = re.fullmatch(r"\s*([1-3]?\s*[A-Za-z][A-Za-z .]*?)\s*(\d{1,3}):(\d{1,3})(?:\s*[-–]\s*(\d{1,3}))?\s*", ref)
    if not m:
        fail(f"bad bible ref {ref!r}; use e.g. 'Genesis 3:6' or 'Matt 19:23-24'")
    book = ABBR.get(re.sub(r"[\s.]", "", m[1]).lower())
    if not book:
        fail(f"unknown Bible book {m[1]!r}")
    c, a, b = int(m[2]), int(m[3]), int(m[4] or m[3])
    chs = BIBLE[book]
    if c > len(chs) or b < a or b - a > 2 or b > len(chs[c - 1]):
        fail(f"bible ref {ref!r} invalid (max 3 verses)")
    text = " ".join(chs[c - 1][v - 1] for v in range(a, b + 1))
    return text, f"{book} {c}:{a}" + (f"–{b}" if b > a else "") + " · ASV"


def strip_marks(s):
    return "".join(ch for ch in unicodedata.normalize("NFD", s) if not unicodedata.combining(ch))


def all_cards(before=None, kind="reading"):
    out = []
    for f in sorted(CARDS.glob("*.json")):
        try:
            c = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        if c.get("type") != kind or (before and c.get("date", "") >= before):
            continue
        out.append(c)
    return sorted(out, key=lambda c: c["date"])


def root_status(card):
    key = card["root"]["translit"].lower()
    prior = all_cards(before=card["date"])
    seen = [c for c in prior if c.get("root", {}).get("translit", "").lower() == key]
    if seen:
        d = dt.date.fromisoformat(seen[-1]["date"]).strftime("%-d %b")
        return f"Review · last {d}"
    n = len({c["root"]["translit"].lower() for c in prior if c.get("root")}) + 1
    return f"New root · #{n}"


def check_reading(card):
    for k in ["date", "plan", "title", "translation", "root", "body", "question", "source_label"]:
        if not card.get(k):
            fail(f"card missing {k}")
    r = card["root"]
    for k in ["letters", "translit", "meaning", "verse", "index", "word_translit", "word_meaning"]:
        if not r.get(k):
            fail(f"root missing {k}")
    letters = [x for x in r["letters"].split() if x]
    if not 2 <= len(letters) <= 4 or not all(re.fullmatch(r"[ء-ي]", x) for x in letters):
        fail("root.letters must be 2-4 Arabic letters separated by spaces, e.g. 'ر ح م'")
    if bool(card.get("bible")) and bool(card.get("parallel_label")):
        fail("give `bible` or `parallel_label`, not both")
    if (card.get("bible") or card.get("parallel_label")) and card.get("relation") not in RELATIONS:
        fail(f"a parallel needs relation in {list(RELATIONS)}")
    if card.get("parallel_label") and not card.get("parallel_text"):
        fail("`parallel_label` needs `parallel_text`")
    news = card.get("news") or {}
    if news and not (news.get("text") and str(news.get("url", "")).startswith("https://")):
        fail("news needs text and an https url")
    sizes = dict(card, news_text=news.get("text"))
    for k, n in LIMITS.items():
        if words(sizes.get(k)) > n:
            fail(f"{k} has {words(sizes.get(k))} words; limit is {n}")


def arabic_html(p, root):
    s = str(p["surah"])
    rv, ri = int(root["verse"]), int(root["index"])
    if not p["from"] <= rv <= p["to"]:
        fail(f"root.verse {rv} is outside the passage {p['from']}-{p['to']}")
    parts = []
    for v in range(p["from"], p["to"] + 1):
        toks = QURAN[s][str(v)].split(" ")
        esc = [html.escape(t) for t in toks]
        if v == rv:
            if not 1 <= ri <= len(toks):
                fail(f"root.index {ri} out of range; verse {v} has {len(toks)} words")
            word = strip_marks(toks[ri - 1])
            hits = sum(1 for L in root["letters"].split() if L in word or (L in "اوي" ) or (L == "ء" and any(h in word for h in "أإؤئءٱ")))
            if hits < 2:
                fail(f"root letters {root['letters']} don't fit the word {toks[ri - 1]} (verse {v}, word {ri})")
            esc[ri - 1] = f'<span class="hw">{esc[ri - 1]}</span>'
        parts.append(" ".join(esc) + f' <span class="n">﴿{str(v).translate(AR_DIGITS)}﴾</span>')
    bas = ""
    if p["from"] == 1 and s not in ("1", "9"):
        bas = f'<div class="bas">{html.escape(QURAN["_basmala"])}</div>'
    return bas + " ".join(parts)


def letters_html(letters):
    return "".join(f"<span>{html.escape(x)}</span>" for x in letters.split())


def rich(text):
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", html.escape(text))


def fmt_date(d):
    return dt.date.fromisoformat(d).strftime("%-d %b %Y")


def reading_data(card):
    check_reading(card)
    p = passage(int(card["plan"]))
    _, qref = ref_text(p)
    r = card["root"]
    d = {
        "tag": f"Reading {card['plan']} of {len(PLAN)}",
        "day": dt.date.fromisoformat(card["date"]).strftime("%a").upper(),
        "over": html.escape(f"{p['name']} · {p['surah']}:{p['from']}" + (f"–{p['to']}" if p["to"] > p["from"] else "")),
        "title": html.escape(card["title"]),
        "arabic": arabic_html(p, r),
        "translation": "“" + html.escape(card["translation"]) + "”",
        "ref": html.escape(qref),
        "letters": letters_html(r["letters"]),
        "rt": f"{html.escape(r['translit'])} <span>· {html.escape(r['meaning'])}</span>",
        "badge": html.escape(root_status(card)),
        "rw": f"<b>{html.escape(r['word_translit'])}</b> = {html.escape(r['word_meaning'])}",
        "body": rich(card["body"]),
        "question": html.escape(card["question"]),
        "source": html.escape(card["source_label"]),
        "date": fmt_date(card["date"]),
        "_hide": [],
    }
    if card.get("bible"):
        t, ref = parse_bible(card["bible"])
        d.update(relation=RELATIONS[card["relation"]], ptext="“" + html.escape(t) + "”", pref=html.escape(ref))
    elif card.get("parallel_label"):
        d.update(relation=OTHER_REL[card["relation"]], ptext="“" + html.escape(card["parallel_text"]) + "”",
                 pref=html.escape(card["parallel_label"] + " · paraphrase"))
    else:
        d["_hide"].append("bible")
    if card.get("news"):
        d["news"] = "<b>In the news</b>" + html.escape(card["news"]["text"])
    else:
        d["_hide"].append("news")
    return "card.html", d


def week_cards(card):
    end = dt.date.fromisoformat(card["date"])
    start = (end - dt.timedelta(days=6)).isoformat()
    return [c for c in all_cards(before=card["date"]) if c["date"] >= start]


def recap_data(card):
    wk = week_cards(card)
    if not wk:
        fail("no reading cards in the last 6 days to recap")
    roots, seen = [], set()
    for c in wk:
        k = c["root"]["translit"].lower()
        if k not in seen:
            seen.add(k)
            roots.append(c["root"])
    items = []
    for c in wk:
        p = passage(int(c["plan"]))
        r = f"{p['surah']}:{p['from']}" + (f"–{p['to']}" if p["to"] > p["from"] else "")
        items.append(f'<div class="item"><span class="r">{r}</span><span>{html.escape(c["title"])}</span></div>')
    tiles = [
        f'<div class="rt"><div class="l">{letters_html(x["letters"])}</div>'
        f'<div><div class="t">{html.escape(x["translit"])}</div><div class="w">{html.escape(x["word_translit"])}</div></div></div>'
        for x in roots
    ]
    last = max(int(c["plan"]) for c in wk)
    d = {
        "day": dt.date.fromisoformat(card["date"]).strftime("%a").upper(),
        "title": html.escape(card.get("title") or "This week in the Qur'an"),
        "sub": f"{len(items)} passages · {len(roots)} roots",
        "passages": "".join(items),
        "roots": "".join(tiles),
        "question": html.escape(card.get("question") or "Reread one passage aloud and point to each root you know."),
        "progress": f"Reading {last} of {len(PLAN)} · {round(100 * last / len(PLAN))}% of the plan",
        "date": fmt_date(card["date"]),
        "_hide": [],
    }
    return "recap.html", d


def render(card_path, out_path):
    card = json.loads(pathlib.Path(card_path).read_text(encoding="utf-8"))
    kind = card.get("type")
    if kind == "reading":
        tpl, data = reading_data(card)
    elif kind == "recap":
        tpl, data = recap_data(card)
    else:
        fail("type must be 'reading' or 'recap'")
    hide = data.pop("_hide")
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        br = p.chromium.launch()
        pg = br.new_page(viewport={"width": 1080, "height": 1350})
        pg.goto((ROOT / "template" / tpl).as_uri())
        pg.evaluate("([d, h]) => { for (const [k,v] of Object.entries(d)) { const e = document.getElementById(k); if (e) e.innerHTML = v; }"
                    " for (const id of h) document.getElementById(id).classList.add('hide'); }", [data, hide])
        pg.evaluate("document.fonts.ready")
        pg.wait_for_timeout(300)
        h = pg.evaluate("document.getElementById('card').scrollHeight")
        if h > MAX_HEIGHT:
            fail(f"card is too tall ({h}px, max {MAX_HEIGHT}); shorten the text")
        pg.locator("#card").screenshot(path=str(out_path))
        br.close()
    return card, h


if __name__ == "__main__":
    src = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else str(pathlib.Path(src).with_suffix(".png"))
    _, h = render(src, out)
    print(f"rendered {out} ({h}px tall)")
