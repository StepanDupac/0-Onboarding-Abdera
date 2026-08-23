"""Generate every figure in the handbook, from the real trade record where one exists.

    python3 code/make_figures.py

Writes SVG into figures/. Vector, so it stays sharp in the PDF at any zoom.
"""
from __future__ import annotations

import csv
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter

ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "figures"
TRADES = ROOT / "exercise" / "data" / "strategy_trades.csv"

INK = "#14161a"
CREAM = "#f4efe4"
ACCENT = "#b8894a"
BLUE = "#2f5d78"
RED = "#a4443a"
GREEN = "#3f6b52"
GREY = "#8b929b"
FAINT = "#dfe3e7"

BUFFER_USD = 2000.0
TARGET_USD = 3000.0

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Charter", "Georgia", "DejaVu Serif"],
    "font.size": 9,
    "axes.edgecolor": GREY,
    "axes.labelcolor": INK,
    "axes.titlesize": 10.5,
    "axes.titleweight": "bold",
    "axes.titlecolor": INK,
    "text.color": INK,
    "xtick.color": GREY,
    "ytick.color": GREY,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.06,
})


def style(ax, grid_axis="y"):
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.grid(axis=grid_axis, color=FAINT, linewidth=0.7)
    ax.set_axisbelow(True)


def money(value, _pos=None):
    sign = "-" if value < 0 else ""
    return f"{sign}${abs(value):,.0f}"


def save(fig, name):
    FIGURES.mkdir(exist_ok=True)
    fig.savefig(FIGURES / f"{name}.svg", format="svg")
    plt.close(fig)
    print(f"  figures/{name}.svg")


def load_trades():
    """The real 143-trade record. Dates are reduced to the calendar year on purpose: every figure
    here needs the year and none needs the day, and the exact session dates of a live candidate are
    not something to publish."""
    with TRADES.open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    return (
        np.array([row["year"] for row in rows]),
        np.array([float(row["net_usd"]) for row in rows]),
        np.array([row["exit_reason"] for row in rows]),
    )


# ----------------------------------------------------------------- mathematics

def figure_cost_hurdle():
    fig, ax = plt.subplots(figsize=(6.4, 3.1))
    widths = np.linspace(20, 320, 400)
    for cost, colour, label in ((6.0, BLUE, "S&P, 6 ticks"), (9.0, ACCENT, "Nasdaq, 9 ticks")):
        ax.plot(widths, 100 * cost / widths, color=colour, linewidth=2, label=f"cost C = {label}")
    ax.axhline(3.0, color=RED, linestyle="--", linewidth=1.2)
    ax.text(305, 3.6, "comfort line, 3 points", color=RED, fontsize=8, ha="right")
    ax.scatter([34], [17.6], s=44, color=RED, zorder=5)
    ax.annotate("tight fade\nS=12 T=22\n17.6 points", (34, 17.6), (74, 16.4),
                fontsize=8, color=RED, arrowprops=dict(arrowstyle="->", color=RED, lw=1))
    ax.scatter([288], [3.1], s=44, color=GREEN, zorder=5)
    ax.annotate("wide continuation\nS=48 T=240\n3.1 points", (288, 3.1), (196, 8.2),
                fontsize=8, color=GREEN, arrowprops=dict(arrowstyle="->", color=GREEN, lw=1))
    ax.set_xlabel("bracket width  S + T  (ticks)")
    ax.set_ylabel("win-rate points the signal\nmust manufacture")
    ax.set_title("The cost hurdle is inversely proportional to bracket width")
    ax.set_ylim(0, 22)
    ax.legend(frameon=False, fontsize=8)
    style(ax)
    save(fig, "cost_hurdle")


def figure_win_rate_null():
    fig, ax = plt.subplots(figsize=(6.4, 3.0))
    rr = np.linspace(0.4, 6.0, 300)
    ax.plot(rr, 100 / (1 + rr), color=BLUE, linewidth=2, label="free win rate  1/(1+RR)")
    ax.plot(rr, 100 * (1 + 1.5 * 9.0 / 48.0) / (1 + rr), color=ACCENT, linewidth=2,
            label="required at the gate (S = 48, C = 9)")
    ax.fill_between(rr, 100 / (1 + rr), 100 * (1 + 1.5 * 9.0 / 48.0) / (1 + rr),
                    color=ACCENT, alpha=0.12)
    ax.set_xlabel("reward : risk")
    ax.set_ylabel("win rate (%)")
    ax.set_title("A high win rate is a statement about geometry until proved otherwise")
    ax.legend(frameon=False, fontsize=8)
    ax.set_ylim(0, 75)
    style(ax)
    save(fig, "win_rate_null")


