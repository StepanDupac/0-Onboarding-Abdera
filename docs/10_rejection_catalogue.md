# 11. What gets work thrown out

Every item is a real failure from this firm's history. None is a style preference. Read this before
your first strategy and again before your first export.

## Failures that make a strategy unmeasurable

These are the worst kind, because the strategy still runs, still reports, and still produces a
verdict — about something other than what you think.

### Mixing price units

Every price the engine hands a strategy is an **integer tick index**, not a price. On the Nasdaq
contract they differ by a factor of four. Comparing one against the other does not raise; it
produces a number.

Measured on one real strategy, over the 32,444 bars where every input was finite:

| condition | before the fix | after |
|---|---:|---:|
| `close > long level` | **0** | 11,124 |
| `close < short level` | **32,444** | 8,456 |

The long branch was unsatisfiable and the short condition was true on every bar, which made its
crossing requirement unsatisfiable in turn. **The whole branch was dead in both directions** — not
biased, dead — and the strategy had produced a full set of results.

This has now happened **three times** at this firm, most recently in a package that had already
shipped. The defence is mechanical: publish the series you intend to compare and read it back by
name, then count how many bars satisfy each clause.

### Sizing off a quantity that ratchets

Live headroom — the distance to your drawdown floor — is not a risk budget. Under a trailing
drawdown the floor rises with your high-water mark and **never retreats**, so after the first
drawdown headroom stops being a budget and becomes a distance that only shrinks.

Two strategies sized off it. Headroom froze at `$506.92`, the computed quantity floored to zero, and
the strategy was **silent for 2.25 million bars** — nine trades in seven years — while reporting a
healthy status the entire time. Nothing breached, because nothing traded.

Latch a base budget once from the account's *starting* allowance. Use live headroom only as a cap
that can shrink the position, never as the base.

### A latch with no clearing condition

Two strategies set a portfolio lock when drawdown reached a threshold and cleared it **nowhere**.
The lock closed 25 sessions into a seven-year backtest and stayed closed for the remaining 6.9
years.

Every state variable that survives a day needs a documented clearing condition and a test for it.
Initialisation at start-up is not a clearing condition. If the intended condition genuinely is
"never", say so in the notes and accept that the backtest measures only the period before it fired.

### `quantity == 0` as a silent return

A strategy that declines to size is indistinguishable in the output from one that saw no signal.
That is precisely how the failure above went unnoticed for an entire research programme. Record it
as an event.

## Failures that make evidence meaningless

### Windowed grids instead of a contiguous run

The tempting design is a grid of overlapping fixed-length windows, each starting a fresh account.
It is a start-date sensitivity study, and it is **structurally blind to any state that survives a
day** — a latch, a counter, a peak, an account floor.

Two strategies scored five of eight joint passes on such a grid. The same strategies in a
contiguous single-account run traded almost nothing for years. Both reports were arithmetically
correct about different experiments; only one was about the strategy.

### Reporting a mean without its concentration

Report the mean after removing the top 5% of trades beside the untrimmed mean, and a per-year panel.

One strategy earned `+17.68` ticks per trade. Twenty trades out of 616 — three trading days a year —
supplied **55% of everything it earned in seven years**. Remove them and it lands within 4% of the
threshold it was supposed to clear.

Concentration is not automatically disqualifying; breakout strategies are supposed to look like
this. What is disqualifying is reporting the headline without it.

### A win rate without its geometric null

A win rate is a statement about barrier geometry until you prove otherwise. In a sweep of twenty
mean-reversion cells, widening the stop and shrinking the target moved the win rate from 13.9% to
**79.3%** while the mean stayed pinned near zero. That monotone gradient with a flat mean is the
signature of no drift — it is what a martingale looks like.

Report your win rate next to `1/(1+RR)` every time.

### Optimising against a subsample selected by a filter

An early study recorded the research engine as "3.5× more pessimistic" than a hand reconstruction,
which invited a correction factor. The gap was an artifact of comparing against a gate-truncated
subsample rather than a random one. On like-for-like samples the two agreed within noise.

When two measurements disagree, first prove they are being fed the same trades. Almost every
cross-engine discrepancy in this firm's history has been a comparison error.

## Failures of process

**Editing a frozen artifact to make a check pass.** Frozen sources, protocols, manifests and hash
constants are an audit record, not configuration. If an upstream change breaks a frozen check,
write a disclosure and let the owner decide. Making the suite green by rewriting what was known at
decision time destroys the only thing that made the record worth keeping.

**Running diagnostics after a gate has failed.** Once a kill gate fails, every further statistic is
a search for a reason to continue. Stop.

**Reporting the exploration window and calling the confirmation window "needs more data".** A cell
that inverts out of sample is a negative result. Say so.

**Narrowing a definition after seeing outcomes.** Before outcomes, it is modelling. After, it is
fitting. The distinction is invisible in the final artifact unless the protocol was frozen first,
which is the entire reason protocols are frozen.

**Quietly designing around an assumed constraint.** If a downstream system appears unable to support
something your work needs, state the dependency and ship whatever makes it cheap to implement. Do
not silently remove the feature — the constraint may not be real, and you will have thrown away a
result to satisfy it.
