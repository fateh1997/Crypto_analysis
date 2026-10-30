"""Stage 1: fetch OHLC candles from Kraken and validate their shape.

No external dependencies on purpose: urllib + json from the standard
library are enough for a single unauthenticated GET request.
"""

import json
import urllib.request
from collections import namedtuple

Candle = namedtuple("Candle", "time open high low close vwap volume count")

PAIRS = ["XBTUSD", "ETHUSD", "SOLUSD", "XRPUSD", "ADAUSD"]
INTERVAL = 1440  # daily candles


def fetch_ohlc(pair, interval=INTERVAL):
    url = f"https://api.kraken.com/0/public/OHLC?pair={pair}&interval={interval}"
    with urllib.request.urlopen(url, timeout=15) as resp:
        data = json.loads(resp.read())

    if data["error"]:
        raise ValueError(f"{pair}: {data['error']}")

    # Kraken's result key isn't always the pair name we asked for
    # (e.g. XBTUSD comes back as XXBTZUSD). Read it dynamically.
    result_key = next(k for k in data["result"] if k != "last")
    raw_candles = data["result"][result_key]

    candles = [
        Candle(
            time=row[0],
            open=float(row[1]),
            high=float(row[2]),
            low=float(row[3]),
            close=float(row[4]),
            vwap=float(row[5]),
            volume=float(row[6]),
            count=row[7],
        )
        for row in raw_candles
    ]

    # The last candle is always today's, still-forming one (per Kraken's docs).
    current = candles[-1]
    complete = candles[:-1]
    return complete, current


def validate(complete, current):
    """Cheap sanity checks. Returns a list of human-readable warning strings."""
    issues = []

    expected = 720
    if len(complete) != expected:
        issues.append(f"expected {expected} complete candles, got {len(complete)}")

    for a, b in zip(complete, complete[1:]):
        gap = b.time - a.time
        if gap != 86400:
            issues.append(f"gap of {gap}s between {a.time} and {b.time} (expected 86400)")

    for c in complete + [current]:
        if not (c.low <= c.open <= c.high and c.low <= c.close <= c.high):
            issues.append(f"OHLC invariant broken at {c.time}: {c}")

    return issues


if __name__ == "__main__":
    for pair in PAIRS:
        complete, current = fetch_ohlc(pair)
        issues = validate(complete, current)
        print(f"{pair}: {len(complete)} complete candles, current candle time={current.time}")
        if issues:
            for issue in issues:
                print(f"  ! {issue}")
        else:
            print("  all checks passed")
