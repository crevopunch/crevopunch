# Cross-venue perp spread backtests: 2026-11-26 order-book sample

Script: `hf/spread_hf.py`. Rows: `hf/results_hf.csv`. Per-day figures = 8h sample x 24/8 (x3).

Net bps are per trade on one leg notional (size $), after taker or maker fees per side. pnl_usd = sum over trades of size x net bps / 1e4. Pair labels: `X>Y` = sell X, buy Y (S1, S4 = OKX-led); `X|Y` = both directions of the pair (S2); `M-maker/LTR-hedge` = S3.

## Data and method

- Input: 9 files (20261126_01..09; 20261125_19 excluded), 1,288,487 rows, 1,288,487 kept after de-duplication and dropping zero or crossed quotes.
- Grid: 28437 points at 1s, 2026-11-26 01:11:34 to 2026-11-26 09:05:30.392000 UTC.
- S3 ETH HL o=3 $100: 1 hedge prices fell back to mid
- S3 ETH HL o=3 $1000: 1 hedge prices fell back to mid
- S3 ETH HL o=3 $10000: 1 hedge prices fell back to mid
- S3 ETH AST o=3 $100: 1 hedge prices fell back to mid
- S3 ETH AST o=3 $1000: 1 hedge prices fell back to mid
- S3 ETH AST o=3 $10000: 1 hedge prices fell back to mid
- S3 MORPHO OKX o=3 $10000: 1 hedge prices fell back to mid
- S3 MORPHO OKX o=5 $10000: 1 hedge prices fell back to mid
- S3 MORPHO OKX o=10 $10000: 1 hedge prices fell back to mid
- S3 MORPHO KRK o=3 $10000: 1 hedge prices fell back to mid
- S3 MORPHO KRK o=5 $10000: 1 hedge prices fell back to mid
- S3 MORPHO HL o=3 $10000: 7 hedge prices fell back to mid
- S3 MORPHO HL o=5 $10000: 4 hedge prices fell back to mid
- S3 MORPHO HL o=10 $10000: 5 hedge prices fell back to mid
- S3 MORPHO AST o=3 $10000: 1 hedge prices fell back to mid
- S3 MORPHO AST o=5 $10000: 1 hedge prices fell back to mid
- S3 MORPHO AST o=10 $10000: 1 hedge prices fell back to mid
- S3 SKY OKX o=3 $10000: 143 hedge prices fell back to mid
- S3 SKY OKX o=5 $10000: 100 hedge prices fell back to mid
- S3 SKY OKX o=10 $10000: 46 hedge prices fell back to mid
- S3 SKY HL o=3 $10000: 75 hedge prices fell back to mid
- S3 SKY HL o=5 $10000: 52 hedge prices fell back to mid
- S3 SKY HL o=10 $10000: 30 hedge prices fell back to mid
- S3 SKY AST o=3 $10000: 127 hedge prices fell back to mid
- S3 SKY AST o=5 $10000: 97 hedge prices fell back to mid
- S3 SUI KRK o=3 $100: 1 hedge prices fell back to mid
- S3 SUI KRK o=3 $1000: 1 hedge prices fell back to mid
- S3 SUI KRK o=3 $10000: 1 hedge prices fell back to mid
- S3 SUI AST o=5 $100: 1 hedge prices fell back to mid
- S3 SUI AST o=5 $1000: 1 hedge prices fell back to mid
- S3 SUI AST o=5 $10000: 1 hedge prices fell back to mid
- Venues: OKX, Kraken, Hyperliquid, Aster, Lighter. Depth columns (*_1k, *_10k) exist only for Hyperliquid and Lighter. For OKX, Kraken and Aster, $1k and $10k trades use top-of-book price and are taken only if top-of-book notional covers the size.
- Sanity filter: venue medians vs cross-venue median; clean 10/100/1000 factors rescaled, others dropped.
  - No venue/coin pairs needed rescaling or dropping.

## Coins (price tick in bps; coins with tick > 1 bp are flagged as quantisation-limited)

