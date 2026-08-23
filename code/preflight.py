"""Pre-flight arithmetic: the calculations that kill an idea before you write a strategy.

Every line here is a kill switch. Running this on paper costs ten minutes; discovering the same
thing after a month of implementation costs a month. Run it first, every time.

    python3 code/preflight.py
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Geometry:
    """A bracket: a stop and a target, both as tick distances from entry."""

    stop_ticks: float
    target_ticks: float
    round_turn_cost_ticks: float
    gate_multiple: float = 1.5

    @property
    def reward_risk(self) -> float:
        return self.target_ticks / self.stop_ticks

    @property
    def geometric_breakeven_win_rate(self) -> float:
        """P(target before stop) for a driftless random walk.

        A price path with no drift hits the nearer barrier more often, in exact proportion to the
        distances: P(target first) = S / (S + T) = 1 / (1 + RR). This is the number your signal has
        to beat. A win rate that merely exceeds a coin flip means nothing; a win rate that exceeds
        this means something.
        """
        return self.stop_ticks / (self.stop_ticks + self.target_ticks)

    @property
    def cost_burden_points(self) -> float:
        """Win-rate percentage points the signal must manufacture just to pay costs.

        Breakeven after cost C requires  p*(T) - (1-p)(S) = C,  so  p* = (S + C) / (S + T).
        Subtracting the driftless null S / (S + T) leaves exactly  C / (S + T).

        The whole cost hurdle, expressed in win-rate points, is inversely proportional to the
        total width of the bracket. Narrow brackets are expensive. This single ratio has killed
        more candidate strategies here than bad signals have.
        """
        return 100.0 * self.round_turn_cost_ticks / (self.stop_ticks + self.target_ticks)

    @property
    def required_win_rate(self) -> float:
        """Win rate needed to clear the gate multiple, not merely to break even."""
        numerator = self.stop_ticks + self.gate_multiple * self.round_turn_cost_ticks
        return numerator / (self.stop_ticks + self.target_ticks)

    def expected_gross_ticks(self, win_rate: float) -> float:
        return win_rate * self.target_ticks - (1.0 - win_rate) * self.stop_ticks


WARN_BURDEN_POINTS = 3.0
KILL_REQUIRED_WIN_RATE = 0.60
KILL_MIN_TRADES = 100


def report(name: str, geometry: Geometry, honest_win_rate: float, expected_trades: int) -> str:
    """Print the pre-flight table and return DEAD, MARGINAL or OK.

    The binding kills are the ones you cannot argue with: your own honest estimate falling short
    of the required win rate, and a sample too small to reach the statistical gates. The cost
    burden is a warning that scales rather than a cliff -- at 3 points you are already asking the
    signal for a lot, at 17 you are asking for something no equity-index signal has ever
    delivered.
    """
    print(f"\n{name}")
    print("-" * len(name))
    rows = [
        ("stop / target (ticks)", f"{geometry.stop_ticks:.0f} / {geometry.target_ticks:.0f}"),
        ("reward:risk", f"{geometry.reward_risk:.2f}"),
        ("round-turn cost (ticks)", f"{geometry.round_turn_cost_ticks:.2f}"),
        ("geometric breakeven win rate", f"{geometry.geometric_breakeven_win_rate:.1%}"),
        ("cost burden (win-rate points)", f"{geometry.cost_burden_points:.1f}"),
        ("required win rate at gate", f"{geometry.required_win_rate:.1%}"),
        ("your honest win-rate estimate", f"{honest_win_rate:.1%}"),
        ("expected gross ticks/trade", f"{geometry.expected_gross_ticks(honest_win_rate):+.2f}"),
        ("expected trade count", f"{expected_trades}"),
    ]
    for label, value in rows:
        print(f"  {label:32s} {value:>10s}")

    kills, warnings = [], []
    if geometry.cost_burden_points > WARN_BURDEN_POINTS:
        warnings.append(
            f"cost burden {geometry.cost_burden_points:.1f} points is above the "
            f"{WARN_BURDEN_POINTS:.0f}-point comfort line; the barrier geometry is doing a lot of "
            "the work and a wider bracket would cost less"
        )
    if geometry.required_win_rate > KILL_REQUIRED_WIN_RATE:
        kills.append(
            f"required win rate {geometry.required_win_rate:.1%} exceeds "
            f"{KILL_REQUIRED_WIN_RATE:.0%}; fix the geometry or abandon the idea"
        )
    if honest_win_rate < geometry.required_win_rate:
        kills.append(
            f"your own estimate {honest_win_rate:.1%} is below the required "
            f"{geometry.required_win_rate:.1%}"
        )
    if expected_trades < KILL_MIN_TRADES:
        kills.append(
            f"expected trade count {expected_trades} is below {KILL_MIN_TRADES}; "
            "the statistical gates cannot be reached"
        )

    for reason in warnings:
        print(f"    warning: {reason}")
    if kills:
        print("  VERDICT: DEAD")
        for reason in kills:
            print(f"    - {reason}")
        return "DEAD"
    if warnings:
        print("  VERDICT: MARGINAL -- proceed only with a named mechanism for the excess")
        return "MARGINAL"
    print("  VERDICT: OK (permission to start, not a result)")
    return "OK"


def main() -> None:
    print("PRE-FLIGHT ARITHMETIC")
    print("=" * 70)
    print("Cost figures below are the NQ stress surface used in the research workspace.")

    report(
        "A: mean-reversion fade, tight bracket",
        Geometry(stop_ticks=12, target_ticks=22, round_turn_cost_ticks=6.0),
        honest_win_rate=0.45,
        expected_trades=400,
    )
    report(
        "B: opening-drive continuation, wide bracket",
        Geometry(stop_ticks=48, target_ticks=240, round_turn_cost_ticks=9.0),
        honest_win_rate=0.29,
        expected_trades=143,
    )
    report(
        "C: a good geometry with too few trades",
        Geometry(stop_ticks=40, target_ticks=160, round_turn_cost_ticks=9.0),
        honest_win_rate=0.30,
        expected_trades=42,
    )

    print("\n" + "=" * 70)
    print("Read A against B. Both sound plausible in words. A must manufacture 17.6 win-rate")
    print("points over the driftless null and its own honest estimate falls 17 points short, so")
    print("it is dead before a line of code exists. B asks for 3.1 points and its estimate clears")
    print("the requirement, so it is worth building. C has an acceptable geometry and cannot")
    print("reach the sample gates, which is a different kind of dead and just as final.")
    print("")
    print("Nothing downstream of the entry decision moves these numbers. Sizing, risk management,")
    print("plan selection and lockout logic move dollars around; they do not move gross ticks per")
    print("contract, which is a property of the signal and the barrier alone.")


if __name__ == "__main__":
    main()
