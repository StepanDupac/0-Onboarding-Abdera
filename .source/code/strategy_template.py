"""The portable strategy contract, annotated.

A strategy source in this firm is one file that runs byte-for-byte in three places: the research
workspace, the firm's measurement engine, and the live runtime. That promise is what the rules
below protect. In the real repository these files carry NO comments and NO docstrings -- naming
carries the explanation, and a linter enforces it. This copy is annotated because it is teaching
material; strip the prose when you write the real thing.

Every rule here exists because breaking it destroyed a result. The annotations say which.
"""
from __future__ import annotations

import numpy as np

# In the real workspace every import comes from the portable kit, never from the engine internals.
# from veritas_kit import (ANCHOR_RTH, BarArray, Context, Params, SessionFlag, Strategy,
#                          atr, opening_range, param, register, time_since_session_open)


class ExampleParams:
    """Every tunable is a declared parameter with bounds. No numeric literals in the logic.

    Bounds are not decoration: they define the search space an optimiser may explore, and they are
    part of the frozen record of what the strategy was allowed to be.
    """

    range_minutes = 30           # opening range length
    stop_atr = 0.9               # stop as a multiple of ATR
    reward_risk = 5.0            # target = reward_risk * stop
    min_stop_ticks = 40
    max_stop_ticks = 120
    risk_cost_ticks = 9.0        # cost buffer folded into the risk budget
    max_risk_usd = 980.0         # FLAT stake: no account term anywhere
    max_quantity = 40
    last_entry_minutes = 180
    max_history_gap_days = 7


class ExampleStrategy:
    """One registered strategy class per file. Never import another strategy."""

    name = "research_example_opening_breakout"
    symbols = ("MNQ",)           # execution instrument
    bar_spec = "1m"
    warmup_bars = 180            # at least the longest indicator period, with margin
    family = "opening_range"     # from a shared vocabulary; part of the identity
    lane = "prop_aggressive"

    def prepare(self, bars) -> dict[str, np.ndarray]:
        """Vectorised indicators, computed once over the whole history.

        RULE: publish every series you intend to compare, and read it back in on_bar. Do not
        compare a value from the engine's price accessor against an indicator. Every OHLC value a
        strategy sees is an INTEGER TICK INDEX, not a price; on the Nasdaq contract the two differ
        by a factor of four. Three strategies in this firm's history compared the two units. The
        comparison does not raise -- it silently produces a number -- and in each case a whole
        branch became unreachable while the strategy kept running and kept reporting.

        RULE: recompute indicators per contract. A futures series is spliced from delivery months,
        and an indicator that runs across a roll boundary smears two different instruments
        together. Measured on real data: roll gaps up to 1,131 ticks against an ATR of 10 to 40.
        """
        close = bars.close.astype(np.float64)

        risk_band = np.full(len(bars), np.nan)
        contract_changes = np.flatnonzero(bars.contract[1:] != bars.contract[:-1]) + 1
        starts = [0] + [int(index) for index in contract_changes]
        stops = starts[1:] + [len(bars)]
        for start, stop in zip(starts, stops, strict=True):
            risk_band[start:stop] = atr(  # noqa: F821 - illustrative
                bars.high[start:stop], bars.low[start:stop], bars.close[start:stop], 20
            )

        upper, lower = opening_range(bars, self.params.range_minutes, ANCHOR_RTH)  # noqa: F821
        return {
            "close_tick_index": close,
            "opening_range_high_tick_index": upper,
            "opening_range_low_tick_index": lower,
            "risk_band_ticks": risk_band,
            "rth_elapsed_seconds": time_since_session_open(bars, ANCHOR_RTH),  # noqa: F821
        }

    def on_day_start(self, ctx, trade_date: int) -> None:
        """Every latch is cleared here, and this is the documented clearing condition.

        RULE: a latch with no clearing condition is fatal. Two strategies in this firm set a
        portfolio lock when drawdown reached a threshold and cleared it nowhere. It closed 25
        sessions into a seven-year backtest and stayed closed for the remaining 6.9 years, while
        the run reported a healthy status the whole time, because nothing breached -- because
        nothing traded.
        """
        ctx.state["attempted"] = False
        ctx.state["quantity_zero"] = 0

    def on_bar(self, ctx) -> None:
        elapsed = ctx.series("rth_elapsed_seconds")

        if ctx.session_flag != SessionFlag.RTH:  # noqa: F821
            return
        if not ctx.position.is_flat or ctx.state.get("attempted", False):
            return
        if not np.isfinite(elapsed) or elapsed > self.params.last_entry_minutes * 60.0:
            return

        close = ctx.series("close_tick_index")
        previous = ctx.series("close_tick_index", 1)   # lag >= 0 only; a negative lag raises
        upper = ctx.series("opening_range_high_tick_index")
        risk_band = ctx.series("risk_band_ticks")

        # RULE: guard every comparison with isfinite. Indicators return NaN over their warm-up and
        # propagate it, and `nan > x` is False, so a missing guard produces a strategy that
        # silently never trades and reports "no signal" rather than "bug".
        if not all(np.isfinite(v) for v in (close, previous, upper, risk_band)):
            return
        if not (previous <= upper and close > upper):
            return

        stop_ticks = min(
            max(int(round(self.params.stop_atr * risk_band)), self.params.min_stop_ticks),
            self.params.max_stop_ticks,
        )
        target_ticks = max(int(round(stop_ticks * self.params.reward_risk)), stop_ticks + 1)

        # RULE: size from a quantity that does not ratchet. Live headroom is a distance to breach,
        # not a risk budget. Two strategies sized off headroom; under an end-of-day trailing
        # drawdown the floor only ever rises, headroom froze at $506.92, quantity floored to zero,
        # and the strategy was silent for 2.25 million bars.
        risk_per_contract = (stop_ticks + self.params.risk_cost_ticks) * ctx.instrument.tick_value
        quantity = min(self.params.max_quantity, int(self.params.max_risk_usd // risk_per_contract))

        # RULE: quantity == 0 is an EVENT, not a silent return. A strategy that declines to size is
        # otherwise indistinguishable in the results from one that saw no signal, and that is
        # exactly how the failure above went unnoticed for a whole research programme.
        if quantity <= 0:
            ctx.state["quantity_zero"] += 1
            return

        ctx.state["attempted"] = True
        ctx.bracket("buy", quantity=quantity,
                    take_profit_ticks=target_ticks, stop_loss_ticks=stop_ticks, tag=self.name)


CHECKLIST = """
Before a strategy source is accepted:

  units       every comparison is tick index against tick index; no price/tick mixing
  causality   a signal formed on bar i fills on i+1 or later; no negative lags; nothing in
              prepare() normalises, centres or filters over the whole sample
  reachability every branch proved reachable, with per-clause bar counts. A clause firing on 0%
              or 100% of bars is a bug until proved otherwise
  rolls       every feature that differences across a session boundary either back-adjusts or
              refuses roll sessions, and the notes say which
  latches     every state variable that survives a day has a clearing condition and a test for it
  sizing      the base budget does not read a ratcheting quantity; quantity == 0 is recorded
  structure   one registered class per file, no cross-strategy imports, no comments or docstrings
"""