| coin | venues used | cross-venue mid | tick bps | flag |
|---|---|---|---|---|
| ASTER | OKX,KRK,HL,AST,LTR | 0.500385 | 1.99 | TICK-LIMITED |
| AVAX | OKX,KRK,HL,AST,LTR | 6.672000 | 1.50 | TICK-LIMITED |
| BNB | OKX,KRK,HL,AST,LTR | 557.220000 | 0.18 |  |
| BTC | OKX,KRK,HL,AST,LTR | 60,753.850000 | 0.02 |  |
| CRO | OKX,KRK,LTR | 0.039750 | 2.52 | TICK-LIMITED |
| DOGE | OKX,KRK,HL,AST,LTR | 0.056685 | 1.76 | TICK-LIMITED |
| ENA | OKX,KRK,HL,AST,LTR | 0.102960 | 0.97 |  |
| ETH | OKX,KRK,HL,AST,LTR | 1,698.050000 | 0.06 |  |
| HYPE | OKX,KRK,HL,AST,LTR | 61.705500 | 0.16 |  |
| JUP | OKX,KRK,HL,AST,LTR | 0.232325 | 4.30 | TICK-LIMITED |
| KAS | KRK,HL,AST | 0.026575 | 3.76 | TICK-LIMITED |
| LINK | OKX,KRK,HL,AST,LTR | 9.184360 | 1.09 | TICK-LIMITED |
| LTC | OKX,KRK,HL,AST,LTR | 43.545500 | 2.30 | TICK-LIMITED |
| MORPHO | OKX,KRK,HL,AST,LTR | 1.605850 | 0.62 |  |
| ONDO | OKX,KRK,HL,AST,LTR | 0.287100 | 3.48 | TICK-LIMITED |
| PEPE | OKX,KRK,HL,AST,LTR | 0.000004 | 0.28 |  |
| PUMP | OKX,KRK,HL,AST,LTR | 0.002629 | 3.81 | TICK-LIMITED |
| SKY | OKX,HL,AST,LTR | 0.043139 | 1.28 | TICK-LIMITED |
| SOL | OKX,KRK,HL,AST,LTR | 71.035000 | 1.41 | TICK-LIMITED |
| SUI | OKX,KRK,HL,AST,LTR | 0.672250 | 1.49 | TICK-LIMITED |
| TAO | OKX,KRK,HL,AST,LTR | 183.885000 | 0.54 |  |
| VVV | OKX,HL,AST,LTR | 27.490575 | 0.36 |  |
| WLD | OKX,KRK,HL,AST,LTR | 0.243050 | 4.12 | TICK-LIMITED |
| WLFI | OKX,KRK,HL,AST,LTR | 0.042492 | 2.35 | TICK-LIMITED |
| XRP | OKX,KRK,HL,AST,LTR | 0.955371 | 1.05 | TICK-LIMITED |

## Venue basis vs Lighter mid (median over time, bps; median across coins)

S3 quotes are centred on Lighter mid, so a persistent venue basis shifts every maker quote. S2 and S1 are mostly basis-neutral.

| venue | coins | median basis | min across coins | max across coins |
|---|---|---|---|---|
| OKX | 24 | -0.10 | -11.40 | 7.57 |
| KRK | 22 | -2.47 | -11.29 | 9.54 |
| HL | 23 | 1.34 | -6.42 | 9.92 |
| AST | 23 | 1.50 | -9.51 | 24.44 |

## Best config per strategy and size (by $/day summed over coins)

| strategy | $100 | $1k | $10k |
|---|---|---|---|
| S1 | 16.76 (X=5bps, HL>LTR) | 176.62 (X=5bps, HL>LTR) | 337.21 (X=5bps, LTR>HL) |
| S2 | 7.88 (\|z\|>3 (30m roll), AST\|LTR) | -2,356.55 (\|z\|>3 (30m roll), KRK\|AST) | -3,575.13 (\|z\|>3 (30m roll), KRK\|AST) |
| S3 | -183.28 (offset=10bps, KRK-maker/LTR-hedge) | -1,999.91 (offset=10bps, KRK-maker/LTR-hedge) | -16,794.26 (offset=10bps, KRK-maker/LTR-hedge) |
| S4 | 97.27 (OKX mid move >10bps within 5s -> take lagging venue, OKX->LTR) | -333.28 (OKX mid move >10bps within 5s -> take lagging venue, OKX->LTR) | -693.49 (OKX mid move >10bps within 5s -> take lagging venue, OKX->KRK) |

