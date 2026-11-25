#!/usr/bin/env python3
"""Cross-venue funding-carry backtest (stdlib only). Reads data/<COIN>.csv written by fetch.py.

Per coin: $100 collateral on Hyperliquid (HL) and $100 on Kraken, long one venue / short the other,
same USD notional per leg = min(equity_HL, equity_KR) * L. Direction from trailing 7d mean funding,
re-checked every 24h; flips only if the opposite differential exceeds 10% annualised.
Variant A: no rebalancing. Variant B: transfer when one leg < 60% of the other (effective +1h,
$1 cost) and re-size notional monthly. Liquidation uses the hourly high/low (worst case).

Writes results.csv and summary.md into the backtest folder.
"""
import csv
import json
import statistics
import os

BASE = '/home/user/crevopunch/research/backtest'
DATA = os.path.join(BASE, 'data')
LEVS = [1, 3, 5, 10, 20]
VARIANTS = ['A', 'B']
EQ0 = 100.0            # collateral per venue
FEE = {'H': 4.5e-4, 'K': 5e-4}
TRANSFER = 1.0
WARM = 168             # trailing 7 days
HPY = 8760
FLIP = 0.10            # annualised differential needed to flip
REBAL = 0.60
STOP = 20.0
MIN_HOURS = 365 * 24   # ~12 months of complete overlap


def slip(coin):
    return 2e-4 if coin in ('BTC', 'ETH') else 5e-4


def load(coin):
    """Hours with both funding rates and Kraken prices. Hyperliquid candles only exist from
    ~2026-04-30 (API depth limit), so earlier HL OHLC is proxied by Kraken OHLC (flag: proxied)."""
    rows, proxied = [], 0
    with open(os.path.join(DATA, f'{coin}.csv')) as f:
        for r in csv.DictReader(f):
            if r['hl_funding'] == '' or r['kr_funding'] == '' or r['kr_close'] == '':
                continue
            kr = [float(r['kr_close']), float(r['kr_high']), float(r['kr_low'])]
            if r['hl_close'] == '':
                hl = kr
                proxied += 1
            else:
                hl = [float(r['hl_close']), float(r['hl_high']), float(r['hl_low'])]
            rows.append((r['hour_utc'], hl[0], hl[1], hl[2], float(r['hl_funding']),
                         kr[0], kr[1], kr[2], float(r['kr_funding'])))
    load.proxied = proxied
    return rows


def liquidated(leg, hi, lo, mmr):
    q = leg['q']
    if q == 0:
        return False
    w = lo if q > 0 else hi  # worst price within the hour
    return leg['cash'] + q * (w - leg['e']) < mmr * abs(q) * w


def eq(leg, p):
    return leg['cash'] + leg['q'] * (p - leg['e'])


def trade(leg, qnew, p, rate, acc):
    """Move a leg to signed units qnew at price p; fee+slippage on traded notional."""
    q, e = leg['q'], leg['e']
    dq = qnew - q
    if dq == 0:
        return
    cost = abs(dq) * p * rate
    leg['cash'] -= cost
    acc['fees'] += cost
    if q != 0 and qnew * q >= 0 and abs(qnew) <= abs(q):      # reduce or close
        leg['cash'] += (q - qnew) * (p - e)
        leg['q'] = qnew
        if qnew == 0:
            leg['e'] = 0.0
    elif q != 0 and qnew * q < 0:                            # sign flip: close, then open
        leg['cash'] += q * (p - e)
        leg['q'], leg['e'] = qnew, p
    else:                                                    # open or increase
        leg['e'] = p if q == 0 else (q * e + dq * p) / qnew
        leg['q'] = qnew


