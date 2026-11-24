# Venue risk research: perps for a French retail user (as of 2026-11-24)

## Method and limits (read first)

- **Status 2026-11-24:** Re-check attempted with WebFetch. hyperliquid.gitbook.io, docs.asterdex.com, docs.lighter.xyz, docs.dydx.xyz and www.amf-france.org all fail DNS resolution (`getaddrinfo ENOTFOUND`). No ToS, restricted-jurisdiction page or AMF blacklist entry was read; the France status in section 1 is unchanged and still UNVERIFIED.

- Research was done with WebSearch only. Every fetch attempt failed with DNS errors (defillama.com, www.theblock.co, coincentral.com, onekey.so, www.blockworks.com, www.coinperps.com). The tool reported these hosts as outside the session's allowed network domains, so no page was read in full. **All claims below come from search-result snippets and titles, not from the pages themselves.**
- Most sources are secondary (crypto news, comparison sites, tax-software blogs). Primary sources (AMF, ESMA, venue ToS, DefiLlama, Hyperliquid docs) were not read.
- Items marked **UNVERIFIED** are single-source, conflicting, or not researched. Dates below are the dates shown in snippets; "date n/s" means no date was shown.
- Some snippets contain claims that look inconsistent (for example, a Binance incident dated both Aug 28 and Oct 2026). Treat specific figures as leads to check, not facts.

---

## 1. Availability for a French retail resident (2026)

### Regulatory baseline
- **AMF PSAN transition ends 1 July 2026.** Providers that offered crypto services before MiCA have until that date to obtain a MiCA authorisation. The AMF urged firms without a filing to file promptly and, if unable, to wind down. Source: AMF communications, AMF site, 2026 (exact release date n/s). https://www.amf-france.org/en/news-publications/news-releases/amf-news-releases/crypto-assets-autorite-des-marches-financiers-warns-public-about-activities-several-unauthorized-1
- **AMF crypto blacklist.** AMF release dated 2026-04-22: 23 names added since start of 2026. A separate AMF/ACPR warning says 26 crypto-derivative sites were added in 2026 (11 in Q2). One entry (Neverless.com) was removed 2026-06-02. Source: same AMF pages (snippet). **UNVERIFIED: whether any of the eight venues appear on the blacklist.** None of the eight was named in the snippets I saw, but I did not check the list itself.
- **Whitelist check.** The AMF whitelist of authorised providers is the place to confirm status for each venue. Not fetched.
- **Perps classification.** Secondary reports say ESMA (Feb/Mar 2026) said perpetual-style crypto products may fall within CFD intervention measures, and that under MiFID II perps would be CFDs. **UNVERIFIED** (no ESMA page read). Source (secondary): https://blockeden.xyz/blog/2026/04/17/okx-x-perps-europe-mifid-5-year-expiry-perpetual-futures/ (date 2026-04-17 per URL).

### Venue by venue

| Venue | French user lands on | Perps for French retail? | Evidence and date |
|---|---|---|---|
| **Binance** | Binance France (MiCA application) | **Reported no.** Secondary reports say futures, spot and margin stopped for French users around 2026-07-01 after the MiCA application was withdrawn; withdrawals still allowed. Account closure reported for 2026-12-31, and deposits reported stopped (conflicting reports). **UNVERIFIED** against Binance or AMF. | Snippets from mitrade.com (2026-07-06 per URL), coincentral.com, blockonomi.com, cryptonomist.ch (2026-07-06 per URL). |
| **Bybit** | Bybit EU GmbH (Austrian FMA MiCA licence, passported to France). AMF whitelist entry dated 2025. | **Unclear, leaning no.** Secondary reports: Bybit EU offers spot, spot margin, savings and card. Futures/options not offered per one source; another says spot only. A MiFID II licence is reportedly being sought. Global Bybit perps (including the April 2026 stock/commodity perps) are not offered to EU users. **UNVERIFIED.** | AMF whitelist PDF (Bybit EU GmbH). Secondary: crypto.news, cryptoslate, theblock (title "Bybit will end services and stop offering products in France", date n/s; may be an older event, **UNVERIFIED**). |
| **OKX** | OKX Europe (Malta MiFID entity) for EEA retail | **Yes, via X-Perps.** Five-year-expiry futures, structured to avoid the CFD label. Offered to EEA retail after appropriateness test, up to 10x (one summary). Offshore margin and options not offered to EEA retail. Simple Mode reported live 2026-07-28. | Cointelegraph/blockeden (2026-04-17 per URL); coincentral; thefintechtimes. **UNVERIFIED** details (leverage, Simple Mode date). |
| **Kraken** | Payward Europe / Cypriot MiFID entity | **Yes, reportedly.** EEA perpetuals launched May 2025 (up to 10x, 150+ markets on Kraken Pro; Nov 2025 added BTC/ETH collateral). Feb 2026 ESMA warning; Kraken then listed perpetuals on tokenised equity and gold products. **France exclusion: only one comparison site (coinperps) says France is excluded. UNVERIFIED and contradicted by nothing I could check.** | blog.kraken.com (EU derivatives posts, dates n/s); crypto.news; crowdfundinsider 2025-05. |
| **Hyperliquid** | Front end (not an EU entity) | **No EU-specific restriction found.** Third-party guides list France as supported; one lists France as restricted for Polymarket (a different venue). Restrictions are described as applied at the front end via risk-scoring tools; the protocol itself is reachable directly. **UNVERIFIED** against the ToS (sections 1.5 and 3.1.5 per secondary sources, updated 2025-01-26 and possibly 2026-06-15). Legal grey zone: unlicensed offer to French retail under MiFID/AMF rules. | datawallet.com, coinperps.com (2026 pages, dates n/s). |
| **Aster** | Not researched | **UNVERIFIED** | No geo or licence information retrieved. |
| **Lighter** | Not researched | **UNVERIFIED** | No geo or licence information retrieved. |
| **dYdX v4** | Not researched | **UNVERIFIED** | Only found an onekey.so note on US geo-blocks (not France); page not readable. |

