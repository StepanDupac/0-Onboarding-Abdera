# 6. Scaling the test

The small tests told you the strategy is not broken. They said nothing about whether it works. This
section is how you find out in a way that will still be true next year.

## Preregistration

Before any outcome is computed, write the protocol down and freeze it. Its hash goes into the
research ledger, and any later change is an **amendment** that records what changed and why — never
an edit.

This is not ceremony. Without it, the sequence "compute a result, dislike it, adjust a threshold,
recompute" is indistinguishable from research, including to the person doing it. The frozen
protocol is what makes the difference visible afterwards.

A protocol states:

| | |
|---|---|
| **Mechanism and payer** | why the effect should exist |
| **Information set** | every field, with the exact time it becomes knowable |
| **Feature definitions** | the formulas, frozen with the implementation version |
| **Partitions** | which data may be looked at when |
| **Primary endpoint** | **one** statistic, named before it is computed |
| **Secondary diagnostics** | named, and never promotable on their own |
| **Controls** | the nulls the effect must beat |
| **Kill gates** | in order, with thresholds, and the stop-on-failure rule |
| **Known limitations** | stated up front, not discovered in review |

**One primary endpoint.** Not a family of related statistics from which the best is reported. The
arithmetic in section 3.5 is why: with 54 cells, pure noise reaches `t = 2.1`, and `code/gates.py`
demonstrates the same thing empirically — a 95% interval is wrong one time in twenty by
construction, so a single significant cell out of many is the *expected* behaviour of the method,
not a discovery.

## Partitions

Split the history once, in advance, and respect the split:

| Partition | Rule |
|---|---|
| **Development** | open. Iterate freely here |
| **Calibration** | sealed. Opened once per frozen candidate; no retuning afterwards |
| **Forward** | candidate-blind. Single shot, and only on explicit authorisation |

Data quality checks — coverage, missingness, distributions — are not outcomes and may run on any
partition at any time. Anything that joins your feature to a subsequent price move is an outcome
and obeys the table.

## Kill gates

Ordered, thresholded, and evaluated in sequence. **Stop at the first failure.**

A representative set, from the worked example:

1. **Sample.** Fewer than 100 events per group → dead.
2. **Primary differential.** Its 95% session-bootstrap interval includes zero → dead.
3. **Beats phantom levels.** The real level's effect does not exceed levels 100 to 200 ticks away →
   dead; the level is not special.
4. **Implementation consistency.** The modelling assumption's inversion produces the exact
   arithmetic negation it must. A deviation is a bug, not a finding.
5. **Survives the scramble.** A significant effect with randomised labels → dead; the labelling
   carries nothing.
6. **Era agreement.** Sign disagreement across the sample's structural break → flagged, and any
   surviving claim must be stated as the narrower claim.

Stopping matters more than the thresholds. Once a gate has failed, every further statistic is a
search for a reason to continue, and a programme that always finds one never kills anything. When
the worked example failed gate 2, gates 3 to 6 were **not evaluated** — and an unevaluated gate is
never a pass. `code/gates.py` implements exactly this and prints what it did not evaluate.

## What a promotable result looks like

Six things, all of which are properties of the evidence rather than of the strategy:

- **A contiguous single-account run** over the full history, reporting coverage and last trade
  date. A grid of overlapping windows does not substitute: each window restarts a fresh account, so
  the design is *structurally blind* to any state that survives a day — a latch, a counter, an
  account floor. Two strategies here scored well on such a grid while trading almost nothing in a
  continuous account. Both reports were arithmetically correct about different experiments; only
  one was about the strategy.
- **`quantity == 0` recorded as an event.** A strategy that declines to size is otherwise
  indistinguishable in the output from one that saw no signal.
- **Every latch documented with its clearing condition, and a test for it.** Initialisation at
  start-up is not a clearing condition.
- **Time-to-pass and accumulated fees**, not only profit. For an account that pays monthly rent,
  the median days to clear the target and the fees spent getting there decide the economics more
  than the equity curve does.
- **Both account plans swept.** The same signal on the same tape passed at 30.4% on one plan and
  12.6% on another, entirely because of the firms' rules. A strategy whose edge concentrates in one
  trade is structurally incompatible with a consistency rule, and that is knowable before any
  backtest.
- **Concentration.** The mean after removing the top 5% of trades, beside the untrimmed mean, and a
  per-year panel. A positive mean that turns negative after trimming is a lottery ticket, and this
  has killed more candidates here than bad signals have.

## Two diagnostics worth more than they look

**A stable pass rate with collapsing profit.** One strategy held a 30.4% pass rate across an
out-of-sample cut while net profit went from `+$1,400` to `−$16,106`. Cadence durable, payoff not:
the winning trades got smaller, not rarer. That single comparison says where to work — on what
happens *after* entry, not on when to enter.

**A better pass rate that loses money.** Reducing risk per trade raised a strategy's pass rate from
42.9% to 66.7% and dropped net profit from `+$13,989` to `+$148`. Smaller size meant twice as many
trades per attempt, each attempt ran far longer, and each accumulated more monthly rent. Higher
pass rate, fewer passes, same rent, less money.

Both are counterintuitive, both are measured, and neither is visible if you report profit alone.
