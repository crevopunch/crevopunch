# Cross-exchange perp arbitrage for a small retail trader ($100 – $10k per leg)

**Data date:** live sampling 2026-11-24 23:29–23:58 UTC (30 snapshots, 60 s apart); funding history 2026-11-18 → 2026-11-24; fees/docs read 2026-11-24.
**Venues measured live:** OKX, Kraken Futures, Hyperliquid, Aster, Lighter, dYdX v4.
**Not measured live:** Binance and Bybit. Their APIs geo-block this US-hosted server (HTTP 451/403). Their fees come from docs/search only.
**Universe:** top-50 non-stablecoin coins by CoinGecko market cap that list a perp on ≥2 of the 6 venues (`data/listings.csv`).

## TL;DR

1. **Spread trading (buy cheap venue, sell rich venue, close when the gap converges) is not profitable at your size.**
   - We tested 1,144 directional coin × venue-pair combinations on live books.
   - Even with **perfect hindsight** (best entry, best later exit), only 14 cleared taker fees, by at most 15 bps. That is $1.50 on a $1k leg and $15 on $10k, before transfer costs.
   - The median hindsight gross edge was **0.7 bps** against a round-trip fee of **8–20 bps**.
2. **Funding-rate carry (long the low-funding venue, short the high-funding one, hold for days) is the only variant with positive expected value.**
   - It works only on a handful of alts, mainly where Kraken funding is persistently negative.
   - Expect roughly **+0.5% to +2% per month on notional** *if* the last week's funding gaps persist. They often don't.
   - On $10k per leg that is about **$50–200/month** before tax, with tail risk.
   - On $1k it is **$5–20/month**, which is not worth the operational risk.
3. **Regulatory blocker for France.**
   - The live data comes from the *global* OKX and Kraken order books. A French retail account is routed to OKX Europe (5-year-expiry "X-Perps") or Kraken's EU MiFID entity, with leverage capped (~10x). Their books, fees and funding may differ.
   - Binance France reportedly stopped derivatives in July 2026. Bybit EU reportedly offers no perps.
   - The DEXs (Hyperliquid, Lighter, Aster, dYdX) are not licensed in France (grey zone).
   - All of this is **UNVERIFIED** from primary sources; see `risks.md`.

**Bottom line: spread arbitrage is a no; funding carry is a small, risky "maybe" that only makes sense at ≥$5–10k per leg.**

---

## 1. Fees used in the math (base retail tier)

| Venue | Maker | Taker | Funding interval | Status |
|---|---|---|---|---|
| Hyperliquid | 0.015% | 0.045% | 1h | **verified** (docs, 2026-11-24) |
| Lighter Standard | 0 | 0 | 1h (±0.5%/h clamp) | **verified** |
| Lighter Premium | 0.004% | 0.028% | 1h | **verified** |
| Aster | 0% | 0.04% | 8h default; 4h/1h on some symbols (seen in API) | fees verified, interval from API |
| dYdX v4 | 0.01% | 0.05% | 1h | **verified** |
| OKX | 0.02% | 0.05% | 8h (1–4h on some) | **UNVERIFIED** (page JS-only) |
| Kraken Futures | 0.02% | 0.05% | 1h (seen in API) | **UNVERIFIED** |
| Binance USDⓈ-M | 0.02% | 0.05% (−10% paying in BNB) | 8h (4h/1h some) | **UNVERIFIED**, geo-blocked |
| Bybit | 0.02% | 0.055% | 8h, dynamic | snippet only |

**Discounts (verified):**
- **Hyperliquid HYPE staking:** 5% off at >10 HYPE, up to 40% at >500k HYPE.
- **Lighter Premium LIT staking:** 2.5% off at 1k LIT, up to 30% at 500k LIT.

None of these change the conclusion at retail size. The first volume tiers need millions per month.