**Bottom line for France:** For a French retail user, the realistic regulated route is OKX (X-Perps via a MiFID entity) and possibly Kraken (MiFID entity); Bybit EU and Binance France are unlikely to offer perps. The DEXs are not licensed in France and sit in a legal grey zone. Confirm each against the venue's own EU country list and the AMF whitelist before relying on this.

---

## 2. Exchange and counterparty risk (2024-2026)

### Hacks and losses (2026, snippets)
- **Aggregate, UNVERIFIED.** A snippet cites DefiLlama (as of about 2026-11-12/13) with $8.78b lost across 343 incidents in 2026, the largest a Binance CEX incident at $6.36b (Oct 2026). One DefiLlama span dates the Binance incident to 2026-08-28. The DefiLlama page was not readable. Source: https://defillama.com/hacks (not fetched).
- **Mercado Bitcoin** (CEX): about $40m+ moved from exchange wallets, 2026-11-02 (snippet). **UNVERIFIED.**
- **BitMart** (CEX): about $391k, same day (snippet). **UNVERIFIED.**
- **AFX Trade** (perp DEX, Arbitrum): $24.15m drained via a custody bridge the protocol operates; 30% bounty offered to the attacker. Source: https://decrypt.co/374133 (date n/s).
- **Ostium** (perp DEX, Arbitrum): oracle signer key compromised, about $18m (one report) or $23.75m (another, dated 2026-07-15); trading resumed later. Source: https://decrypt.co/373566 (date n/s); coinstats snippet.
- **Drift Protocol** (perp DEX, Solana): about $280-285m, dated 2026-04-01 (two sources disagree on the figure). **UNVERIFIED.**
- **Arcus** (perp DEX, Robinhood Chain): $2.23m, 2026-11-10, sub-account accounting bug; operators covered it from treasury. Source: https://cryptoticker.io/en/arcus-exploit-perp-dex-sub-account-bug/ (date from snippet).

### Hyperliquid events
- **JELLY (March 2025).** A trader opened about an $8m short on the low-cap JELLY token, then pushed the onchain price up; the position was taken over by the HLP vault. Hyperliquid delisted JELLY and forced closes. Whether this was ADL or a settlement is disputed. Source: https://www.coindesk.com/markets/2025/03/26/hyperliquid-delists-jellyjelly-after-vault-squeezed-in-usd13m-tussle (URL from snippet, dated 2025-03-26 in URL).
- **XPL pre-market (date n/s, late 2025).** A price spike in the pre-launch perp caused mostly short-side liquidations. Hyperliquid said hyperps are isolated-margin only and changed the hyperp mark price to incorporate external perp prices (e.g. Binance). Source: The Block (snippet). Aster also compensated users for an XPL perp glitch in Sept 2025 (theblock.co/post/372500).
- **Oct 10, 2025 cascade.** A research preprint (snippet) reports about $641m force-sold on Hyperliquid at 21:19 UTC, of which about $576m went to the backstop and about $64m to the order book. Cross-margin ADL was triggered for the first time in over two years. Open interest reportedly roughly halved and had not recovered by late October. **No official Hyperliquid postmortem found.** Source: theblock.co 2025-10-21 snippet; Blockworks (date n/s).
- **Oct 10, 2025 outages.** Lighter reported about 4.5h of downtime on 2025-10-10 (L2BEAT). Other CEX/DEX outages in the same event were not checked.

### Proof of reserves
- **Not researched.** No proof-of-reserves reports for any of the eight venues were retrieved. **UNVERIFIED / gap.**

---

## 3. Smart-contract and bridge risk

