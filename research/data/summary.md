# Cross-venue perp arbitrage: live sampling summary

- Sampling window (UTC): **2026-11-24T23:29:08Z to 2026-11-24T23:58:18Z**; first/last sample ts 2026-11-24T23:29:08Z / 2026-11-24T23:58:08Z; 30 samples, 60 s apart.
- Coins: 50 with at least one sampled venue, top-50 by CoinGecko rank that list on 2+ venues. Venues: OKX, Kraken, Hyperliquid, Aster, Lighter, dYdX. Coin-venue pairs compared: 575 (572 after mismatch filter).
- Mid gap = |mA - mB| / avg mid. Executable spread = max(bidA - askB, bidB - askA) / avg mid. Both in bps, gross of fees, top-of-book only, no transfer or funding-timing costs.
- Funding: annualised = rate x 8760 / interval_h x 100. Differential = 7d mean of per-period annualised rates. Positive A-B => short A, long B.
- Sign conventions: positive rate = longs pay shorts. Lighter history sign taken from `direction` (long = +).
- Mismatch filter: coin-pairs whose median mid ratio is outside 1/1.5..1.5 are excluded from rankings (symbol identity or unit issue).

**Excluded as mismatched:** QNT OKX-Aster (mid ratio 0.205); QNT OKX-Kraken (mid ratio 0.205); QNT OKX-Lighter (mid ratio 0.205)

## Pooled by venue pair (all coins, ok pairs only)

| pair | coin-pairs | samples | med abs gap | exec med | exec p90 | exec max | >0 % | >10 % | >20 % | >30 % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| OKX-Kraken | 38 | 1140 | 3.1 | -0.9 | 5.3 | 17.8 | 36.6 | 0.4 | 0.0 | 0.0 |
| OKX-Hyperliquid | 40 | 1200 | 2.1 | 0.6 | 4.2 | 17.0 | 59.6 | 2.2 | 0.0 | 0.0 |
| OKX-Aster | 44 | 1320 | 2.1 | -1.1 | 5.3 | 29.2 | 27.5 | 4.3 | 2.2 | 0.0 |
| OKX-Lighter | 40 | 1200 | 2.5 | 0.0 | 5.3 | 17.6 | 47.2 | 2.1 | 0.0 | 0.0 |
| OKX-dYdX | 31 | 930 | 8.5 | -23.3 | -3.6 | 14.6 | 3.7 | 0.2 | 0.0 | 0.0 |
| Kraken-Hyperliquid | 40 | 1200 | 3.8 | 0.0 | 6.4 | 23.8 | 48.5 | 1.2 | 0.1 | 0.0 |
| Kraken-Aster | 41 | 1230 | 3.9 | -2.1 | 7.5 | 29.1 | 31.1 | 5.0 | 2.4 | 0.0 |
| Kraken-Lighter | 40 | 1200 | 3.7 | -0.7 | 6.9 | 15.4 | 42.4 | 1.0 | 0.0 | 0.0 |
| Kraken-dYdX | 33 | 990 | 10.4 | -26.3 | -1.4 | 23.2 | 7.9 | 1.4 | 0.2 | 0.0 |
| Hyperliquid-Aster | 43 | 1290 | 2.3 | -0.4 | 4.6 | 29.4 | 40.2 | 6.8 | 2.1 | 0.0 |
| Hyperliquid-Lighter | 42 | 1260 | 3.0 | 0.5 | 5.5 | 12.0 | 55.2 | 0.6 | 0.0 | 0.0 |
| Hyperliquid-dYdX | 33 | 990 | 8.5 | -23.9 | -2.5 | 15.5 | 5.9 | 0.2 | 0.0 | 0.0 |
| Aster-Lighter | 42 | 1260 | 3.2 | -0.5 | 5.4 | 26.2 | 39.6 | 4.2 | 2.0 | 0.0 |
| Aster-dYdX | 33 | 990 | 8.7 | -23.9 | -4.0 | 15.0 | 3.4 | 0.2 | 0.0 | 0.0 |
| Lighter-dYdX | 32 | 960 | 8.3 | -23.7 | -2.2 | 15.3 | 4.0 | 0.2 | 0.0 | 0.0 |

(Pooled over all samples including flagged coin-pairs, so use the per-pair rows for ranking.)

## Top 25 by p90 executable spread (bps)

