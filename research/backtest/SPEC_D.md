# Simulation D: the "everything on" carry bot

Same window, data conventions and cost model as A/B (2024-11-25 → 2026-11-24, hourly), except for the changes below. **No lookahead:** every signal uses only data available up to that hour.

Capital: $100 per leg ($200 total). Run it with leverage caps ∈ {3, 5, 10, 20}.

## Venues & universe
- **Venues:**
  - Hyperliquid + Kraken for the full window.
  - Add **Lighter** (zero fee) and **Aster** from whenever their public history starts:
    - Lighter `/api/v1/fundings` + `/api/v1/candlesticks` on mainnet.zklighter.elliot.ai. The funding rate is in percent units, and the sign comes from `direction`.
    - Aster `/fapi/v1/fundingRate` + `/fapi/v1/klines`. Funding is 8h, or per `fundingInfo`.
  - If a venue's history can't be fetched, skip it and say so.
- **Dynamic universe:** at each hour, any coin listed on ≥2 of those venues at that time. This includes coins that list during the window, so new-listing funding spikes get caught.
- **Two-pass fetch to keep it cheap:**
  1. Download funding for all candidate coins.
  2. Download hourly candles only for coins that are ever selected.

## Section 1: cost rules
1. **Maker entry/exit on one leg:**
   - The slower or more expensive leg is filled as maker: HL 1.5 bps, Kraken 2 bps, Lighter 0, Aster 0.
   - The other leg is hedged as taker right after: HL 4.5, Kraken 5, Lighter 0, Aster 4.
   - Add 1 bp of adverse selection to the maker leg and 1h execution delay on fill.
2. **Zero-fee leg:** when the coin is on Lighter and Lighter is on the right side of the funding gap (or within 5% ann of the best venue), use Lighter as one leg.
3. **Fewer flips:** switch pair, coin or direction only if (new expected 7-day funding gain − current expected 7-day funding gain) > 2 × the full switching cost (fees + slippage + transfer).
4. **Fewer transfers:** move collateral only when liquidation protection requires it (see rule 11) or on a rotation that changes venues. Charge $1 each.
5. **Referral discount:** 5% off all fees. UNVERIFIED; flag it in the output.

## Section 2: revenue rules
6. **Rotation scanner:** each hour, rank all (coin, venue-pair, direction) by forecast funding differential net of switching cost. Hold the **top 2** positions, with equity split between them; the minimum order is $10 per leg. Also report a top-1 version.
7. **New listings and squeezes:** no special code. The scanner plus dynamic universe should pick these up. Report how much P&L came from coins in their first 30 days of listing.
8. **Favourable-gap entry:** when opening, wait up to 6h for an hour where the price gap between the venues (using closes) is ≥ 0 in our favour. Enter at the end of the 6h regardless.
9. **Funding forecast:** signal = 0.5 × last-24h mean + 0.3 × last-7d mean + 0.2 × latest hourly rate (annualised). Use the signal, not the raw 7d mean.
10. **8h-venue timing:** for 8h venues, model discrete payouts at the venue's funding timestamps. You only receive or pay if holding at the timestamp. Prefer opening an 8h-venue leg ≤1h before a payout in our favour, and avoid holding through one against us when a switch is pending.

## Risk + sizing
11. **Close before liquidation:**
    - If a leg's margin usage reaches **75%** (equity ≤ maintenance margin / 0.75), first try a rebalance transfer (1h delay, $1).
    - If usage reaches **90%** before the transfer lands, **close both legs** as taker.
    - Real liquidations are still simulated with high/low; on a liquidation, auto-close the other leg as in A.
12. **Volatility-adjusted leverage:**
    - Leverage = clamp(cap × (target_vol / realised_vol_24h), 1, min(cap, venue maxLev)).
    - realised_vol_24h = annualised stdev of hourly returns over the last 24h.
    - target_vol = that coin's trailing 30-day median of realised_vol_24h.
    - Re-evaluate every 6h. Adjust size only if it changes by >20%; each adjustment pays fees on the delta.
13. **Compounding:** size = current leg equity × leverage at every (re)entry and adjustment.

## Outputs
- `results_D.csv`: one row per cap × (top-1, top-2), with:
  - final equity, total return %, CAGR, max drawdown
  - # real liquidations, # pre-emptive closes
  - funding earned, fees, slippage, transfers
  - # switches
  - P&L from new listings
  - P&L split by venue pair
- Add the A/B results for the same caps to `summary.md` for side-by-side comparison.
- **Ablation, if time allows** (cap 10, top-2): turn each rule off one at a time to show how much each one contributes.
- `equity_curves_D.png`, if matplotlib is available.
