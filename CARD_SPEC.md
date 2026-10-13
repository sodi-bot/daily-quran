# Daily card: Qur'an × Bible, through a Lutheran lens

One card a day. Each card pairs a Qur'an passage with its biblical (or other late antique)
parallel, says plainly **where they meet or part**, explains how **academic scholarship**
accounts for the relationship, and how the **Lutheran tradition** reads the biblical side.

Write `cards/YYYY-MM-DD.json` (Jakarta date), render it to check it, then commit and push to
`main`. The GitHub Action renders the PNG and sends it to Telegram.
`examples/adam-forgiven.json` is a model card.

## 1. Pick the pairing

Take the next unused row of `TOPICS.md` (lowest `#` not yet used as `topic` in `cards/`).
You may swap in a news hook instead **only** when today's news connects naturally to a
pairing (e.g. a manuscript find, an archaeology story, Ramadan or Easter, a flood for Noah).
Then set `tag` to `news`, keep the Bible parallel, and use one sentence of the body for the news.

## 2. What the body must do (≤ 70 words, aim 55–65)

In this order, briefly:
1. **What the two texts share** and **where they differ**, concretely (one detail each).
2. **The scholarly explanation**: e.g. the Qur'an reworking biblical or post-biblical
   traditions (midrash, Syriac Christian homilies, infancy gospels), Arabic word history,
   dating, or a debate between named scholars or early interpreters.
3. **The Lutheran reading** of the biblical side, when there is a real one: Luther's own
   writings (lectures on Genesis, Small and Large Catechism, prefaces to the Bible, On
   Secular Authority), the Augsburg Confession / Book of Concord, or core Lutheran themes
   (sola scriptura, sola gratia/fide, law and gospel, theology of the cross, original sin,
   Christ as the centre of Scripture). Also fair game: Lutheran-rooted historical criticism
   (Wellhausen, Gunkel, Bultmann) and the fact that Luther wrote a preface to Bibliander's
   1543 Latin Qur'an.

Mark 2–3 key phrases with `**bold**`.

## 3. Rules for fairness and accuracy

- Describe, don't adjudicate. Never say which scripture is right, corrupted, or superior.
  Give each tradition's self-understanding in its own terms.
- Luther's polemical writings about Islam ("the Turk") may be mentioned as history, plainly
  labelled, never adopted.
- Present scholarly debates as debates. Name the source (Reynolds, Sinai, Neuwirth,
  Griffith, Zellentin, Witztum, el-Badawi, van Putten; al-Tabari, Ibn Kathir; Luther, Book of Concord).
- Only state what you have verified. If an angle in `TOPICS.md` can't be verified, change it.
- No forced links to current tragedies, wars or elections.

## 4. Fields

| field | rules |
|---|---|
| `topic` | the `#` from TOPICS.md |
| `date` | `YYYY-MM-DD` (Asia/Jakarta) |
| `tag` | `bible` (default) or `news` |
| `relation` | `aligns` (Where they meet), `differs` (Where they part), `retells` (Same story, retold) |
| `title` | ≤ 9 words, sentence case |
| `verses` | Qur'an `S:A` or `S:A-B`, max 4 verses. Arabic is pulled automatically from `data/quran-uthmani.json`; never type Arabic |
| `translation` | ≤ 40 words, your own plain English rendering of the Qur'an verses |
| `bible` | Bible ref like `Genesis 3:7` or `Matt 19:23-24`, max 3 verses. Text is pulled from `data/bible-asv.json` (ASV 1901) |
| `parallel_label` + `parallel_text` | instead of `bible`, for non-biblical texts (e.g. `Infancy Gospel of Thomas 2`); `parallel_text` ≤ 35 words, your own paraphrase |
| `body` | ≤ 70 words, see section 2 |
| `question` | ≤ 24 words, one open question comparing the two texts |
| `source_label` | short: the key scholarly / Lutheran source(s) |
| `source_url` | optional https link (a primary text, e.g. bookofconcord.org, or the news story) |
| `reading` | optional: one book or article to go deeper |

Use curly quotes (“ ” ’) inside text so the JSON stays valid.

## 5. Check, then publish

```
pip install playwright --break-system-packages   # if needed
python3 scripts/render.py cards/YYYY-MM-DD.json /tmp/card.png
```
Look at the PNG: nothing cut off, Arabic and Bible text match the references, ≤ 1750px tall.
Then `git add cards/YYYY-MM-DD.json && git commit -m "Card YYYY-MM-DD" && git push`.
Don't commit the PNG.
