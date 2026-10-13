# daily-quran

A daily bite-size card comparing a Qur'an passage with its biblical parallel (academic angle, Lutheran lens), sent to Telegram.

- `cards/YYYY-MM-DD.json` — one card per day, written by a scheduled Claude task (see `CARD_SPEC.md`, `TOPICS.md`)
- `examples/` — model card
- `scripts/render.py` — turns a card into a PNG (Playwright + `template/card.html`)
- `scripts/send.py` — sends the PNG to Telegram
- `.github/workflows/send-card.yml` — on every push of a new card: render, then send
- `data/` — Qur'an Arabic text (Tanzil Uthmani, see `data/TANZIL_NOTICE.txt`), surah names, and the American Standard Version Bible (1901, public domain)
- `fonts/` — Inter and Amiri / Amiri Quran (SIL Open Font License, `fonts/OFL.txt`)

Repo secrets needed: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`.

To resend a card: Actions → Send daily card → Run workflow → enter the card path.
