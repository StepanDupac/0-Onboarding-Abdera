# 9. Worked example two: the thing that shipped

The dealer-gamma family died on a Sunday afternoon. A deliverable shipped the same day — from a
different direction entirely, and the contrast is the lesson.

## Where a shipped strategy usually comes from

Not from a new mechanism. From the best mechanism you already have, improved along an axis nobody
has measured.

The firm's most reliable family is **opening-drive continuation**: a large overnight displacement,
a same-direction drive in the first half hour of the cash session, and a confirmed breakout with
trend, momentum and order-flow agreement. One member of that family had already been measured at
tick level by the firm's engine and runs on a live demo account.

The question asked was not "what else could work" but: **the account pays monthly rent, so what
happens if we optimise for speed instead of reliability?**

## The reasoning, before any code

The existing strategy passes an evaluation in a **52-session median**. Every month of that costs a
subscription. Two levers are available, and both trade reliability for speed:

- **loosen the entry gate** — more qualifying sessions, so the first opportunity arrives sooner;
- **increase the stake** — fewer trades needed to clear the target, so an attempt resolves faster.

Both make the account *more* likely to fail. Conventional risk management says that is wrong. The
economics say otherwise, and the firm had already measured it: reducing risk per trade on an
evaluation strategy raised the pass rate from 42.9% to 66.7% and dropped net profit from `+$13,989`
to `+$148`, because smaller size meant twice as many trades per attempt, each attempt ran longer,
and each accumulated more rent.

**For an account that pays rent by the month, time is a cost, and the correct direction for an
evaluation lane is more risk per trade, not less.** That is a counterintuitive, measured, and
narrow result — it applies to the evaluation stage only. The funded stage, where survival is the
objective, keeps the opposite rule.

So the change was a **constant-transform** of a tick-verified strategy: identical logic, identical
code path, three constants moved. Nothing about the signal was touched, which means the tick-level
evidence for the mechanism still applies and only the risk geometry is new.

## The measurement gap

To answer the question, we needed a statistic nobody had been computing: not "did this account
survive" but **"how many evaluations does this pass per year, and what did the attempts cost"**.

So two instruments were built before any parameter was tried:

**A cadence harness.** Non-overlapping single-account runs on a rolling grid of start dates. Each
run reports its terminal state, days elapsed, trades, and an estimated fee including monthly
renewals. The aggregate gives pass rate, median days to pass, and fee per pass.

**A payout probe.** For the funded stage, the published rule implemented directly: a non-withdrawable
buffer plus a minimum request, no single day above half the cumulative profit, and a minimum number
of profitable days. It reports what share of funded accounts reach a first withdrawal, and how many
die first.

Building the measuring instrument before running the experiment is not overhead — it is the
experiment. And it paid immediately: the harness surfaced a defect in the research engine's own
risk layer, where a conservative buffer was converting account failures into a limbo state in which
nothing traded and rent accrued indefinitely. Switching it off changed the terminal-state
distribution completely and made the measurement match live behaviour.

## The result

Twenty-five non-overlapping starts across five years, stress cost assumptions, pooled with an
independent grid offset by 45 sessions:

| | Existing strategy | Speed-optimised profile |
|---|---:|---:|
| Pass rate | 30.8% | 24.0% |
| **Median sessions to pass** | 52 | **15** |
| **Fees per pass** | ~$1,492 | **~$759** |
| Mean profit on a pass | ~$4,308 | ~$5,580 |

A lower pass rate, and **half the time and half the cost per pass**. That is the trade the
economics predicted, confirmed on data that had not been used to design it.

Two supporting numbers mattered as much as the headline:

**Concentration.** On an unconstrained account so that no early termination truncates the sample:
143 trades, mean `+$500`, and a **top-5%-trimmed mean of `+$188`**. The result survives removing its
best trades, which is the test that has killed more candidates at this firm than bad signals have.
Five of six years positive.

**Plan structure.** The same profile on the other account plan: **1 pass in 13 starts** at nearly
four times the fee. That plan caps any single day at half the total profit and requires two trading
days, which structurally forbids the one-trade pass this geometry produces. The account plan is a
research variable, not a deployment detail.

## The credibility check

The harness is new, so before trusting it, it was pointed at the existing strategy whose behaviour
the firm's engine had already measured independently.

Local pass rate: **30.8%**. The engine's out-of-sample number: **30.8%**.

That agreement is what earns the new numbers the right to be read at all. **A new measuring
instrument gets calibrated against a known answer before it is used to produce an unknown one.**

## Packaging, and a defect found on the way out

The package shipped as one source with two profiles — a fast evaluation profile and a
survival-tuned funded profile carrying the volatility filter from section 8 — each with its own
identity, and a specification and data table for the feed the funded profile needs.

An automated packaging gate was written for the export: it recomputes every hash, checks the
parameter file against the class defaults, recomputes each profile's identity from its declared
overrides, and cross-checks the index and route configuration against the manifests.

**Its first run found a genuine unit bug in a package that had already shipped** and was waiting to
be measured. That strategy stores a reference level as a tick index and compares it against a
display price. On the Nasdaq contract the units differ by a factor of four, so the computed
displacement is around −63,000 on every session regardless of what the market did, which pins the
direction to short on every trade, renders a magnitude threshold permanently inert, and kills a
cancellation path entirely. Every performance figure attached to it describes a different object
than the one its documentation describes.

The frozen source was **not** edited. The defect was written into a known-defects register with the
mechanism, the consequence and a recommendation, and the re-freeze decision left to the owner.

That is the third instance of the same unit error in this firm's history, which is why section 5
puts branch reachability counts ahead of everything else, and why the check is now mechanical.

## What to take from the contrast

Section 8 is a good idea, well tested, that turned out to be false. This section is an existing
mechanism, re-optimised along an axis the economics pointed at, that turned out to be worth
shipping.

Both were the same day's work and both are the job. The difference between them is not skill or
luck — it is that one asked "is this true?" and the other asked "given what is already true, what
follows?". The second question has a much higher hit rate, and a researcher who only asks the first
will produce a lot of well-documented nothing.

**Ask both. Spend most of your time on the second.**
