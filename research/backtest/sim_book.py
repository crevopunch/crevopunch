#!/usr/bin/env python3
"""Simulations C and D: multi-venue carry book (stdlib only). See SPEC_D.md.

Book: $200 total equity, a set of K slots (K=1 or 2), each slot a pair of legs (short venue a, long venue b)
on one coin. Free equity is split equally across empty slots. Venues: HL, KR (full window), LT (Lighter),
AS (Aster). Timeline starts at the first Kraken funding hour (2025-11-19 09:00Z) + 7-day warm-up, the same
start as the A/B runs (2025-11-26).

C = B mechanics (60% leg-equity rebalance) + rules 1, 6 (top-1, HL-KR only, with rule 3), 11, 12, 13.
D = all rules on (rule 4 replaces the 60% rebalance with rule 11 transfers only).
Ablation toggles any rule off in D (cap 10, top-2).
"""
import csv
import datetime as dt
import json
import math
import os
import statistics
import sys
import argparse

import slipmodel

BASE = '/home/user/crevopunch/research/backtest'
DATA = os.path.join(BASE, 'data')
H = 3600
WARM = 168
HPY = 8760
START = 200.0            # total equity = 2 x collateral per leg (--capital)
SLIP_MODE = 'flat'     # 'flat' (old model) or 'size' (depth.csv curve, floored at flat)
TRANSFER = 1.0
REBAL = 0.60
ORDER_MIN = 10.0
VENUES = ['HL', 'KR', 'LT', 'AS']
FEE_T = {'HL': 4.5e-4, 'KR': 5e-4, 'LT': 0.0, 'AS': 4e-4}
FEE_M = {'HL': 1.5e-4, 'KR': 2e-4, 'LT': 0.0, 'AS': 0.0}
ADVERSE = 1e-4
RULES_ALL = [1, 2, 3, 4, 5, 6, 8, 9, 11, 12, 13]


def NO_SLIP(N):
    return 0.0


def _f(x):
    return float(x) if x not in ('', None) else None


def _scale_ratio(a, b):
    """Power-of-10 scale that brings venue price a onto the reference b (median ratio)."""
    rs = [x / y for x, y in zip(a, b) if x and y]
    if len(rs) < 100:
        return 1.0
    r = statistics.median(rs)
    e = round(math.log10(r))
    return 10.0 ** e if abs(e) >= 1 else 1.0


def forecast(rates, n):
    """Return (signal_9, mean7) arrays, causal; None where incomplete."""
    pre = [0.0] * (n + 1)
    cnt = [0] * (n + 1)
    for i, r in enumerate(rates):
        pre[i + 1] = pre[i] + (r or 0.0)
        cnt[i + 1] = cnt[i] + (1 if r is not None else 0)
    s9 = [None] * n
    m7 = [None] * n
    for i in range(WARM - 1, n):
        if rates[i] is None or cnt[i + 1] - cnt[i + 1 - WARM] < WARM:
            continue
        m24 = (pre[i + 1] - pre[i + 1 - 24]) / 24
        m168 = (pre[i + 1] - pre[i + 1 - WARM]) / WARM
        s9[i] = 0.5 * m24 + 0.3 * m168 + 0.2 * rates[i]
        m7[i] = m168
    return s9, m7