**Other costs:**
- **Hyperliquid:** $1 USDC withdrawal (UNVERIFIED). Builder fees only apply if you trade through a third-party front-end.
- **dYdX:** about $0.1–7 plus gas to withdraw, minimum 11 USDC (snippet).
- **Gas:** effectively zero for trading on Hyperliquid, Lighter and dYdX.
- **Cross-venue rebalancing:** CEX↔DEX transfers cost about $1–5 per move. Converting USDT↔USDC on a CEX costs about 0–10 bps.

**Note:** Lighter Standard's zero fee comes with slower (delayed) order execution for those accounts. This was not measured and is **UNVERIFIED**.

## 2. Price spread between venues (live, bps of mid)

Source: `data/summary.md`, `data/pairs_stats.csv`.

**Pooled medians over all coins:**
- **Mid-to-mid gap:** 2–4 bps between OKX, Kraken, Hyperliquid, Aster and Lighter. It is 8–10 bps vs dYdX.
- **Executable cross spread** (sell one venue's bid, buy the other's ask): median −2 to +0.6 bps, p90 4–7.5 bps.
  - It exceeded **10 bps in only 0.4–7%** of samples, and exceeded **20 bps in ≤2.4%**.
  - It **never exceeded 30 bps** for any pair.
- **Break-even with four taker fills** (open and close both legs):
  - 8 bps for Lighter+Aster
  - 9 bps for Lighter+Hyperliquid
  - 10 bps for Lighter+OKX/Kraken
  - 17–19 bps for any two fee-paying venues
  - add 1–6 bps of slippage per leg at $1–10k (section 4)
- **The large "gaps" don't converge, so they are not arbitrage:**
  - **ASTER** on Aster trades 23–27 bps above every other venue in 100% of samples, matching ~+20% annualised funding.
  - **BNB, WLFI and HYPE** on Aster show the same kind of offset.
  - These are funding-driven basis. You can't buy one side and sell the other and close later at a profit unless the basis collapses.
  - They belong in the carry strategy, not the spread strategy.
- **Hindsight simulation** (`spread_sim.py`):
  - The best results were SKY Lighter/Aster (+14.7 bps net), SKY Lighter/OKX (+12.7) and BTW OKX/Aster (+6.5).
  - All of them depend on Lighter's 0 fee and a perfectly timed exit.
  - Real execution (latency, partial fills, two legs not filling simultaneously) will eat this.
- **Limitation:** only 30 minutes on one quiet night. Spreads widen in volatile periods, and those spikes are where pros earn, using co-located bots, VIP fees and pre-positioned inventory. A retail trader won't be fast enough.

## 3. Funding rates and per-pair differentials

7-day means, annualised. Full table in `data/funding.csv` and `data/carry.csv`.

**BTC/ETH/SOL:** venues are within about ±10% annualised of each other.
- BTC 7d means: OKX 0.5%, Kraken 5.7%, Hyperliquid 3.9%, Aster 6.0%, Lighter 9.6%, dYdX 3.7%.
- A gap of about 5–9% annualised is 1.4–2.5 bps/day. Recovering 10–20 bps of round-trip costs takes about 1–2 weeks, and the sign flips often (52–97% of periods positive).
- **Not worth it on majors.**

**Alt carry candidates.** Ranked by the 30-day projection at $10k (`carry.py`). They assume the 7-day average persists, which is optimistic.

| # | Coin | Short (pays you) | Long | 7d diff (ann.) | Edge/day | Round-trip cost $1k / $10k | Break-even hold | Net 30d @ $1k | Net 30d @ $10k |
|---|---|---|---|---|---|---|---|---|---|
| 1 | KAS | Hyperliquid | Kraken | 88.7% | 24 bps | 48 / 110 bps | 2.0 / 4.5 d | +$68 | +$619 |
| 2 | VVV | Lighter | Hyperliquid | 35.9% | 9.8 bps | 13 / 28 bps | 1.3 / 2.8 d | +$28 | +$267 |
| 3 | VVV | Lighter | OKX | 44.2% | 12.1 bps | 20 / 39 bps | 1.6 / 3.2 d | +$34 | +$324 |
| 4 | PUMP | Lighter | Kraken | 39.8% | 10.9 bps | 28 / 35 bps | 2.6 / 3.2 d | +$30 | +$292 |
| 5 | PEPE | Lighter | Kraken | 33.9% | 9.3 bps | 29 / 35 bps | 3.1 / 3.8 d | +$25 | +$243 |
| 6 | MORPHO | Lighter | Kraken | 57.3% | 15.7 bps | 57 / 101 bps | 3.6 / 6.4 d | +$41 | +$370 |
| 7 | QNT | Lighter | Kraken | 29.3% | 8.0 bps | 26 / 32 bps | 3.2 / 4.0 d | +$22 | +$209 |
| 8 | ONDO | Lighter | Kraken | 29.3% | 8.0 bps | 21 / 36 bps | 2.7 / 4.5 d | +$22 | +$205 |

