# 4. Data

## What the firm holds

### The futures tick dataset

The primary source. Everything that touches price comes from it.

| | |
|---|---|
| Size | 2.74 billion trades, 6.6 GB |
| Instruments | S&P and Nasdaq futures, three FX pairs, two crypto contracts |
| Span | 2020-08 to 2026-08 |
| Per trade | price, size, **the best bid and ask at the moment of the trade**, and the aggressor side |
| Order book | top ten levels on a one-second grid, S&P and Nasdaq, from 2025-10 only |
| Prices | **integer tick counts**, not floats |

The bid, ask and aggressor on every trade matter more than the size of the file. They mean you can
*measure* your cost assumption rather than inherit one, and that a fill model can be checked against
what actually traded.

### The options dataset

Added mid-2026 for the worked example in section 8. End-of-day greeks, implied volatility and open
interest per contract per day, for the S&P index option complex and the two large index ETFs;
1,541 sessions per root, aligned to the futures calendar.

### What we do not have

No history before 2020-08 — no COVID crash, no 2018 volatility regime. This is the hardest
constraint on what any result here can claim. Six years is enough for an honest out-of-sample
split; it is not enough to claim a rule survives a regime it has never seen, and saying so is part
of the job.

No queue position and no order lifetime. The book is one-second snapshots, not an event stream, so
strategies that depend on queue priority cannot be tested honestly and are deferred rather than
approximated.

---

## If you need data we do not have, we buy it

This is a real policy and it is worth stating plainly, because it is unusual and it is one of the
better reasons to work here.

**If an idea is worth testing and the data to test it does not exist in-house, the firm acquires
it.** Any commercial API, any vendor feed, any historical archive. You do not have to make a
business case for a subscription before you are allowed to have a hypothesis.

The worked example in section 8 is exactly this. The dealer-gamma hypothesis required option greeks
and open interest by strike, which the firm did not hold. The subscription was bought **the same
day the hypothesis was framed**, the full six-year history was downloaded within the hour, and the
hypothesis was tested to a verdict inside two days.

The verdict was that the idea does not work. The subscription was still the right call: the
alternative was to keep wondering, and wondering is more expensive than eighty dollars.

What the firm asks in return is only that you know *what you would do with the data* before asking
for it — the information set, the timestamps, the fallback if a field turns out to be unavailable.
That is section 2's hypothesis template, and it is the whole approval process.

---

## Five traps, all of which have cost this firm something

**1. Prices are integer tick counts.** Real price is `count × tick size`. This is the correct unit
for a strategy and the wrong unit for a human, so convert only at the moment you print something.
The failure mode is comparing a converted price against an unconverted indicator — see trap 5.

**2. Large trades arrive split into pieces.** When one aggressive order fills against several
resting orders, the feed emits one record per fill, flagged first / middle / last. To recover
exchange-level trades, group each run from a first-flag to the next last-flag and sum the sizes.
Compute a trade-size distribution without doing this and you will systematically understate large
trades — which are the ones an order-flow hypothesis is about.

**3. The sub-millisecond timestamp is a counter, not a clock.** It saturates, so in bursts several
records share a timestamp. Row order is authoritative. Sorting by timestamp destroys sequence.

**4. The trade price is not always inside the recorded quote.** Between 1% and 13% of trades print
outside the recorded bid-ask, depending on instrument. That is a property of how the quote was
captured, not an error. A fill model that asserts otherwise silently rejects real trades.

**5. Contract rolls contaminate anything that differences across a session boundary.** A futures
series is spliced from consecutive delivery months. On a roll day, "today's open minus yesterday's
close" is the price difference between two *different instruments* — carry, not information.
Measured on the Nasdaq contract: 27 roll sessions in 1,790, with gaps up to **1,131 ticks** against
a typical volatility of 10 to 40 ticks.

The consequence was not hypothetical. A filter gated on overnight displacement fired on 70% of
roll days against 45% of ordinary days, and because carry was positive on every roll after 2023 it
fired **systematically long** — 16 of 19 times. Handle it one of two ways, back-adjust the series
or refuse roll sessions entirely, and **state in your notes which one you chose**.

For any feature conditioned on a gap, report the **roll-day firing ratio**:

```math
\mathrm{ratio}\;=\;\dfrac{\text{firing rate on roll days}}{\text{firing rate on other days}}
```

Above roughly 1.5, the feature is reading carry rather than information.

---

## Provenance is part of the result

Two rules that look bureaucratic and are not.

**Every dataset carries a manifest with a hash of every file**, verified after any move or copy. A
result you cannot tie to a specific, verified input is not reproducible, and the firm has been
bitten: a legacy archive was deleted, and every result measured on it became a *historical
statement* — citable from frozen evidence, not re-derivable. Those results are still in the record,
labelled exactly that way.

**Vendor semantics are part of the tested claim, so measure them.** In the worked example the
option open-interest reports were assumed to publish at 06:30 each morning. A publication-time
assertion in the feature builder refused two full years of data, which is how we discovered the
vendor batch-stamps the early era at 07:01 and emits late tails as far as 20:15. The fix was
row-level enforcement of the actual report time, with the excluded mass recorded per session — not
a looser clock.

An unverified "this is available at 09:00" line in a protocol is a look-ahead bug waiting to be
discovered by someone downstream, and it will be discovered after you have built on it.
