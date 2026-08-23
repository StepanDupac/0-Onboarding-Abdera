# 5. Building it, and the first small tests

## The strategy contract

A strategy is **one file** that runs byte-for-byte in the research workspace, in the firm's
measurement engine, and in the live runtime. Annotated template: `code/strategy_template.py`.

The rules that a linter enforces, each of which exists because breaking it destroyed a result:

| Rule | Why |
|---|---|
| One registered strategy class per file, no cross-strategy imports | two classes in one file defeat the identity hashing |
| Imports from the portable kit only, never engine internals | that is what makes the file portable |
| **No comments and no docstrings** | explanation goes in the notes; names carry the meaning |
| No numeric literals outside declared parameters | every tunable is part of the frozen record |
| Publish the series you intend to compare, read it back by name | prevents the unit bug |
| Guard every comparison against an indicator with a finiteness check | `nan > x` is `False`, so a missing guard yields a strategy that silently never trades |
| A signal formed on a bar fills on the next bar or later | anything else is look-ahead |

That third rule surprises people. In a research repository, a comment is a claim about the code
that no test enforces and that drifts silently away from what the code does. Explanation belongs in
the notes file, which is reviewed as documentation; the code should be readable from its names
alone. This pack's `code/` directory is annotated because it is teaching material — the real thing
is not.

## Pilot before you build

Pull a small slice of the data first — a few weeks — and check the shape of it before the
hypothesis has any chance to make you credulous.

In the worked example the pilot was three weeks: 76 files, 703,000 rows, one minute of wall clock.
It immediately exposed a definition problem that would have silently poisoned everything.

The model computes "walls" — the strikes carrying the most dealer gamma. Computed across the full
90-day option book, the biggest strikes were far-out-of-the-money hedges sitting hundreds of points
from the market, which is a true statement about the book and useless for an intraday level. The
definition was narrowed to contracts expiring within ten days **before any outcome was opened**, and
the change was recorded as a preregistered definition rather than a tuning decision.

The distinction is everything. Narrowing a definition *before* seeing outcomes is modelling.
Narrowing it *after* is fitting, and it produces a result that will not survive contact with new
data.

## The three tests that catch a broken strategy

Run all three before the first real backtest.

### Units

Every comparison must be tick index against tick index. Search the file for any call that returns a
display price and justify each one. On the Nasdaq contract the two units differ by a factor of
four, and the comparison does not raise — it produces a number.

### Branch reachability

For every clause of your predicate, count how many bars satisfy it in isolation and cumulatively.
**A clause firing on 0% or 100% of bars is a bug until proved otherwise.** This takes ten minutes.

The real output from the shipped strategy in section 9, over 492,417 candidate bars:

| clause, applied in order | bars surviving |
|---|---:|
| regular trading hours | 492,417 |
| all features finite | 446,907 |
| inside the entry window | 189,000 |
| overnight displacement gate | 67,500 |
| directional drive gate | 32,400 |
| not a contract-roll session | 32,400 |
| breakout cross, either direction | 828 |

and in isolation, the check that matters most: **4,645 upward crossings against 4,219 downward**.
Both directions alive and balanced.

Three strategies in this firm's history failed exactly this. In one, a comparison between a display
price and a tick index made the long branch unsatisfiable and the short condition true on *every*
bar — the whole branch was dead in both directions, not biased, dead. The strategy ran, reported,
and produced a verdict. In another, found during the export in section 9, the same unit error pinned
the direction to short on every session and rendered a magnitude threshold inert; it had already
been shipped and was waiting to be measured.

### Causality

Nothing that computes indicators over the whole history may use information from after the bar it
labels. No centring on the full sample, no filters that run forwards and backwards, no fitting on
data that includes the future. The engine enforces the obvious cases by refusing negative lags; the
subtle ones are yours to avoid, and the standard test is to corrupt the tail of the input and assert
that the earlier output is byte-identical.

## Then, and only then, the first backtest

One contiguous run over the full history on a single account. Not a grid of overlapping windows —
that comes later and answers a different question. Two statistics are mandatory:

- **coverage**: sessions where an order was submitted, divided by eligible sessions;
- **last trade date**, compared against the end of the window.

A run whose last trade is years before the window ends did not measure a signal. It measured a
latch. Three strategies at this firm reported healthy status while trading nothing for years,
because nothing had breached — because nothing had traded. Section 10 has the causes.
