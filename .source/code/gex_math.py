"""Dealer gamma exposure: the model, from the option chain to a price level on the futures grid.

This is the mathematical core of the worked example in docs/07_worked_example.md. The family was
tested and closed -- it carries no edge -- which is exactly why it is safe and useful to publish
in full. The method is the transferable part.

    python3 code/gex_math.py
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np


CONTRACT_MULTIPLIER = 100.0
ONE_PERCENT = 0.01
MILLION = 1_000_000.0


def normal_pdf(x: np.ndarray) -> np.ndarray:
    return np.exp(-0.5 * x**2) / math.sqrt(2.0 * math.pi)


def d1(spot, strike, sigma, tau, rate, dividend_yield):
    """The Black-Scholes d1 term.

        d1 = [ ln(S/K) + (r - q + sigma^2 / 2) * tau ] / (sigma * sqrt(tau))
    """
    return (
        np.log(spot / strike) + (rate - dividend_yield + 0.5 * sigma**2) * tau
    ) / (sigma * np.sqrt(tau))


def black_scholes_gamma(spot, strike, sigma, tau, rate=0.0, dividend_yield=0.0):
    """Gamma: the second derivative of option value with respect to spot.

        Gamma = exp(-q * tau) * phi(d1) / (S * sigma * sqrt(tau))

    Gamma is identical for a call and a put at the same strike and expiry, which is why the sign
    convention below is a separate modelling decision rather than something the mathematics
    supplies.
    """
    return (
        np.exp(-dividend_yield * tau)
        * normal_pdf(d1(spot, strike, sigma, tau, rate, dividend_yield))
        / (spot * sigma * np.sqrt(tau))
    )


def dollar_gamma_per_percent(gamma, open_interest, spot):
    """Dollar value of the hedge a 1% move forces, per contract line.

        DG = Gamma * OI * multiplier * S^2 * 0.01

    Gamma is a change in delta per unit change in spot. Multiplying by S converts to delta per
    1% move; multiplying by S again and by the contract multiplier converts delta into dollars.
    """
    return gamma * open_interest * CONTRACT_MULTIPLIER * spot**2 * ONE_PERCENT


def dealer_signs(rights: np.ndarray, convention: str = "long_calls_short_puts") -> np.ndarray:
    """The modelling assumption, isolated so it can be ablated.

    Open interest counts contracts. It does not say who is long and who is short. Every published
    GEX number therefore rests on a convention, and the convention IS the model. Isolate it, name
    it, and test the result against its inversion and against random signs.
    """
    if convention == "long_calls_short_puts":
        return np.where(rights == "CALL", 1.0, -1.0)
    if convention == "inverted":
        return np.where(rights == "CALL", -1.0, 1.0)
    raise ValueError(f"unknown convention {convention!r}")


def net_gamma_profile(grid, strikes, sigmas, taus, signs, open_interest, rate=0.0, dividend_yield=0.0):
    """Net dealer dollar gamma as a function of hypothetical spot.

    Evaluates every contract's gamma at every point of the spot grid and sums the signed dollar
    gamma. The result N(S) is the quantity whose zero crossing defines the flip level.
    """
    spot_matrix = grid[np.newaxis, :]
    gamma_matrix = black_scholes_gamma(
        spot_matrix,
        strikes[:, np.newaxis],
        sigmas[:, np.newaxis],
        taus[:, np.newaxis],
        rate,
        dividend_yield,
    )
    weights = (signs * open_interest)[:, np.newaxis]
    return (gamma_matrix * weights * CONTRACT_MULTIPLIER * spot_matrix**2 * ONE_PERCENT).sum(axis=0)


def flip_level(grid: np.ndarray, profile: np.ndarray, spot: float) -> float:
    """The zero crossing of N(S) nearest spot, by linear interpolation.

    Above the flip, dealers are net long gamma and hedge against the move, which dampens it.
    Below it they are net short gamma and hedge with the move, which amplifies it. That is the
    theory. Returns NaN when the profile never crosses zero on the grid, which is a real and
    frequent outcome rather than an error.
    """
    products = profile[:-1] * profile[1:]
    candidates = []
    for index in np.flatnonzero(products < 0.0):
        left, right = profile[index], profile[index + 1]
        fraction = left / (left - right)
        candidates.append(grid[index] + fraction * (grid[index + 1] - grid[index]))
    candidates.extend(float(grid[i]) for i in np.flatnonzero(profile == 0.0))
    if not candidates:
        return float("nan")
    return float(min(candidates, key=lambda level: abs(level - spot)))


@dataclass(frozen=True)
class BasisMap:
    """Converting an index level into a futures tick index.

    The option chain prices the cash index; the strategy trades a futures contract on a discrete
    tick grid. The two differ by basis -- carry, dividends and financing -- which is measured from
    the same instant on both sides, never assumed.
    """

    futures_close: float
    index_close: float
    tick_size: float

    @property
    def basis_points(self) -> float:
        return self.futures_close - self.index_close

    def to_tick_index(self, index_level: float) -> float:
        if not np.isfinite(index_level):
            return float("nan")
        return float(round((index_level + self.basis_points) / self.tick_size))


def main() -> None:
    print("DEALER GAMMA: a worked calculation")
    print("=" * 70)

    spot = 5000.0
    strikes = np.array([4900.0, 4950.0, 5000.0, 5050.0, 5100.0, 5100.0])
    rights = np.array(["PUT", "PUT", "CALL", "CALL", "CALL", "PUT"])
    sigmas = np.array([0.22, 0.20, 0.18, 0.18, 0.19, 0.21])
    taus = np.array([7, 7, 7, 14, 14, 30]) / 365.0
    open_interest = np.array([9000.0, 6000.0, 5000.0, 4000.0, 8000.0, 3000.0])

    signs = dealer_signs(rights)
    gamma_at_spot = black_scholes_gamma(spot, strikes, sigmas, taus)
    per_line = dollar_gamma_per_percent(gamma_at_spot, open_interest, spot)

    print(f"\nspot = {spot:.0f}\n")
    print(f"{'strike':>8s} {'right':>6s} {'OI':>8s} {'gamma':>10s} {'$gamma/1%':>14s} {'signed':>14s}")
    for i in range(len(strikes)):
        print(
            f"{strikes[i]:8.0f} {rights[i]:>6s} {open_interest[i]:8.0f} "
            f"{gamma_at_spot[i]:10.6f} {per_line[i]:14,.0f} {signs[i] * per_line[i]:14,.0f}"
        )
    net = float(np.sum(signs * per_line))
    print(f"\nnet dealer gamma at spot: {net / MILLION:+.2f} $M per 1% move")
    print(f"regime: {'SHORT gamma (amplifying)' if net < 0 else 'LONG gamma (dampening)'}")

    grid = np.linspace(spot * 0.95, spot * 1.05, 81)
    profile = net_gamma_profile(grid, strikes, sigmas, taus, signs, open_interest)
    flip = flip_level(grid, profile, spot)
    print(f"flip level: {flip:.1f}  ({flip - spot:+.1f} from spot)")

    inverted = net_gamma_profile(
        grid, strikes, sigmas, taus, dealer_signs(rights, "inverted"), open_interest
    )
    print(f"\nsanity check, inverted convention: profile is exact negation "
          f"({np.allclose(profile, -inverted)}), so the flip LOCATION is convention-invariant")
    print("while the REGIME LABEL flips. Any test whose result depends on the convention must")
    print("therefore be tested against the inversion; that is what makes it an ablation and not")
    print("a decoration.")

    basis = BasisMap(futures_close=5012.5, index_close=5000.0, tick_size=0.25)
    print(f"\nbasis: {basis.basis_points:+.2f} index points")
    print(f"flip on the futures tick grid: {basis.to_tick_index(flip):.0f} ticks")


if __name__ == "__main__":
    main()
