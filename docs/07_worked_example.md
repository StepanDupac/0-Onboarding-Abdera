# 8. Worked example one: the idea that died

Read this section closely. It is the complete arc of a research family, from a practitioner claim
to a measured verdict, in two days. It is the most representative thing in the pack.

## The idea

Options dealers who sell options carry gamma risk and must delta-hedge continuously. When their
book is net **short** gamma they hedge in the direction of the move — buying as price rises, selling
as it falls — which amplifies it. When net **long** gamma they hedge against the move, damping it
and pinning price near strikes with large open interest.

Practitioner writing goes further: the level where net dealer gamma crosses zero, the *flip*, is
supposedly a regime boundary, with trending behaviour below it and mean-reverting behaviour above.

The mechanism is genuinely attractive by our own filter in section 2. There is a named payer — the
hedger paying for immediacy — the flow is mechanical and price-insensitive, and its *location* is
computable in advance from public data. That is more than most ideas offer.

It was also, at the time, the most-hyped idea in retail and semi-professional market commentary,
which is neither evidence for nor against it. This firm had already established something adjacent
and unwelcome: implied volatility predicts the *magnitude* of a session's move and says nothing
about its *direction*. That prior mattered, and it turned out to be the whole story.

## Getting the data

The firm held no option data. The hypothesis was framed, an options subscription was purchased the
same day, and the full six-year history was downloading within the hour: end-of-day greeks, implied
volatility and open interest by strike and expiry.

The download took an hour and produced 6,164 files under a hash manifest. Before any hypothesis
touched it, the data was checked against what the vendor claimed — which is where the first real
finding appeared.

**The publication times were not what the documentation said.** A causal assertion in the feature
builder — "no row may be used before the moment it was knowable" — refused two entire years of
data. Investigation showed the vendor batch-stamps early-era reports at 07:01 rather than the
documented 06:30, and emits late tails as far as 20:15 in every era. The fix was row-level
enforcement of the actual report time, with the excluded mass recorded per session; not a looser
clock.

That assertion was ten lines of code. Without it, two years of look-ahead would have entered the
study silently and every result afterwards would have been worthless in a way that is nearly
impossible to detect from the outside.

## The model

Section 3.3 has the mathematics; `code/gex_math.py` runs it. Per session, using only information
knowable before the opening auction:

1. take open interest by strike and expiry, published overnight, describing the prior close;
2. take greeks and implied volatility from the prior session's end-of-day report;
3. compute each contract's dollar gamma per 1% move, `Γ · OI · m · S² · 0.01`;
4. sign each line by the dealer convention and sum to get net gamma `N(S)`;
5. find the flip level as the zero crossing of `N` nearest spot;
6. map it onto the futures tick grid through a **measured** basis.

Every session also carries a quality figure — the share of the option book, weighted by open
interest, that arrived on time and could be priced — and sessions below 85% were excluded before
any outcome was opened.

## First death: no events

The preregistered primary endpoint was the 30-minute continuation after price first *touches* the
flip level, compared between short-gamma and long-gamma sessions, with a floor of 100 events per
group.

The count came back at **52 and 70**.

An epsilon ladder — widening the touch tolerance from 2 ticks to 12 — moved the short-gamma count
from 52 to 58. The tolerance was not the limiter. Price simply approaches the flip at all on only
about a quarter of sessions, and no honest definition of "touch" reaches the floor. Extending the
window into the calibration partition reached 82, still short, and would have spent a sealed
partition to get there.

**Dead at the sample gate, with zero outcome statistics ever computed.**

That last clause is what made the next step legitimate. Because the dry run consumed only *counts*,
no outcome existed to be fitted to, and the redesign that followed was a genuine preregistration
rather than a response to a disappointing result. Had the counts been computed alongside the
outcomes — which would have been more convenient — the redesign would have been post-hoc tuning
wearing a protocol's clothes.

**The lesson, and it is cheap: check the event rate before you freeze an endpoint.** Counting is
free. Freezing an endpoint whose sample cannot exist is not.

## The redesign

An amendment moved the measurement from the rare touch to the mechanism's natural scale: every
qualifying session becomes one observation.

For each session, with `d₀` the displacement from the opening reference to the flip level and `m`
the session's move:

