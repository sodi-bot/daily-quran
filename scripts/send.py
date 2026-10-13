#!/usr/bin/env python3
"""Send a rendered card to Telegram.

Usage: python3 scripts/send.py cards/2026-10-14.json cards/2026-10-14.png
Needs env TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID.
Recap cards get the root meanings in the caption as tap-to-reveal spoilers.
"""
import html
import json
import os
import pathlib
import sys
import urllib.request
import uuid

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import render  # noqa: E402


def caption(card):
    e = lambda s: html.escape(s, quote=False)
    if card.get("type") == "recap":
        lines, seen = ["<b>Roots this week</b> (tap to reveal):"], set()
        for c in render.week_cards(card):
            r = c["root"]
            if r["translit"].lower() in seen:
                continue
            seen.add(r["translit"].lower())
            lines.append(f"{e(r['translit'])} · {e(r['word_translit'])} → <tg-spoiler>{e(r['meaning'])} · {e(r['word_meaning'])}</tg-spoiler>")
        return "\n".join(lines)
    lines = []
    if card.get("source_url"):
        lines.append(f"Source: {e(card['source_url'])}")
    if card.get("news"):
        lines.append(f"News: {e(card['news']['url'])}")
    if card.get("reading"):
        lines.append(f"Further reading: {e(card['reading'])}")
    lines.append("Arabic text: Tanzil.net · Bible: ASV (1901)")
    return "\n".join(lines)


def send_photo(token, chat_id, png_path, text):
    boundary = uuid.uuid4().hex
    parts = []
    for name, value in (("chat_id", chat_id), ("caption", text[:1024]), ("parse_mode", "HTML")):
        parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n'.encode())
    with open(png_path, "rb") as f:
        img = f.read()
    parts.append(
        f'--{boundary}\r\nContent-Disposition: form-data; name="photo"; filename="card.png"\r\n'
        f"Content-Type: image/png\r\n\r\n".encode() + img + b"\r\n"
    )
    parts.append(f"--{boundary}--\r\n".encode())
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendPhoto",
        data=b"".join(parts),
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        res = json.load(r)
    if not res.get("ok"):
        raise SystemExit(f"Telegram error: {res}")
    print("sent message", res["result"]["message_id"])


if __name__ == "__main__":
    card = json.load(open(sys.argv[1], encoding="utf-8"))
    send_photo(os.environ["TELEGRAM_BOT_TOKEN"], os.environ["TELEGRAM_CHAT_ID"], sys.argv[2], caption(card))
