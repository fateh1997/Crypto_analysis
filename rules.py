"""Stage 4: apply threshold rules to the computed metrics.

Thresholds come from the real data (see README's "why this number"
explanation), not invented in the abstract. These are observations,
not trading signals.

Trend gets two readings on purpose: a fixed cutoff (simple, stable
across days) and a dynamic one (relative to that day's spread, same
idea as the volatility rule). They won't always agree; both are
reported so you can compare.
"""

import statistics

from fetch import PAIRS, fetch_ohlc
from metrics import max_drawdown, moving_average, trend_status, volatility

TREND_THRESHOLD_FIXED = 5.0  # percentage points; chosen from an actual gap seen in one day's data


def volatility_rule(pair_volatilities):
    """pair_volatilities: {pair: volatility}. Returns {pair: 'elevated'|'typical'}."""
    median = statistics.median(pair_volatilities.values())
    return {
        pair: "elevated" if vol > median else "typical"
        for pair, vol in pair_volatilities.items()
    }


def trend_rule_fixed(direction, deviation_pct, threshold=TREND_THRESHOLD_FIXED):
    qualifier = "notably " if abs(deviation_pct) > threshold else ""
    return f"{qualifier}{direction}"


def trend_rule_dynamic(direction, deviation_pct, median_abs_deviation):
    """'notably' if this coin's |deviation| is above today's median |deviation| across all coins."""
    qualifier = "notably " if abs(deviation_pct) > median_abs_deviation else ""
    return f"{qualifier}{direction}"


if __name__ == "__main__":
    results = {}
    for pair in PAIRS:
        complete, current = fetch_ohlc(pair)
        closes = [c.close for c in complete]
        direction, deviation = trend_status(current.close, moving_average(closes))
        results[pair] = {
            "volatility": volatility(closes),
            "drawdown": max_drawdown(closes),
            "direction": direction,
            "deviation": deviation,
        }

    vol_labels = volatility_rule({p: r["volatility"] for p, r in results.items()})
    median_abs_deviation = statistics.median(abs(r["deviation"]) for r in results.values())

    print(f"(today's dynamic trend threshold: {median_abs_deviation:.2f} percentage points)\n")

    for pair, r in results.items():
        fixed_label = trend_rule_fixed(r["direction"], r["deviation"])
        dynamic_label = trend_rule_dynamic(r["direction"], r["deviation"], median_abs_deviation)
        print(
            f"{pair}: volatility {r['volatility']:.2%} ({vol_labels[pair]}), "
            f"drawdown {r['drawdown']:.2%}"
        )
        print(
            f"  trend {r['deviation']:+.2f}%  |  fixed (5pt): {fixed_label}"
            f"  |  dynamic ({median_abs_deviation:.2f}pt median): {dynamic_label}"
        )
