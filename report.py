"""Stage 5: build a Markdown report and write it into reports/.

Running this file alone is the "one command" the assignment asks for:
it fetches, computes metrics, applies rules, and writes the report.
A separate main.py would just be a one-line wrapper around
write_report(), so it's skipped, one less file that does nothing of
its own.
"""

import statistics
from datetime import datetime, timezone
from pathlib import Path

from fetch import PAIRS, fetch_ohlc
from metrics import max_drawdown, moving_average, trend_status, volatility
from rules import TREND_THRESHOLD_FIXED, trend_rule_dynamic, trend_rule_fixed, volatility_rule

REPORTS_DIR = Path(__file__).parent / "reports"


def gather_results():
    results = {}
    data_timestamp = None
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
        data_timestamp = complete[-1].time  # most recent complete day, same across pairs
    return results, data_timestamp


def build_report():
    results, data_timestamp = gather_results()
    vol_labels = volatility_rule({p: r["volatility"] for p, r in results.items()})
    median_abs_deviation = statistics.median(abs(r["deviation"]) for r in results.values())

    data_date = datetime.fromtimestamp(data_timestamp, tz=timezone.utc).strftime("%Y-%m-%d")
    now = datetime.now(tz=timezone.utc)
    generated_at = now.strftime("%Y-%m-%d %H:%M UTC")

    most_volatile = max(results, key=lambda p: results[p]["volatility"])

    lines = [
        "# Crypto Volatility & Trend Report",
        "",
        f"Data as of: {data_date} (last complete daily candle, UTC)",
        f"Report generated: {generated_at}",
        "",
        "**Question:** Over the last 30 days, which of these five coins (BTC, ETH, SOL, "
        "XRP, ADA) has been the most volatile, and is each one currently trading above "
        "or below its own recent trend?",
        "",
        f"**Most volatile over the last 30 days: {most_volatile}** "
        f"({results[most_volatile]['volatility']:.2%} daily standard deviation of returns).",
        "",
        f"Trend is reported two ways: a fixed {TREND_THRESHOLD_FIXED:.1f}-point cutoff, and a "
        f"dynamic one ({median_abs_deviation:.2f} points today), the median |deviation| across "
        "all 5 coins, same relative approach as the volatility label.",
        "",
        "| Pair | Volatility (30d) | Vol. label | Drawdown (30d) | vs 7d MA | Fixed (5pt) | Dynamic |",
        "|------|------------------|------------|-----------------|----------|-------------|---------|",
    ]

    for pair, r in results.items():
        fixed_label = trend_rule_fixed(r["direction"], r["deviation"])
        dynamic_label = trend_rule_dynamic(r["direction"], r["deviation"], median_abs_deviation)
        lines.append(
            f"| {pair} | {r['volatility']:.2%} | {vol_labels[pair]} | "
            f"{r['drawdown']:.2%} | {r['deviation']:+.2f}% | {fixed_label} | {dynamic_label} |"
        )

    lines += [
        "",
        "These are observations drawn from historical price data, not predictions, "
        "and not trading signals.",
        "",
        "This project is for education only and is not financial advice.",
        "",
    ]

    return "\n".join(lines), now


def write_report():
    content, now = build_report()
    REPORTS_DIR.mkdir(exist_ok=True)
    filename = REPORTS_DIR / f"report_{now.strftime('%Y%m%d_%H%M%S')}.md"
    filename.write_text(content, encoding="utf-8")
    print(f"Wrote {filename}")


if __name__ == "__main__":
    write_report()