**Haircut these projections:**
- **Volatile:** funding std is 15–90% annualised.
- **Kraken-driven:** many candidates come from Kraken alt funding being persistently negative, so you'd be long on Kraken. Kraken EU's product is not identical to the PF_ book we sampled.
- **Not sustained:** 30-day persistence of a 7-day gap is unlikely; assume half.
- **Realistic expectation at $10k:** about **$50–250 per month on the best 1–2 pairs combined**, with drawdowns.

**Excluded from carry:**
- **MNT on Kraken:** the +428% mean is a single spike (std 2,050%).
- **BTW, CC:** the current rate disagrees with the 7d sign.
- **Any dYdX leg:** books too thin (section 4).

## 4. Slippage and depth at your size

Source: `data/depth.csv`. Values are median (p90) VWAP slippage vs mid, one side, including the half-spread.

| Venue | $100 | $1k | $10k | Median quoted spread |
|---|---|---|---|---|
| Hyperliquid | 0.5 (2.5) | 1.3 (3.5) | 3.0 (9.4) | 0.9 bps |
| OKX | 1.0 (3.5) | 1.8 (6.0) | 4.3 (19) | 1.6 |
| Lighter | 1.9 (4.3) | 2.1 (6.7) | 3.9 (11.5) | 3.7 |
| Aster | 2.5 (8.6) | 3.4 (12) | 5.9 (26) | 4.8 |
| Kraken | 2.9 (7.6) | 3.7 (9.9) | 6.0 (24) | 5.4 |
| dYdX | 30 (145) | 30 (193) | 36 (463) | **60** |

**dYdX:** the books are too thin to be a leg in anything.

**Bad $10k fills seen:** CRO on Kraken (book swept), MORPHO on Aster (136 bps), KAS on Aster (51 bps), PUMP on dYdX (390 bps).

**Fill risk:**
- **Speed:** to fill both legs at once you need API execution or near-simultaneous IOC orders. Manual clicking will routinely leave you with one leg filled and the other not.
- **Minimums:** Hyperliquid's minimum order is $10. OKX has contract-size lots. Both are fine at your size.

## 5. Risks and constraints

Sources: `risks.md`. Most of it comes from secondary sources and is marked **UNVERIFIED** there.

- **Liquidation:**
  - Each leg is margined separately on a different venue. A 20–30% move on an alt liquidates the losing leg at 3–5x, even while you're hedged overall.
  - Keep each venue at **≤2–3x**, and rebalance collateral ($1–5 and minutes to hours per transfer).
- **Venue risk:**
  - **Hyperliquid Oct-10-2025 cascade:** about $641m force-sold and cross-margin auto-deleveraging (ADL). ADL can close your profitable hedge leg.
  - **Hyperliquid manipulation:** JELLY and XPL incidents.
  - **Perp-DEX exploits in 2026:** Drift (~$280m, UNVERIFIED), Ostium, AFX, Arcus.
  - **Lighter:** a "Stage 0" rollup, meaning the team controls upgrades (L2BEAT). Its escape hatch is audited.
  - **CEX counterparty risk:** reports of a large 2026 Binance incident are UNVERIFIED and conflicting.
- **Listings:**
  - OKX lacks XMR, PAXG, MNT and KAS.
  - QNT on OKX is a different instrument (priced at about 30 vs 148 elsewhere); don't pair it.
  - Full matrix in `data/listings.csv`.
