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
    rows = []
    with open(os.path.join(DATA, f'{coin}.csv')) as f:
        for r in csv.DictReader(f):
            try:
                v = [float(r[k]) for k in ('hl_close', 'hl_high', 'hl_low', 'hl_funding',
                                           'kr_close', 'kr_high', 'kr_low', 'kr_funding')]
            except ValueError:
                continue  # incomplete hour: dropped (counted in main)
            rows.append((r['hour_utc'], *v))
    return rows


def liquidated(leg, hi, lo, mmr):
    q = leg['q']
    if q == 0:
        return False
    w = lo if q > 0 else hi  # worst price within the hour
    return leg['cash'] + q * (w - leg['e']) < mmr * abs(q) * w


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
            tot = H['cash'] + K['cash']
            H['cash'] = K['cash'] = (tot - TRANSFER) / 2
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
            N = min(H['cash'], K['cash']) * L
            sH = -N / pH if short == 'H' else N / pH
            sK = -N / pK if short == 'K' else N / pK
            trade(H, sH, pH, rate['H'], acc)
            trade(K, sK, pK, rate['K'], acc)
            acc['resizes'] += 1
        # (g) variant B: schedule transfer when a leg falls below 60% of the other
        if variant == 'B' and in_pos and pend_xfer is None:
            lo, hi = min(H['cash'], K['cash']), max(H['cash'], K['cash'])
            if lo < REBAL * hi:
                pend_xfer = i + 1
        # (h) mark to market at this venue's close
        series.append(H['cash'] + K['cash'] + H['q'] * (pH - H['e']) + K['q'] * (pK - K['e']))

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
        'funding_usd': acc['fund'], 'fees_slippage_usd': acc['fees'], 'transfer_usd': acc['xfer'],
        'flips': acc['flips'], 'resizes': acc['resizes'], 'transfers': acc['xfers'],
        'dead': dead, 'years': years,
    }


def main():
    meta = json.load(open(os.path.join(DATA, 'meta.json')))['coins']
    out, info = [], {}
    for coin, m in meta.items():
        if 'skipped' in m:
            info[coin] = {'skip': m['skipped']}
            continue
        rows = load(coin)
        dropped = m['complete_hours'] and (sum(1 for _ in open(os.path.join(DATA, f'{coin}.csv'))) - 1 - len(rows))
        if len(rows) < MIN_HOURS:
            info[coin] = {'skip': f'<12m overlap ({len(rows)} h)'}
            continue
        info[coin] = {'hours': len(rows), 'start': rows[WARM - 1][0][:10], 'maxlev': m['hl_max_leverage'],
                      'dropped_incomplete': dropped}
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
    # compact print
    for coin, d in info.items():
        if 'skip' in d:
            print(coin, 'SKIP', d['skip'])
        else:
            print(f"{coin:5} start={d['start']} hrs={d['hours']} maxLev={d['maxlev']} "
                  f"annFund HL={d['ann_hl_pct']:.1f}% KR={d['ann_kr_pct']:.1f}% dropped={d['dropped_incomplete']}")


if __name__ == '__main__':
    main()
