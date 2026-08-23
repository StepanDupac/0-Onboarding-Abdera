"""Inference: how we decide whether a measured difference is real.

Three ideas do most of the work here.

1. Sessions are the unit of independence, not trades. Trades inside one session share a regime,
   a news cycle and an opening auction, so a bootstrap that resamples trades understates
   uncertainty. We resample whole sessions.
2. A maximum over many cells is not a discovery. Search enough variants of an idea and the best
   one always looks good; the honest comparison is against what the best of pure noise would have
   produced.
3. Gates run in a fixed order and stop at the first failure. Diagnostics run after a failure are
   how a dead result gets resurrected.

    python3 code/gates.py
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np


BOOTSTRAP_DRAWS = 2000
BOOTSTRAP_SEED = 20260823


def session_bootstrap_mean(values, sessions, draws=BOOTSTRAP_DRAWS, seed=BOOTSTRAP_SEED) -> dict:
    """Cluster bootstrap of a mean, resampling whole sessions with replacement."""
    values, sessions = np.asarray(values, float), np.asarray(sessions)
    finite = np.isfinite(values)
    values, sessions = values[finite], sessions[finite]
    if not len(values):
        return {"n": 0}
    unique = np.unique(sessions)
    table = {key: values[sessions == key] for key in unique}
    generator = np.random.default_rng(seed)
    means = np.empty(draws)
    for draw in range(draws):
        picked = generator.choice(unique, size=len(unique), replace=True)
        means[draw] = np.concatenate([table[key] for key in picked]).mean()
    return {
        "n": int(len(values)),
        "sessions": int(len(unique)),
        "mean": float(values.mean()),
        "ci_low": float(np.quantile(means, 0.025)),
        "ci_high": float(np.quantile(means, 0.975)),
    }


def two_sample_session_bootstrap(a_values, a_sessions, b_values, b_sessions,
                                 draws=BOOTSTRAP_DRAWS, seed=BOOTSTRAP_SEED) -> dict:
    """Cluster bootstrap of a difference in means between two disjoint groups of sessions."""
    a_values, a_sessions = np.asarray(a_values, float), np.asarray(a_sessions)
    b_values, b_sessions = np.asarray(b_values, float), np.asarray(b_sessions)
    a_table = {k: a_values[a_sessions == k] for k in np.unique(a_sessions)}
    b_table = {k: b_values[b_sessions == k] for k in np.unique(b_sessions)}
    a_keys, b_keys = np.array(list(a_table)), np.array(list(b_table))
    generator = np.random.default_rng(seed)
    diffs = np.empty(draws)
    for draw in range(draws):
        a_pick = generator.choice(a_keys, size=len(a_keys), replace=True)
        b_pick = generator.choice(b_keys, size=len(b_keys), replace=True)
        diffs[draw] = (
            np.concatenate([a_table[k] for k in a_pick]).mean()
            - np.concatenate([b_table[k] for k in b_pick]).mean()
        )
    return {
        "diff": float(a_values.mean() - b_values.mean()),
        "n_a": int(len(a_values)), "n_b": int(len(b_values)),
        "sessions_a": int(len(a_keys)), "sessions_b": int(len(b_keys)),
        "ci_low": float(np.quantile(diffs, 0.025)),
        "ci_high": float(np.quantile(diffs, 0.975)),
        "excludes_zero": bool(np.quantile(diffs, 0.025) > 0 or np.quantile(diffs, 0.975) < 0),
    }


def expected_max_t(cells: int) -> float:
    """Expected maximum of `cells` independent standard normal draws.

        E[max] ~ sqrt(2 ln n) - (ln ln n + ln 4pi) / (2 sqrt(2 ln n))

    Use it as the noise ceiling for a search. If you swept 54 cells and your best t-statistic is
    1.6, you have found nothing: independent noise alone would be expected to produce about 2.1.
    Correlated cells lower the ceiling, so this is the generous version of the comparison.
    """
    if cells < 2:
        return 0.0
    root = math.sqrt(2.0 * math.log(cells))
    return root - (math.log(math.log(cells)) + math.log(4.0 * math.pi)) / (2.0 * root)


def design_effect(trades_per_session: float, intra_session_correlation: float) -> float:
    """Variance inflation from clustering: sqrt(1 + (m - 1) * rho)."""
    return math.sqrt(1.0 + (trades_per_session - 1.0) * intra_session_correlation)


@dataclass
class Gate:
    name: str
    passed: bool
    detail: str


def run_gates(gates: list[Gate]) -> dict:
    """Evaluate gates in order and stop at the first failure.

    Stopping matters. Once a gate has failed, every further statistic is a search for a reason to
    keep going, and a research programme that always finds one never kills anything.
    """
    for index, gate in enumerate(gates):
        if not gate.passed:
            return {
                "verdict": "DEAD",
                "failed_at": gate.name,
                "detail": gate.detail,
                "gates_not_evaluated": [g.name for g in gates[index + 1:]],
            }
    return {"verdict": "SURVIVES", "failed_at": None}


def main() -> None:
    print("INFERENCE")
    print("=" * 70)

    print("\n1. The noise ceiling for a search")
    print(f"   {'cells swept':>12s} {'E[max |t|] under pure noise':>30s}")
    for cells in (1, 5, 20, 54, 200, 1287):
        print(f"   {cells:12d} {expected_max_t(cells):30.2f}")
    print("\n   A real sweep from the workspace: 54 vol-surface cells, best explore t = 1.62.")
    print("   Independent noise alone would be expected to reach 2.13. The search did not even")
    print("   clear its own null, which is as clean a negative as this method produces.")

    print("\n2. Clustering inflates the standard error")
    print(f"   {'trades/session':>15s} {'rho':>6s} {'design effect':>15s}")
    for m, rho in ((1.3, 0.30), (3.0, 0.30), (5.0, 0.30), (10.0, 0.30)):
        print(f"   {m:15.1f} {rho:6.2f} {design_effect(m, rho):15.2f}")
    print("\n   At roughly one trade per session clustering costs almost nothing. At five it costs")
    print("   half again on the standard error, which is the difference between t = 2.1 and 1.4.")

    print("\n3. Does the test find a real effect, and does it reject a fake one?")
    replications = 40
    detected_real = detected_null = 0
    for replication in range(replications):
        generator = np.random.default_rng(1000 + replication)
        sessions_a = np.repeat([f"a{i}" for i in range(60)], 3)
        sessions_b = np.repeat([f"b{i}" for i in range(60)], 3)
        real = two_sample_session_bootstrap(
            generator.normal(8.0, 12.0, 180), sessions_a,
            generator.normal(0.0, 12.0, 180), sessions_b,
            draws=400, seed=replication)
        null = two_sample_session_bootstrap(
            generator.normal(0.0, 12.0, 180), sessions_a,
            generator.normal(0.0, 12.0, 180), sessions_b,
            draws=400, seed=replication)
        detected_real += real["excludes_zero"]
        detected_null += null["excludes_zero"]
    print(f"   planted +8 effect detected in {detected_real}/{replications} replications (power)")
    print(f"   planted NO effect detected in {detected_null}/{replications} replications "
          f"(false positives)")
    print("\n   The second number is the one to internalise. A 95% interval is wrong about one")
    print("   time in twenty BY CONSTRUCTION, so a single significant cell is not a discovery --")
    print("   it is the expected behaviour of the method. That is the whole reason we preregister")
    print("   ONE primary endpoint, and why a result found by sweeping needs a far higher bar")
    print("   than a result found by asking one question.")

    print("\n4. Gates stop at the first failure")
    outcome = run_gates([
        Gate("sample", True, "243 short / 211 long sessions against a floor of 100"),
        Gate("primary_differential", False, "-7.43 ticks, 95% CI [-31.75, +18.93] contains zero"),
        Gate("beats_phantom_levels", True, "never evaluated"),
        Gate("survives_sign_scramble", True, "never evaluated"),
    ])
    print(f"   verdict: {outcome['verdict']} at {outcome['failed_at']}")
    print(f"   detail: {outcome['detail']}")
    print(f"   not evaluated: {outcome['gates_not_evaluated']}")
    print("\n   Those later gates are not passes. They are absent, and an absent gate can never")
    print("   count towards a pass.")


if __name__ == "__main__":
    main()