- **Delisting:** mainly small caps; Binance delisted several in 2026 with auto-settlement. No large-cap delistings found. Carry legs on newer or small tokens (VVV, PUMP, KAS, MORPHO, WLFI, SKY, BTW, CC) carry delisting and manipulation risk.
- **France (UNVERIFIED):**
  - Realistic regulated routes: **OKX Europe (X-Perps, ≤10x)** and **Kraken EU (MiFID, ≤10x)**.
  - Binance France and Bybit EU: probably no perps.
  - DEXs: not authorised. Use is a legal grey zone; no France-specific front-end block was found.
  - None of the 8 venues appears in the AMF's 22-Apr-2026 warning list (verified). The full blacklist was not checked.
- **Tax (France):** flat tax (PFU) reportedly 31.4% in 2026; treatment of perp/derivative gains is uncertain. **UNVERIFIED.** Funding received is likely taxable income even when the hedge leg loses.

## 6. Answers

**Ranking of coin and venue-pair combinations with positive expected net:**
- **Spread trading:** none survive realistic execution.
- **Funding carry, preferred pairs:**
  - **VVV** short Lighter / long Hyperliquid. Lowest cost, both DEX, break-even ~1.3–2.8 days.
  - **PUMP** or **PEPE** short Lighter / long Kraken. Break-even ~3 days.
  - **KAS** short Hyperliquid / long Kraken. Biggest edge but most volatile. Break-even 2–4.5 days.
  - Hold ≥1–2 weeks, and re-check funding daily. Exit when the 24h-average differential drops below about 10% annualised.

**Realistic profit:**

| Leg size | Spread trading | Carry (after costs, if gaps half-persist) |
|---|---|---|
| $100 | negative | about $0–1/month; fixed transfer fees dominate |
| $1,000 | negative | about $5–20/month (0.5–2%) |
| $10,000 | negative | about $50–200/month (0.5–2%) |

You need **≥$5–10k per leg** (≥$10–20k capital in total, since collateral sits on two venues) before the carry covers your time, transfer costs and the risk of a funding flip. Below that, a stablecoin yield of ~4–8% APR with no basis or liquidation risk is competitive.

**Carry vs spread:** carry is clearly better. Spread edges are 0–5 bps after fees and need bot-level speed. Carry pays 8–25 bps/day on a few alts and can be entered with maker orders on one leg to cut fees.

**Coins and venues to avoid:**
- **dYdX** as a venue: 60 bps quoted spreads.
- **QNT on OKX:** instrument mismatch.
- **MNT on Kraken:** funding spikes.
- **CRO on Kraken** and **MORPHO, KAS on Aster** at $10k: thin books.
- **Aster's own token (ASTER) on Aster:** venue-native token, persistent basis.
- Very new or meme tokens (BTW, CC, SKY, PUMP, WLFI, VVV) at more than small size: manipulation and delisting risk. Be aware that several of the carry picks are in this group.
- Majors (BTC/ETH/SOL) aren't risky, but there's no edge in them.

## 7. What could not be verified

- No live Binance or Bybit data (geo-block).
- OKX, Kraken, Binance and Bybit fee pages could not be read; their fees are standard published base rates, **UNVERIFIED**.
- EU entity books, fees and funding (OKX Europe X-Perps, Kraken EU) were not sampled.
- Most France and legal claims, incident figures, withdrawal fees and max leverage come from secondary sources.
- Lighter funding history sign was inferred from the `direction` field.
- Hyperliquid book depth was truncated to 20 levels and Lighter to 100 orders.
- The sampling window was 30 minutes on one day, and funding history covers 7 days. Re-run `collect.py` and `analyze.py` across several days, including a volatile one, before committing capital.

## Files

- `collect.py`, `analyze.py`, `carry.py`, `spread_sim.py`: rerunnable scripts.
- `data/`: raw samples, depth, funding, listings, summaries.
- `fees.md`, `risks.md`: source notes with URLs and verification status.
