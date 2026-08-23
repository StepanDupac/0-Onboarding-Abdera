# 3. The mathematical framework

This section is the one to read carefully. Everything here is done **before** any code is written,
and most ideas die in it.

Runnable: `python3 code/preflight.py`, `python3 code/gex_math.py`, `python3 code/gates.py`.

---

## 3.1 Barrier geometry, or why most ideas are dead on arrival

Almost every intraday strategy here is a **bracket**: enter, and exit at whichever of two barriers
is touched first — a stop `S` ticks against you, or a target `T` ticks in your favour.

Model the price path as a driftless random walk. The probability of touching the target before the
stop is the classic gambler's-ruin result, and it depends only on the distances:

```math
p_{\mathrm{null}}\;=\;\dfrac{S}{S+T}\;=\;\dfrac{1}{1+RR},\qquad RR\equiv\dfrac{T}{S}
```

This is the win rate your strategy gets **for free, with no edge at all**. It is the number any
observed win rate must be compared against, and it is why a high win rate on its own is not
evidence of anything: widen the stop and shrink the target and you can manufacture a 79% win rate
out of pure noise, with an expected profit of exactly zero.

Now add cost. Let `C` be the round-turn transaction cost in ticks. Breakeven requires

```math
p\,T-(1-p)\,S\;=\;C\qquad\Longrightarrow\qquad p^{*}\;=\;\dfrac{S+C}{S+T}
```

Subtract the free win rate, and everything collapses to one expression:

```mathbox
p^{*}-p_{\mathrm{null}}\;=\;\dfrac{C}{S+T}
```

**The entire cost hurdle, expressed in win-rate percentage points, is inversely proportional to the
total width of the bracket.** This is the single most useful formula in the pack.

Read what it implies. A tight mean-reversion bracket of `S = 12`, `T = 22` ticks against a cost of
6 ticks needs the signal to manufacture `6/34 = 17.6` percentage points of win rate over the
driftless null. No equity-index signal delivers that. A wide continuation bracket of `S = 48`,
`T = 240` against a cost of 9 ticks needs `9/288 = 3.1` points. Same instrument, same cost, one
idea impossible and the other worth building — and you know which before writing a line of code.

We require a margin over breakeven, not breakeven itself, so the operative threshold is

```math
p^{*}_{\mathrm{gate}}\;=\;\dfrac{S+\lambda C}{S+T},\qquad \lambda=1.5
```

![cost_hurdle](Figure: the cost hurdle against bracket width)

### The rule of thumb

| Cost burden `C/(S+T)` | Reading |
|---|---|
| under ~3 points | the geometry is affordable; the signal only has to be real |
| 3 to 6 points | you need a named mechanism for the excess |
| above ~6 points | the geometry is wrong; fix it or abandon the idea |

And the rule that follows: **nothing downstream of the entry decision can move mean gross ticks per
contract.** Position sizing, risk management, account selection and lockout logic move dollars
around. They do not move ticks. Ticks are a property of the signal and the barrier alone, and that
is the number that has to be right first.

![win_rate_null](Figure: the free win rate, and what the gate demands)

---

## 3.2 Why R-multiples, not ticks, when stops vary

If a strategy clips its stop into a range — say 40 to 120 ticks — then pooling raw tick outcomes
across trades is a mistake, and an expensive one.

Under a bracket the outcome is `+RR·S` or `−S`, so

```math
\mathrm{Var}\!\left(\mathrm{gross}\mid S\right)\;=\;S^{2}\,p(1-p)\,(1+RR)^{2}
```

Variance scales with `S²`. Across a 3-to-1 spread of stops that is a **9-fold variance ratio**
between the widest and tightest trades, so the wide-stop trades set the standard error almost by
themselves. The resulting t-statistic answers "did the wide-stop trades win", not "does the signal
have edge".

Report the **R-multiple** instead: for each trade,

```math
R_i\;=\;\dfrac{\mathrm{gross\ ticks}_i/q_i\;-\;C}{S_i}
```

