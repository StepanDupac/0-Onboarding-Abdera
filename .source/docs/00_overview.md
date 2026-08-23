# 1. The role, and what this pack is

You are looking at the complete record of one day of quantitative research at Abdera Trading: one
hypothesis taken from the literature to a measured verdict, and one deliverable shipped. Nothing
here is idealised. The headline idea **died**, and the thing that shipped came from somewhere else.
That is the ordinary shape of the work, and it is why this is the pack we send to candidates
rather than a success story.

If you are strong in mathematics, statistics or physics and have never done this before, this pack
is written for you. It assumes you can read a derivation and write clean code. It assumes nothing
about markets.

## What the job actually is

A quant researcher here turns a vague idea into a falsifiable claim, tests it so that the answer
can be trusted, and writes down what was learned either way.

Notice what is not in that sentence. Not "finds strategies that make money" — that is the outcome
we want, but if you optimise for it directly you will produce results that look profitable and are
not, which is worse than producing nothing. The discipline is the product. A well-evidenced
negative result is a success, and we treat it as one.

The realistic ratio, from Abdera's own record: across research batches 005 to 016, more than
twenty families were tested. Almost all were rejected. Two survived far enough to be measured at
tick level by the firm's engine. One of those runs on a live demo account today.

**If a month of careful work ending in "this does not work, here is the number that closed it" would
feel like failure to you, this is the wrong job.** If it feels like a result, read on.

## The five stages

```
   research workspace  ->  frozen packages  ->  measurement engine  ->  permanent archive
   (you are here)          (hashed, versioned)   (issues the verdict)    (every result, forever)
                                                        |
                                                        v
                                                  live demo account
```

| Stage | The question it answers |
|---|---|
| **Research workspace** | Is this idea worth an hour of tick-level measurement? |
| **Frozen packages** | Is this package hashed, reproducible, and exactly what was measured? |
| **Measurement engine** | Does it survive the firm's risk model, and can the result be told from luck? |
| **Archive** | What did we try, what happened, where is the evidence? |
| **Live demo** | Which ones get real money, and what does the operator need to know? |

You work in stage one. Almost everything in this pack is about stage one, because that is the job
being offered.

**A result produced in the research workspace is a screening decision, not a measurement.** When we
say a candidate is worth promoting, we mean "worth an hour of tick-level measurement downstream" —
never "this works". Every dollar figure a researcher produces is pre-measurement. The word
*verdict* belongs to the measurement engine alone, and it is a different team's word.

That distinction is not modesty. The research engine simulates fills on one-minute bars; the
measurement engine walks every tick against the real bid and ask under the firm's risk model. A
matching signal trace is not a matching profit path.

## Where you start: a $50,000 prop account, not the firm's capital

**New researchers do not trade the firm's own capital.** You start on **proprietary-trading-firm
evaluation accounts, at the $50,000 size**, and everything in this pack is written for that
setting.

This is deliberate, and it is worth understanding before you decide whether the job appeals.

**It bounds the downside while you build a track record.** A prop account has a hard, external
drawdown limit. The worst case is a failed evaluation and a lost subscription fee — a known,
small, bounded number. Nobody has to decide how much of the firm's balance sheet to hand a
researcher whose work nobody has seen yet, which means you get to start immediately rather than
after months of proving yourself on paper.

**It is real money under real rules.** This is not a simulator. The account is live, the drawdown
is enforced by someone else, the daily flatten is mandatory, and the fee is charged whether or not
you pass. Every constraint below is a real constraint, and a strategy that ignores one does not
merely score badly — it fails.

**The constraints are what make the problem specific.** A researcher told "make money in futures"
has an unbounded, unfalsifiable brief. A researcher told "pass a $3,000 target against a $2,000
ratcheting drawdown, flat by the close, while paying monthly rent" has a real optimisation problem
with a measurable objective. Most of the interesting results in this pack — including the
counterintuitive one in section 9, where *more* risk per trade turned out to be correct — exist
only because the constraints are sharp.

**Progression follows a track record, not a job title.** Researchers whose candidates survive
tick-level measurement and hold up on live demo accounts take on more, including allocations of the
firm's own capital. That path is earned with measured results, and the prop route is where those
results get made. Nobody here started anywhere else.

## What we trade, and the constraint that shapes everything

Nasdaq and S&P futures, intraday, inside those evaluation accounts. The account rules are not a
detail — they are the objective function:

- a **$50,000** notional account with a **$2,000** trailing drawdown that ratchets up and never
  retreats;
- a **$3,000** profit target to pass;
- a **mandatory flatten** every afternoon, so nothing is held overnight;
- a **monthly subscription** for as long as the attempt takes.

That last one changes the mathematics of the whole problem. Because the account pays rent by the
month, **time is a cost**. A strategy that passes more reliably but takes three times as long can
be worth less than one that fails more often and resolves quickly. This is not intuition; it is
measured, and it is in section 9.

## How to read this pack

| | |
|---|---|
| `docs/01` | Where ideas come from, and the filter every idea passes before it costs anything |
| `docs/02` | The mathematics you do **before** writing code |
| `docs/03` | The data we hold, its traps, and how you get data we do not hold |
| `docs/04` | Building the first version, and the tests that catch a broken one |
| `docs/05` | Scaling the test: preregistration, controls, kill gates |
| `docs/06` | Promotion, packaging, and how a strategy gets its identity |
| `docs/07` | **Worked example one: the idea that died.** Read this one closely |
| `docs/08` | **Worked example two: the thing that shipped** |
| `docs/09` | The catalogue of what gets work thrown out |
| `code/` | Runnable implementations of everything above |
| `exercise/` | A task. If you want to be taken seriously as a candidate, do it |

Everything in `code/` runs with Python 3 and numpy and nothing else. Start with:

```bash
python3 code/preflight.py
```
