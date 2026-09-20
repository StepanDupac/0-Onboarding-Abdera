"""Generate the self-contained sample dataset used by the screen and the exercise.

The real research data is 1.2 GB of proprietary tick files and a paid options subscription. This
generator produces a small synthetic stand-in with the same SHAPE, so a candidate can run the whole
method end to end on a laptop with nothing but numpy.

Two variants are written, and which is which is recorded in the manifest but NOT in the file names:

  sessions_a.csv   one of them contains a planted, economically plausible effect
  sessions_b.csv   the other contains nothing but noise

Your job in the exercise is to decide which, using the method rather than by peeking. The planted
effect is deliberately modest -- about the size of a real one -- so a sloppy test will find it in
both files and a careless one will find it in neither.

    python3 code/make_sample_data.py
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np


OUT = Path(__file__).resolve().parents[1] / "exercise" / "data"

SESSIONS = 500
TICK_SIZE = 0.25
BARS_PER_SESSION = 390
PLANTED_EFFECT_TICKS = 26.0


def build(seed: int, planted: bool) -> list[dict]:
    generator = np.random.default_rng(seed)
    rows = []
    level = 5000.0
    for index in range(SESSIONS):
        session_date = f"2024-{1 + index // 21:02d}-{1 + index % 21:02d}"

        # A regime label the candidate is allowed to condition on. In the real family this was the
        # sign of net dealer gamma; here it is simply a labelled state with realistic persistence.
        regime = -1.0 if generator.random() < 0.45 else 1.0

        # Session volatility depends on the regime. THIS IS REAL IN BOTH FILES: the options book
        # genuinely prices magnitude. It is not the effect you are looking for.
        daily_sigma_ticks = 55.0 if regime < 0 else 38.0

        open_ref = level

        # A published level, analogous to the gamma flip: known before the open, near the price.
        # The session's displacement from it is what the endpoint conditions on.
        displacement_ticks = generator.normal(0.0, 25.0)
        published_level = open_ref - displacement_ticks * TICK_SIZE

        # The planted effect, when present: in negative-regime sessions only, the session drifts
        # AWAY from the published level. Aligning the drift with the displacement is what makes it
        # an effect about the level rather than an unconditional bias -- and it is why a test that
        # ignores the displacement sign will never see it.
        drift = 0.0
        if planted and regime < 0:
            drift = PLANTED_EFFECT_TICKS * np.sign(displacement_ticks)

        path = generator.normal(drift / BARS_PER_SESSION, daily_sigma_ticks / np.sqrt(BARS_PER_SESSION),
                                BARS_PER_SESSION).cumsum()
        close_330 = open_ref + path[329] * TICK_SIZE
        high = open_ref + path.max() * TICK_SIZE
        low = open_ref + path.min() * TICK_SIZE

        rows.append({
            "session_date": session_date,
            "regime_sign": f"{regime:.0f}",
            "open_ref": f"{open_ref:.2f}",
            "published_level": f"{published_level:.2f}",
            "session_high": f"{high:.2f}",
            "session_low": f"{low:.2f}",
            "close_330": f"{close_330:.2f}",
            "data_quality": f"{min(1.0, 0.86 + generator.random() * 0.14):.4f}",
        })
        level = close_330
    return rows


def write(rows: list[dict], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    generator = np.random.default_rng(4242)
    planted_is_a = bool(generator.integers(0, 2))

    write(build(seed=11, planted=planted_is_a), OUT / "sessions_a.csv")
    write(build(seed=22, planted=not planted_is_a), OUT / "sessions_b.csv")

    (OUT / "MANIFEST.json").write_text(json.dumps({
        "sessions_per_file": SESSIONS,
        "tick_size": TICK_SIZE,
        "planted_effect_ticks": PLANTED_EFFECT_TICKS,
        "columns": {
            "session_date": "the trading date",
            "regime_sign": "-1 or +1, a state published before the open",
            "open_ref": "reference price at the open, in index points",
            "published_level": "a level published before the open, in index points",
            "session_high": "session high, index points",
            "session_low": "session low, index points",
            "close_330": "close of the session, index points",
            "data_quality": "share of the source that was on time and usable; gate at 0.85",
        },
        "note": "One of the two files contains a planted effect and the other does not. "
                "The answer is in ANSWER.txt, which you should not open until you have decided.",
    }, indent=2) + "\n", encoding="utf-8")

    (OUT / "ANSWER.txt").write_text(
        f"The planted effect is in sessions_{'a' if planted_is_a else 'b'}.csv.\n"
        f"It is a drift of {PLANTED_EFFECT_TICKS:.0f} ticks away from the opening reference, "
        "present only in negative-regime sessions.\n"
        "Both files contain a REAL volatility difference between regimes. If your method reported "
        "an effect in both files, you measured volatility and called it direction -- which is the "
        "exact mistake that closed the real family this exercise is modelled on.\n",
        encoding="utf-8",
    )
    print(f"wrote {SESSIONS} sessions to each of sessions_a.csv and sessions_b.csv in {OUT}")
    print("MANIFEST.json describes the columns; ANSWER.txt holds the answer.")


if __name__ == "__main__":
    main()
