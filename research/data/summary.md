# Cross-venue perp arbitrage: live sampling summary

- Sampling window (UTC): **2026-11-24T23:29:08Z to in progress**; first/last sample ts 2026-11-24T23:29:08Z / 2026-11-24T23:31:08Z; 3 samples, 60 s apart.
- Coins: 50 with at least one sampled venue, top-50 by CoinGecko rank that list on 2+ venues. Venues: OKX, Kraken, Hyperliquid, Aster, Lighter, dYdX. Coin-venue pairs compared: 575 (572 after mismatch filter).
- Mid gap = |mA - mB| / avg mid. Executable spread = max(bidA - askB, bidB - askA) / avg mid. Both in bps, gross of fees, top-of-book only, no transfer or funding-timing costs.
- Funding: annualised = rate x 8760 / interval_h x 100. Differential = 7d mean of per-period annualised rates. Positive A-B => short A, long B.
- Sign conventions: positive rate = longs pay shorts. Lighter history sign taken from `direction` (long = +).
- Mismatch filter: coin-pairs whose median mid ratio is outside 1/1.5..1.5 are excluded from rankings (symbol identity or unit issue).

**Excluded as mismatched:** QNT OKX-Aster (mid ratio 0.205); QNT OKX-Kraken (mid ratio 0.205); QNT OKX-Lighter (mid ratio 0.205)

## Pooled by venue pair (all coins, ok pairs only)

| pair | coin-pairs | samples | med abs gap | exec med | exec p90 | exec max | >0 % | >10 % | >20 % | >30 % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| OKX-Kraken | 38 | 114 | 2.8 | -0.9 | 5.4 | 9.7 | 33.3 | 0.0 | 0.0 | 0.0 |
| OKX-Hyperliquid | 40 | 120 | 2.0 | 0.5 | 4.3 | 11.3 | 59.2 | 1.7 | 0.0 | 0.0 |
| OKX-Aster | 44 | 132 | 2.4 | -1.1 | 5.6 | 20.7 | 28.0 | 4.5 | 1.5 | 0.0 |
| OKX-Lighter | 40 | 120 | 2.9 | 0.2 | 5.2 | 11.1 | 52.5 | 1.7 | 0.0 | 0.0 |
| OKX-dYdX | 31 | 93 | 9.7 | -22.9 | -5.4 | 1.4 | 2.2 | 0.0 | 0.0 | 0.0 |
| Kraken-Hyperliquid | 40 | 120 | 4.3 | -0.2 | 6.6 | 14.2 | 46.7 | 2.5 | 0.0 | 0.0 |
| Kraken-Aster | 41 | 123 | 4.2 | -2.4 | 7.3 | 22.8 | 31.7 | 4.9 | 1.6 | 0.0 |
| Kraken-Lighter | 40 | 120 | 3.1 | -1.3 | 6.2 | 10.5 | 40.8 | 0.8 | 0.0 | 0.0 |
| Kraken-dYdX | 33 | 99 | 12.4 | -24.6 | -1.7 | 9.5 | 7.1 | 0.0 | 0.0 | 0.0 |
| Hyperliquid-Aster | 43 | 129 | 2.1 | -0.5 | 5.9 | 24.7 | 39.5 | 6.2 | 1.6 | 0.0 |
| Hyperliquid-Lighter | 42 | 126 | 3.0 | 0.4 | 5.5 | 8.9 | 53.2 | 0.0 | 0.0 | 0.0 |
| Hyperliquid-dYdX | 33 | 99 | 8.8 | -22.2 | -4.2 | 4.1 | 6.1 | 0.0 | 0.0 | 0.0 |
| Aster-Lighter | 42 | 126 | 3.6 | -0.5 | 5.1 | 21.6 | 42.1 | 5.6 | 1.6 | 0.0 |
| Aster-dYdX | 33 | 99 | 10.4 | -23.4 | -5.1 | 1.4 | 4.0 | 0.0 | 0.0 | 0.0 |
| Lighter-dYdX | 32 | 96 | 9.0 | -22.6 | -3.1 | 0.7 | 5.2 | 0.0 | 0.0 | 0.0 |

(Pooled over all samples including flagged coin-pairs, so use the per-pair rows for ranking.)

## Top 25 by p90 executable spread (bps)