with its mean, its session-clustered standard error, and the t-statistic. In this firm's history a
strategy showed `+6.75` net ticks at `t = 1.25` in raw ticks — a marginal but live-looking result —
and `+0.043 R` at `t = 0.57` once expressed properly, which also revealed that the tight-stop half
was losing money after costs the whole time.

---

## 3.3 The specific model: dealer gamma

The worked example needs a model that turns an option chain into a price level. This is what it
looks like when a hypothesis is made concrete. Full implementation: `code/gex_math.py`.

**Gamma** is the second derivative of option value with respect to spot — the rate at which a
hedger's delta changes as price moves:

```math
\Gamma\;=\;e^{-q\tau}\,\dfrac{\varphi(d_1)}{S\,\sigma\sqrt{\tau}}\qquad\quad d_1\;=\;\dfrac{\ln(S/K)+\left(r-q+\frac{1}{2}\sigma^{2}\right)\tau}{\sigma\sqrt{\tau}}
```

where S spot, K strike, sigma implied volatility, tau time to expiry, r rate, q dividend yield, phi the standard normal density.

Gamma is **identical for a call and a put at the same strike and expiry**. That fact is load-bearing
and we return to it.

Convert to the dollar hedge a 1% move forces, per contract line:

```math
DG_i\;=\;\Gamma_i\cdot OI_i\cdot m\cdot S^{2}\cdot 0.01
```

where `OI` is open interest and `m` the contract multiplier. One factor of `S` converts gamma into
delta-per-1%-move; the second converts delta into dollars.

Aggregate with a sign for which side the dealer is on:

```math
N(S)\;=\;\sum_i \epsilon_i\,DG_i(S),\qquad \epsilon_i\in\{-1,+1\}
```

and define the **flip level** as the zero crossing of `N` nearest spot:

```math
N(S^{*})\;=\;0
```

Above it dealers are net long gamma and hedge against the move; below it they are net short and
hedge with it. That is the theory being tested.

![gamma_profile](Figure: per-contract gamma, the net profile, and the flip level)

### The assumption hiding in plain sight

Open interest counts contracts. **It does not say who is long and who is short.** The signs
`ε_i` are a *convention*, not data — the standard one assigns dealers long calls and short puts —
and since gamma is identical for calls and puts, that convention *is* the model. Everything the
hypothesis claims rests on it.

So it gets isolated in one function and tested against its own inversion and against random signs.
This produces a result worth internalising, and `code/gex_math.py` verifies it numerically:
inverting the convention negates `N(S)` exactly, so the flip **location** is convention-invariant
while the **regime label** flips. A test whose result survives the inversion unchanged has learned
nothing about dealer positioning.

**The general principle: find the modelling assumption that your result depends on, isolate it in
one place, and make its ablation a first-class output.** Every model has one. If you cannot name
yours, you have not found it yet.

---

## 3.4 Getting from an index level to a tradeable price

The option chain prices the cash index; you trade a futures contract on a discrete tick grid. They
differ by **basis** — carry, dividends and financing:

```math
b\;=\;F_{\mathrm{close}}-I_{\mathrm{close}},\qquad \mathrm{tick\ index}\;=\;\mathrm{round}\!\left(\dfrac{L+b}{\delta}\right)
```

where F futures close, I index close, L the level in index points, delta the tick size.

measured from the same instant on both sides, never assumed. Two rules here are absolute:

1. **Every price the engine hands a strategy is an integer tick index, not a price.** Mixing the
   two units is silent — the comparison does not raise, it produces a number — and it has destroyed
   three strategies in this firm's history. Section 10.
2. Measure the basis; do not model it. A measured constant per session is fine. A theoretical
   cost-of-carry is a second model stacked on the first.

---

## 3.5 Deciding whether a difference is real

Implementation: `code/gates.py`.

### Sessions are the unit of independence

Trades within one session share a regime, a news cycle and an opening auction. Resampling *trades*
understates uncertainty; we resample whole **sessions**. The variance inflation from clustering is

