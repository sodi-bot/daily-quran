# daily-quran

A daily bite-size card on academic Qur'anic studies, tied to the day's news, sent to Telegram.

- `cards/YYYY-MM-DD.json` — one card per day, written by a scheduled Claude task (see `CARD_SPEC.md`)
- `scripts/render.py` — turns a card into a PNG (Playwright + `template/card.html`)
- `scripts/send.py` — sends the PNG to Telegram
- `.github/workflows/send-card.yml` — on every push of a new card: render, then send
- `data/` — Qur'an Arabic text (Tanzil Uthmani, see `data/TANZIL_NOTICE.txt`) and surah names
- `fonts/` — Inter and Amiri / Amiri Quran (SIL Open Font License, `fonts/OFL.txt`)

Repo secrets needed: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`.

To resend a card: Actions → Send daily card → Run workflow → enter the card path.