## Top 15 configs by $/day at $100

| # | strategy | params | pair | $/day (all coins) | $/day (ex tick-limited) | median trades/coin | total trades | net bps/trade (pooled) |
|---|---|---|---|---|---|---|---|---|
| 1 | S4 | OKX mid move >10bps within 5s -> take lagging venue; exit after 10s; taker both | OKX->LTR | 97.27 | 94.39 | 28 | 2,473 | 1.31 |
| 2 | S4 | OKX mid move >10bps within 5s -> take lagging venue; exit after 60s; taker both | OKX->LTR | 82.97 | 78.59 | 25 | 1,342 | 2.06 |
| 3 | S4 | OKX mid move >10bps within 5s -> take lagging venue; exit after 30s; taker both | OKX->LTR | 78.70 | 78.16 | 26 | 1,734 | 1.51 |
| 4 | S1 | X=5bps; enter spread>RT+X; exit reverse>=0; 4h timeout; taker | HL>LTR | 16.76 | 39.68 | 1 | 318 | 1.76 |
| 5 | S1 | X=5bps; enter spread>RT+X; exit reverse>=0; 4h timeout; taker | LTR>AST | 14.85 | 28.53 | 0 | 194 | 2.55 |
| 6 | S1 | X=5bps; enter spread>RT+X; exit reverse>=0; 4h timeout; taker | LTR>HL | 14.10 | 11.83 | 0 | 603 | 0.78 |
| 7 | S1 | X=5bps; enter spread>RT+X; exit reverse>=0; 4h timeout; taker | HL>AST | 14.09 | 13.05 | 0 | 35 | 13.42 |
| 8 | S1 | X=5bps; enter spread>RT+X; exit reverse>=0; 4h timeout; taker | OKX>LTR | 10.70 | 13.40 | 0 | 105 | 3.40 |
| 9 | S1 | X=2bps; enter spread>RT+X; exit reverse>=0; 4h timeout; taker | HL>AST | 10.37 | 12.83 | 0 | 55 | 6.28 |
| 10 | S2 | \|z\|>3 (30m roll); exit z=0 cross; maker both (limit at mid, 60s, fill rule; size-invariant) | AST\|LTR | 7.88 | 13.54 | 11 | 355 | 0.74 |
| 11 | S1 | X=5bps; enter spread>RT+X; exit reverse>=0; 4h timeout; taker | HL>OKX | 7.63 | 7.78 | 0 | 41 | 6.20 |
| 12 | S1 | X=0bps; enter spread>RT+X; exit reverse>=0; 4h timeout; taker | HL>AST | 7.04 | 12.86 | 0 | 73 | 3.22 |
| 13 | S1 | X=5bps; enter spread>RT+X; exit reverse>=0; 4h timeout; taker | OKX>HL | 3.92 | 2.38 | 0 | 62 | 2.11 |
| 14 | S1 | X=2bps; enter spread>RT+X; exit reverse>=0; 4h timeout; taker | HL>OKX | 3.31 | 8.75 | 0 | 65 | 1.70 |
| 15 | S1 | X=0bps; enter spread>RT+X; exit reverse>=0; 4h timeout; taker | OKX>AST | 2.04 | 2.04 | 0 | 4 | 17.03 |

## Top 15 configs by $/day at $1,000