| # | coin | pair | n | med abs gap | exec med | exec p90 | exec max | >0 % | >10 % | >20 % | >30 % | fund diff 7d (ann %) | trade |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | ASTER | Hyperliquid-Aster | 3 | 25.8 | 24.5 | 24.6 | 24.7 | 100 | 100 | 67 | 0 | -18.01 | short Aster / long Hyperliquid |
| 2 | ASTER | Kraken-Aster | 3 | 27.0 | 20.7 | 22.4 | 22.8 | 100 | 100 | 67 | 0 | -17.41 | short Aster / long Kraken |
| 3 | ASTER | Aster-Lighter | 3 | 25.6 | 21.4 | 21.5 | 21.6 | 100 | 100 | 67 | 0 | 19.56 | short Aster / long Lighter |
| 4 | ASTER | OKX-Aster | 3 | 22.8 | 20.7 | 20.7 | 20.7 | 100 | 100 | 67 | 0 | -22.78 | short Aster / long OKX |
| 5 | WLFI | Aster-Lighter | 3 | 21.2 | 17.5 | 19.5 | 20.0 | 100 | 100 | 0 | 0 | 14.99 | short Aster / long Lighter |
| 6 | BNB | Kraken-Aster | 3 | 17.0 | 13.8 | 15.4 | 15.8 | 100 | 100 | 0 | 0 | -2.21 | short Aster / long Kraken |
| 7 | KAS | Kraken-Hyperliquid | 3 | 22.6 | 11.1 | 13.6 | 14.2 | 100 | 100 | 0 | 0 | -88.68 | short Hyperliquid / long Kraken |
| 8 | HYPE | Hyperliquid-Aster | 3 | 13.2 | 13.0 | 13.1 | 13.2 | 100 | 100 | 0 | 0 | 2.39 | short Hyperliquid / long Aster |
| 9 | WLFI | OKX-Aster | 3 | 12.5 | 10.0 | 12.0 | 12.5 | 100 | 33 | 0 | 0 | -0.76 | short Aster / long OKX |
| 10 | HYPE | OKX-Hyperliquid | 3 | 11.5 | 11.3 | 11.3 | 11.3 | 100 | 67 | 0 | 0 | -5.18 | short Hyperliquid / long OKX |
| 11 | GRAM | OKX-Lighter | 3 | 17.1 | 10.9 | 11.1 | 11.1 | 100 | 67 | 0 | 0 | -3.37 | short Lighter / long OKX |
| 12 | WLFI | Hyperliquid-Aster | 3 | 12.1 | 10.0 | 10.8 | 11.0 | 100 | 33 | 0 | 0 | -13.95 | short Aster / long Hyperliquid |
| 13 | BNB | Hyperliquid-Aster | 3 | 9.8 | 9.6 | 10.7 | 10.9 | 100 | 33 | 0 | 0 | -1.06 | short Aster / long Hyperliquid |
| 14 | GRAM | Aster-Lighter | 3 | 16.3 | 9.4 | 10.6 | 10.9 | 100 | 33 | 0 | 0 | 6.25 | short Aster / long Lighter |
| 15 | BTW | OKX-Aster | 3 | 13.6 | 2.6 | 10.5 | 12.4 | 67 | 33 | 0 | 0 | -57.23 | short Aster / long OKX |
| 16 | BNB | OKX-Aster | 3 | 9.8 | 9.6 | 10.4 | 10.6 | 100 | 33 | 0 | 0 | 0.84 | short OKX / long Aster |
| 17 | BNB | Kraken-Lighter | 3 | 11.3 | 7.8 | 9.9 | 10.5 | 100 | 33 | 0 | 0 | -3.29 | short Lighter / long Kraken |
| 18 | PIEVERSE | OKX-Aster | 3 | 13.3 | 8.8 | 9.6 | 9.8 | 100 | 0 | 0 | 0 | -1.51 | short Aster / long OKX |
| 19 | ETH | OKX-Kraken | 3 | 8.8 | 8.5 | 9.5 | 9.7 | 100 | 0 | 0 | 0 | -4.39 | short Kraken / long OKX |
| 20 | ETH | Kraken-dYdX | 3 | 12.5 | 8.9 | 9.4 | 9.5 | 100 | 0 | 0 | 0 | -8.71 | short dYdX / long Kraken |
| 21 | POL | OKX-Lighter | 3 | 12.3 | 8.3 | 9.4 | 9.6 | 100 | 0 | 0 | 0 | -12.12 | short Lighter / long OKX |
| 22 | HBAR | Hyperliquid-Lighter | 3 | 10.7 | 8.1 | 8.8 | 8.9 | 100 | 0 | 0 | 0 | -8.40 | short Lighter / long Hyperliquid |
| 23 | BTC | OKX-Kraken | 3 | 8.7 | 8.6 | 8.7 | 8.7 | 100 | 0 | 0 | 0 | -5.28 | short Kraken / long OKX |
| 24 | JUP | Aster-Lighter | 3 | 7.4 | 5.0 | 8.6 | 9.5 | 100 | 0 | 0 | 0 | 1.05 | short Aster / long Lighter |
| 25 | BTC | Kraken-Aster | 3 | 8.5 | 8.4 | 8.5 | 8.5 | 100 | 0 | 0 | 0 | -0.29 | short Aster / long Kraken |

