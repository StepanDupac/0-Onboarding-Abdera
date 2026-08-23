# 10. Preliminary results

Everything on this page is **screening evidence**, produced by the research engine on one-minute
bars. It has not been through the firm's tick-level measurement, and until it has, none of it is a
verdict. Read section 1 if you skipped the distinction; it matters most exactly here, where the
numbers look good.

The strategy is the one described in section 9: the opening-drive continuation mechanism at a
speed-optimised risk setting, on the Nasdaq micro contract, 2021-08 to 2026-08, with stress cost
assumptions throughout.

## The trade record

143 trades over five years on an unconstrained account — that is, an account with no drawdown limit
and no profit target, so that nothing truncates the sample and every trade the strategy would have
taken is present.

![equity_curve](Figure: cumulative net and drawdown across the full trade record)

The shape is what an asymmetric continuation strategy is supposed to look like: long flat stretches
punctuated by large winners, with drawdowns that are shallow relative to the eventual gains because
the losses are capped by design.

| | |
|---|---:|
| Trades | 143 |
| Net, stress costs | +$71,467 |
| Mean per trade | +$500 |
| **Top-5%-trimmed mean** | **+$188** |
| Win rate | 29.4% |
| Best / worst trade | +$6,585 / −$2,282 |

## Is it a handful of lucky trades?

This is the first question to ask of any result with a 29% win rate, and the firm has killed more
candidates on this test than on any other.

![trade_distribution](Figure: the distribution of trade outcomes, and what survives trimming)

Removing the best 5% of trades leaves the mean at **+$188**. The result does not depend on a
handful of outliers. Note also the shape of the loss side: losses are tightly clustered because the
stop is a fixed distance, while the win side has a long right tail. That asymmetry *is* the
strategy — it is not a defect to be engineered away.

![per_year](Figure: mean net per trade, by calendar year)

Five of six years positive, the sixth close to flat, and no single year carrying the result.

## What happens to an actual account

The numbers above describe the *signal*. An evaluation account is a different object: it stops the
moment it touches either barrier, and that truncation changes everything about the outcome
distribution.

So we resample the real trade record into four thousand simulated accounts, each starting fresh and
each stopped at its first barrier — pass at +$3,000, breach at −$2,000.

![monte_carlo](Figure: four thousand simulated accounts, each stopped at its first barrier)

| | |
|---|---:|
| Accounts that pass | **44%** |
| Accounts that breach | 56% |
| Median trades to a pass | **1** |

That median of one trade is not a rounding artifact. At this risk setting a single winning trade
clears the entire profit target, and two consecutive losses exhaust the drawdown allowance. **The
account is a two-shot bet**, and its pass rate is close to the strategy's win rate because there is
very little inside a two-trade account for risk management to manage.

That is a legitimate shape for a challenge lane, and it must never be described as a low-risk one.

## Why this beats a more reliable strategy

The Monte Carlo above assumes a fresh account. The economics that matter run over many accounts,
because the subscription is paid monthly for as long as each attempt takes.

![cadence](Figure: time to pass and fees per pass, against the existing strategy)

Measured over twenty-five non-overlapping single-account starts, pooled with an independent grid
offset by 45 sessions:

| | Existing strategy | Speed-optimised profile |
|---|---:|---:|
| Pass rate | 30.8% | 24.0% |
| Median sessions to pass | 52 | **15** |
| Fees per pass | ~$1,492 | **~$759** |
| Mean profit on a pass | ~$4,308 | ~$5,580 |

A lower pass rate, and half the time and half the cost per pass. For an account paying rent by the
month, that trade is the right way round — and it is the opposite of what conventional risk
management would advise, which is why it had to be measured rather than argued.

## The credibility check

A new measuring instrument gets calibrated against a known answer before it is used to produce an
unknown one.

The cadence harness that produced the table above was pointed at the existing strategy, whose
behaviour the firm's tick-level engine had already measured independently. Local pass rate:
**30.8%**. The engine's out-of-sample figure: **30.8%**.

That agreement is what earns the rest of these numbers the right to be read.

## What these numbers are not

Stated plainly, because a page of favourable results is exactly where a reader stops being
sceptical:

1. **No tick-level verdict exists.** These are one-minute-bar fills. The research engine arms
   protective bracket orders one bar after entry, so intrabar stop-and-target ordering is
   unresolved.
2. **Twenty-five account starts is a cadence estimate, not a distribution.** The confidence
   interval on a 24% pass rate from 25 starts is wide, and we have not pretended otherwise.
3. **The risk constants were chosen on this data.** The underlying signal is inherited unchanged
   from a strategy that has been measured at tick level; the three constants that make this profile
   fast were selected here, and there is no untouched holdout behind that choice.
4. **The Monte Carlo resamples the observed trades independently.** It therefore assumes trades are
   exchangeable and independent, which discards any serial structure — clustering of wins in
   trending regimes, for instance. It is a distributional sketch, not a forecast.
5. **Six years of history contains no crisis regime.** The data begins in August 2020.
6. **Nothing here models the funded stage**, so every figure on this page describes what passing
   *costs*, never what passing *earns*.

A candidate who reads this page and asks about item 3 or item 4 unprompted is the kind of candidate
we are looking for.
