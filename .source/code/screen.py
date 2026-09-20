"""A reference screen: one primary endpoint, the controls that make it mean something.

This is the shape of every screen in the workspace, reduced to its essentials and pointed at the
sample data so it runs anywhere. Read it as the answer to "what does testing a hypothesis actually
look like", not as a library.

    python3 code/make_sample_data.py
    python3 code/screen.py
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gates import Gate, run_gates, two_sample_session_bootstrap  # noqa: E402


DATA = Path(__file__).resolve().parents[1] / "exercise" / "data"

TICK_SIZE = 0.25
MIN_DATA_QUALITY = 0.85
MIN_SESSIONS_PER_REGIME = 100
PHANTOM_OFFSETS_TICKS = (-200.0, -150.0, -100.0, 100.0, 150.0, 200.0)


def load(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def displacement_continuation(row: dict, level_offset_ticks: float) -> tuple[float, float] | None:
    """The primary endpoint, computed for one session.

    Displacement  d0 = open_ref - level, in ticks, is where the session started relative to the
    published level. Continuation  A = sign(d0) * (close - open_ref)  is positive when the session
    moved further AWAY from the level. If the level organises the session's path, A should differ
    between regimes; if the level is arbitrary, it should not.
    """
    open_ref = float(row["open_ref"])
    level = float(row["published_level"]) + level_offset_ticks * TICK_SIZE
    displacement = (open_ref - level) / TICK_SIZE
    if displacement == 0.0:
        return None
    move = (float(row["close_330"]) - open_ref) / TICK_SIZE
    return displacement, float(np.sign(displacement)) * move


def collect(rows: list[dict], level_offset_ticks: float = 0.0) -> dict:
    values, sessions, regimes = [], [], []
    for row in rows:
        if float(row["data_quality"]) < MIN_DATA_QUALITY:
            continue
        computed = displacement_continuation(row, level_offset_ticks)
        if computed is None:
            continue
        values.append(computed[1])
        sessions.append(row["session_date"])
        regimes.append(float(row["regime_sign"]))
    values, sessions, regimes = np.array(values), np.array(sessions), np.array(regimes)
    negative, positive = regimes < 0, regimes > 0
    return {
        "a_values": values[negative], "a_sessions": sessions[negative],
        "b_values": values[positive], "b_sessions": sessions[positive],
    }


def differential(rows: list[dict], level_offset_ticks: float = 0.0) -> dict:
    cell = collect(rows, level_offset_ticks)
    return two_sample_session_bootstrap(
        cell["a_values"], cell["a_sessions"], cell["b_values"], cell["b_sessions"]
    )


def screen(path: Path) -> None:
    rows = load(path)
    print(f"\n{path.name}")
    print("=" * 62)

    real = differential(rows)
    print(f"  primary differential (negative minus positive regime)")
    print(f"    sessions      {real['sessions_a']} negative / {real['sessions_b']} positive")
    print(f"    difference    {real['diff']:+7.2f} ticks")
    print(f"    95% interval  [{real['ci_low']:+7.2f}, {real['ci_high']:+7.2f}]")

    # CONTROL 1 -- phantom levels. Run the identical machinery against levels that are definitely
    # not special. If the real level does not beat them, the level is not what produced the result.
    phantoms = [differential(rows, offset)["diff"] for offset in PHANTOM_OFFSETS_TICKS]
    phantom_mean = float(np.mean(phantoms))
    print(f"  phantom-level control")
    print(f"    mean phantom differential  {phantom_mean:+7.2f} ticks")
    print(f"    real minus phantom         {real['diff'] - phantom_mean:+7.2f} ticks")

    # CONTROL 2 -- regime scramble. Shuffle the regime labels across sessions. Anything the test
    # still finds is an artifact of the machinery rather than of the labels.
    generator = np.random.default_rng(11)
    scrambled = []
    for _ in range(5):
        shuffled = [dict(row) for row in rows]
        labels = [row["regime_sign"] for row in rows]
        generator.shuffle(labels)
        for row, label in zip(shuffled, labels, strict=True):
            row["regime_sign"] = label
        scrambled.append(differential(shuffled)["diff"])
    print(f"  regime-scramble control")
    print(f"    scrambled differentials    "
          f"{', '.join(f'{value:+.1f}' for value in scrambled)}")

    outcome = run_gates([
        Gate("sample", min(real["sessions_a"], real["sessions_b"]) >= MIN_SESSIONS_PER_REGIME,
             f"{real['sessions_a']}/{real['sessions_b']} against a floor of {MIN_SESSIONS_PER_REGIME}"),
        Gate("primary_differential", real["excludes_zero"],
             f"{real['diff']:+.2f}, CI [{real['ci_low']:+.2f}, {real['ci_high']:+.2f}]"),
        Gate("beats_phantom_levels", abs(real["diff"]) > abs(phantom_mean) * 2.0,
             f"real {real['diff']:+.2f} against mean phantom {phantom_mean:+.2f}"),
        Gate("survives_regime_scramble", max(abs(v) for v in scrambled) < abs(real["diff"]),
             f"largest scrambled {max(scrambled, key=abs):+.2f}"),
    ])
    print(f"  VERDICT: {outcome['verdict']}"
          + (f" at {outcome['failed_at']} -- {outcome['detail']}" if outcome["failed_at"] else ""))
    if outcome["failed_at"]:
        print(f"  not evaluated: {outcome['gates_not_evaluated']}")


def main() -> None:
    if not (DATA / "sessions_a.csv").exists():
        raise SystemExit("run: python3 code/make_sample_data.py")
    print("REFERENCE SCREEN")
    print("One preregistered primary endpoint, two controls, gates in order, stop on failure.")
    for name in ("sessions_a.csv", "sessions_b.csv"):
        screen(DATA / name)
    print("\n" + "=" * 62)
    print("One of these two files contains a planted effect and the other does not. A method that")
    print("reports an effect in both has measured the volatility difference, which is real in both")
    print("files, and mistaken it for direction. That is precisely the error that closed the real")
    print("research family this screen is modelled on.")


if __name__ == "__main__":
    main()