def figure_noise_ceiling():
    fig, ax = plt.subplots(figsize=(6.4, 2.9))
    cells = np.arange(2, 1400)
    root = np.sqrt(2 * np.log(cells))
    ceiling = root - (np.log(np.log(cells)) + math.log(4 * math.pi)) / (2 * root)
    ax.plot(cells, ceiling, color=BLUE, linewidth=2)
    ax.set_xscale("log")
    ax.scatter([54], [2.13], s=52, color=RED, zorder=5)
    ax.annotate("54 cells swept:\nnoise alone reaches 2.13", (54, 2.13), (100, 1.35),
                fontsize=8, color=RED, arrowprops=dict(arrowstyle="->", color=RED, lw=1))
    ax.axhline(1.62, color=GREEN, linestyle="--", linewidth=1.2)
    ax.text(1300, 1.68, "best observed t = 1.62", color=GREEN, fontsize=8, ha="right")
    ax.set_xlabel("number of cells swept (log scale)")
    ax.set_ylabel("expected max |t|\nunder pure noise")
    ax.set_title("A maximum over many cells is not a discovery")
    ax.set_ylim(0.8, 3.6)
    style(ax)
    save(fig, "noise_ceiling")


def figure_explore_confirm():
    fig, ax = plt.subplots(figsize=(6.4, 3.0))
    labels = ["best explore\ncell", "negative gamma\n+ high front share", "front-share\nlow tercile",
              "monthly expiry\nfollow-through"]
    explore = [29.0, 31.1, 21.8, 59.8]
    confirm = [-6.1, -32.9, -2.0, -10.1]
    x = np.arange(len(labels))
    ax.bar(x - 0.19, explore, 0.38, color=BLUE, label="exploration window")
    ax.bar(x + 0.19, confirm, 0.38, color=RED, label="confirmation window")
    ax.axhline(0, color=INK, linewidth=1)
    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=7.5)
    ax.set_ylabel("follow-through (ticks)")
    ax.set_title("Every cell selected in exploration inverted or collapsed out of sample")
    ax.legend(frameon=False, fontsize=8, loc="lower left")
    style(ax)
    save(fig, "explore_confirm")


def figure_gamma_profile():
    from gex_math import black_scholes_gamma, dealer_signs, flip_level, net_gamma_profile

    spot = 5000.0
    strikes = np.array([4900.0, 4950.0, 5000.0, 5050.0, 5100.0, 5100.0])
    rights = np.array(["PUT", "PUT", "CALL", "CALL", "CALL", "PUT"])
    sigmas = np.array([0.22, 0.20, 0.18, 0.18, 0.19, 0.21])
    taus = np.array([7, 7, 7, 14, 14, 30]) / 365.0
    oi = np.array([9000.0, 6000.0, 5000.0, 4000.0, 8000.0, 3000.0])
    grid = np.linspace(spot * 0.95, spot * 1.05, 400)

    fig, (top, bottom) = plt.subplots(2, 1, figsize=(6.4, 4.5), sharex=True,
                                      gridspec_kw={"height_ratios": [1, 1.3]})
    for strike, right, sigma, tau, quantity in zip(strikes, rights, sigmas, taus, oi):
        gamma = black_scholes_gamma(grid, strike, sigma, tau)
        colour = GREEN if right == "CALL" else RED
        top.plot(grid, gamma * quantity, color=colour, linewidth=1.1, alpha=0.75)
    top.set_ylabel("gamma × OI")
    top.set_title("Each contract's gamma, and the net profile they sum to")
    top.plot([], [], color=GREEN, label="calls"); top.plot([], [], color=RED, label="puts")
    top.legend(frameon=False, fontsize=8)
    style(top)

    profile = net_gamma_profile(grid, strikes, sigmas, taus, dealer_signs(rights), oi) / 1e6
    bottom.plot(grid, profile, color=INK, linewidth=2)
    bottom.fill_between(grid, profile, 0, where=profile > 0, color=GREEN, alpha=0.18)
    bottom.fill_between(grid, profile, 0, where=profile < 0, color=RED, alpha=0.18)
    bottom.axhline(0, color=GREY, linewidth=1)
    flip = flip_level(grid, profile, spot)
    bottom.axvline(flip, color=ACCENT, linestyle="--", linewidth=1.6)
    bottom.text(flip + 6, profile.max() * 0.55, f"flip {flip:.0f}", color=ACCENT, fontsize=8.5)
    bottom.axvline(spot, color=GREY, linestyle=":", linewidth=1.2)
    bottom.text(spot + 6, profile.min() * 0.8, "spot", color=GREY, fontsize=8.5)
    bottom.text(grid[8], profile.min() * 0.62, "short gamma\nhedging amplifies",
                color=RED, fontsize=8)
    bottom.text(grid[-150], profile.max() * 0.62, "long gamma\nhedging damps",
                color=GREEN, fontsize=8)
    bottom.set_xlabel("index level"); bottom.set_ylabel("net dealer gamma\n($M per 1% move)")
    style(bottom)
    save(fig, "gamma_profile")