def simulate(rows, coin, maxlev, L, variant):
    n = len(rows)
    hc = [r[1] for r in rows]; hh = [r[2] for r in rows]; hl = [r[3] for r in rows]
    hf = [r[4] for r in rows]
    kc = [r[5] for r in rows]; kh = [r[6] for r in rows]; kl = [r[7] for r in rows]
    kf = [r[8] for r in rows]
    cumH, cumK = [0.0], [0.0]
    for i in range(n):
        cumH.append(cumH[-1] + hf[i]); cumK.append(cumK[-1] + kf[i])
    mmr = 1.0 / (2 * maxlev)
    rate = {'H': FEE['H'] + slip(coin), 'K': FEE['K'] + slip(coin)}
    H = {'cash': EQ0, 'q': 0.0, 'e': 0.0}
    K = {'cash': EQ0, 'q': 0.0, 'e': 0.0}
    acc = {'fees': 0.0, 'fund': 0.0, 'xfer': 0.0, 'flips': 0, 'liqs': 0, 'resizes': 0, 'xfers': 0}
    short = None          # venue we are short: 'H' or 'K'
    last_dec = None
    pend_xfer = None
    reentry_at = None
    dead = False
    start = WARM - 1
    series = [2 * EQ0]

    def open_pos(i, want):
        N = min(H['cash'], K['cash']) * L
        pH, pK = hc[i], kc[i]
        sH = -N / pH if want == 'H' else N / pH
        sK = -N / pK if want == 'K' else N / pK
        trade(H, sH, pH, rate['H'], acc)
        trade(K, sK, pK, rate['K'], acc)

    def close_pos(i):
        trade(H, 0.0, hc[i], rate['H'], acc)
        trade(K, 0.0, kc[i], rate['K'], acc)

    for i in range(start, n):
        pH, pK = hc[i], kc[i]
        if dead:
            series.append(H['cash'] + K['cash'])
            continue
        # (a) variant-B transfer scheduled for this hour
        if pend_xfer == i:
            pend_xfer = None
            tot = eq(H, pH) + eq(K, pK)
            tgt = (tot - TRANSFER) / 2
            H['cash'] = tgt - H['q'] * (pH - H['e'])
            K['cash'] = tgt - K['q'] * (pK - K['e'])
            acc['xfer'] += TRANSFER; acc['xfers'] += 1
        # (b) liquidation check on this hour's high/low
        if H['q'] or K['q']:
            lh = liquidated(H, hh[i], hl[i], mmr)
            lk = liquidated(K, kh[i], kl[i], mmr)
            if lh or lk:
                acc['liqs'] += int(lh) + int(lk)
                if lh and lk:
                    H['cash'] = K['cash'] = 0.0
                    H['q'] = K['q'] = 0.0
                    dead = True
                    series.append(0.0)
                    continue
                if lh:
                    H['cash'], H['q'], H['e'] = 0.0, 0.0, 0.0
                    trade(K, 0.0, pK, rate['K'], acc)
                else:
                    K['cash'], K['q'], K['e'] = 0.0, 0.0, 0.0
                    trade(H, 0.0, pH, rate['H'], acc)
                short = None
                E = H['cash'] + K['cash']
                if E < STOP:
                    dead = True
                    series.append(E)
                    continue
                H['cash'] = K['cash'] = (E - TRANSFER) / 2     # re-split 50/50, $1 transfer
                acc['xfer'] += TRANSFER; acc['xfers'] += 1
                reentry_at = i + 1
                series.append(H['cash'] + K['cash'])
                continue
        # (c) hourly funding at close: long pays rate*notional, short receives
        if H['q'] or K['q']:
            cfH = -H['q'] * pH * hf[i]
            cfK = -K['q'] * pK * kf[i]
            H['cash'] += cfH; K['cash'] += cfK
            acc['fund'] += cfH + cfK
        # (d) entry when flat
        if not H['q'] and not K['q'] and (reentry_at is None or i >= reentry_at):
            mH = (cumH[i + 1] - cumH[i + 1 - WARM]) / WARM
            mK = (cumK[i + 1] - cumK[i + 1 - WARM]) / WARM
            want = 'H' if mH >= mK else 'K'
            if min(H['cash'], K['cash']) > 0:
                open_pos(i, want)
                short = want; last_dec = i; reentry_at = None
        in_pos = bool(H['q'] or K['q'])
        # (e) 24h direction check; flip costs a full close plus reopen
        if in_pos and i - last_dec >= 24:
            last_dec = i
            mH = (cumH[i + 1] - cumH[i + 1 - WARM]) / WARM
            mK = (cumK[i + 1] - cumK[i + 1 - WARM]) / WARM
            d = (mH - mK) * HPY
            want = 'H' if mH >= mK else 'K'
            if want != short and abs(d) > FLIP:
                close_pos(i)
                open_pos(i, want)
                short = want
                acc['flips'] += 1
        # (f) variant B: monthly re-size of notional to equity x L
        if variant == 'B' and in_pos and i > start and rows[i][0][:7] != rows[i - 1][0][:7]:
            N = min(eq(H, pH), eq(K, pK)) * L
            sH = -N / pH if short == 'H' else N / pH
            sK = -N / pK if short == 'K' else N / pK
            trade(H, sH, pH, rate['H'], acc)
            trade(K, sK, pK, rate['K'], acc)
            acc['resizes'] += 1
        # (g) variant B: schedule transfer when a leg falls below 60% of the other
        if variant == 'B' and in_pos and pend_xfer is None:
            eH, eK = eq(H, pH), eq(K, pK)
            lo, hi = min(eH, eK), max(eH, eK)
            if lo < REBAL * hi:
                pend_xfer = i + 1
        # (h) mark to market at this venue's close
        series.append(H['cash'] + K['cash'] + H['q'] * (pH - H['e']) + K['q'] * (pK - K['e']))

    exit_cost = 0.0
    if not dead and (H['q'] or K['q']):
        before = acc['fees']
        close_pos(n - 1)
        exit_cost = acc['fees'] - before
        series[-1] = H['cash'] + K['cash']
    acc['exit'] = exit_cost
    final = series[-1]
    peak, mdd = series[0], 0.0
    for v in series:
        peak = max(peak, v)
        if peak > 0:
            mdd = min(mdd, v / peak - 1)
    years = (n - start) / HPY
    ret = final / (2 * EQ0) - 1
    cagr = (final / (2 * EQ0)) ** (1 / years) - 1 if final > 0 else -1.0
    return {
        'start_date': rows[start][0][:10], 'final_equity': final, 'total_return_pct': 100 * ret,
        'cagr_pct': 100 * cagr, 'max_drawdown_pct': 100 * mdd, 'liquidations': acc['liqs'],
        'funding_usd': acc['fund'], 'fees_slippage_usd': acc['fees'], 'exit_usd': exit_cost, 'transfer_usd': acc['xfer'],
        'flips': acc['flips'], 'resizes': acc['resizes'], 'transfers': acc['xfers'],
        'dead': dead, 'years': years,
    }


