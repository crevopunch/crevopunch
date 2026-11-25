# Cross-venue funding carry: 2-year backtest summary

Window: trading from 2025-11-26 to 2026-11-24 (~12 months). Kraken funding history only goes back to 2025-11-19, so the 2-year window is not achievable; 7-day warm-up is taken from that start.
Cell = final total equity in $ (start $200) / liquidations. N/A = L above the HL max leverage.

## Variant A (no rebalancing)

| coin | HL maxLev | start | L=1 | L=3 | L=5 | L=10 | L=20 |
|---|---|---|---|---|---|---|---|
| BTC | 40 | 2025-11-26 | 201.4 / 0 | 189.5 / 1 | 114.6 / 8 | 16.6 / 25 | 18.1 / 13 |
| ETH | 25 | 2025-11-26 | 201.7 / 0 | 177.9 / 3 | 74.0 / 12 | 18.9 / 16 | 19.4 / 11 |
| SOL | 20 | 2025-11-26 | 199.7 / 0 | 174.8 / 3 | 73.0 / 13 | 18.7 / 18 | 15.4 / 9 |
| XRP | 20 | 2025-11-26 | 199.8 / 0 | 163.9 / 4 | 133.8 / 5 | 19.9 / 13 | 15.1 / 8 |
| DOGE | 10 | 2025-11-26 | 201.9 / 0 | 169.7 / 3 | 34.1 / 11 | 14.6 / 9 | N/A (max 10x) |
| PEPE | 10 | 2025-11-26 | 205.3 / 0 | 54.0 / 12 | 16.2 / 12 | 18.7 / 8 | N/A (max 10x) |
| KAS | 3 | 2025-11-26 | 201.8 / 0 | 14.2 / 8 | N/A (max 3x) | N/A (max 3x) | N/A (max 3x) |
| SUI | 10 | 2025-11-26 | 202.5 / 0 | 121.2 / 7 | 17.5 / 14 | 16.5 / 8 | N/A (max 10x) |
| LINK | 10 | 2025-11-26 | 206.1 / 0 | 178.6 / 3 | 19.7 / 15 | 19.9 / 8 | N/A (max 10x) |
| AVAX | 10 | 2025-11-26 | 204.1 / 0 | 162.3 / 3 | 17.3 / 15 | 14.8 / 8 | N/A (max 10x) |
| BNB | 10 | 2025-11-26 | 199.7 / 0 | 184.5 / 1 | 92.5 / 5 | 15.5 / 8 | N/A (max 10x) |
| TRX | 10 | 2025-11-26 | 201.1 / 0 | 188.8 / 1 | 136.5 / 3 | 14.9 / 8 | N/A (max 10x) |
| HYPE | 10 | 2025-11-26 | 199.6 / 0 | 102.9 / 7 | 19.1 / 13 | 13.3 / 8 | N/A (max 10x) |
| ZEC | 10 | 2025-11-26 | 179.8 / 3 | 54.0 / 15 | 17.9 / 14 | 18.9 / 7 | N/A (max 10x) |
| ADA | 10 | 2025-11-26 | 198.8 / 0 | 163.1 / 2 | 16.7 / 16 | 19.3 / 9 | N/A (max 10x) |
| XLM | 5 | 2025-11-26 | 201.0 / 0 | 141.5 / 2 | 18.8 / 8 | N/A (max 5x) | N/A (max 5x) |
| BCH | 10 | 2025-11-26 | 202.7 / 0 | 183.2 / 3 | 19.4 / 15 | 17.2 / 8 | N/A (max 10x) |
| NEAR | 10 | 2025-11-26 | 193.5 / 1 | 47.8 / 14 | 16.9 / 15 | 17.9 / 8 | N/A (max 10x) |
| LTC | 10 | 2025-11-26 | 204.6 / 0 | 150.2 / 5 | 69.5 / 9 | 12.6 / 8 | N/A (max 10x) |
| UNI | 10 | 2025-11-26 | 206.7 / 0 | 120.0 / 7 | 16.8 / 14 | 17.2 / 8 | N/A (max 10x) |
| HBAR | 5 | 2025-11-26 | 204.4 / 0 | 46.7 / 8 | 18.3 / 8 | N/A (max 5x) | N/A (max 5x) |
| TAO | 5 | 2025-11-26 | 206.0 / 0 | 18.8 / 12 | 18.2 / 8 | N/A (max 5x) | N/A (max 5x) |
| SHIB | 10 | 2025-11-26 | 203.9 / 0 | 201.6 / 1 | 46.5 / 12 | 19.4 / 7 | N/A (max 10x) |
| PAXG | 10 | 2025-11-26 | 198.8 / 0 | 197.1 / 0 | 165.0 / 1 | 14.9 / 8 | N/A (max 10x) |
| AAVE | 10 | 2025-11-26 | 206.5 / 0 | 118.6 / 8 | 17.4 / 16 | 19.1 / 8 | N/A (max 10x) |
| ONDO | 10 | 2025-11-26 | 207.4 / 0 | 161.5 / 5 | 19.9 / 14 | 14.9 / 10 | N/A (max 10x) |
| ENA | 10 | 2025-11-26 | 193.0 / 1 | 67.1 / 10 | 17.5 / 16 | 15.8 / 8 | N/A (max 10x) |
| WLFI | 5 | 2025-11-26 | 199.7 / 0 | 80.7 / 5 | 16.1 / 8 | N/A (max 5x) | N/A (max 5x) |
| ASTER | 5 | 2025-11-26 | 200.9 / 0 | 147.7 / 4 | 15.3 / 10 | N/A (max 5x) | N/A (max 5x) |
| MNT | 5 | 2025-11-26 | 252.9 / 0 | 188.5 / 4 | 17.1 / 10 | N/A (max 5x) | N/A (max 5x) |
| DOT | 10 | 2025-11-26 | 198.0 / 0 | 137.1 / 5 | 18.5 / 14 | 12.9 / 10 | N/A (max 10x) |
| ICP | 5 | 2025-11-26 | 203.7 / 0 | 58.7 / 8 | 17.4 / 9 | N/A (max 5x) | N/A (max 5x) |
| MORPHO | 5 | 2025-11-26 | 204.0 / 0 | 76.5 / 6 | 17.5 / 9 | N/A (max 5x) | N/A (max 5x) |
| ETC | 5 | 2025-11-26 | 206.9 / 0 | 90.5 / 6 | 16.5 / 8 | N/A (max 5x) | N/A (max 5x) |
| WLD | 10 | 2025-11-26 | 188.5 / 1 | 132.8 / 4 | 19.0 / 14 | 17.3 / 8 | N/A (max 10x) |
| PUMP | 10 | 2025-11-26 | 199.8 / 0 | 53.9 / 13 | 19.1 / 13 | 19.1 / 8 | N/A (max 10x) |
| POL | 5 | 2025-11-26 | 204.9 / 0 | 114.2 / 3 | 19.5 / 8 | N/A (max 5x) | N/A (max 5x) |
| ARB | 10 | 2025-11-26 | 201.3 / 1 | 98.3 / 9 | 17.5 / 16 | 14.8 / 9 | N/A (max 10x) |
| JUP | 10 | 2025-11-26 | 200.6 / 0 | 111.9 / 5 | 15.6 / 16 | 18.3 / 8 | N/A (max 10x) |
| ALGO | 5 | 2025-11-26 | 209.1 / 0 | 63.0 / 8 | 16.9 / 8 | N/A (max 5x) | N/A (max 5x) |
| RENDER | 5 | 2025-11-26 | 197.0 / 0 | 33.2 / 10 | 18.6 / 8 | N/A (max 5x) | N/A (max 5x) |
| ATOM | 5 | 2025-11-26 | 204.6 / 0 | 173.1 / 1 | 17.2 / 8 | N/A (max 5x) | N/A (max 5x) |
| INJ | 5 | 2025-11-26 | 200.9 / 0 | 48.3 / 8 | 14.3 / 10 | N/A (max 5x) | N/A (max 5x) |
| STX | 5 | 2025-11-26 | 203.0 / 0 | 28.5 / 11 | 19.3 / 8 | N/A (max 5x) | N/A (max 5x) |
| CAKE | 3 | 2025-11-26 | 216.0 / 0 | 13.9 / 8 | N/A (max 3x) | N/A (max 3x) | N/A (max 3x) |
| ETHFI | 5 | 2025-11-26 | 209.6 / 0 | 33.8 / 11 | 18.1 / 8 | N/A (max 5x) | N/A (max 5x) |
| FIL | 5 | 2025-11-26 | 205.1 / 0 | 43.3 / 10 | 16.9 / 8 | N/A (max 5x) | N/A (max 5x) |
| ZRO | 5 | 2025-11-26 | 213.0 / 0 | 16.7 / 13 | 14.7 / 8 | N/A (max 5x) | N/A (max 5x) |
| PYTH | 5 | 2025-11-26 | 203.9 / 0 | 16.0 / 12 | 13.2 / 9 | N/A (max 5x) | N/A (max 5x) |
| APT | 10 | 2025-11-26 | 199.2 / 0 | 180.9 / 3 | 19.0 / 14 | 16.9 / 9 | N/A (max 10x) |
| TIA | 5 | 2025-11-26 | 200.4 / 0 | 23.1 / 12 | 16.3 / 9 | N/A (max 5x) | N/A (max 5x) |
| CRV | 10 | 2025-11-26 | 204.6 / 0 | 123.2 / 7 | 17.0 / 15 | 14.6 / 9 | N/A (max 10x) |
| PENGU | 5 | 2025-11-26 | 199.6 / 0 | 16.2 / 12 | 19.9 / 8 | N/A (max 5x) | N/A (max 5x) |
| GRASS | 3 | 2025-11-26 | 182.1 / 2 | 10.9 / 9 | N/A (max 3x) | N/A (max 3x) | N/A (max 3x) |
| SPX | 5 | 2025-11-26 | 198.9 / 0 | 48.0 / 7 | 15.6 / 8 | N/A (max 5x) | N/A (max 5x) |
| FET | 5 | 2025-11-26 | 204.9 / 0 | 17.3 / 14 | 14.2 / 9 | N/A (max 5x) | N/A (max 5x) |
| TRUMP | 10 | 2025-11-26 | 207.1 / 1 | 110.7 / 6 | 15.7 / 19 | 18.4 / 8 | N/A (max 10x) |
| STRK | 5 | 2025-11-26 | 200.6 / 1 | 17.5 / 15 | 15.1 / 9 | N/A (max 5x) | N/A (max 5x) |
| VIRTUAL | 5 | 2025-11-26 | 210.9 / 0 | 27.6 / 12 | 15.6 / 8 | N/A (max 5x) | N/A (max 5x) |
| SEI | 5 | 2025-11-26 | 201.2 / 0 | 95.8 / 5 | 15.2 / 9 | N/A (max 5x) | N/A (max 5x) |
| PENDLE | 5 | 2025-11-26 | 186.1 / 1 | 37.0 / 10 | 16.8 / 8 | N/A (max 5x) | N/A (max 5x) |
| XPL | 10 | 2025-11-26 | 224.0 / 0 | 95.6 / 10 | 17.6 / 31 | 15.6 / 10 | N/A (max 10x) |
| LDO | 5 | 2025-11-26 | 206.1 / 0 | 18.1 / 13 | 17.1 / 8 | N/A (max 5x) | N/A (max 5x) |
| BONK | 10 | 2025-11-26 | 208.1 / 0 | 144.3 / 6 | 16.1 / 16 | 17.8 / 8 | N/A (max 10x) |
| COMP | 5 | 2025-11-26 | 216.0 / 0 | 45.7 / 8 | 17.6 / 9 | N/A (max 5x) | N/A (max 5x) |
| RUNE | 5 | 2025-11-26 | 203.4 / 0 | 118.6 / 5 | 18.8 / 8 | N/A (max 5x) | N/A (max 5x) |
| CFX | 5 | 2025-11-26 | 221.7 / 0 | 158.8 / 5 | 16.4 / 9 | N/A (max 5x) | N/A (max 5x) |
| OP | 5 | 2025-11-26 | 199.4 / 0 | 29.6 / 12 | 17.0 / 8 | N/A (max 5x) | N/A (max 5x) |
| FLOKI | 5 | 2025-11-26 | 210.1 / 0 | 81.5 / 6 | 17.4 / 8 | N/A (max 5x) | N/A (max 5x) |
| ENS | 5 | 2025-11-26 | 205.3 / 0 | 119.5 / 5 | 15.8 / 9 | N/A (max 5x) | N/A (max 5x) |
| JTO | 5 | 2025-11-26 | 207.4 / 0 | 17.0 / 14 | 16.7 / 8 | N/A (max 5x) | N/A (max 5x) |