| # | strategy | params | pair | $/day (all coins) | $/day (ex tick-limited) | median trades/coin | total trades | net bps/trade (pooled) |
|---|---|---|---|---|---|---|---|---|
| 1 | S1 | X=5bps; enter spread>RT+X; exit reverse>=0; 4h timeout; taker | HL>LTR | 176.62 | 174.51 | 0 | 103 | 5.72 |
| 2 | S1 | X=5bps; enter spread>RT+X; exit reverse>=0; 4h timeout; taker | LTR>AST | 131.59 | 167.29 | 0 | 77 | 5.70 |
| 3 | S1 | X=5bps; enter spread>RT+X; exit reverse>=0; 4h timeout; taker | HL>AST | 68.36 | 64.39 | 0 | 14 | 16.28 |
| 4 | S1 | X=2bps; enter spread>RT+X; exit reverse>=0; 4h timeout; taker | HL>AST | 65.47 | 77.37 | 0 | 22 | 9.92 |
| 5 | S1 | X=2bps; enter spread>RT+X; exit reverse>=0; 4h timeout; taker | HL>LTR | 53.04 | 159.81 | 1 | 204 | 0.87 |
| 6 | S1 | X=0bps; enter spread>RT+X; exit reverse>=0; 4h timeout; taker | HL>AST | 51.70 | 76.61 | 0 | 30 | 5.74 |
| 7 | S1 | X=5bps; enter spread>RT+X; exit reverse>=0; 4h timeout; taker | LTR>HL | 37.45 | 25.09 | 0 | 277 | 0.45 |
| 8 | S1 | X=2bps; enter spread>RT+X; exit reverse>=0; 4h timeout; taker | LTR>AST | 19.96 | 148.87 | 0 | 159 | 0.42 |
| 9 | S1 | X=5bps; enter spread>RT+X; exit reverse>=0; 4h timeout; taker | OKX>LTR | 17.92 | 9.83 | 0 | 13 | 4.59 |
| 10 | S1 | X=2bps; enter spread>RT+X; exit reverse>=0; 4h timeout; taker | OKX>HL | 9.76 | 6.65 | 0 | 6 | 5.42 |
| 11 | S1 | X=5bps; enter spread>RT+X; exit reverse>=0; 4h timeout; taker | OKX>HL | 3.86 | 0.75 | 0 | 4 | 3.21 |
| 12 | S1 | X=5bps; enter spread>RT+X; exit reverse>=0; 4h timeout; taker | HL>KRK | 1.09 | 0.00 | 0 | 1 | 3.62 |
| 13 | S1 | X=2bps; enter spread>RT+X; exit reverse>=0; 4h timeout; taker | HL>KRK | 1.09 | 0.00 | 0 | 1 | 3.62 |
| 14 | S1 | X=0bps; enter spread>RT+X; exit reverse>=0; 4h timeout; taker | KRK>AST | 0.00 | 0.00 | 0 | 0 | n/a |
| 15 | S1 | X=2bps; enter spread>RT+X; exit reverse>=0; 4h timeout; taker | OKX>KRK | 0.00 | 0.00 | 0 | 0 | n/a |

## Top 15 configs by $/day at $10,000

| # | strategy | params | pair | $/day (all coins) | $/day (ex tick-limited) | median trades/coin | total trades | net bps/trade (pooled) |
|---|---|---|---|---|---|---|---|---|
| 1 | S1 | X=5bps; enter spread>RT+X; exit reverse>=0; 4h timeout; taker | LTR>HL | 337.21 | 412.51 | 0 | 67 | 1.68 |
| 2 | S1 | X=5bps; enter spread>RT+X; exit reverse>=0; 4h timeout; taker | HL>LTR | 193.39 | 218.68 | 0 | 23 | 2.80 |
| 3 | S1 | X=5bps; enter spread>RT+X; exit reverse>=0; 4h timeout; taker | AST>LTR | 30.79 | 35.36 | 0 | 4 | 2.57 |
| 4 | S1 | X=5bps; enter spread>RT+X; exit reverse>=0; 4h timeout; taker | OKX>LTR | 30.51 | 26.88 | 0 | 4 | 2.54 |
| 5 | S1 | X=2bps; enter spread>RT+X; exit reverse>=0; 4h timeout; taker | HL>LTR | 30.15 | 130.88 | 0 | 39 | 0.26 |
| 6 | S1 | X=2bps; enter spread>RT+X; exit reverse>=0; 4h timeout; taker | OKX>LTR | 19.98 | 26.88 | 0 | 5 | 1.33 |
| 7 | S1 | X=0bps; enter spread>RT+X; exit reverse>=0; 4h timeout; taker | OKX>HL | 15.80 | 0.00 | 0 | 1 | 5.27 |
| 8 | S1 | X=5bps; enter spread>RT+X; exit reverse>=0; 4h timeout; taker | OKX>HL | 15.80 | 0.00 | 0 | 1 | 5.27 |
| 9 | S1 | X=2bps; enter spread>RT+X; exit reverse>=0; 4h timeout; taker | OKX>HL | 15.80 | 0.00 | 0 | 1 | 5.27 |
| 10 | S1 | X=5bps; enter spread>RT+X; exit reverse>=0; 4h timeout; taker | HL>OKX | 11.08 | 0.00 | 0 | 1 | 3.69 |
| 11 | S1 | X=2bps; enter spread>RT+X; exit reverse>=0; 4h timeout; taker | HL>OKX | 11.08 | 0.00 | 0 | 1 | 3.69 |
| 12 | S1 | X=0bps; enter spread>RT+X; exit reverse>=0; 4h timeout; taker | OKX>KRK | 0.00 | 0.00 | 0 | 0 | n/a |
| 13 | S1 | X=2bps; enter spread>RT+X; exit reverse>=0; 4h timeout; taker | KRK>HL | 0.00 | 0.00 | 0 | 0 | n/a |
| 14 | S1 | X=2bps; enter spread>RT+X; exit reverse>=0; 4h timeout; taker | KRK>OKX | 0.00 | 0.00 | 0 | 0 | n/a |
| 15 | S1 | X=5bps; enter spread>RT+X; exit reverse>=0; 4h timeout; taker | KRK>OKX | 0.00 | 0.00 | 0 | 0 | n/a |