```math
\mathrm{design\ effect}\;=\;\sqrt{1+(m-1)\rho}
```

where m trades per session, rho the within-session correlation.

for `m` trades per session and within-session correlation `ρ`. At one trade per session it is
negligible. At five trades and `ρ = 0.3` it is **1.48**, which is the difference between `t = 2.1`
and `t = 1.4` — between a result and nothing.

For a difference between two groups of sessions, resample the sessions in each group independently
and take the 2.5th and 97.5th percentiles of the difference. Nothing more exotic is needed, and
nothing less is honest.

### A maximum over many cells is not a discovery

If you sweep `n` variants, the best one always looks good. The honest comparison is against what
the best of pure noise would have produced. For `n` independent standard normal draws,

```math
\mathbb{E}[\max]\;\approx\;\sqrt{2\ln n}\;-\;\dfrac{\ln\ln n+\ln 4\pi}{2\sqrt{2\ln n}}
```

| cells swept | expected max \|t\| under pure noise |
|---:|---:|
| 1 | 0.00 |
| 20 | 1.71 |
| 54 | 2.13 |
| 200 | 2.61 |
| 1,287 | 3.19 |

A real sweep from the workspace: 54 cells of vol-surface features against next-session direction.
Best t-statistic in the exploration window: **1.62**. Independent noise alone would be expected to
reach 2.13. **The search did not clear its own null** — as clean a negative as this method produces,
and it took one line of arithmetic to see it.

![noise_ceiling](Figure: the noise ceiling of a search)

Correlated cells lower the ceiling, so treat this as the generous version of the comparison.

### Controls: make the null concrete

An interval that excludes zero says the difference is not noise. It does not say the difference is
caused by what you think. That needs controls, and each is cheap:

| Control | What it kills |
|---|---|
| **Phantom levels** — repeat everything at the level ± 100/150/200 ticks | the level is arbitrary; any nearby level would have done |
| **Sign / label scramble** — randomise the modelling assumption | the classification carries no information |
| **Timing null** — draw a random minute in the same session | the day-selection carries it, the entry adds nothing |
| **Side null** — take the same trades with random direction | the direction carries nothing |

The phantom control is the one candidates most often omit and the one that does the most work. In
the worked example, the real level's effect exceeded the phantom pool's by `−5.16` ticks with a
95% interval of `[−19.70, +10.55]`. The level was not special, and no amount of interval-tightening
on the primary endpoint would have revealed that.

### Explore and confirm

Split the history once, in advance. Iterate freely in the exploration window; look at the
confirmation window once, at the end, and report both columns side by side for every cell you show.

A cell that is strong in exploration and inverts in confirmation is not a weak result — it is a
**negative** result, and reporting it as "promising, needs more data" is the most common way a
research programme lies to itself. In the sweep above, the best exploration cell went from
`+29.0` ticks at `t = 2.6` to `−6.1`, and the theory-aligned cell went from `+31.1` to `−32.9`.

---

## 3.6 The pre-flight, as a checklist

Every line is a kill switch. `code/preflight.py` runs it.

| # | Quantity | Kill if |
|---|---|---|
| 1 | round-turn cost `C`, stress column | — |
| 2 | required gross edge `1.5C` | your honest estimate of mean gross is below it |
| 3 | reward:risk `RR = T/S` | `RR < 1` and no mechanism gives a 65%+ hit rate |
| 4 | geometric breakeven `1/(1+RR)` | — |
| 5 | **win-rate excess `C/(S+T)`** | above ~3 points with no named mechanism |
| 6 | required win rate `(S+1.5C)/(S+T)` | above 0.60 |
| 7 | expected trade count | below 100 over the intended window |
| 8 | stop dispersion `max(S)/min(S)` | above ~2 and you are not reporting R |
| 9 | does any feature cross a session boundary? | yes, and you have not handled the contract roll |
| 10 | does sizing read a ratcheting quantity? | yes |