## Variant B (rebalancing + monthly re-size)

| coin | HL maxLev | start | L=1 | L=3 | L=5 | L=10 | L=20 |
|---|---|---|---|---|---|---|---|
| BTC | 40 | 2025-11-26 | 198.5 / 0 | 187.2 / 0 | 157.0 / 0 | 6.1 / 2 | 15.6 / 4 |
| ETH | 25 | 2025-11-26 | 196.9 / 0 | 175.2 / 0 | 129.0 / 0 | 10.3 / 2 | 14.4 / 6 |
| SOL | 20 | 2025-11-26 | 194.1 / 0 | 154.0 / 0 | 96.0 / 0 | 11.3 / 4 | 16.6 / 7 |
| XRP | 20 | 2025-11-26 | 192.1 / 0 | 151.3 / 0 | 34.1 / 1 | 11.9 / 1 | 17.4 / 5 |
| DOGE | 10 | 2025-11-26 | 197.9 / 0 | 171.4 / 0 | 66.6 / 1 | 19.6 / 6 | N/A (max 10x) |
| PEPE | 10 | 2025-11-26 | 194.6 / 0 | 124.4 / 0 | 6.8 / 3 | 15.7 / 5 | N/A (max 10x) |
| KAS | 3 | 2025-11-26 | 192.8 / 0 | 8.7 / 3 | N/A (max 3x) | N/A (max 3x) | N/A (max 3x) |
| SUI | 10 | 2025-11-26 | 193.3 / 0 | 141.0 / 0 | 5.0 / 3 | 16.2 / 8 | N/A (max 10x) |
| LINK | 10 | 2025-11-26 | 202.4 / 0 | 176.4 / 0 | 56.0 / 1 | 11.2 / 7 | N/A (max 10x) |
| AVAX | 10 | 2025-11-26 | 199.7 / 0 | 161.9 / 0 | 83.3 / 1 | 16.6 / 5 | N/A (max 10x) |
| BNB | 10 | 2025-11-26 | 198.4 / 0 | 181.5 / 0 | 143.8 / 0 | 5.9 / 4 | N/A (max 10x) |
| TRX | 10 | 2025-11-26 | 200.2 / 0 | 195.5 / 0 | 187.0 / 0 | 47.7 / 3 | N/A (max 10x) |
| HYPE | 10 | 2025-11-26 | 190.0 / 0 | 109.3 / 0 | 12.6 / 2 | 13.0 / 5 | N/A (max 10x) |
| ZEC | 10 | 2025-11-26 | 180.3 / 0 | 6.3 / 4 | 8.1 / 4 | 12.8 / 7 | N/A (max 10x) |
| ADA | 10 | 2025-11-26 | 193.0 / 0 | 125.9 / 0 | 0.0 / 2 | 19.6 / 5 | N/A (max 10x) |
| XLM | 5 | 2025-11-26 | 194.8 / 0 | 105.2 / 1 | 7.8 / 6 | N/A (max 5x) | N/A (max 5x) |
| BCH | 10 | 2025-11-26 | 197.2 / 0 | 163.1 / 0 | 65.5 / 2 | 17.7 / 6 | N/A (max 10x) |
| NEAR | 10 | 2025-11-26 | 192.2 / 0 | 91.0 / 1 | 8.5 / 3 | 19.8 / 5 | N/A (max 10x) |
| LTC | 10 | 2025-11-26 | 200.2 / 0 | 182.5 / 0 | 150.2 / 0 | 17.3 / 5 | N/A (max 10x) |
| UNI | 10 | 2025-11-26 | 197.1 / 0 | 112.5 / 1 | 10.2 / 4 | 17.8 / 5 | N/A (max 10x) |
| HBAR | 5 | 2025-11-26 | 201.2 / 0 | 109.9 / 1 | 15.4 / 4 | N/A (max 5x) | N/A (max 5x) |
| TAO | 5 | 2025-11-26 | 193.2 / 0 | 122.6 / 0 | 12.3 / 4 | N/A (max 5x) | N/A (max 5x) |
| SHIB | 10 | 2025-11-26 | 200.9 / 0 | 168.8 / 0 | 51.7 / 1 | 11.1 / 6 | N/A (max 10x) |
| PAXG | 10 | 2025-11-26 | 197.8 / 0 | 187.7 / 0 | 165.9 / 0 | 6.3 / 3 | N/A (max 10x) |
| AAVE | 10 | 2025-11-26 | 202.5 / 0 | 155.3 / 0 | 80.9 / 0 | 19.5 / 5 | N/A (max 10x) |
| ONDO | 10 | 2025-11-26 | 197.9 / 0 | 134.9 / 0 | 4.3 / 3 | 18.0 / 5 | N/A (max 10x) |
| ENA | 10 | 2025-11-26 | 181.2 / 0 | 45.3 / 1 | 17.8 / 1 | 14.9 / 5 | N/A (max 10x) |
| WLFI | 5 | 2025-11-26 | 194.9 / 0 | 155.4 / 0 | 11.3 / 5 | N/A (max 5x) | N/A (max 5x) |
| ASTER | 5 | 2025-11-26 | 199.5 / 0 | 70.2 / 1 | 15.3 / 4 | N/A (max 5x) | N/A (max 5x) |
| MNT | 5 | 2025-11-26 | 257.2 / 0 | 367.1 / 0 | 14.9 / 5 | N/A (max 5x) | N/A (max 5x) |
| DOT | 10 | 2025-11-26 | 190.9 / 0 | 128.2 / 0 | 45.6 / 0 | 14.5 / 5 | N/A (max 10x) |
| ICP | 5 | 2025-11-26 | 192.3 / 0 | 94.6 / 1 | 19.5 / 4 | N/A (max 5x) | N/A (max 5x) |
| MORPHO | 5 | 2025-11-26 | 187.1 / 0 | 112.6 / 0 | 9.8 / 6 | N/A (max 5x) | N/A (max 5x) |
| ETC | 5 | 2025-11-26 | 204.4 / 0 | 109.8 / 1 | 10.8 / 5 | N/A (max 5x) | N/A (max 5x) |
| WLD | 10 | 2025-11-26 | 179.2 / 0 | 2.9 / 2 | 11.5 / 3 | 16.7 / 5 | N/A (max 10x) |
| PUMP | 10 | 2025-11-26 | 180.3 / 0 | 4.4 / 2 | 5.7 / 3 | 12.0 / 6 | N/A (max 10x) |
| POL | 5 | 2025-11-26 | 192.5 / 0 | 152.4 / 0 | 19.3 / 5 | N/A (max 5x) | N/A (max 5x) |
| ARB | 10 | 2025-11-26 | 191.3 / 0 | 119.4 / 0 | 18.4 / 2 | 16.1 / 4 | N/A (max 10x) |
| JUP | 10 | 2025-11-26 | 189.1 / 0 | 107.0 / 0 | 16.9 / 1 | 13.2 / 5 | N/A (max 10x) |
| ALGO | 5 | 2025-11-26 | 202.5 / 0 | 172.1 / 0 | 17.9 / 4 | N/A (max 5x) | N/A (max 5x) |
| RENDER | 5 | 2025-11-26 | 189.1 / 0 | 59.7 / 1 | 12.9 / 6 | N/A (max 5x) | N/A (max 5x) |
| ATOM | 5 | 2025-11-26 | 199.4 / 0 | 156.4 / 0 | 4.3 / 5 | N/A (max 5x) | N/A (max 5x) |
| INJ | 5 | 2025-11-26 | 189.5 / 0 | 42.5 / 1 | 16.9 / 5 | N/A (max 5x) | N/A (max 5x) |
| STX | 5 | 2025-11-26 | 200.1 / 0 | 93.1 / 1 | 11.9 / 4 | N/A (max 5x) | N/A (max 5x) |
| CAKE | 3 | 2025-11-26 | 221.3 / 0 | 12.9 / 5 | N/A (max 3x) | N/A (max 3x) | N/A (max 3x) |
| ETHFI | 5 | 2025-11-26 | 204.0 / 0 | 136.1 / 0 | 14.2 / 5 | N/A (max 5x) | N/A (max 5x) |
| FIL | 5 | 2025-11-26 | 196.8 / 0 | 71.0 / 2 | 6.1 / 4 | N/A (max 5x) | N/A (max 5x) |
| ZRO | 5 | 2025-11-26 | 198.2 / 0 | 18.5 / 3 | 18.9 / 4 | N/A (max 5x) | N/A (max 5x) |
| PYTH | 5 | 2025-11-26 | 191.3 / 0 | 114.9 / 0 | 11.4 / 4 | N/A (max 5x) | N/A (max 5x) |
| APT | 10 | 2025-11-26 | 190.4 / 0 | 120.1 / 0 | 6.0 / 3 | 19.1 / 6 | N/A (max 10x) |
| TIA | 5 | 2025-11-26 | 188.4 / 0 | 99.3 / 0 | 14.6 / 4 | N/A (max 5x) | N/A (max 5x) |
| CRV | 10 | 2025-11-26 | 198.6 / 0 | 94.9 / 1 | 5.5 / 3 | 12.6 / 7 | N/A (max 10x) |
| PENGU | 5 | 2025-11-26 | 188.9 / 0 | 108.0 / 0 | 14.5 / 4 | N/A (max 5x) | N/A (max 5x) |
| GRASS | 3 | 2025-11-26 | 178.9 / 0 | 19.3 / 3 | N/A (max 3x) | N/A (max 3x) | N/A (max 3x) |
| SPX | 5 | 2025-11-26 | 191.4 / 0 | 66.0 / 0 | 12.6 / 5 | N/A (max 5x) | N/A (max 5x) |
| FET | 5 | 2025-11-26 | 189.6 / 0 | 55.0 / 1 | 10.5 / 5 | N/A (max 5x) | N/A (max 5x) |
| TRUMP | 10 | 2025-11-26 | 181.7 / 0 | 49.9 / 1 | 9.9 / 5 | 18.4 / 5 | N/A (max 10x) |
| STRK | 5 | 2025-11-26 | 187.3 / 0 | 19.9 / 4 | 12.2 / 5 | N/A (max 5x) | N/A (max 5x) |
| VIRTUAL | 5 | 2025-11-26 | 204.3 / 0 | 27.8 / 2 | 17.3 / 6 | N/A (max 5x) | N/A (max 5x) |
| SEI | 5 | 2025-11-26 | 195.9 / 0 | 141.5 / 0 | 12.2 / 3 | N/A (max 5x) | N/A (max 5x) |
| PENDLE | 5 | 2025-11-26 | 197.0 / 0 | 140.9 / 0 | 19.6 / 4 | N/A (max 5x) | N/A (max 5x) |
| XPL | 10 | 2025-11-26 | 214.1 / 0 | 107.3 / 2 | 17.1 / 13 | 14.0 / 8 | N/A (max 10x) |
| LDO | 5 | 2025-11-26 | 195.9 / 0 | 144.0 / 0 | 12.6 / 4 | N/A (max 5x) | N/A (max 5x) |
| BONK | 10 | 2025-11-26 | 201.2 / 0 | 155.7 / 0 | 0.0 / 3 | 17.0 / 5 | N/A (max 10x) |
| COMP | 5 | 2025-11-26 | 210.9 / 0 | 121.7 / 1 | 11.7 / 6 | N/A (max 5x) | N/A (max 5x) |
| RUNE | 5 | 2025-11-26 | 198.9 / 0 | 156.5 / 0 | 15.2 / 4 | N/A (max 5x) | N/A (max 5x) |
| CFX | 5 | 2025-11-26 | 219.2 / 0 | 149.8 / 1 | 19.3 / 5 | N/A (max 5x) | N/A (max 5x) |
| OP | 5 | 2025-11-26 | 185.9 / 0 | 108.4 / 0 | 13.2 / 4 | N/A (max 5x) | N/A (max 5x) |
| FLOKI | 5 | 2025-11-26 | 201.5 / 0 | 172.6 / 0 | 14.4 / 4 | N/A (max 5x) | N/A (max 5x) |
| ENS | 5 | 2025-11-26 | 201.8 / 0 | 170.5 / 0 | 11.8 / 4 | N/A (max 5x) | N/A (max 5x) |
| JTO | 5 | 2025-11-26 | 189.9 / 0 | 12.4 / 3 | 13.8 / 4 | N/A (max 5x) | N/A (max 5x) |