| # | coin | pair | n | med abs gap | exec med | exec p90 | exec max | >0 % | >10 % | >20 % | >30 % | fund diff 7d (ann %) | trade |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | ASTER | OKX-Aster | 30 | 26.0 | 22.9 | 27.0 | 29.2 | 100 | 100 | 97 | 0 | -22.78 | short Aster / long OKX |
| 2 | ASTER | Hyperliquid-Aster | 30 | 24.7 | 23.0 | 25.9 | 29.4 | 100 | 100 | 90 | 0 | -18.01 | short Aster / long Hyperliquid |
| 3 | ASTER | Aster-Lighter | 30 | 28.1 | 22.9 | 25.2 | 26.2 | 100 | 100 | 83 | 0 | 19.56 | short Aster / long Lighter |
| 4 | ASTER | Kraken-Aster | 30 | 28.1 | 22.9 | 25.2 | 29.1 | 100 | 100 | 93 | 0 | -17.41 | short Aster / long Kraken |
| 5 | WLFI | Aster-Lighter | 30 | 17.5 | 15.0 | 17.5 | 20.0 | 100 | 63 | 0 | 0 | 14.99 | short Aster / long Lighter |
| 6 | BNB | Kraken-Aster | 30 | 17.0 | 14.0 | 16.5 | 20.1 | 100 | 100 | 3 | 0 | -2.21 | short Aster / long Kraken |
| 7 | CRO | OKX-Kraken | 30 | 5.7 | -10.2 | 15.3 | 17.8 | 27 | 17 | 0 | 0 | 43.37 | short OKX / long Kraken |
| 8 | KAS | Kraken-Hyperliquid | 30 | 22.2 | 10.4 | 14.6 | 23.8 | 100 | 50 | 3 | 0 | -88.68 | short Hyperliquid / long Kraken |
| 9 | GRAM | OKX-Lighter | 30 | 16.5 | 9.9 | 13.8 | 16.3 | 97 | 50 | 0 | 0 | -3.37 | short Lighter / long OKX |
| 10 | HYPE | Hyperliquid-Aster | 30 | 12.4 | 12.2 | 13.4 | 14.0 | 100 | 97 | 0 | 0 | 2.39 | short Hyperliquid / long Aster |
| 11 | VVV | OKX-Hyperliquid | 30 | 9.4 | 7.7 | 13.1 | 17.0 | 93 | 23 | 0 | 0 | -8.28 | short Hyperliquid / long OKX |
| 12 | ETH | Kraken-dYdX | 30 | 11.6 | 7.7 | 12.8 | 23.2 | 100 | 13 | 7 | 0 | -8.71 | short dYdX / long Kraken |
| 13 | BTC | Kraken-dYdX | 30 | 12.8 | 7.6 | 12.8 | 15.9 | 100 | 33 | 0 | 0 | 2.05 | short Kraken / long dYdX |
| 14 | PIEVERSE | OKX-Aster | 30 | 14.4 | 8.6 | 11.4 | 13.4 | 97 | 17 | 0 | 0 | -1.51 | short Aster / long OKX |
| 15 | HYPE | OKX-Hyperliquid | 30 | 10.2 | 10.0 | 11.3 | 11.9 | 100 | 57 | 0 | 0 | -5.18 | short Hyperliquid / long OKX |
| 16 | BNB | Hyperliquid-Aster | 30 | 10.8 | 10.4 | 11.1 | 13.0 | 100 | 87 | 0 | 0 | -1.06 | short Aster / long Hyperliquid |
| 17 | BNB | OKX-Aster | 30 | 10.2 | 10.0 | 10.9 | 12.4 | 100 | 57 | 0 | 0 | 0.84 | short OKX / long Aster |
| 18 | BNB | Kraken-Lighter | 30 | 11.2 | 8.3 | 10.3 | 13.2 | 100 | 17 | 0 | 0 | -3.29 | short Lighter / long Kraken |
| 19 | XMR | Kraken-Lighter | 30 | 14.6 | 7.2 | 10.0 | 15.4 | 100 | 10 | 0 | 0 | 19.18 | short Kraken / long Lighter |
| 20 | WLFI | OKX-Aster | 30 | 10.0 | 7.5 | 10.0 | 12.5 | 100 | 7 | 0 | 0 | -0.76 | short Aster / long OKX |
| 21 | HBAR | OKX-Lighter | 30 | 8.9 | 6.0 | 9.9 | 11.9 | 97 | 3 | 0 | 0 | 1.61 | short OKX / long Lighter |
| 22 | HYPE | Hyperliquid-Lighter | 30 | 8.9 | 8.1 | 9.8 | 10.9 | 100 | 10 | 0 | 0 | 2.93 | short Hyperliquid / long Lighter |
| 23 | POL | OKX-Lighter | 30 | 10.6 | 7.7 | 9.7 | 11.2 | 97 | 10 | 0 | 0 | -12.12 | short Lighter / long OKX |
| 24 | VVV | OKX-Lighter | 30 | 7.8 | 4.0 | 9.6 | 13.4 | 83 | 7 | 0 | 0 | -44.15 | short Lighter / long OKX |
| 25 | JUP | Aster-Lighter | 30 | 10.3 | 5.4 | 9.5 | 15.8 | 100 | 3 | 0 | 0 | 1.05 | short Aster / long Lighter |

