# Daily Qur'an card: how to write one

The cards read through the Qur'an **in order**, a few verses a day, starting with Al-Fatiha and
then the short surahs of Juz' Amma from 114 back to 78 (`data/plan.json`, 146 readings).
Each card teaches **one Arabic root**, explains the passage from an **academic angle**, and,
when there is one, compares it with a **Bible parallel** and the **Lutheran** reading of it.

- **Monday–Saturday**: a reading card (`type: "reading"`).
- **Sunday**: a weekly recap card (`type: "recap"`), built automatically from the week's cards.

Write `cards/YYYY-MM-DD.json` (Jakarta date), render it to check, then commit and push to
`main`. The GitHub Action renders the PNG and sends it to Telegram.
`examples/reading-1-fatiha.json` is a model reading card.

## Sunday: recap

Write only:
```json
{"type": "recap", "date": "YYYY-MM-DD"}
```
Optionally add `"question"` (≤ 24 words): a short prompt that links the week's passages.
If there were no reading cards in the past 6 days, skip the recap and write a reading card instead.

## Monday–Saturday: reading

1. Run `python3 scripts/passage.py`. It prints the next reading with every Arabic word
   numbered, plus the roots taught so far. Never type Arabic verse text yourself.
2. **Root.** Pick one root that appears in the passage. Prefer a new, common, useful root
   (high frequency in the Qur'an, or key to this passage). About one card in five, choose a
   root already taught (a review); the card marks it automatically. Point to the word by
   `verse` and `index` (the numbers from passage.py).
3. **Academic angle (the body).** One concrete thing scholars discuss about this passage:
   - word history (Aramaic/Syriac/Ethiopic/South Arabian links), e.g. Jeffery, *Foreign Vocabulary*; Sinai, *Key Terms of the Qur'an*
   - early interpreters disagreeing (al-Tabari, Ibn Kathir, Ibn Abbas, Ibn Mas'ud)
   - dating and structure (Nöldeke's chronology, Neuwirth, Sinai), rhyme and form
   - historical context of late antique Arabia (inscriptions, Himyar, Byzantium, Persia)
   - manuscripts and readings (Birmingham, Sana'a, qira'at), van Putten, Sadeghi
4. **Bible parallel, if any.** If a real biblical (or other late antique) parallel exists, add
   it with a `relation`, and say in the body how Lutherans read the biblical side when
   there is a real Lutheran angle: Luther's own writings (Small and Large Catechism, lectures
   on Genesis, prefaces), the Augsburg Confession and Book of Concord, or core themes
   (sola scriptura, grace and faith, law and gospel, theology of the cross, original sin).
   Many passages have no real parallel. Then leave it out; never force one.
5. **News, if any.** Add `news` only when today's news connects naturally to this passage.
   Never as commentary on a tragedy, war or election.

Fairness and accuracy:
- Describe, don't adjudicate. Never say which scripture is right or superior.
- Present scholarly debates as debates and name the source.
- Verify every claim (WebSearch/WebFetch) before using it. If you can't verify it, choose another angle.

## Reading card fields

| field | rules |
|---|---|
| `type` | `"reading"` |
| `date` | `YYYY-MM-DD` (Asia/Jakarta) |
| `plan` | reading number from passage.py |
| `title` | ≤ 9 words, sentence case |
| `translation` | ≤ 60 words, your own plain English rendering of the whole passage |
| `root.letters` | the root letters in Arabic separated by spaces, e.g. `"ر ح م"` |
| `root.translit` | e.g. `"r-ḥ-m"` (use the same spelling every time a root returns) |
| `root.meaning` | core meaning, ≤ 4 words |
| `root.verse`, `root.index` | position of the word in the passage, from passage.py |
| `root.word_translit`, `root.word_meaning` | that word, e.g. `"al-raḥmān"`, `"the Most Merciful"` |
| `body` | ≤ 60 words; the academic angle, plus the Lutheran reading if there's a parallel. Mark 2–3 phrases with `**bold**` |
| `bible` + `relation` | optional. Bible ref like `Matthew 6:9-10` (max 3 verses; text comes from ASV automatically). `relation`: `aligns`, `differs`, `retells`, or `echo` |
| `parallel_label` + `parallel_text` + `relation` | instead of `bible`, for non-biblical texts (Mishnah, infancy gospels, Syriac legends); text ≤ 35 words, your paraphrase |
| `news` | optional `{"text": "≤ 22 words", "url": "https://..."}` |
| `question` | ≤ 24 words, one open question that sends the reader back to the text |
| `source_label` | short: the key scholarly / Lutheran source(s) |
| `source_url` | optional https link to a primary or scholarly source |
| `reading` | optional: one book or article to go deeper |

Use curly quotes (“ ” ’) inside text so the JSON stays valid.

## Check, then publish

```
pip install playwright --break-system-packages   # if needed
python3 scripts/render.py cards/YYYY-MM-DD.json /tmp/card.png
```
The renderer refuses bad references, a root that doesn't fit the chosen word, and text that's
too long. Look at the PNG: nothing cut off, highlighted word correct, ≤ 1900px tall.
Then `git add cards/YYYY-MM-DD.json && git commit -m "Card YYYY-MM-DD" && git push`.
Don't commit the PNG.