## Top 25 by 7d funding differential (annualised %, absolute)

| # | coin | pair | fund diff (ann %) | A ann mean | B ann mean | trade | exec p90 (bps) |
|---:|---|---|---:|---:|---:|---|---:|
| 1 | MNT | Kraken-Hyperliquid | 463.93 | 428.22 | -35.71 | short Kraken / long Hyperliquid | 1.4 |
| 2 | MNT | Kraken-Lighter | 428.82 | 428.22 | -0.60 | short Kraken / long Lighter | -2.5 |
| 3 | KAS | Kraken-Aster | -90.65 | -79.70 | 10.95 | short Aster / long Kraken | -7.7 |
| 4 | KAS | Kraken-Hyperliquid | -88.68 | -79.70 | 8.98 | short Hyperliquid / long Kraken | 13.6 |
| 5 | MORPHO | Kraken-Aster | -60.93 | -57.53 | 3.41 | short Aster / long Kraken | -14.6 |
| 6 | JUP | Kraken-dYdX | -60.76 | -60.08 | 0.68 | short dYdX / long Kraken | -27.9 |
| 7 | CRO | Kraken-Lighter | -59.78 | -52.94 | 6.84 | short Lighter / long Kraken | -9.7 |
| 8 | MORPHO | OKX-Kraken | 59.75 | 2.22 | -57.53 | short OKX / long Kraken | -8.9 |
| 9 | MORPHO | Kraken-Lighter | -57.30 | -57.53 | -0.22 | short Lighter / long Kraken | -10.7 |
| 10 | BTW | OKX-Aster | -57.23 | 4.58 | 61.81 | short Aster / long OKX | 10.5 |
| 11 | MORPHO | Kraken-Hyperliquid | -45.59 | -57.53 | -11.94 | short Hyperliquid / long Kraken | -4.2 |
| 12 | VVV | OKX-Lighter | -44.15 | 10.95 | 55.10 | short Lighter / long OKX | 2.8 |
| 13 | CRO | OKX-Kraken | 43.37 | -9.57 | -52.94 | short OKX / long Kraken | -13.2 |
| 14 | JUP | Hyperliquid-dYdX | -40.74 | -40.06 | 0.68 | short dYdX / long Hyperliquid | -16.7 |
| 15 | CC | Aster-Lighter | -40.70 | -39.87 | 0.83 | short Lighter / long Aster | -4.2 |
| 16 | PUMP | Kraken-Aster | -40.29 | -31.36 | 8.93 | short Aster / long Kraken | -4.1 |
| 17 | PUMP | Kraken-Lighter | -39.79 | -31.36 | 8.43 | short Lighter / long Kraken | 4.1 |
| 18 | JUP | OKX-Kraken | 37.67 | -22.40 | -60.08 | short OKX / long Kraken | -9.9 |
| 19 | WLD | Kraken-dYdX | -37.14 | -37.15 | -0.01 | short dYdX / long Kraken | -22.0 |
| 20 | VVV | Aster-Lighter | -36.95 | 18.15 | 55.10 | short Lighter / long Aster | 0.2 |
| 21 | PUMP | Kraken-Hyperliquid | -36.69 | -31.36 | 5.33 | short Hyperliquid / long Kraken | 0.0 |
| 22 | VVV | Hyperliquid-Lighter | -35.87 | 19.23 | 55.10 | short Lighter / long Hyperliquid | 3.6 |
| 23 | MNT | Hyperliquid-Lighter | -35.11 | -35.71 | -0.60 | short Lighter / long Hyperliquid | 5.3 |
| 24 | PUMP | OKX-Kraken | 34.48 | 3.12 | -31.36 | short OKX / long Kraken | -4.1 |
| 25 | PEPE | Kraken-Lighter | -33.92 | -23.80 | 10.12 | short Lighter / long Kraken | -5.1 |

Full per coin x venue-pair table (all metrics, incl. flagged rows): `data/pairs_stats.csv`. Raw data: `data/samples.csv`, `data/depth.csv`, `data/funding.csv`, `data/listings.csv`.