## What drives the results

At L=1 the hedge is nearly flat and earns the HL-minus-Kraken funding gap net of about 0.1-0.3% of fees, so the strategy is close to a small, reliable carry. Above L=3 the unrebalanced legs get liquidated on adverse hourly moves of roughly 1/L minus the maintenance margin, and each liquidation costs fees plus a $1 transfer, so the equity compounds down; variant B's rebalancing does not rescue this and is worse at L=3 because it transfers collateral only after the legs have already diverged.

## Portfolio row

Skipped: the monthly top-5 re-pick with cross-coin capital transfers was not built.

## Caveats

- Hyperliquid candles are only served from ~2026-04-30; earlier HL OHLC is proxied by Kraken OHLC (zero basis on those hours, see `proxied_hl_hours` in data/coin_info.json).
- Position sizes are in units fixed at open; funding accrues on the mark (venue close).
- Liquidation is checked on each venue's hourly high/low against maintenance margin 1/(2 x HL maxLev).
- No exit cost on the final mark-to-market equity; no funding-rate caps; no slippage beyond the flat bps.
## Side-by-side: A, B, C, D (equal $200 start; caps 3/5/10/20; exit costs included)

A and B are medians across the coins where the cap is allowed (n shown); C and D are one book across the 73-coin universe. Cell = final $ / CAGR % / max DD % / liquidations.

