# Crypto Analysis

## Question
    Over the last 30 days, which of these five coins (BTC, ETH, SOL, XRP, ADA) has been the most volatile, and is each one currently trading above or below its own recent trend?

## What I learned about the data
    Each candle is an 8-item array: time, open, high, low, close, vwap, volume, and trade count. Price/volume fields come back as strings, not numbers; only time and count are raw integers. Requesting interval=1440 for ~2 years of history returns 721 candles: 720 completed days plus one extra, always-present candle for the current, still-forming day, which has artificially low volume since the day isn’t finished. The response’s dictionary key for a pair isn’t always what you requested (XBTUSD comes back as XXBTZUSD), so code must read keys dynamically rather than assuming them. An unknown pair returns only an error array with no result key at all.

## General Workflow

crypto_analysis/
├── README.md
├── requirements.txt   (intentionally near-empty, see Stage 1)
├── .gitignore
├── AI_LOG.md
├── fetch.py
├── metrics.py
├── rules.py
├── report.py
├── main.py
└── reports/


## Analysis Method

Volatility uses sample standard deviation (statistics.stdev, divides by n−1), not population stdev. Standard convention when treating your 30 days as a sample rather than the entire universe of possible days, and it’s what Excel’s STDEV and most finance tooling default to. With n=30 the difference from population stdev is small, but worth knowing which one you’re reporting.

7-day window for the moving average, picked as a middle ground: long enough to smooth day-to-day noise, short enough to still react within a week. If you’d rather see 14-day or 20-day, it’s a one-line change (TREND_WINDOW), no real reason it has to be 7 beyond “reasonable default,” happy to change it if you want to justify a different number in the README instead.

## Rules
Rule 1 (volatility): flag a coin “elevated” if its volatility is above the median of the 5, “typical” otherwise. Median of your run (1.52, 1.91, 2.17, 2.30, 3.54) is 2.17%, so XRP and ADA would be “elevated,” BTC/ETH/SOL “typical.” Why relative-to-the-group instead of a fixed number like “above 3% is high”: an absolute cutoff would need updating every time the market’s overall volatility regime shifts; a relative one adapts on its own.

Rule 2 (trend): “notably” below/above if the deviation from the 7-day MA exceeds 5 percentage points, otherwise plain “below”/”above”. Why 5: it’s not arbitrary, there’s an actual gap in your real data, BTC/ETH/XRP cluster at -3.65% to -4.52%, SOL/ADA sit apart at -5.81%/-5.84%. 5% sits right in that gap.

## How to run it
No external packages needed (standard library only).

1. Clone the repo
2. From inside the `crypto_analysis` folder, run: main.py
3. This fetches live data for all 5 coins, computes the metrics, applies both rules, and writes a timestamped `.md` file into `reports/`.