def load_all():
    meta = json.load(open(os.path.join(DATA, 'meta.json')))['coins']
    coins = [c for c, m in meta.items() if 'skipped' not in m]
    btc = list(csv.DictReader(open(os.path.join(DATA, 'BTC.csv'))))
    t0 = next(i for i, r in enumerate(btc) if r['kr_funding'] != '')
    hours = [r['hour_utc'] for r in btc[t0:]]
    n = len(hours)
    D = {'hours': hours, 'n': n, 'coins': {}, 'maxlev': {}}
    for c in coins:
        base = list(csv.DictReader(open(os.path.join(DATA, f'{c}.csv'))))[t0:]
        ext = list(csv.DictReader(open(os.path.join(DATA, f'{c}_ext.csv'))))[t0:]
        assert [r['hour_utc'] for r in base] == hours
        D['maxlev'][c] = meta[c]['hl_max_leverage']
        kr_c = [_f(r['kr_close']) for r in base]
        kr_h = [_f(r['kr_high']) for r in base]
        kr_l = [_f(r['kr_low']) for r in base]
        hl_c = [_f(r['hl_close']) for r in base]
        hl_h = [_f(r['hl_high']) for r in base]
        hl_l = [_f(r['hl_low']) for r in base]
        # Hyperliquid price proxied by Kraken where HL candles do not exist (pre 2026-04-30)
        hlc = [h if h is not None else k for h, k in zip(hl_c, kr_c)]
        hlh = [h if h is not None else k for h, k in zip(hl_h, kr_h)]
        hll = [h if h is not None else k for h, k in zip(hl_l, kr_l)]
        V = {}
        hl_rate = [_f(r['hl_funding']) for r in base]
        kr_rate = [_f(r['kr_funding']) for r in base]
        V['HL'] = {'rate': hl_rate, 'pay': [1] * n, 'hrate': hl_rate, 'c': hlc, 'h': hlh, 'l': hll}
        V['KR'] = {'rate': kr_rate, 'pay': [1] * n, 'hrate': kr_rate, 'c': kr_c, 'h': kr_h, 'l': kr_l}
        # Lighter: hourly funding, candles only for selected coins
        lt_rate = [_f(r['lt_rate']) for r in ext]
        lt_c = [_f(r['lt_close']) for r in ext]
        if any(x is not None for x in lt_c):
            s = _scale_ratio(lt_c, kr_c)
            lt_c = [None if x is None else x / s for x in lt_c]
            lt_h = [None if x is None else _f(r['lt_high']) / s for x, r in zip(lt_c, ext)]
            lt_l = [None if x is None else _f(r['lt_low']) / s for x, r in zip(lt_c, ext)]
            V['LT'] = {'rate': lt_rate, 'pay': [1] * n, 'hrate': lt_rate, 'c': lt_c, 'h': lt_h, 'l': lt_l}
        # Aster: 8h rate applied only at its funding hours; hourly-equivalent carried for the signal
        as_raw = [_f(r['as_rate']) for r in ext]
        as_c = [_f(r['as_close']) for r in ext]
        if any(x is not None for x in as_c) or any(x is not None for x in as_raw):
            as_h, last = [], None
            for x in as_raw:
                if x is not None:
                    last = x / 8
                as_h.append(last)
            if any(x is not None for x in as_c):
                s = _scale_ratio(as_c, kr_c)
                as_c = [None if x is None else x / s for x in as_c]
                as_hh = [None if x is None else _f(r['as_high']) / s for x, r in zip(as_c, ext)]
                as_ll = [None if x is None else _f(r['as_low']) / s for x, r in zip(as_c, ext)]
                V['AS'] = {'rate': as_raw, 'pay': [1 if x is not None else 0 for x in as_raw],
                           'hrate': as_h, 'c': as_c, 'h': as_hh, 'l': as_ll}
        # causal signals; a venue's signal is usable only with a full 168h history
        for v, d in V.items():
            d['s9'], d['m7'] = forecast(d['hrate'], n)
        # reference price for volatility: HL (proxied) close
        ref = hlc
        rv = [None] * n
        rets = [None] + [math.log(ref[i] / ref[i - 1]) if ref[i] and ref[i - 1] else None for i in range(1, n)]
        for i in range(25, n):
            w = rets[i - 23:i + 1]
            if any(x is None for x in w):
                continue
            rv[i] = statistics.pstdev(w) * math.sqrt(HPY)
        tv = [None] * n
        for i in range(0, n, 6):
            w = [x for x in rv[max(0, i - 719):i + 1] if x is not None]
            if len(w) >= 24 * 7:
                tv[i] = statistics.median(w)
        D['coins'][c] = {'V': V, 'rv': rv, 'tv': tv}
    return D


def liq_leg(leg, hi, lo, mmr):
    q = leg['q']
    if q == 0:
        return False
    w = lo if q > 0 else hi
    return leg['cash'] + q * (w - leg['e']) < mmr * abs(q) * w


