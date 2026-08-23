# Build sources — internal

Everything needed to regenerate the handbook. **Not part of what candidates receive**; the pack
itself is the PDF, the code and the exercise one level up.

```
docs/                  the twelve chapters, in Markdown — the actual source of the handbook
figures/               the ten charts, as SVG, embedded into the PDF at build time
strategy_trades.csv    the 143-trade record behind the results chapter, year-only dates
abdera-logo-v1.png     cover mark; its background is #090908, matched by the cover CSS
make_figures.py        regenerates figures/ from the trade record and the models
build_pdf.py           renders docs/ + figures/ into ../Quant_Research_Handbook.pdf
```

## Rebuilding

```bash
python3 .source/make_figures.py     # only when a figure or the trade record changed
python3 .source/build_pdf.py        # always
```

`build_pdf.py` carries its own Markdown converter and typesets the mathematics with matplotlib's
mathtext, so there is no pandoc and no LaTeX to install. Equations are cached under
`figures/equations/` and are git-ignored; they regenerate automatically.

## Issuing a revision

Candidates keep copies, so revisions have to be tellable apart:

1. edit `docs/`, and `make_figures.py` if a chart changed;
2. bump `PACK_ID` in `build_pdf.py` (`ABD-ONB-R2`, and so on);
3. bump `revision`, `revision_note` and `issued` in `../PACK.json`;
4. rebuild, then refresh the handbook `sha256` in `../PACK.json`.

## Keeping it true

The handbook describes the research method used in `3_Workspace`. If a kill gate, the pre-flight
arithmetic, the identity scheme, the data sources or the account model changes there, this pack
becomes wrong for the people being hired on the strength of it. Check it after any material change.