```math
A\;=\;\mathrm{sign}(d_0)\cdot m
```

`A` is positive when the session moved *away* from the flip. The primary endpoint became the
difference in mean `A` between short-gamma and long-gamma sessions. The mechanism predicts it is
positive. One observation per session, 243 and 211 sessions — the sample gate now cleared with
margin.

Everything else was carried over unchanged: partitions, quality gate, controls, gate order.

## Second death: no effect

| | |
|---|---|
| Primary differential | **−7.43 ticks** |
| 95% session-bootstrap interval | **[−31.75, +18.93]** |
| Real level minus phantom levels | −5.16, interval [−19.70, +10.55] |
| Inverted-convention control | exact arithmetic negation, mismatch 0.0 |
| Random-sign control | not significant, as a true null requires |
| Era split | signs disagree across the structural break |

Zero inside the interval, and the sign is the opposite of the prediction. The phantom control is
the more informative line: **the real flip level behaved no differently from a level 25 to 50 points
away.**

Gate 2 failed, so gates 3 through 6 were **not evaluated**. No rescue diagnostics were run.

Two strategies had been written against this hypothesis. Both died **without ever receiving a
backtest**, which is the cheapest death a strategy can have and exactly what the preregistration
existed to produce.

## Confirming the null three more ways

With the primary endpoint dead, three independent exploratory lanes ran in parallel over roughly
1,400 cells, on the last five years, with an explore/confirm split reported side by side.

**Lane A — gamma regime conditioning an opening-range breakout.** Every cell selected in
exploration inverted or collapsed in confirmation. The best went from `+29.0` ticks at `t = 2.6` to
`−6.1`. The theory-aligned cell — negative gamma with a high share of near-dated gamma — went from
`+31.1` at `t = 2.3` to `−32.9` at `t = −3.0`. The practitioners' claim did not merely fail; in the
confirmation window it inverted.

**Lane B — expiry and pinning, 1,287 cells.** Zero cells positive in both windows. The apparent
"convergence toward large strikes" turned out to be a diffusion artifact: under a random walk the
distance to a fixed nearby point *increases* in expectation, so the effect was present in the null
as well. Monthly-expiry follow-through flipped sign between windows, `+59.8` at `t = 3.5` to `−10.1`.

**Lane C — the volatility surface as a directional signal, 54 cells.** Best exploration t-statistic:
**1.62**. Independent noise alone would be expected to reach 2.13. The search did not clear its own
null.

Finally, the underlying breakout was measured through the engine with real fills: **968 trades,
−$20,831, win rate 31.5%** — which is the geometric null for that bracket. The base strategy had no
edge either, so the conditioning had nothing to condition.

![explore_confirm](Figure: every exploration-selected cell, out of sample)

## What survived

One thing, and it is not directional.

Trade days with **high near-dated implied volatility** carried `−$718` per trade at a 10% win rate
in the confirmation window, against `+$629` and 48% on low-volatility days. Used as a filter on a
funded account, it cut account failures from **9 of 13 to 2 of 13** with payout eligibility
unchanged.

Used on an *evaluation* account it was actively harmful: filtering removes trade days, which
lengthens a fee-paying attempt from a 15-session median to 79 and nearly quadruples the fee per
pass. Survival is what a funded account buys; speed is what an evaluation buys, and the same filter
is right for one and wrong for the other.

**The general result, now confirmed three independent times at this firm: the options book prices
magnitude and survival, never direction.** Ask it about size and risk. Do not ask it which way.

## The register entry

The family is closed with what was tested, what closed it, and what would make a retest legitimate.
Stating the boundary precisely is the difference between a useful register and a superstition:

> What is falsified is **direction**, from the **overnight-carried** book, at **session** scale, on
> the **S&P** contract. Intraday-updated positioning is a different object and is untested.
> Nasdaq-native features are untested. Volatility-regime stratification of evidence is untested and
> is an infrastructure use rather than a signal.

## What this cost, and what it bought

Two days, one eighty-dollar subscription, and a research pipeline that is now permanent
infrastructure. It bought a definitive answer to a question the whole retail market is currently
arguing about, one measured filter that is in production, three reusable lessons, and a register
entry that will stop the next person spending a month on it.

**That is a good outcome, and it is what most of the job looks like.**