| variant | cap 3 | cap 5 | cap 10 | cap 20 |
|---|---|---|---|---|
| A (per coin, median) | 95.8 / -52.2 / -53.1 / 7 (n=71) | 17.5 / -91.4 / -91.3 / 9 (n=68) | 17.2 / -91.5 / -91.4 / 8 (n=33) | 16.8 / -91.7 / -91.6 / 10 (n=4) |
| B (per coin, median) | 120.1 / -40.1 / -41.2 / 0 (n=71) | 14.3 / -92.9 / -93.0 / 4 (n=68) | 15.7 / -92.2 / -92.2 / 5 (n=33) | 16.1 / -92.0 / -91.9 / 6 (n=4) |
| C (book) | 340.8 / 70.7 / -19.3 / 0 | 17.1 / -91.5 / -91.8 / 4 | 12.8 / -93.7 / -93.6 / 8 | 16.0 / -92.1 / -92.0 / 7 |
| D top1 (book) | 133.1 / -33.6 / -57.7 / 2 | 19.7 / -90.2 / -91.7 / 6 | 16.1 / -92.0 / -93.1 / 7 | 16.9 / -91.6 / -92.7 / 8 |
| D top2 (book) | 169.5 / -15.3 / -39.1 / 2 | 31.6 / -84.3 / -84.5 / 7 | 33.3 / -83.5 / -83.6 / 11 | 12.7 / -93.7 / -93.7 / 12 |