def write_summary(out, info):
    """summary.md: per variant, rows = coins, columns = L; cell = final equity / liquidations."""
    cells = {(r['coin'], r['variant'], r['L']): r for r in out}
    coins = [c for c in info if 'skip' not in info[c]]
    lines = ['# Cross-venue funding carry: 2-year backtest summary', '',
             'Window: trading from 2025-11-26 to 2026-11-24 (~12 months). Kraken funding history only goes back to '
             '2025-11-19, so the 2-year window is not achievable; 7-day warm-up is taken from that start.',
             'Cell = final total equity in $ (start $200) / liquidations. N/A = L above the HL max leverage.', '']
    for v in VARIANTS:
        name = 'A (no rebalancing)' if v == 'A' else 'B (rebalancing + monthly re-size)'
        lines += [f'## Variant {name}', '',
                  '| coin | HL maxLev | start | ' + ' | '.join(f'L={L}' for L in LEVS) + ' |',
                  '|---|---|---|' + '---|' * len(LEVS)]
        for c in coins:
            cs = []
            for L in LEVS:
                r = cells.get((c, v, L))
                if r is None or r['status'] != 'ok':
                    cs.append(r['status'] if r else 'n/a')
                else:
                    cs.append(f"{r['final_equity']:.1f} / {r['liquidations']}")
            lines.append(f"| {c} | {info[c]['maxlev']} | {info[c]['start']} | " + ' | '.join(cs) + ' |')
        lines.append('')
    lines += ['## What drives the results', '',
              'At L=1 the hedge is nearly flat and earns the HL-minus-Kraken funding gap net of about 0.1-0.3% of fees, '
              'so the strategy is close to a small, reliable carry. Above L=3 the unrebalanced legs get liquidated on '
              'adverse hourly moves of roughly 1/L minus the maintenance margin, and each liquidation costs fees plus '
              'a $1 transfer, so the equity compounds down; variant B\'s rebalancing does not rescue this and is '
              'worse at L=3 because it transfers collateral only after the legs have already diverged.', '',
              '## Portfolio row', '', 'Skipped: the monthly top-5 re-pick with cross-coin capital transfers was not built.', '',
              '## Caveats', '',
              '- Hyperliquid candles are only served from ~2026-04-30; earlier HL OHLC is proxied by Kraken OHLC '
              '(zero basis on those hours, see `proxied_hl_hours` in data/coin_info.json).',
              '- Position sizes are in units fixed at open; funding accrues on the mark (venue close).',
              '- Liquidation is checked on each venue\'s hourly high/low against maintenance margin 1/(2 x HL maxLev).',
              '- No exit cost on the final mark-to-market equity; no funding-rate caps; no slippage beyond the flat bps.']
    cd_path = os.path.join(BASE, 'results_CD.csv')
    if os.path.exists(cd_path):
        cd = list(csv.DictReader(open(cd_path)))
        lines += ['## Side-by-side: A, B, C, D (equal $200 start; caps 3/5/10/20; exit costs included)', '',
                  'A and B are medians across the coins where the cap is allowed (n shown); C and D are one book '
                  'across the 73-coin universe. Cell = final $ / CAGR % / max DD % / liquidations.', '',
                  '| variant | ' + ' | '.join(f'cap {L}' for L in (3, 5, 10, 20)) + ' |',
                  '|---|' + '---|' * 4]
        for v in VARIANTS:
            cells = []
            for L in (3, 5, 10, 20):
                ok = [r for r in out if r['variant'] == v and r['L'] == L and r['status'] == 'ok']
                if not ok:
                    cells.append('n/a'); continue
                med = lambda k: statistics.median(float(r[k]) for r in ok)
                cells.append(f"{med('final_equity'):.1f} / {med('cagr_pct'):.1f} / {med('max_drawdown_pct'):.1f} / "
                             f"{statistics.median(int(r['liquidations']) for r in ok):.0f} (n={len(ok)})")
            lines.append(f'| {v} (per coin, median) | ' + ' | '.join(cells) + ' |')
        for name in ('C', 'D top1', 'D top2'):
            cells = []
            for L in (3, 5, 10, 20):
                key = {'C': 'C', 'D top1': 'D1', 'D top2': 'D2'}[name]
                r = next((x for x in cd if x['run'] == key and int(x['cap']) == L and not x['ablation_off']), None)
                cells.append('n/a' if r is None else
                             f"{float(r['final_equity']):.1f} / {float(r['cagr_pct']):.1f} / "
                             f"{float(r['max_drawdown_pct']):.1f} / {r['liquidations']}")
            lines.append(f'| {name} (book) | ' + ' | '.join(cells) + ' |')
        lines += ['', '## D ablation (cap 10, top-2): one rule off at a time', '',
                  '| rule off | final $ | CAGR % | max DD % | liquidations | pre-emptive closes | transfers | switches | funding $ | fees $ | funding $ from |rate|>0.1%/h prints |',
                  '|---|---|---|---|---|---|---|---|---|---|---|']
        full = next((x for x in cd if x['run'] == 'D2' and int(x['cap']) == 10 and not x['ablation_off']), None)
        if full:
            lines.append(f"| none (full D) | {float(full['final_equity']):.1f} | {float(full['cagr_pct']):.1f} | "
                         f"{float(full['max_drawdown_pct']):.1f} | {full['liquidations']} | {full['preemptive_closes']} | "
                         f"{full['transfers']} | {full['switches']} | {float(full['funding_usd']):.1f} | "
                         f"{float(full['fees_usd']):.1f} | {float(full['funding_from_extreme_usd']):.1f} |")
        for r in cd:
            if r['run'] == 'ABL':
                lines.append(f"| rule {r['ablation_off']} | {float(r['final_equity']):.1f} | {float(r['cagr_pct']):.1f} | "
                             f"{float(r['max_drawdown_pct']):.1f} | {r['liquidations']} | {r['preemptive_closes']} | "
                             f"{r['transfers']} | {r['switches']} | {float(r['funding_usd']):.1f} | "
                             f"{float(r['fees_usd']):.1f} | {float(r['funding_from_extreme_usd']):.1f} |")
        lines.append('')
    with open(os.path.join(BASE, 'summary.md'), 'w') as f:
        f.write('\n'.join(lines) + '\n')


