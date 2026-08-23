# Candidate exercise

A few hours. Self-contained: Python 3 and numpy, nothing else. No market knowledge required.

**We are not looking for a strategy that makes money. We are looking at how you decide whether
something is real.** A correct "there is nothing here" is a complete pass.

---

## Setup

```bash
python3 code/make_sample_data.py
```

This writes `exercise/data/sessions_a.csv` and `sessions_b.csv`, 500 synthetic sessions each, plus
`MANIFEST.json` describing the columns.

**One of the two files contains a planted effect. The other is pure noise.** The answer is base64-encoded in
`exercise/data/ANSWER.txt` so that seeing it is a deliberate act rather than an accident while
browsing the repository. Reveal it with `python3 exercise/reveal_answer.py`, and only after you
have committed to an answer in writing.

Both files also contain a **real** volatility difference between the two regime labels. That is
deliberate: it is the shape of the true finding in the worked example, where the option book priced
magnitude and not direction. A method that reports "an effect" in both files has measured
volatility and called it direction — the exact error that closed the real family.

## Columns

| Column | Meaning |
|---|---|
| `session_date` | trading date |
| `regime_sign` | `-1` or `+1`, a state published **before** the open |
| `open_ref` | reference price at the open, index points |
| `published_level` | a level published **before** the open, index points |
| `session_high` / `session_low` | session extremes |
| `close_330` | session close |
| `data_quality` | share of the source that was on time and usable |

One tick is 0.25 index points. Report everything in ticks.

---

## Part 1 — on paper, before any code (30 minutes)

You are considering a bracket strategy on these sessions: enter at the open in the direction away
from `published_level`, stop `S` ticks against you, target `T` ticks in favour. Round-turn cost is
**6 ticks**.

1. For `S = 20, T = 40` and for `S = 20, T = 200`, compute the geometric breakeven win rate, the
   win-rate excess the signal must manufacture to cover cost, and the win rate required to clear a
   1.5× cost margin.
2. Which geometry would you pursue, and why — in one paragraph, using your numbers.
3. State the **falsifier**: the specific observation that would make you abandon the hypothesis
   that `published_level` organises these sessions. Write it before you look at any outcome.

`code/preflight.py` implements this arithmetic. Use it to check yourself, not to skip the thinking.

## Part 2 — the test (2-3 hours)

Decide which file contains the planted effect, using the method rather than by peeking.

Write your own screen. `code/screen.py` is a working reference — read it, but a submission that is
a copy with the names changed tells us nothing.

Your screen must include, at minimum:

- **a single primary endpoint**, named in writing before you compute it;
- **uncertainty that respects sessions as the unit of independence** — trades within a session are
  not independent observations;
- **a phantom-level control**: repeat everything against levels that are definitely not special,
  and show that the real level beats them;
- **a control that scrambles the regime labels**;
- **the quality gate** applied at 0.85;
- **kill gates evaluated in order, stopping at the first failure**, and a statement of which gates
  were consequently never evaluated.

## Part 3 — the report (1 page)

Write it as though the next researcher will rely on it and you will not be available.

1. Your primary endpoint, and why that one.
2. The result for each file: the statistic, its interval, and your verdict.
3. What your controls showed.
4. **Which file has the planted effect, and your confidence.**
5. A "not verified" section. It must not be empty.
6. If you had another week and any dataset in the world, what would you do next and why?

Then run `python3 exercise/reveal_answer.py`.

**If you were wrong, say so in the report and diagnose why.** A candidate who gets it wrong and
correctly identifies which step failed is more interesting to us than one who gets it right and
cannot say how.

---

## What we assess

| | |
|---|---|
| **Judgment** | Did you kill the bad geometry in Part 1 on arithmetic alone? |
| **Method** | Are your controls real, or decorative? Did you stop at the first failed gate? |
| **Honesty** | Does the report state what it does not know? Is the confidence calibrated? |
| **Code** | Readable, deterministic, seeded, reproducible by us. |
| **Writing** | Could a colleague act on this without asking you a question? |

## What loses points

- A significant result with no control that could have shown it was spurious.
- Sweeping many variants and reporting the best without accounting for the search.
- Reporting an effect in **both** files. Read the note about volatility above.
- Any statistic computed after a kill gate has already failed.
- An empty, or absent, "not verified" section.

## Submitting

Your code, your report, and the exact commands to reproduce. Tell us how long it took.
