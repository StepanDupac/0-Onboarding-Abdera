# 7. Promotion, packaging and identity

## What leaves the workspace

When a candidate survives, it is **frozen** into a package and handed to the measurement team. The
package is four files:

| File | Contents |
|---|---|
| `strategy.py` | the frozen source, byte-for-byte, LF line endings |
| `params.yaml` | **exactly** the class defaults, nothing else |
| `manifest.json` | identity, hashes, taxonomy, status, and what could not be verified |
| `NOTES.md` | the evidence, in a fixed section order ending in *Not verified* |

The measurement engine reads the **class defaults** and applies overrides on top, so `params.yaml`
is documentation rather than configuration. Keeping it equal to the defaults is enforced
mechanically: if it ever drifts, the engine silently measures something other than what the file
says.

`NOTES.md` ends with a section titled **Not verified**, and it must not be empty. This is the single
highest-return convention in the pipeline. One package listed four properties it could not
establish; three turned out to be genuine issues and the fourth was resolved in minutes — because
it had been named. Naming what you do not know is not weakness in a research report. It is most of
the value.

## Identity

Two strategies must never be confusable, across time, across researchers, across machines. So an
identifier is minted from **content**, not from a name.

```
        W3 - OD - MNQ - BACRBD
        │    │     │      └── checksum, derived from the content
        │    │     └───────── instrument
        │    └─────────────── family, from a shared vocabulary
        └──────────────────── originating workspace
```

The checksum is the first 30 bits of

```
sha256( workspace | family | symbol | strategy_hash | params_hash )
```

rendered in Crockford base32, where:

- **`strategy_hash`** is the SHA-256 of the *normalised* source — line endings unified, trailing
  whitespace stripped, blank lines and comment-only lines dropped — truncated to 32 hex characters.
  Reformatting does not move it; changing a line of logic does. The identity follows the logic, not
  the formatting.
- **`params_hash`** is the SHA-256 of a canonical JSON of the parameter class name and its sorted
  values, floats rounded to fixed precision, truncated to 16 hex characters.

Four consequences, and they are the point of the design:

1. **Identical content mints an identical identifier.** Re-exporting an unchanged strategy does not
   create a new identity, because it is not a new strategy.
2. **Any change to the logic mints a different one.**
3. **A changed parameter mints a different one.** The same file at two different risk settings is
   two strategies with two different results and two identities. This is not pedantry: a firm that
   calls them by one name eventually cannot say which configuration produced which number.
4. **The parameter class name is inside the hash.** Renaming the class moves the identity even with
   identical values, which is intended — it is a different declared object.

### The ledger

Every minted identifier is appended to a ledger that is never edited or reordered: identifier,
timestamp, strategy, both hashes, symbol, family, source path, and a note. Minting refuses if the
identifier already exists with different content, which turns a one-in-a-billion silent collision
into a loud failure at export time.

The ledger is also the **honest trial count**. Statistical corrections for multiple testing need to
know how many things were tried, and a register that only records successes gives an answer that is
wrong in the direction that flatters you. Screens rejected before a source ever existed — the
twenty-plus families of earlier batches, the 1,287 cells of one sweep — have no ledger row, so the
count is handed over together with the research ledger that does record them.

### Worked example

The strategy in section 9 has three identities from one file:

| Configuration | Identity |
|---|---|
| class defaults (reference only, never traded) | `W3-OD-MNQ-BACRBD` |
| evaluation profile: looser gate, larger stake, wider target | `W3-OD-MNQ-0ZYC0A` |
| funded profile: smaller stake, volatility filter on | `W3-OD-MNQ-BC1TX8` |

One source, one `strategy_hash`, three `params_hash` values, three identities. The two traded
profiles are recorded as explicit overrides in the route configuration, so what was measured and
what would be deployed are the same object.

## Packaging discipline

Three rules, each learned expensively:

**Freeze then mint, never the reverse.** The identity is a function of the frozen content. If a
package is edited after minting, it must be re-frozen and re-minted — there is no such thing as a
small edit to a shipped package.

**Never repair a frozen source to make a check pass.** During the export in section 9, an automated
gate found a genuine unit bug in a package that had already shipped and was awaiting measurement.
The source was **not** edited. The defect was written into a known-defects register with the
mechanism, the consequence and a recommendation, and the decision to re-freeze was left to the
owner. Silently fixing it would have destroyed the link between the package and the evidence
measured from it.

**State dependencies; do not quietly design around them.** The same export initially had a feature
removed because the destination system appeared unable to support the data feed it needed. That was
the wrong call — it discarded the single measured improvement of an entire research programme to
satisfy a constraint nobody had confirmed. The correct move, and what the package now does, is to
keep the feature, declare the dependency loudly, ship the feed specification and the data table so
implementing it is a small job, and offer an inert fallback setting.
