# Daily Qur'an card — how to write one

One card a day: a short, academic look at a Qur'an passage, hooked to something in the news.
Write `cards/YYYY-MM-DD.json` (Jakarta date), render it to check it, then commit and push to `main`.
The GitHub Action renders the PNG and sends it to Telegram.

## 1. Pick the hook (news from the last 1–2 days)

Read a few front pages (e.g. aljazeera.com/news, bbc.com/news/world, theguardian.com/world,
channelnewsasia.com). Prefer stories with a **natural thematic link** to a passage:
weather and nature (haze, floods, drought, earthquakes), migration and travel, trade and
fair measure, famine and food, science and astronomy, archaeology, manuscript or museum news,
justice and courts, orphans and the poor, language and translation, calendars and moon sightings.

Rules:
- Never present a verse as commentary on, prediction of, or judgment about a current tragedy,
  conflict, election or named politician. No "this is God's punishment" framing of disasters.
- Don't take sides in contested political conflicts. If the only big stories are wars or
  elections, use a quieter story or a calendar hook (an anniversary, a find, a festival).
- If no link is natural, say so plainly in the body ("Not in the news today, but...")
  rather than forcing one.
- Check `cards/` first: don't reuse a passage used in the last 60 days, and vary surahs.

## 2. Pick the angle (academic, historical-critical)

Each card teaches one concrete thing scholars actually discuss, for example:
- how early interpreters disagreed (Ibn Mas'ud vs Ibn Abbas, al-Tabari's reports)
- a word's meaning, root, or a loanword (Syriac, Aramaic, Ethiopic, Greek), e.g. Jeffery, *Foreign Vocabulary*
- parallels with the Bible, Jewish or Syriac Christian literature, and how the Qur'an reworks them
- dating and structure (Meccan/Medinan, Nöldeke's chronology, Sinai, Neuwirth)
- manuscripts and variant readings (Birmingham, Sana'a, qira'at), van Putten, Sadeghi
- historical context of late antique Arabia (inscriptions, Himyar, Byzantium, Persia)

Only state what you are confident is in the scholarship. Name the scholar or source.
Present debates as debates. Respectful, neutral tone toward believers and sceptics alike.

## 3. Fields

| field | rules |
|---|---|
| `date` | `YYYY-MM-DD` (Asia/Jakarta) |
| `tag` | default `Qur'an & the news`; `Qur'an & history` on days with no news hook |
| `icon` | one of: book, scroll, cloud, smoke, water, leaf, globe, scale, flame, star, moon, people, mountain, seed, ship |
| `title` | ≤ 9 words, sentence case, a phrase not a question |
| `verses` | `S:A` or `S:A-B`, max 4 verses. The renderer pulls the exact Arabic from `data/quran-uthmani.json` — never type Arabic yourself |
| `translation` | ≤ 45 words, your own plain English rendering (don't copy a published translation) |
| `body` | ≤ 75 words (aim 50–65). 1 sentence on the news, the rest on the scholarship. Mark 2–3 key phrases with `**bold**` |
| `question` | ≤ 26 words, one open question that sends the reader back to the text |
| `source_label` | short: outlet + date, plus the scholarly source |
| `source_url` | https link to the news story used |
| `reading` | optional: one book or article for going deeper |

Use curly quotes (“ ” ’) inside text so the JSON stays valid.

## 4. Check, then publish

```
pip install playwright --break-system-packages   # if needed
python3 scripts/render.py cards/YYYY-MM-DD.json /tmp/card.png
```
Look at the PNG: nothing cut off, Arabic matches the verse reference, card ≤ 1600px tall.
Then `git add cards/YYYY-MM-DD.json && git commit -m "Card YYYY-MM-DD" && git push`.
Don't commit the PNG.
