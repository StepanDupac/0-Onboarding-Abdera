# Code

Everything here runs with **Python 3 and numpy** and nothing else. Each file is executable and
prints a worked demonstration of the section it belongs to.

```bash
python3 code/preflight.py          # section 3.1  the arithmetic that kills ideas cheaply
python3 code/gex_math.py           # section 3.3  option greeks to a price level
python3 code/gates.py              # section 3.5  bootstrap, noise ceiling, ordered gates
python3 code/make_sample_data.py   # writes the exercise dataset
python3 code/screen.py             # a complete screen with controls, on that dataset
python3 code/make_figures.py       # every figure in the handbook, from the real trade record
```

`strategy_template.py` is the portable strategy contract, annotated. It is not executable on its
own: it references the firm's engine kit, which is not distributed. Read it as a specification.

## What each file is for

| File | Purpose |
|---|---|
| `preflight.py` | Barrier geometry, the cost hurdle `C/(S+T)`, required win rate, and the three-level verdict. Run this on any idea before writing anything else. |
| `gex_math.py` | Black-Scholes gamma, dollar gamma per 1% move, the net-gamma profile and its zero crossing, and the index-to-futures basis map. Includes the numerical proof that the flip location is invariant to the dealer sign convention while the regime label is not. |
| `gates.py` | Session-cluster bootstrap for a mean and for a difference, the expected maximum t-statistic of a search, the clustering design effect, and ordered kill gates that stop at the first failure. Demonstrates power and false-positive rate on planted data. |
| `make_sample_data.py` | Generates two synthetic session files, one with a planted effect and one without, both containing a real volatility difference between regimes. |
| `screen.py` | A reference screen: one primary endpoint, a phantom-level control, a label scramble, gates in order. Correctly rejects the noise file and detects the planted one. |
| `make_figures.py` | Every figure in the handbook. The strategy charts are built from `exercise/data/strategy_trades.csv`, the real 143-trade record; the Monte Carlo resamples it into four thousand simulated accounts, each stopped at its first barrier. |
| `strategy_template.py` | The strategy contract with every rule annotated and the failure that motivated it. |

## A note on style

The real repository forbids comments and docstrings in strategy sources — explanation lives in the
notes file, which is reviewed as documentation, while the code is expected to be readable from its
names alone. The files here are heavily annotated because they are teaching material. When you
write the real thing, strip the prose and let the names carry it.

Everything is seeded. Re-running any file reproduces its output exactly; if it does not, that is a
bug worth reporting.