## D ablation (cap 10, top-2): one rule off at a time

| rule off | final $ | CAGR % | max DD % | liquidations | pre-emptive closes | transfers | switches | funding $ | fees $ | funding $ from |rate|>0.1%/h prints |
|---|---|---|---|---|---|---|---|---|---|---|
| none (full D) | 33.3 | -83.5 | -83.6 | 11 | 1 | 44 | 17 | 8.9 | 4.6 | 6.9 |
| rule 1 | 38.5 | -80.9 | -82.1 | 8 | 6 | 52 | 27 | 7.4 | 8.5 | 8.8 |
| rule 2 | 33.3 | -83.5 | -83.6 | 11 | 1 | 44 | 17 | 8.9 | 4.6 | 6.9 |
| rule 3 | 39.5 | -80.4 | -80.5 | 8 | 2 | 84 | 52 | 12.1 | 11.2 | 5.9 |
| rule 4 | 26.4 | -86.9 | -87.0 | 7 | 2 | 92 | 24 | 8.8 | 5.2 | 6.3 |
| rule 5 | 33.2 | -83.5 | -83.6 | 11 | 1 | 44 | 17 | 8.9 | 4.9 | 6.9 |
| rule 6 | 33.0 | -83.6 | -83.7 | 13 | 5 | 23 | 0 | 9.9 | 2.6 | 8.0 |
| rule 8 | 25.1 | -87.6 | -87.8 | 11 | 4 | 61 | 21 | 10.9 | 5.4 | 2.4 |
| rule 9 | 30.4 | -84.9 | -84.8 | 7 | 2 | 55 | 2 | 13.8 | 1.7 | 8.1 |
| rule 11 | 33.5 | -83.4 | -83.5 | 16 | 0 | 11 | 11 | 3.5 | 3.4 | 3.6 |
| rule 12 | 29.1 | -85.5 | -85.6 | 11 | 2 | 36 | 12 | 3.0 | 3.3 | 2.4 |
| rule 13 | 36.0 | -82.1 | -82.2 | 11 | 3 | 52 | 21 | 12.1 | 5.2 | 10.5 |


