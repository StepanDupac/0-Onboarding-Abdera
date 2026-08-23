# 12. How the work actually runs

## The rhythm

There is no ticket queue. A researcher owns a hypothesis from the literature search to the ledger
entry, and the unit of work is a **batch**: one family, one protocol, one verdict, one record.

A batch is typically one to three weeks. The dealer-gamma family in section 8 was unusually fast at
two days, because the sample gate killed the first endpoint before any expensive computation ran —
which is the pre-flight discipline paying for itself.

## What you are expected to produce

Whatever the outcome, a batch ends with the same five artifacts. This is the deliverable, and a
negative result produces all five exactly as a positive one does:

| | |
|---|---|
| **A frozen protocol** | with its hash in the ledger, written before outcomes were opened |
| **Canonical evidence** | the actual numbers, versioned, tied to a hashed input |
| **A ledger entry** | append-only: what was decided, on what evidence, on what date |
| **A register entry** | if the hypothesis is closed: what was tested, what closed it, what would make a retest legitimate |
| **A durable lesson** | if the batch produced one that generalises beyond its family |

## What good looks like

The researcher who is valuable here is not the one with the most ideas. It is the one whose
negative results are trustworthy enough that nobody has to repeat them.

Concretely:

- **Kills their own ideas fast.** The pre-flight arithmetic is ten minutes and it should be the
  first thing you reach for, including — especially — when you like the idea.
- **Writes the falsifier down first.** If you cannot state in advance what observation would make
  you abandon the hypothesis, you are not going to abandon it.
- **Reports the number that closed it.** "It didn't work" is not a result. "−7.43 ticks, 95%
  interval [−31.75, +18.93], and the real level was indistinguishable from a phantom 100 ticks
  away" is a result, and it is permanent.
- **Builds the measuring instrument before the experiment**, and calibrates it against a known
  answer first.
- **Names what they could not verify.** Every report ends with that section and it is never empty.

## Where the work lands

Everything you research is aimed at a **$50,000 prop-firm evaluation account** — see section 1. You
are not researching for a hypothetical book, and you are not researching for the firm's own capital
on day one. The route is concrete:

```
   your research   ->   frozen package   ->   tick-level measurement   ->   live demo account
   (this pack)          (hashed)              (the verdict)                 (real, prop-funded)
```

A candidate that survives all four stages is funded on a prop evaluation account and traded for
real. The firm carries the subscription cost; you carry the research. Researchers whose strategies
survive that route take on more over time, including the firm's own capital — but the prop route is
where the track record is built, and it is where everyone starts.

Two consequences worth internalising early:

- **Your objective function is the account's rules**, not an abstract Sharpe ratio. Time-to-pass,
  fees, and the drawdown floor are first-class research variables, and section 9 shows a case where
  optimising for them reversed the conventional answer.
- **A failed account is a bounded, expected cost**, not a disaster. The aggressive lane accepts that
  many accounts fail; what it does not accept is not knowing why.

## What we provide

- **Data.** Everything in section 4, and anything else the work needs — see the acquisition policy
  there. It is not a formality; it has been exercised.
- **Compute.** Local, and sized so that a full six-year backtest is minutes rather than hours.
- **A measurement engine you do not have to build.** Tick-level fills against real quotes under the
  firm's risk model, with a placebo suite, a Monte Carlo, walk-forward, and a look-ahead detector.
  Your job is to produce candidates worth its time.
- **The record.** Every result the firm has ever produced, including every failure, with the number
  that closed it. You will spend real time reading it, and it will save you more.

## What we ask

Speak plainly about weak evidence. The failure mode this firm guards against hardest is not a bad
idea — it is a mediocre result described in language that makes it sound better than it is. There
is no penalty here for saying "this does not work", and there is a large one for saying "this looks
promising" about something that does not.

## The exercise

`exercise/README.md` contains a task with a self-contained dataset. It takes a few hours and it is
the fastest way for both sides to find out whether this work suits you.

We are not looking for a strategy that makes money. We are looking at how you decide whether
something is real.