## Top 25 by 7d funding differential (annualised %, absolute)

| # | coin | pair | fund diff (ann %) | A ann mean | B ann mean | trade | exec p90 (bps) |
|---:|---|---|---:|---:|---:|---|---:|
| 1 | MNT | Kraken-Hyperliquid | 463.93 | 428.22 | -35.71 | short Kraken / long Hyperliquid | 3.9 |
| 2 | MNT | Kraken-Lighter | 428.82 | 428.22 | -0.60 | short Kraken / long Lighter | 3.9 |
| 3 | KAS | Kraken-Aster | -90.65 | -79.70 | 10.95 | short Aster / long Kraken | -7.3 |
| 4 | KAS | Kraken-Hyperliquid | -88.68 | -79.70 | 8.98 | short Hyperliquid / long Kraken | 14.6 |
| 5 | MORPHO | Kraken-Aster | -60.93 | -57.53 | 3.41 | short Aster / long Kraken | -13.0 |
| 6 | JUP | Kraken-dYdX | -60.76 | -60.08 | 0.68 | short dYdX / long Kraken | -26.6 |
| 7 | CRO | Kraken-Lighter | -59.78 | -52.94 | 6.84 | short Lighter / long Kraken | 7.6 |
| 8 | MORPHO | OKX-Kraken | 59.75 | 2.22 | -57.53 | short OKX / long Kraken | -1.7 |
| 9 | MORPHO | Kraken-Lighter | -57.30 | -57.53 | -0.22 | short Lighter / long Kraken | -5.0 |
| 10 | BTW | OKX-Aster | -57.23 | 4.58 | 61.81 | short Aster / long OKX | 6.7 |
| 11 | MORPHO | Kraken-Hyperliquid | -45.59 | -57.53 | -11.94 | short Hyperliquid / long Kraken | -5.7 |
| 12 | VVV | OKX-Lighter | -44.15 | 10.95 | 55.10 | short Lighter / long OKX | 9.6 |
| 13 | CRO | OKX-Kraken | 43.37 | -9.57 | -52.94 | short OKX / long Kraken | 15.3 |
| 14 | JUP | Hyperliquid-dYdX | -40.74 | -40.06 | 0.68 | short dYdX / long Hyperliquid | -15.7 |
| 15 | CC | Aster-Lighter | -40.70 | -39.87 | 0.83 | short Lighter / long Aster | -5.2 |
| 16 | PUMP | Kraken-Aster | -40.29 | -31.36 | 8.93 | short Aster / long Kraken | -4.1 |
| 17 | PUMP | Kraken-Lighter | -39.79 | -31.36 | 8.43 | short Lighter / long Kraken | 8.2 |
| 18 | JUP | OKX-Kraken | 37.67 | -22.40 | -60.08 | short OKX / long Kraken | -4.5 |
| 19 | WLD | Kraken-dYdX | -37.14 | -37.15 | -0.01 | short dYdX / long Kraken | -21.2 |
| 20 | VVV | Aster-Lighter | -36.95 | 18.15 | 55.10 | short Lighter / long Aster | 2.1 |
| 21 | PUMP | Kraken-Hyperliquid | -36.69 | -31.36 | 5.33 | short Hyperliquid / long Kraken | 0.4 |
| 22 | VVV | Hyperliquid-Lighter | -35.87 | 19.23 | 55.10 | short Lighter / long Hyperliquid | 2.3 |
| 23 | MNT | Hyperliquid-Lighter | -35.11 | -35.71 | -0.60 | short Lighter / long Hyperliquid | 8.5 |
| 24 | PUMP | OKX-Kraken | 34.48 | 3.12 | -31.36 | short OKX / long Kraken | -4.1 |
| 25 | PEPE | Kraken-Lighter | -33.92 | -23.80 | 10.12 | short Lighter / long Kraken | -0.6 |

Full per coin x venue-pair table (all metrics, incl. flagged rows): `data/pairs_stats.csv`. Raw data: `data/samples.csv`, `data/depth.csv`, `data/funding.csv`, `data/listings.csv`.