## Scaled capital

Collateral per leg = CAP (total start = 2 x CAP); TRANSFER fixed at $1; stop (A/B only) = 10% of starting total. Size-dependent slippage from depth.csv (see slipmodel.py), floored at the old flat rate. Caps for C/D are leverage caps. Cell = return % / max DD % / #liquidations.

### CAP = $100 per leg

| row | cap 3 | cap 5 | cap 10 | cap 20 |
|---|---|---|---|---|
| A (coin median) | -52.1 / -53.1 / 7 | -91.3 / -91.3 / 9 | -91.4 / -91.4 / 8 | -91.6 / -91.6 / 10 |
| B (coin median) | -40.0 / -41.2 / 0 | -93.2 / -93.5 / 4 | -92.2 / -92.2 / 5 | -91.9 / -91.9 / 6 |
| C | 68.1 / -18.6 / 0 | -91.5 / -91.8 / 4 | -93.6 / -93.6 / 8 | -92.0 / -92.0 / 7 |
| D top-1 | -25.7 / -53.2 / 2 | -91.9 / -93.1 / 6 | -92.0 / -93.2 / 7 | -91.6 / -92.8 / 8 |
| D top-2 | -11.9 / -39.3 / 2 | -84.2 / -84.6 / 7 | -83.4 / -83.6 / 11 | -93.7 / -93.8 / 12 |