# --------------------------------------------------------------- the strategy

def figure_equity_curve():
    dates, net, _ = load_trades()
    equity = np.concatenate([[0.0], np.cumsum(net)])
    peak = np.maximum.accumulate(equity)
    fig, (top, bottom) = plt.subplots(2, 1, figsize=(6.4, 4.2), sharex=True,
                                      gridspec_kw={"height_ratios": [2.4, 1]})
    x = np.arange(len(equity))
    top.plot(x, equity, color=BLUE, linewidth=1.9)
    top.fill_between(x, equity, 0, color=BLUE, alpha=0.10)
    top.yaxis.set_major_formatter(FuncFormatter(money))
    top.set_ylabel("cumulative net")
    top.set_title(f"Evaluation profile, {len(net)} trades, stress costs, unconstrained account")
    years = {}
    for index, year in enumerate(dates):
        years.setdefault(year, index)
    last_label = -99
    for year, index in years.items():
        top.axvline(index, color=FAINT, linewidth=0.8, zorder=0)
        if index - last_label >= 9:
            top.text(index + 1.5, equity.max() * 1.02, year, color=GREY, fontsize=7.5,
                     ha="left", va="top")
            last_label = index
    style(top)

    bottom.fill_between(x, equity - peak, 0, color=RED, alpha=0.35, linewidth=0)
    bottom.yaxis.set_major_formatter(FuncFormatter(money))
    bottom.set_ylabel("drawdown"); bottom.set_xlabel("trade number")
    style(bottom)
    save(fig, "equity_curve")


def figure_trade_distribution():
    _, net, _ = load_trades()
    fig, (left, right) = plt.subplots(1, 2, figsize=(6.4, 2.9))
    bins = np.linspace(net.min(), net.max(), 34)
    left.hist(net[net > 0], bins=bins, color=GREEN, alpha=0.85, label=f"wins ({(net > 0).sum()})")
    left.hist(net[net <= 0], bins=bins, color=RED, alpha=0.85, label=f"losses ({(net <= 0).sum()})")
    left.axvline(0, color=INK, linewidth=1)
    left.xaxis.set_major_formatter(FuncFormatter(money))
    left.set_xlabel("net per trade"); left.set_ylabel("trades")
    left.set_title(f"Win rate {100 * (net > 0).mean():.1f}%", fontsize=9.5)
    left.legend(frameon=False, fontsize=7.5)
    style(left)

    ordered = np.sort(net)[::-1]
    trimmed = ordered[max(1, int(round(len(ordered) * 0.05))):]
    bars = [net.mean(), trimmed.mean()]
    right.bar(["untrimmed", "top 5%\nremoved"], bars, color=[BLUE, ACCENT], width=0.55)
    for index, value in enumerate(bars):
        right.text(index, value + 14, money(value), ha="center", fontsize=8.5, color=INK)
    right.axhline(0, color=INK, linewidth=1)
    right.set_ylabel("mean per trade")
    right.set_title("Survives its own trimming", fontsize=9.5)
    right.set_ylim(0, max(bars) * 1.3)
    style(right)
    save(fig, "trade_distribution")


