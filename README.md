# Quantitative Research at Abdera Trading

`ABD-ONB-R1`

**What the work looks like, told through one real day of it.**

This pack exists because "quant researcher" means very different things at different firms, and
strong mathematicians frequently arrive without a picture of the day-to-day. So rather than
describe the role abstractly, it walks through one complete day of research — a hypothesis taken
from the literature to a measured verdict, and a deliverable shipped.

**The headline idea died. The thing that shipped came from somewhere else.** That is the ordinary
shape of the work, and it is why this is the pack we send rather than a success story.

---

## Start here

| | |
|---|---|
| **`Quant_Research_Handbook.pdf`** | everything below, as one document |
| `docs/00_overview.md` | the role, the pipeline, and what a result here means |
| `docs/07_worked_example.md` | **the idea that died** — read this one closely |
| `docs/08_delivery_example.md` | **the thing that shipped** |
| `docs/09_preliminary_results.md` | **its equity curve, trade distribution and Monte Carlo** |
| `exercise/README.md` | a task. If you want to be taken seriously, do it |

If you have twenty minutes, read the overview and the two worked examples. If you have an evening,
read everything and run the code.

## Contents

```
docs/    00 overview          the role, the pipeline, what a screening result means
         01 finding an idea   literature, the payer test, writing a falsifiable hypothesis
         02 mathematics       barrier geometry, the cost hurdle, the model, inference
         03 data              what we hold, five traps, and how you get data we do not hold
         04 building          the strategy contract and the tests that catch a broken one
         05 scaling           preregistration, partitions, controls, kill gates
         06 promotion         packaging, and how a strategy gets its identity
         07 worked example 1  dealer gamma, from a practitioner claim to a measured null
         08 worked example 2  the deliverable, and why it came from an existing mechanism
         09 results           equity curve, concentration, Monte Carlo, cadence economics
         10 rejection         what gets work thrown out, with the real failures behind each
         11 how we work       the rhythm, what you produce, what we provide

code/     runnable implementations of everything in docs/02, /03, /05 and the figures
figures/  every chart in the handbook, as vector SVG, regenerated from the trade record
exercise/ a self-contained task with data, and how it is assessed
```

## Running the code

Python 3 and numpy. Nothing else.

```bash
python3 code/preflight.py         # the arithmetic that kills most ideas in ten minutes
python3 code/gex_math.py          # option chain to a tradeable price level
python3 code/gates.py             # how we decide whether a difference is real
python3 code/make_sample_data.py  # generate the exercise dataset
python3 code/screen.py            # a complete screen, with its controls
python3 code/make_figures.py      # every figure in the handbook
python3 build_pdf.py              # rebuild the PDF itself
```

The handbook is generated from `docs/` — the mathematics is typeset with matplotlib and the PDF is
printed by headless Chrome, so there is no LaTeX or pandoc to install. Editing a document and
re-running `build_pdf.py` is the whole loop.

## Three things worth knowing before you read

**A research result here is a screening decision, not a measurement.** When a researcher promotes a
candidate they mean "worth an hour of tick-level measurement downstream" — never "this works". The
word *verdict* belongs to the measurement team.

**Negative results are the product.** Across research batches 005 to 016, more than twenty families
were tested and almost all were rejected. If a month of careful work ending in "this does not work,
here is the number that closed it" would feel like failure, this is the wrong job.

**You start on a $50,000 prop account, not the firm's capital.** New researchers work on
proprietary-trading-firm evaluation accounts at the $50,000 size. It is real money under externally
enforced rules — a hard drawdown, a mandatory daily flatten, a monthly fee — which bounds the risk
while you build a track record and, more usefully, turns "make money in futures" into a specific
optimisation problem with a measurable objective. Progression to larger mandates, including the
firm's own capital, follows measured results. Section 1 explains the reasoning.

**If an idea needs data we do not have, the firm buys it.** Any API, any vendor, any archive. The
worked example in section 8 required an options subscription that did not exist in-house; it was
purchased the day the hypothesis was framed and the hypothesis was answered within two days. The
answer was no. It was still the right call.

---

*Some figures are illustrative and some parameter values of live strategies are held back. The
methods, the mathematics, the failures and the reasoning are exactly as they happened.*

---

Pack `ABD-ONB-R1`. Provenance and rebuild instructions: `PACK.json`.

© Abdera Trading. Shared with candidates for assessment purposes.