1x median return: A 1.4%, B -2.1% (n=71 coins).

### CAP = $1,000 per leg

| row | cap 3 | cap 5 | cap 10 | cap 20 |
|---|---|---|---|---|
| A (coin median) | -48.9 / -53.6 / 7 | -90.8 / -90.9 / 9 | -91.5 / -91.5 / 9 | -91.1 / -91.1 / 10 |
| B (coin median) | -2.1 / -9.1 / 0 | -79.7 / -82.6 / 4 | -91.6 / -91.6 / 6 | -91.4 / -91.4 / 6 |
| C | 130.5 / -23.4 / 0 | 34.4 / -66.6 / 2 | -91.8 / -93.9 / 14 | -99.2 / -99.2 / 12 |
| D top-1 | -39.4 / -62.0 / 0 | -92.1 / -93.3 / 5 | -99.4 / -99.5 / 14 | -99.2 / -99.3 / 13 |
| D top-2 | -24.8 / -30.2 / 2 | -80.0 / -80.5 / 12 | -98.3 / -98.3 / 22 | -98.7 / -98.7 / 23 |

1x median return: A 1.4%, B 2.0% (n=71 coins).

### CAP = $10,000 per leg

| row | cap 3 | cap 5 | cap 10 | cap 20 |
|---|---|---|---|---|
| A (coin median) | -50.4 / -52.8 / 7 | -90.8 / -90.8 / 9 | -91.4 / -91.4 / 8 | -91.1 / -91.1 / 10 |
| B (coin median) | -1.2 / -10.5 / 0 | -76.7 / -80.0 / 4 | -91.0 / -91.0 / 6 | -91.2 / -91.2 / 6 |
| C | 62.9 / -22.2 / 0 | -25.7 / -67.4 / 2 | -96.1 / -96.9 / 17 | -99.9 / -99.9 / 18 |
| D top-1 | -81.4 / -84.9 / 0 | -98.2 / -98.4 / 5 | -99.9 / -99.9 / 19 | -99.9 / -99.9 / 19 |
| D top-2 | -44.1 / -47.6 / 1 | -90.3 / -92.4 / 15 | -99.8 / -99.8 / 36 | -99.9 / -99.9 / 36 |