## S4 lead-lag: Pearson corr of 1s returns, OKX_t vs venue_{t+k} (pooled over coins)

Positive k: venue lags OKX. Negative k: venue leads OKX. Returns use forward-filled quotes.

| venue | k=-10 | k=-5 | k=-3 | k=-1 | k=0 | k=1 | k=2 | k=3 | k=5 | k=7 | k=10 | max over k>=0 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| KRK | -0.000 | 0.004 | 0.016 | 0.046 | 0.477 | 0.022 | 0.046 | 0.004 | 0.003 | 0.001 | -0.007 | lag 0s (0.477) |
| HL | 0.000 | 0.009 | 0.012 | 0.128 | 0.212 | 0.226 | 0.210 | 0.126 | 0.011 | 0.010 | -0.001 | lag 1s (0.226) |
| AST | -0.003 | 0.002 | 0.010 | 0.037 | 0.613 | 0.026 | 0.022 | 0.002 | -0.000 | -0.004 | -0.003 | lag 0s (0.613) |
| LTR | -0.007 | 0.003 | 0.013 | 0.075 | 0.225 | 0.109 | 0.211 | 0.090 | 0.026 | 0.000 | -0.001 | lag 0s (0.225) |

Most correlation sits at k=0 and k=1 to 2. On a 1s grid with forward-filled quotes this reflects near-simultaneous moves and poll timing, so it cannot resolve sub-second lead-lag or prove that OKX leads.

## S5 funding windows: executable spread (bps, $100 top of book), in-window vs out

| window | pair | in-window samples (s) | mean in | mean out | mean max(.,0) in | mean max(.,0) out |
|---|---|---|---|---|---|---|
| HL hourly | AST\|LTR | 75750 | 1.255 | 1.455 | 2.669 | 2.785 |
| HL hourly | HL\|AST | 79456 | 1.574 | 1.652 | 2.999 | 2.992 |
| HL hourly | HL\|LTR | 109644 | 1.028 | 1.242 | 1.704 | 1.866 |
| HL hourly | KRK\|AST | 42655 | 1.183 | 1.498 | 3.971 | 4.086 |
| HL hourly | KRK\|HL | 62464 | 1.313 | 1.252 | 2.644 | 2.678 |
| HL hourly | KRK\|LTR | 61928 | -0.789 | -0.398 | 1.628 | 1.695 |
| HL hourly | OKX\|AST | 59786 | 0.671 | 0.688 | 1.793 | 1.793 |
| HL hourly | OKX\|HL | 81790 | 1.280 | 1.311 | 1.610 | 1.627 |
| HL hourly | OKX\|KRK | 48936 | 0.652 | 0.721 | 2.134 | 2.162 |
| HL hourly | OKX\|LTR | 83457 | 0.410 | 0.476 | 1.362 | 1.412 |
| OKX/AST 00-08-16 | AST\|LTR | 9439 | 1.383 | 1.422 | 2.509 | 2.771 |
| OKX/AST 00-08-16 | HL\|AST | 9752 | 1.369 | 1.644 | 2.866 | 2.996 |
| OKX/AST 00-08-16 | HL\|LTR | 13608 | 1.349 | 1.203 | 2.088 | 1.833 |
| OKX/AST 00-08-16 | KRK\|AST | 2846 | 1.574 | 1.446 | 3.628 | 4.072 |
| OKX/AST 00-08-16 | KRK\|HL | 4038 | 1.719 | 1.258 | 2.812 | 2.671 |
| OKX/AST 00-08-16 | KRK\|LTR | 3946 | 0.002 | -0.466 | 1.677 | 1.684 |
| OKX/AST 00-08-16 | OKX\|AST | 7695 | 0.414 | 0.691 | 1.552 | 1.799 |
| OKX/AST 00-08-16 | OKX\|HL | 10227 | 1.224 | 1.308 | 1.532 | 1.626 |
| OKX/AST 00-08-16 | OKX\|KRK | 3313 | 1.105 | 0.705 | 2.178 | 2.157 |
| OKX/AST 00-08-16 | OKX\|LTR | 10507 | 0.412 | 0.466 | 1.383 | 1.404 |