- **Lighter (zk rollup).**
  - Desert/escape-hatch circuits audited by zkSecurity, 2025-11-03 start, two consultants, one week. Spot-market circuits audited later in Nov 2025. Sources: https://reports.zksecurity.xyz/reports/zklighter-desertexit (2025-11); https://reports.zksecurity.xyz/reports/zklighter-spot-market.md.
  - Escape mode: if the operator misses a forced-transaction deadline of 14 days, anyone can freeze the L1 contract and exit (L2BEAT, May 2026, per snippet).
  - Residual risks per L2BEAT: Stage 0; the team controls the upgrade path (an instant malicious upgrade could weaken exits); the escape hatch does not verify input fairness; sequencer ordering unchanged. The desert-mode circuit source was not publicly available as of Jan 2026 (snippet). Source: https://l2beat.com/publications/exchange-risk-and-how-lighter-escapes-it (May 2026 per snippet).
  - Robinhood Chain fork (USDG-based): contracts instantly upgradable, no exit window (L2BEAT listing).
- **Hyperliquid bridge and validators.** **Not researched. UNVERIFIED.** The "validator put" Blockworks article exists (date n/s), but its content was not read.
- **Aster.** Immunefi bounty up to $200k (10% of affected funds), listing updated 2026-04-17. HashEx (Nov 2025) automated AI-style review of the ASTER token contract only, zero findings, but flagged self-destruct functionality. No full manual audit of the exchange contracts found. An unverified Nov 2026 claim cites a $4.56m user loss and a partner data breach affecting 27,000 orders (Coin Turk snippet). **UNVERIFIED.**
- **dYdX v4 (chain).** **Not researched.**
- **General lesson from 2026 incidents:** the main failure modes in the snippets are oracle-signer key compromise (Ostium), custody-bridge compromise (AFX), and accounting bugs in sub-accounts (Arcus), not core-chain exploits.

---

## 4. Delisting risk

- **Binance (USDS-M and COIN-M perps, 2026, from snippets):**
  - 2026-01-21: four contracts (BIDUSDT, DMCUSDT, ZRCUSDT, TANSSIUSDT).
  - 2026-02-10: RVVUSDT and YALAUSDT, auto-settled at 09:00 UTC.
  - 2026-03-25: COIN-M APTUSD and OPUSD terminated.
  - 2026-04-28/29: six USDS-M perps, auto-settlement, tighter liquidation rules in the final hour.
  - Stated rationale: regular product review; per secondary sources, liquidity and volume criteria.
  - Sources: Binance announcements (URLs from snippets, e.g. binance.com/en/support/announcement/746056ce732d43dda12c1e5ae1b7a059, dated 2025-12-05).
- **OKX:** removed MAJORUSDT and VINEUSDT on 2025-09-26 (OKX help center, https://www.okx.com/en-us/help/okx-to-delist-several-perpetual-futures-20250922). Only 2025 delistings were found.
- **Bybit and Hyperliquid:** no 2026 delisting notices found in the snippets.
- **Large caps:** none of the recent delistings found were large-cap coins. **Coverage gap:** no full list checked.
- **Criteria (secondary):** liquidity, trading volume, product review; for Hyperliquid, squeeze/manipulation risk on thin markets (JELLY precedent). **UNVERIFIED** against official criteria pages.

---

## 5. Leg and fill risk for cross-venue arbitrage

**Not researched, except as noted.** No figures were retrieved for API latency, rate limits, withdrawal times, or minimum order sizes. Known from background knowledge only (UNVERIFIED, must be checked on each venue's docs):
- Hyperliquid: $10 minimum order notional (UNVERIFIED).
- OKX: contract-size and lot rules per instrument (UNVERIFIED).
- Withdrawal and deposit times (on-chain confirmation plus any manual review) vary by venue and asset; not checked.
- The Oct 10, 2025 event and Hyperliquid ADL show that during cascades, fills and liquidations can move far from the mark price, which affects hedge legs.

---

## 6. French tax note

Secondary 2026 tax guides (plisio.net, blockpit.io, finary.com; dates n/s) say the flat tax on crypto gains (PFU) is 30%, with some saying it rose to 31.4% (12.8% income tax plus 18.6% social contributions) from 2026-01-01 after the PLFSS 2026. Blockpit still shows the older 30% (12.8% plus 17.2%). Taxpayers can opt for the progressive scale instead. A €305 annual disposal threshold is mentioned, and article 150 VH bis CGI is cited for occasional crypto gains. **UNVERIFIED: the 31.4% rate (check the loi de finances / PLFSS 2026 text and BOFiP), and the €305 threshold.** **UNVERIFIED: how perpetual-futures or other derivative gains are taxed.** No source addressed derivatives. Derivative gains may fall under a different regime than spot disposals. Consult a French tax adviser and BOFiP before relying on any figure.

---

## Gaps and next steps (priority order)

1. Confirm AMF whitelist and blacklist status for all eight venues (AMF site, not fetched).
2. Check each venue's EU/France country restriction list and product page (Binance, Bybit, OKX, Kraken, and the three DEX front ends).
3. Read Hyperliquid's official ToS and any frontend geoblock notice; confirm the bridge validator set.
4. Read the Hyperliquid official Oct 10 postmortem, if one exists, and the DefiLlama hacks page.
5. Check withdrawal times, API rate limits, and minimum order sizes on each venue's docs.
6. Tax: BOFiP and the 2026 finance law text.
7. Not yet researched: proof-of-reserves reports for every venue.