1x median return: A 1.3%, B 2.2% (n=71 coins).

### Top 5 coins at 3x, variant B

| CAP | coin | return % | max DD % | #liq |
|---|---|---|---|---|
| 100 | MNT | 83.5 | -22.3 | 0 |
| 100 | TRX | -2.2 | -3.8 | 0 |
| 100 | PAXG | -6.1 | -6.9 | 0 |
| 100 | BTC | -6.4 | -6.5 | 0 |
| 100 | LTC | -8.8 | -8.9 | 0 |
| 1000 | MNT | 106.7 | -21.9 | 0 |
| 1000 | VIRTUAL | 16.0 | -5.3 | 0 |
| 1000 | BONK | 15.2 | -11.7 | 0 |
| 1000 | NEAR | 13.7 | -2.0 | 0 |
| 1000 | ALGO | 13.1 | -4.9 | 0 |
| 10000 | MNT | 81.8 | -25.3 | 0 |
| 10000 | VIRTUAL | 20.9 | -5.0 | 0 |
| 10000 | BONK | 17.4 | -12.0 | 0 |
| 10000 | LDO | 15.5 | -5.3 | 0 |
| 10000 | ALGO | 15.0 | -4.9 | 0 |

### C at cap 3: funding and slippage shares

| CAP | funding from hours with abs(funding) > 0.1%/h | slippage as % of gross P&L |
|---|---|---|
| 100 | 60.3% | 11.5% (slip $35.48, gross $308.09) |
| 1000 | 61.5% | 14.2% (slip $543.51, gross $3835.18) |
| 10000 | 61.3% | 30.0% (slip $7374.93, gross $24606.28) |

Caveats for this section:
- Slippage: per (coin, venue) curve from data/depth.csv (buy/sell mean, ok rows only, venues Hyperliquid/Kraken/Lighter/Aster; OKX and dYdX not used by the sims). Log-N linear between $100, $1k, $10k; below $100 held at the $100 value; above $10k s(10k) x sqrt(N/10k) capped at 300 bps. Missing pairs use the venue median curve. Floored at the old flat rate. Maker fills still carry no slippage.
- Two pairs exceed 300 bps in range (CRO/Kraken 2957 bps at $10k, OKB/Aster 746 bps at $10k). Their extrapolation drops to 300 bps, so the cost is non-monotone above $10k. Left as specified, not adjusted.
- Book (C/D): the book sim has no stop rule (STOP was defined but never used), so none is applied. Start total = 2 x CAP. Forecast cost uses leg notional approximated as free/slots/2 x min(cap, HL max lev) (ignores rule-12 vol sizing). ORDER_MIN ($10) and the $20 floor in the transfer forecast are unchanged.
- Shares: funding share = funding from hours with |rate| > 0.1%/h divided by net funding. Slippage share = slippage divided by gross P&L, where gross = (final - 2 x CAP) + fees + slippage + transfers.
- Reproduction: sim.py --slip flat at $100 matches results.csv (710/710 rows) and sim_book.py --slip flat matches results_CD.csv (23/23 rows).
- Reproduce: `python3 sim.py --capital 1000 --slip size --out X.csv`, `python3 sim_book.py --capital 1000 --slip size --out Y.csv`; merge and tables were built from those runs.
