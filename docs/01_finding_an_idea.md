# 2. Finding an idea

## Where they come from

Four sources, in rough order of how often they produce something worth testing.

**Academic literature.** SSRN, arXiv q-fin, the Journal of Financial Economics, the Review of
Financial Studies. Papers on market microstructure, dealer intermediation, option hedging flows,
and order-flow imbalance are the productive neighbourhoods for intraday index futures. A published
result is not a strategy — sample periods end, effects decay, and transaction costs are usually
understated or absent — but a published result comes with a *mechanism*, and the mechanism is what
you are shopping for.

**Practitioner writing.** Desk commentary, options-flow services, market-structure blogs. Lower
signal-to-noise than the literature and rarely quantified, but this is where you learn what
participants actually believe and act on, which is itself tradeable information. The worked example
in section 8 came from here.

**Exchange and regulator documentation.** Contract specifications, settlement procedures, margin
rules, expiration mechanics. Dry, and it is where the genuinely structural effects live, because
they come from rules rather than from behaviour.

**Anomalies you observe.** Something in the data that you cannot explain. Treat these with the most
suspicion — you found them by looking, which means the multiple-testing problem starts before you
have written anything down.

## The filter every idea passes first

Before an idea costs anything, it has to survive two questions.

### Who pays, and why?

Name the counterparty who loses the money you expect to make, and the reason they are willing to.
Acceptable answers look like:

- *a dealer who must hedge an option book continuously, whose flow is mechanical and
  price-insensitive, and who is paying for immediacy;*
- *an index fund that must trade at the close regardless of price;*
- *a leveraged participant forced to liquidate by a margin rule.*

Unacceptable answers: "the market is inefficient", "the pattern is visible in the chart", "momentum
exists". If you cannot name the payer, you do not have a hypothesis — you have a shape.

### Has it already been closed?

The firm keeps a register of falsified hypotheses. Each entry records what was tested, on what data
and at what horizon, what closed it, and **what would have to change for a retest to be
legitimate**. Read it before proposing anything.

This matters more than it sounds. A family being falsified at one horizon is not falsified at all
of them, and a family being popular is evidence of neither. In the worked example, what was closed
was *direction*, from the *overnight* option book, at *session* scale, on the S&P contract.
Intraday-updated positioning is a different object and remains untested. Saying which one you mean
is the difference between a new hypothesis and a repeat.

## Writing the hypothesis down

A usable hypothesis names five things. If you cannot fill these in, you are not ready to write
code.

| | |
|---|---|
| **Mechanism** | who is forced to trade, and why |
| **Information set** | exactly which fields, known at exactly what time |
| **Instrument and horizon** | what you trade, and over what holding period |
| **Prediction** | the direction and rough size of the effect, stated before you look |
| **Falsifier** | the observation that would make you abandon it |

Here is the one from the worked example, written before any data was pulled:

> **Mechanism.** Option dealers delta-hedge continuously. When their book is net short gamma they
> must trade in the direction of the move, amplifying it; when net long gamma they trade against
> it, damping it. The hedging flow is mechanical, price-insensitive, and its *location* is
> computable in advance from the option chain.
>
> **Information set.** Open interest by strike and expiry, published overnight and describing the
> prior close; option greeks and implied volatility from the prior session's end-of-day report.
> Both known before the opening auction.
>
> **Instrument and horizon.** S&P futures, one session, entry after the open and exit before the
> mandatory flatten.
>
> **Prediction.** Conditional on the regime, price behaves differently near the computed "flip"
> level than near an arbitrary level: continuation in short gamma, reversion in long gamma.
>
> **Falsifier.** The difference between regimes is indistinguishable from zero, or the real level
> is indistinguishable from a level a hundred ticks away.

Note the last line. **The falsifier was written before the data existed**, and it is what the test
was eventually designed to hit. It hit.

## What it costs to be wrong later rather than early

The pre-flight arithmetic in the next section takes ten minutes. Implementation takes days, and a
full test takes a week of wall-clock time. The ordering is not a formality: an idea killed by
arithmetic costs ten minutes, and the identical idea killed after implementation costs a week and
leaves you invested in it, which is the more expensive of the two problems.