def figure_monte_carlo():
    """Simulate whole ACCOUNTS, not equity curves.

    An evaluation account stops the moment it touches a barrier: +$3,000 passes it, -$2,000 ends
    it. Letting a simulated path run past either barrier would describe something that cannot
    happen, so every path here is truncated at its first touch. That truncation is the entire
    reason the outcome distribution looks the way it does.
    """
    _, net, _ = load_trades()
    generator = np.random.default_rng(20260823)
    accounts, max_trades = 4000, 30

    paths, outcomes, lengths = [], [], []
    for _ in range(accounts):
        equity, path = 0.0, [0.0]
        outcome = "neither"
        for trade in range(max_trades):
            equity += generator.choice(net)
            path.append(equity)
            if equity >= TARGET_USD:
                outcome = "pass"; break
            if equity <= -BUFFER_USD:
                outcome = "breach"; break
        paths.append(path); outcomes.append(outcome); lengths.append(len(path) - 1)

    passed = outcomes.count("pass")
    breached = outcomes.count("breach")
    neither = outcomes.count("neither")
    pass_lengths = [n for n, o in zip(lengths, outcomes) if o == "pass"]

    fig, (left, right) = plt.subplots(1, 2, figsize=(6.4, 3.3),
                                      gridspec_kw={"width_ratios": [1.45, 1]})
    for path, outcome in list(zip(paths, outcomes))[:260]:
        colour = GREEN if outcome == "pass" else RED if outcome == "breach" else GREY
        left.plot(range(len(path)), path, color=colour, linewidth=0.7, alpha=0.32)
    left.axhline(TARGET_USD, color=GREEN, linewidth=1.6)
    left.text(9.6, TARGET_USD + 260, "pass  +$3,000", color=GREEN, fontsize=8.5, ha="right")
    left.axhline(-BUFFER_USD, color=RED, linewidth=1.6)
    left.text(9.6, -BUFFER_USD - 700, "breach  -$2,000", color=RED, fontsize=8.5, ha="right")
    left.axhline(0, color=GREY, linewidth=0.9, linestyle=":")
    left.set_xlim(0, 10); left.set_ylim(-3600, 6200)
    left.yaxis.set_major_formatter(FuncFormatter(money))
    left.set_xlabel("trades taken"); left.set_ylabel("account equity")
    left.set_title("4,000 simulated accounts, each stopped at its\nfirst barrier", fontsize=9.5)
    style(left)

    bars = [100 * passed / accounts, 100 * breached / accounts, 100 * neither / accounts]
    right.bar(["pass", "breach", "open"], bars, color=[GREEN, RED, GREY], width=0.58)
    for index, value in enumerate(bars):
        right.text(index, value + 1.6, f"{value:.0f}%", ha="center", fontsize=10, color=INK)
    right.set_ylabel("% of accounts")
    right.set_ylim(0, max(bars) * 1.32)
    right.set_title(f"Median {int(np.median(pass_lengths))} trade to pass;\n"
                    f"the account gets about two attempts", fontsize=9.5)
    style(right)
    save(fig, "monte_carlo")
    return passed / accounts, breached / accounts, float(np.median(pass_lengths))


def figure_cadence():
    fig, (left, right) = plt.subplots(1, 2, figsize=(6.4, 2.9))
    labels = ["existing\nstrategy", "speed-optimised\nprofile"]
    left.bar(labels, [52, 15], color=[GREY, ACCENT], width=0.5)
    for index, value in enumerate([52, 15]):
        left.text(index, value + 1.6, f"{value}", ha="center", fontsize=10, color=INK)
    left.set_ylabel("median sessions to pass")
    left.set_title("Time to clear the target", fontsize=9.5)
    style(left)

    right.bar(labels, [1492, 759], color=[GREY, ACCENT], width=0.5)
    for index, value in enumerate([1492, 759]):
        right.text(index, value + 40, money(value), ha="center", fontsize=9.5, color=INK)
    right.yaxis.set_major_formatter(FuncFormatter(money))
    right.set_title("Fees per pass", fontsize=9.5)
    style(right)
    save(fig, "cadence")


def figure_per_year():
    dates, net, _ = load_trades()
    years = sorted(set(dates))
    means = [net[dates == year].mean() for year in years]
    counts = [int((dates == year).sum()) for year in years]
    fig, ax = plt.subplots(figsize=(6.4, 2.7))
    colours = [GREEN if value > 0 else RED for value in means]
    ax.bar(years, means, color=colours, width=0.6)
    for index, (value, count) in enumerate(zip(means, counts)):
        offset = 42 if value > 0 else -78
        ax.text(index, value + offset, f"n={count}", ha="center", fontsize=7.5, color=GREY)
    ax.axhline(0, color=INK, linewidth=1)
    ax.yaxis.set_major_formatter(FuncFormatter(money))
    ax.set_ylabel("mean net per trade")
    ax.set_title("Five of six years positive; the sixth is near flat")
    style(ax)
    save(fig, "per_year")


def main():
    print("building figures")
    figure_cost_hurdle()
    figure_win_rate_null()
    figure_noise_ceiling()
    figure_explore_confirm()
    figure_gamma_profile()
    figure_equity_curve()
    figure_trade_distribution()
    passed, breached, median_trades = figure_monte_carlo()
    figure_cadence()
    figure_per_year()
    print(f"\nMonte Carlo: pass {passed:.1%}, breach {breached:.1%}, "
          f"median {median_trades:.0f} trade(s) to pass")


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    main()