def eqleg(leg, p):
    return leg['cash'] + leg['q'] * (p - leg['e'])


def set_units(leg, qnew, p, fee, sl, acc):
    """Move leg to signed units qnew at price p; fee and slip(notional) charged on traded notional."""
    q, e = leg['q'], leg['e']
    dq = qnew - q
    if dq == 0:
        return
    N = abs(dq) * p
    cf = N * fee
    cs = N * sl(N)
    leg['cash'] -= cf + cs
    acc['fees'] += cf
    acc['slip'] += cs
    if q != 0 and qnew * q >= 0 and abs(qnew) <= abs(q):
        leg['cash'] += (q - qnew) * (p - e)
        leg['q'] = qnew
        if qnew == 0:
            leg['e'] = 0.0
    elif q != 0 and qnew * q < 0:
        leg['cash'] += q * (p - e)
        leg['q'], leg['e'] = qnew, p
    else:
        leg['e'] = p if q == 0 else (q * e + dq * p) / qnew
        leg['q'] = qnew


def run(D, cfg):
    n = D['n']
    R = {r: (1 if r in cfg['rules'] else 0) for r in RULES_ALL}
    cap, K = cfg['cap'], cfg['topk']
    allowed = cfg['venues']
    REF = 0.95 if R[5] else 1.0
    start = WARM - 1
    free = START
    acc = {'fees': 0.0, 'slip': 0.0, 'fund': 0.0, 'xfer': 0.0, 'xfers': 0, 'liq': 0, 'pre': 0, 'switch': 0, 'fund_ext': 0.0}
    active, closing, pend = [], [], []
    pnl_pair = {}
    st = {'newlist': 0.0}
    series = [START]
    first_seen = {}
    for c, d in D['coins'].items():
        for v, vd in d['V'].items():
            first_seen[(c, v)] = next((i for i, x in enumerate(vd['hrate']) if x is not None), None)

    def fees(v, c, maker):
        if maker:
            return FEE_M[v] * REF, NO_SLIP
        return FEE_T[v] * REF, slipmodel.rate_fn(c, slipmodel.VENUE_NAME[v], SLIP_MODE)

    def V(coin, v):
        return D['coins'][coin]['V'][v]

    def mark(pos, i):
        return sum(eqleg(l, V(pos['coin'], l['v'])['c'][i]) for l in pos['legs'])

    def finalize(pos):
        cash = sum(l['cash'] for l in pos['legs'])
        free_add[0] += cash
        pnl = cash - pos['alloc']
        pair = f"{pos['s']}short/{pos['l']}long"
        pnl_pair[pair] = pnl_pair.get(pair, 0.0) + pnl
        if pos['newlist']:
            st['newlist'] += pnl
        pos['done'] = True

    free_add = [0.0]

    def close_pos(pos, i, force_taker=False):
        """Close both legs. The maker leg closes next hour under rule 1; a taker close is immediate."""
        pos['closing'] = True
        if pos in active:
            active.remove(pos)
        closing.append(pos)
        for leg in pos['legs']:
            if leg['q'] == 0:
                continue
            p = V(pos['coin'], leg['v'])['c'][i]
            if R[1] and not force_taker and leg['v'] == pos['maker']:
                leg['pend_close'] = i + 1
            else:
                f, sl = fees(leg['v'], pos['coin'], False)
                set_units(leg, 0.0, p, f, sl, acc)
        if all(l['q'] == 0 and l['pend_close'] is None for l in pos['legs']):
            closing.remove(pos)
            finalize(pos)

    def open_pos(coin, s, l, i, rotate):
        nonlocal free
        empty = max(1, K - len(active))
        alloc = free / empty
        if alloc < 2 * ORDER_MIN:
            return False
        if rotate:
            acc['xfer'] += TRANSFER; acc['xfers'] += 1
            alloc = (free - TRANSFER) / empty
        mx = D['maxlev'][coin]
        lev = min(cap, mx) if not R[12] else lev_rule12(D, coin, i, cap, mx)
        N = (alloc / 2) * lev
        free -= alloc
        legs = [{'v': v, 'cash': alloc / 2, 'q': 0.0, 'e': 0.0, 'pend': None, 'pend_close': None} for v in (s, l)]
        maker = max((s, l), key=lambda v: FEE_T[v]) if R[1] else None
        newlist = any((first_seen.get((coin, v)) or 0) > start and i - (first_seen.get((coin, v)) or 0) <= 30 * 24
                      for v in (s, l))
        pos = {'coin': coin, 's': s, 'l': l, 'legs': legs, 'alloc': alloc, 'lev': lev, 'N': N, 'open_i': i,
               'maker': maker, 'xfer': None, 'closing': False, 'done': False, 'last_adj': i, 'newlist': newlist}
        active.append(pos)
        for leg in legs:
            p = V(coin, leg['v'])['c'][i]
            sign = -1 if leg['v'] == s else 1
            if maker == leg['v']:
                leg['pend'] = (i + 1, sign)   # maker fill one hour later
                continue
            f, sl = fees(leg['v'], coin, False)
            set_units(leg, sign * N / p, p, f, sl, acc)
        return True

    def cands_for(i):
        out = []
        for coin in D['coins']:
            av = []
            for v in allowed:
                if v not in D['coins'][coin]['V']:
                    continue
                vd = V(coin, v)
                if vd['c'][i] is None:
                    continue
                s9 = vd['s9'][i] if R[9] else vd['m7'][i]
                if s9 is None:
                    continue
                av.append((v, s9))
            if len(av) < 2:
                continue
            pairs = []
            for a, sa in av:
                for b, sb in av:
                    if a == b or (cfg.get('hl_kr_only') and {a, b} != {'HL', 'KR'}):
                        continue
                    gain = WARM * (sa - sb)
                    Nl = (free / max(1, K - len(active)) / 2) * min(cap, D['maxlev'][coin])  # forecast leg notional
                    fc = 2 * sum(f + sl(Nl) for f, sl in (fees(v, coin, False) for v in (a, b)))
                    fc += TRANSFER / max(20.0, (free + sum(mark(p, i) for p in active)) / K)
                    pairs.append({'coin': coin, 's': a, 'l': b, 'gain': gain, 'cost': fc, 'net': gain - fc,
                                  'lt': 'LT' in (a, b)})
            if not pairs:
                continue
            best = max(pairs, key=lambda x: x['net'])
            if R[2]:
                lts = [x for x in pairs if x['lt']]
                if lts:
                    lb = max(lts, key=lambda x: x['net'])
                    if lb['gain'] >= best['gain'] - WARM * 0.05 / HPY:
                        best = lb
            out.append(best)
        out.sort(key=lambda x: -x['net'])
        return out

    def cur_gain(p, i):
        a, b = V(p['coin'], p['s']), V(p['coin'], p['l'])
        sa = a['s9'][i] if R[9] else a['m7'][i]
        sb = b['s9'][i] if R[9] else b['m7'][i]
        return WARM * (sa - sb) if sa is not None and sb is not None else -1.0

    for i in range(start, n):
        # (0) maker-leg fills and maker-leg closes due this hour
        for pos in list(active) + list(closing):
            for leg in pos['legs']:
                if leg['pend'] and leg['pend'][0] == i:
                    p = V(pos['coin'], leg['v'])['c'][i]
                    if p:
                        f, _ = fees(leg['v'], pos['coin'], True)
                        set_units(leg, leg['pend'][1] * pos['N'] / p, p, f + ADVERSE, NO_SLIP, acc)
                    leg['pend'] = None
                if leg['pend_close'] == i:
                    p = V(pos['coin'], leg['v'])['c'][i]
                    f, _ = fees(leg['v'], pos['coin'], True)
                    set_units(leg, 0.0, p, f + ADVERSE, NO_SLIP, acc)
                    leg['pend_close'] = None
        for pos in list(closing):
            if all(l['q'] == 0 and l['pend_close'] is None for l in pos['legs']):
                closing.remove(pos)
                finalize(pos)

        # (1) scheduled collateral transfers (1h delay, $1 each, within the position)
        for pos in active:
            if pos['xfer'] == i:
                pos['xfer'] = None
                pr = {l['v']: V(pos['coin'], l['v'])['c'][i] for l in pos['legs']}
                if all(pr.values()):
                    tot = sum(eqleg(l, pr[l['v']]) for l in pos['legs'])
                    tgt = (tot - TRANSFER) / 2
                    for l in pos['legs']:
                        l['cash'] = tgt - l['q'] * (pr[l['v']] - l['e'])
                    acc['xfer'] += TRANSFER; acc['xfers'] += 1

        # (2) real liquidations on the hour's high/low; other leg closed at the close as taker
        for pos in list(active):
            hit = []
            for leg in pos['legs']:
                d = V(pos['coin'], leg['v'])
                if d['h'][i] is None or leg['q'] == 0:
                    continue
                if liq_leg(leg, d['h'][i], d['l'][i], 1.0 / (2 * D['maxlev'][pos['coin']])):
                    hit.append(leg)
            if hit:
                acc['liq'] += len(hit)
                for leg in hit:
                    leg['cash'], leg['q'], leg['e'] = 0.0, 0.0, 0.0
                    leg['pend'] = None
                pos['legs'] = [l for l in pos['legs'] if l not in hit] + hit
                active.remove(pos)
                closing.append(pos)
                for leg in pos['legs']:
                    if leg not in hit and leg['q'] != 0:
                        f, sl = fees(leg['v'], pos['coin'], False)
                        set_units(leg, 0.0, V(pos['coin'], leg['v'])['c'][i], f, sl, acc)
                    leg['pend_close'] = None
                closing.remove(pos)
                finalize(pos)

        # (3) funding at close: a long pays rate x notional, a short receives; 8h venues pay only at payout hours
        for pos in active + closing:
            for leg in pos['legs']:
                d = V(pos['coin'], leg['v'])
                r = d['rate'][i]
                if leg['q'] != 0 and r is not None and d['pay'][i] and d['c'][i]:
                    cf = -leg['q'] * d['c'][i] * r
                    leg['cash'] += cf
                    acc['fund'] += cf
                    if abs(r) > 0.001:
                        acc['fund_ext'] += cf

        # (4) margin usage: pre-emptive close (rule 11) and the 60% leg-equity rebalance (rule 4 off)
        for pos in list(active):
            usage, eqs = [], {}
            for leg in pos['legs']:
                p = V(pos['coin'], leg['v'])['c'][i]
                if p is None:
                    continue
                eqL = eqleg(leg, p)
                eqs[leg['v']] = eqL
                if leg['q'] != 0:
                    mm = abs(leg['q']) * p / (2 * D['maxlev'][pos['coin']])
                    usage.append(mm / eqL if eqL > 0 else 9.0)
            if not usage:
                continue
            # 90% usage after any transfer that landed this hour (it did not fix the margin): close as taker
            if R[11] and max(usage) >= 0.90:
                close_pos(pos, i, force_taker=True)
                acc['pre'] += 1
                continue
            if R[11] and max(usage) >= 0.75 and pos['xfer'] is None:
                pos['xfer'] = i + 1
            if not R[4] and pos['xfer'] is None and len(eqs) == 2:
                if min(eqs.values()) < REBAL * max(eqs.values()):
                    pos['xfer'] = i + 1

        # (5) leverage re-evaluation every 6h (rule 12, adjust if >20%) and compounding (rule 13)
        for pos in list(active):
            due = (R[12] and i % 6 == 0 and i - pos['last_adj'] >= 6) or \
                  (not R[12] and R[13] and D['hours'][i][:7] != D['hours'][i - 1][:7])
            if not due:
                continue
            pos['last_adj'] = i
            new_lev = lev_rule12(D, pos['coin'], i, cap, D['maxlev'][pos['coin']]) if R[12] else pos['lev']
            if R[12] and abs(new_lev / pos['lev'] - 1) <= 0.20:
                continue
            if R[13]:
                base_eq = sum(eqleg(l, V(pos['coin'], l['v'])['c'][i] or 0.0) for l in pos['legs'])
            else:
                base_eq = pos['alloc']
            pos['lev'] = new_lev
            pos['N'] = base_eq / 2 * new_lev
            for leg in pos['legs']:
                p = V(pos['coin'], leg['v'])['c'][i]
                if p is None or leg['q'] == 0:
                    continue
                sign = -1 if leg['v'] == pos['s'] else 1
                f, sl = fees(leg['v'], pos['coin'], False)
                set_units(leg, sign * pos['N'] / p, p, f, sl, acc)

        # (6) pending entries (rule 8: enter at the first hour where the short venue price >= long venue price,
        #     else at the 6h deadline)
        still = []
        for pe in pend:
            ps = V(pe['coin'], pe['s'])['c'][i]
            pl = V(pe['coin'], pe['l'])['c'][i]
            if ps is None or pl is None:
                still.append(pe)
                continue
            if pe.get('rot'):
                if len(active) < K and open_pos(pe['coin'], pe['s'], pe['l'], i, rotate=True):
                    acc['switch'] += 1
                else:
                    still.append(pe)
                continue
            if (ps - pl) >= 0 or i >= pe['deadline']:
                if len(active) < K and not any(p['coin'] == pe['coin'] for p in active):
                    open_pos(pe['coin'], pe['s'], pe['l'], i, rotate=False)
            else:
                still.append(pe)
        pend[:] = still

        # (7) scanner: fill empty slots with the best net-positive candidates; rule 6 rotation with rule 3 switch test
        cands = cands_for(i)
        held = {p['coin'] for p in active} | {pe['coin'] for pe in pend}
        for cd in cands:
            if len(active) + len(pend) >= K:
                break
            if cd['coin'] in held or cd['net'] <= 0:
                continue
            if R[8]:
                pend.append({'coin': cd['coin'], 's': cd['s'], 'l': cd['l'], 'deadline': i + 6})
            else:
                open_pos(cd['coin'], cd['s'], cd['l'], i, rotate=False)
            held.add(cd['coin'])
        if R[6] and cands and len(active) >= K and not pend and i > start and not closing:
            weakest = min(active, key=lambda p: cur_gain(p, i))
            held = {p['coin'] for p in active}
            best = next((c for c in cands if c['coin'] not in held and c['net'] > 0), None)
            if best is not None:
                mult = 2.0 if R[3] else 0.0
                if best['gain'] - cur_gain(weakest, i) > mult * best['cost']:
                    close_pos(weakest, i)
                    # the new position opens once the old one's cash is free (maker exit can take an hour)
                    pend.append({'coin': best['coin'], 's': best['s'], 'l': best['l'], 'deadline': i,
                                 'rot': True})
        free += free_add[0]
        free_add[0] = 0.0

        # (8) mark to market
        series.append(free + sum(mark(p, i) for p in active + closing))

    # exit: close every open position at the final close, all taker
    i = n - 1
    for pos in list(active):
        close_pos(pos, i, force_taker=True)
    for pos in list(closing):
        for leg in pos['legs']:
            if leg['q'] != 0:
                f, sl = fees(leg['v'], pos['coin'], False)
                set_units(leg, 0.0, V(pos['coin'], leg['v'])['c'][i], f, sl, acc)
            leg['pend_close'] = None
        closing.remove(pos)
        finalize(pos)
    free += free_add[0]
    final = free
    series[-1] = final
    peak, mdd = series[0], 0.0
    for v in series:
        peak = max(peak, v)
        if peak > 0:
            mdd = min(mdd, v / peak - 1)
    years = (n - start) / HPY
    cagr = (final / START) ** (1 / years) - 1 if final > 0 else -1.0
    return {
        'final_equity': final, 'total_return_pct': 100 * (final / START - 1), 'cagr_pct': 100 * cagr,
        'max_drawdown_pct': 100 * mdd, 'liquidations': acc['liq'], 'preemptive_closes': acc['pre'],
        'funding_usd': acc['fund'], 'fees_usd': acc['fees'], 'slippage_usd': acc['slip'],
        'transfer_usd': acc['xfer'], 'transfers': acc['xfers'], 'switches': acc['switch'],
        'newlisting_pnl_usd': st['newlist'], 'pnl_by_pair': pnl_pair, 'start_date': D['hours'][start][:10],
        'funding_from_extreme_usd': acc['fund_ext'],
        'years': years,
    }


