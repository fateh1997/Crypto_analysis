"""Stage 2: compute volatility, trend, and drawdown metrics from the fetched candles."""

import statistics

from fetch import PAIRS, fetch_ohlc

VOLATILITY_WINDOW = 30  # days of returns
TREND_WINDOW = 7        # days for the moving average
DRAWDOWN_WINDOW = 30    # days


def daily_returns(closes):
    return [(closes[i] - closes[i - 1]) / closes[i - 1] for i in range(1, len(closes))]


def volatility(closes, window=VOLATILITY_WINDOW):
    """Sample standard deviation (n-1) of the last `window` days' returns."""
    recent_closes = closes[-(window + 1):]
    returns = daily_returns(recent_closes)
    return statistics.stdev(returns)


def moving_average(closes, window=TREND_WINDOW):
    return statistics.mean(closes[-window:])


def trend_status(current_price, ma):
    deviation_pct = (current_price - ma) / ma * 100
    direction = "above" if current_price >= ma else "below"
    return direction, deviation_pct


def max_drawdown(closes, window=DRAWDOWN_WINDOW):
    """Largest peak-to-trough decline, as a positive fraction, over the window."""
    recent = closes[-window:]
    peak = recent[0]
    worst = 0.0
    for price in recent:
        peak = max(peak, price)
        drawdown = (peak - price) / peak
        worst = max(worst, drawdown)
    return worst


if __name__ == "__main__":
    for pair in PAIRS:
        complete, current = fetch_ohlc(pair)
        closes = [c.close for c in complete]

        vol = volatility(closes)
        ma = moving_average(closes)
        direction, deviation = trend_status(current.close, ma)
        dd = max_drawdown(closes)

        print(f"{pair}:")
        print(f"  30-day volatility (stdev of daily returns): {vol:.2%}")
        print(f"  7-day moving average: {ma:,.4f}")
        print(f"  current price {current.close:,.4f} is {direction} the 7-day MA ({deviation:+.2f}%)")
        print(f"  30-day max drawdown: {dd:.2%}")