def main():
    meta = json.load(open(os.path.join(DATA, 'meta.json')))['coins']
    out, info = [], {}
    for coin, m in meta.items():
        if 'skipped' in m:
            info[coin] = {'skip': m['skipped']}
            continue
        rows = load(coin)
        if len(rows) < MIN_HOURS:
            info[coin] = {'skip': f'<12m overlap ({len(rows)} h)'}
            continue
        info[coin] = {'hours': len(rows), 'start': rows[WARM - 1][0][:10], 'maxlev': m['hl_max_leverage'],
                      'proxied_hl_hours': load.proxied, 'first_hour': rows[0][0][:10]}
        # sanity: annualised funding by venue
        fH = [r[4] for r in rows]; fK = [r[8] for r in rows]
        info[coin]['ann_hl_pct'] = 100 * HPY * sum(fH) / len(fH)
        info[coin]['ann_kr_pct'] = 100 * HPY * sum(fK) / len(fK)
        for v in VARIANTS:
            for L in LEVS:
                base = {'coin': coin, 'L': L, 'variant': v}
                if L > m['hl_max_leverage']:
                    out.append({**base, 'status': f"N/A (max {m['hl_max_leverage']}x)"})
                    continue
                r = simulate(rows, coin, m['hl_max_leverage'], L, v)
                out.append({**base, 'status': 'ok', **r})
    fields = ['coin', 'variant', 'L', 'status', 'start_date', 'final_equity', 'total_return_pct', 'cagr_pct',
              'max_drawdown_pct', 'liquidations', 'funding_usd', 'fees_slippage_usd', 'transfer_usd',
              'flips', 'resizes', 'transfers', 'dead']
    with open(os.path.join(BASE, 'results.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
        w.writeheader()
        for r in out:
            w.writerow({k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()})
    json.dump(info, open(os.path.join(BASE, 'data', 'coin_info.json'), 'w'), indent=1)
    write_summary(out, info)
    # compact print
    for coin, d in info.items():
        if 'skip' in d:
            print(coin, 'SKIP', d['skip'])
        else:
            print(f"{coin:6} start={d['start']} hrs={d['hours']} maxLev={d['maxlev']:>2} proxied={d['proxied_hl_hours']} "
                  f"annFund HL={d['ann_hl_pct']:6.1f}% KR={d['ann_kr_pct']:6.1f}%")


if __name__ == '__main__':
    main()