def lev_rule12(D, coin, i, cap, mx):
    d = D['coins'][coin]
    rv, tv = d['rv'][i], d['tv'][i - (i % 6)]
    if rv is None or tv is None or rv <= 0:
        return min(cap, mx)
    return max(1.0, min(cap * tv / rv, min(cap, mx)))


CONFIGS = {
    'C_top1_cap': lambda cap: dict(name=f'C cap{cap}', cap=cap, topk=1, venues=['HL', 'KR'], hl_kr_only=True,
                                   rules={1, 3, 6, 11, 12, 13}),
    'D_top1_cap': lambda cap: dict(name=f'D top1 cap{cap}', cap=cap, topk=1, venues=VENUES,
                                   rules=set(RULES_ALL)),
    'D_top2_cap': lambda cap: dict(name=f'D top2 cap{cap}', cap=cap, topk=2, venues=VENUES,
                                   rules=set(RULES_ALL)),
}


def main():
    global START, SLIP_MODE
    ap = argparse.ArgumentParser()
    ap.add_argument('--capital', type=float, default=100.0, help='collateral per leg, USD')
    ap.add_argument('--slip', choices=['flat', 'size'], default='flat')
    ap.add_argument('--out', help='output CSV (default results_CD.csv)')
    a = ap.parse_args()
    START = 2 * a.capital; SLIP_MODE = a.slip
    D = load_all()
    print('hours', D['n'], D['hours'][0], D['hours'][-1], 'coins', len(D['coins']), flush=True)
    rows = []
    specs = []
    for cap in (3, 5, 10, 20):
        specs.append(('C', cap, None, CONFIGS['C_top1_cap'](cap)))
        specs.append(('D1', cap, None, CONFIGS['D_top1_cap'](cap)))
        specs.append(('D2', cap, None, CONFIGS['D_top2_cap'](cap)))
    for r in RULES_ALL:
        cfg = CONFIGS['D_top2_cap'](10)
        cfg['rules'] = set(RULES_ALL) - {r}
        cfg['name'] = f'D top2 cap10 no{r}'
        specs.append(('ABL', 10, r, cfg))
    for tag, cap, off, cfg in specs:
        res = run(D, cfg)
        res.update({'run': tag, 'cap': cap, 'ablation_off': off if off else '', 'name': cfg['name']})
        pairs = res.pop('pnl_by_pair')
        res['pnl_by_pair'] = ';'.join(f'{k}={v:.2f}' for k, v in sorted(pairs.items(), key=lambda x: -x[1])[:6])
        rows.append(res)
        print(f"{cfg['name']:22} final={res['final_equity']:8.2f} liq={res['liquidations']:3} pre={res['preemptive_closes']:3} "
              f"xfers={res['transfers']:3} switches={res['switches']:3} fund={res['funding_usd']:7.2f} "
              f"fees={res['fees_usd']:6.2f} cagr={res['cagr_pct']:7.1f}", flush=True)
    fields = ['run', 'name', 'cap', 'ablation_off', 'start_date', 'final_equity', 'total_return_pct', 'cagr_pct',
              'max_drawdown_pct', 'liquidations', 'preemptive_closes', 'funding_usd', 'fees_usd', 'slippage_usd',
              'transfer_usd', 'transfers', 'switches', 'newlisting_pnl_usd', 'funding_from_extreme_usd', 'pnl_by_pair']
    with open(a.out or os.path.join(BASE, 'results_CD.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
        w.writeheader()
        for r in rows:
            w.writerow({k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()})
    print('wrote', a.out or 'results_CD.csv')


if __name__ == '__main__':
    main()
