# Daily Qur'an card: how to write one

The cards visit **every surah once, in the order of revelation reconstructed by Theodor
Nöldeke** (the academic standard), starting with 96 al-'Alaq (`data/plan.json`, 114 readings,
see `data/NOLDEKE_SOURCE.txt`). Short surahs are read whole; for long ones the card shows one
key passage. Each card is labelled with Nöldeke's period (Early, Middle, Late Meccan, Medinan).
Each card teaches **one Arabic root**, explains the passage from an **academic angle**, and,
when there is one, compares it with a **Bible parallel** and the **Lutheran** reading of it.

Which card to write today (Asia/Jakarta):
- **Sunday**: a weekly recap card (`type: "recap"`), built automatically from the week's cards.
- **Other days**: if the most recent reading card has no answer card yet (no `answer` whose
  `answers` is that reading's date), write its **answer card** (`type: "answer"`). Otherwise
  write the next **reading card** (`type: "reading"`). This gives Reading / Answer / Reading /
  Answer / Reading / Answer / Recap, and keeps the pairs together if a day is missed.

Write `cards/YYYY-MM-DD.json` (Jakarta date), render it to check, then commit and push to
`main`. The GitHub Action renders the PNG and sends it to Telegram.
`examples/reading-1-alaq.json` and `examples/answer-1-alaq.json` are a model reading and its answer.

## Sunday: recap

Write only:
```json
{"type": "recap", "date": "YYYY-MM-DD"}
```
Optionally add `"question"` (≤ 24 words): a short prompt that links the week's passages.
If there were no reading cards in the past 6 days, skip the recap and write a reading card instead.

## Answer card

Answers the previous reading card's question. Reread that card first.

- **`debate` question**: summarise the main positions (2–3 points), who holds each, and the
  evidence. Name a winner only when there is real scholarly consensus; otherwise `bottom_text`
  says where the evidence leans and what is still open.
- **`open` question**: one point `What research comes close` (the nearest real scholarship,
  named), and one point labelled exactly `One possible reading`: a reasoned reading of the
  wording, argued from the text, never a theological ruling. `bottom_text` gives the strongest
  counter-view so the reader has something to weigh.
- Pick the **Arabic phrase** the question turns on (max 5 words) by verse and word numbers
  from `python3 scripts/passage.py N [S:A-B]`.
- Verify every claim; `source_url` is required and must support the main point.

| field | rules |
|---|---|
| `type` | `"answer"` |
| `date` | today, `YYYY-MM-DD` |
| `answers` | date of the reading card being answered |
| `title` | ≤ 9 words: the answer in a phrase |
| `phrase` | `{"verse", "from", "to", "translit", "meaning"}`: word numbers in that verse |
| `points` | 2–3 of `{"label" ≤ 5 words, "text" ≤ 45 words, "who" ≤ 10 words, optional}`; `**bold**` allowed |
| `bottom_text` | ≤ 32 words. Shown as “Where it stands” (debate) or “Weigh it” (open) |
| `source_label`, `source_url` | required, as for reading cards |

The card also shows the reading's root again as a review, automatically.

## Reading card

1. Run `python3 scripts/passage.py`. It prints the next reading, plus the roots taught so far.
   Never type Arabic verse text yourself.
   - **Whole surah**: every word is printed with numbers. Use the plan's range; no `verses` field.
   - **Long surah**: the whole surah is printed. Choose **one key passage** (max 5 consecutive
     verses, 450 Arabic characters): the passage scholars most discuss, the one that best shows
     the surah's main theme or what is typical of its period, and, where the surah has one, a
     passage with a real Bible parallel (Joseph in 12, Mary in 19, Moses in 20, Abraham in 37…).
     Then run `python3 scripts/passage.py N S:A-B` for word numbers and set `verses` to `S:A-B`.
     Say in the body, briefly, where the passage sits in the surah if that helps.
   - Nöldeke dates some verses later than their surah (e.g. 73:20 is usually seen as Medinan).
     If your passage is one of these, say so.
2. **Root.** Pick one root that appears in the passage. Prefer a new, common, useful root
   (high frequency in the Qur'an, or key to this passage). About one card in five, choose a
   root already taught (a review); the card marks it automatically. Point to the word by
   `verse` and `index` (the numbers from passage.py).
3. **Academic angle (the body).** One concrete thing scholars discuss about this passage:
   - word history (Aramaic/Syriac/Ethiopic/South Arabian links), e.g. Jeffery, *Foreign Vocabulary*; Sinai, *Key Terms of the Qur'an*
   - early interpreters disagreeing (al-Tabari, Ibn Kathir, Ibn Abbas, Ibn Mas'ud)
   - dating and structure (Nöldeke's chronology, Neuwirth, Sinai), rhyme and form; how this
     passage fits its period, and what changes from earlier periods
   - historical context of late antique Arabia (inscriptions, Himyar, Byzantium, Persia)
   - manuscripts and readings (Birmingham, Sana'a, qira'at), van Putten, Sadeghi
4. **Bible parallel, if any.** If a real biblical parallel exists, add it with a `relation`,
   and say in the body how Lutherans read the biblical side when there is a real Lutheran
   angle: Luther's own writings (Small and Large Catechism, lectures on Genesis, prefaces),
   the Augsburg Confession and Book of Concord, or core themes (sola scriptura, grace and
   faith, law and gospel, theology of the cross, original sin). **The Bible and its Lutheran
   reading come first.**
   - **Other late antique texts** (Syriac Christian homilies and legends, apocryphal gospels,
     Mishnah, Talmud, Midrash) are often closer to the Qur'an than the Bible is. When the
     passage has a biblical parallel too, keep the Bible in `bible` and mention the other
     text briefly in the body (e.g. Luke 1 as the parallel for Mary in Surah 19, with the
     Protevangelium of James named in the body). Use `parallel_label` / `parallel_text`
     instead of `bible` only when there is no real biblical parallel (e.g. the Seven Sleepers
     in Surah 18 and Jacob of Serugh; Iblis refusing to bow and the Cave of Treasures).
   - Good starting points: Corpus Coranicum's database of texts from the Qur'an's
     environment (https://corpuscoranicum.org); Sidney Griffith, Gabriel Said Reynolds,
     Joseph Witztum, Holger Zellentin, Angelika Neuwirth. Treat a parallel as part of a shared
     late antique conversation, not proof of copying; present contested theories (e.g.
     Luxenberg's Syriac readings) as contested.
   - Many passages have no real parallel. Then leave it out; never force one.
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
| `verses` | only for long surahs: the key passage, `S:A-B`, max 5 verses |
| `title` | ≤ 9 words, sentence case |
| `translation` | ≤ 60 words, your own plain English rendering of the whole passage |
| `root.letters` | the root letters in Arabic separated by spaces, e.g. `"ر ح م"` |
| `root.translit` | e.g. `"r-ḥ-m"` (use the same spelling every time a root returns) |
| `root.meaning` | core meaning, ≤ 4 words |
| `root.verse`, `root.index` | position of the word in the passage, from passage.py |
| `root.word_translit`, `root.word_meaning` | that word, e.g. `"al-raḥmān"`, `"the Most Merciful"` |
| `body` | ≤ 60 words; the academic angle, plus the Lutheran reading if there's a parallel. Mark 2–3 phrases with `**bold**` |
| `bible` + `relation` | optional. Bible ref like `Matthew 6:9-10` (max 3 verses; text comes from ASV automatically). `relation`: `aligns`, `differs`, `retells`, or `echo` |
| `parallel_label` + `parallel_text` + `relation` | instead of `bible`, only when there is no real biblical parallel: non-biblical texts (Mishnah, infancy gospels, Syriac homilies and legends); text ≤ 35 words, your paraphrase |
| `news` | optional `{"text": "≤ 22 words", "url": "https://..."}` |
| `question` | ≤ 24 words, one question about the text. Set `question_type`: `debate` when it asks the reader to weigh a real scholarly disagreement (ideally the one in the body), or `open` when it goes beyond the research: a fresh angle on the wording or a connection scholars rarely make. Mix both kinds over the week, roughly half each. Open questions must still be fair to the text: no false claims, no premise the wording contradicts |
| `question_type` | `debate` (card label: “Scholars debate”) or `open` (card label: “Open question”) |
| `source_label` | short: the key scholarly / Lutheran source(s) |
| `source_url` | **required** https link to the main source behind the body: the scholarly article, book page, inscription record or primary text (e.g. bookofconcord.org). Open it with WebFetch and confirm it supports the claim. Prefer open-access pages over paywalls |
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