Only one 00/08/16 UTC event (08:00) falls in the sample, so the OKX/AST window statistics rest on about 10 minutes of data. The HL hourly family has 8 events (02:00 to 09:00 UTC).

## Caveats

- 8h sample (01:11 to 09:05 UTC, one day). Results are not a multi-day estimate; per-day numbers are an extrapolation of 8h x 3, and intraday regimes differ.
- Polling gaps: Hyperliquid was rate-limited (HTTP 429) during collection (see collect.log), and quote staleness limits (8s, 12s Lighter) drop periods where a venue is silent. Entries are skipped in those periods.
- Price precision: many low-priced coins are quoted to 4 to 6 decimals, so one tick is several bps (PEPE about 2500 bps). Tick-limited coins (> 1 bp) produce meaningless bps and are excluded from the "ex tick-limited" column. The all-coins column is still shown as requested.
- Depth: only Hyperliquid and Lighter have $1k and $10k depth. OKX, Kraken and Aster use top-of-book prices with a notional check, so their $1k and $10k fills are optimistic (no walking the book) and many larger trades are skipped.
- No queue position. Maker fills use the trade-through rule: a bid fills only when a later ask prints 0.5 bp through the quote, and an ask only when a later bid prints 0.5 bp through it. This is a conservative approximation, not a fill model. It ignores queue position, partial fills and cancel latency. S2 maker-maker uses limits at mid with a 60s life and taker fallback. It is size-invariant (top of book).
- Hedge latency: S3 hedges at the next Lighter quote after the fill. Adverse selection is captured by the price move to that quote. Inventory is limited to one unit.
- Not modelled: perp funding payments (S1, S2 and S3 hold for up to 4h or 30min), borrow for short legs, margin and liquidation, withdrawal or transfer costs, and fees beyond the stated schedule.
- Taker S1 and S2 exits: S1 exits when closing now is non-negative in gross price terms (4h timeout). S2 holds until z crosses zero, with no timeout, so trades can be long. These are the stated rules, and they are not optimised.
- S3 result is driven partly by venue basis, not only by fills. Kraken trades a median of about 2.5 bps below Lighter across coins (BTC about 7.6 bps below), with a per-coin range of roughly -11 to +10 bps. The maker quote is centred on Lighter mid, so the basis shifts it against the maker venue. A basis-adjusted fair value was not tested.
- S4 is directional on the lagging venue: no hedge, shorts on Kraken, Aster, HL and Lighter are assumed borrowable, and round-trip taker fees are charged on that single leg.
- Lead-lag correlations use forward-filled quotes, so update cadence (2s, 4s, 6s) can create lag structure that is not real lead-lag. Pearson is also sensitive to outlier 1s returns.
- Trades are not independent across coins. S4 signals fire together when OKX moves market-wide, so per-coin counts overstate the number of independent bets. The pooled $/day figures are dominated by a few high-volatility windows.
- Sample size: many configs have few trades. The top-15 ranking is noisy and should not be read as a selected edge without out-of-sample confirmation.
- S5 uses top-of-book executable spreads only and tests three-window samples, which is too thin for a conclusion.
