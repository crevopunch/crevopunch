#!/usr/bin/env python3
"""Lighter + Aster history for simulations C and D (stdlib only). Two passes:

Pass 1 (funding): Lighter and Aster funding for the 71-coin universe (coins with HL and Kraken data),
  written to data/<COIN>_ext.csv together with the HL/Kraken columns needed for the funding-only ranking.
Selection: a funding-only ranking (same 24h/7d/latest forecast as sim) picks the coins that are ever in
  the top 10 by forecast edge; only those coins get candles in pass 2.
Pass 2 (candles): Lighter /candles and Aster /klines for selected coins only.

Lighter fundings: percent units per hour, sign from `direction` (long = positive = longs pay), converted to
fraction. Lighter returns <=749 rows per call, so the window is paged. Aster fundingRate is per 8h and is
applied only at its fundingTime hours (UTC 00/08/16).
"""
import csv
import datetime as dt
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor

BASE = '/home/user/crevopunch/research/backtest'
sys.path.insert(0, BASE)
import fetch as F  # reuse call(), START_S, END_S, DATA  # noqa: E402

LT = 'https://mainnet.zklighter.elliot.ai/api/v1'
AS = 'https://fapi.asterdex.com/fapi/v1'
DATA = F.DATA
H = 3600
S0, S1 = F.START_S // H, F.END_S // H
WARM = 168
TOPN = 10
N_HOURS = S1 - S0


def lighter_markets():
    d = F.call(f'{LT}/orderBooks')['order_books']
    return {m['symbol']: m['market_id'] for m in d if m.get('market_type') == 'perp' and m.get('status') == 'active'}


def aster_symbols():
    d = F.call(f'{AS}/exchangeInfo')['symbols']
    return {s['baseAsset']: s['symbol'] for s in d
            if s.get('quoteAsset') == 'USDT' and s.get('status') == 'TRADING'}


def lt_funding(mid):
    out, t0 = {}, S0 * H
    while t0 < S1 * H:
        t1 = min(t0 + 700 * H, S1 * H)
        d = F.call(f'{LT}/fundings?market_id={mid}&resolution=1h&start_timestamp={t0}'
                   f'&end_timestamp={t1}&count_back=700')
        rows = d.get('fundings') or []
        for x in rows:
            sign = 1 if x.get('direction') == 'long' else -1
            out[int(x['timestamp']) // H] = float(x['rate']) / 100 * sign
        t0 = t1
    return out


def as_funding(sym):
    out, t = {}, F.START_S * 1000
    while True:
        rows = F.call(f'{AS}/fundingRate?symbol={sym}&startTime={t}&limit=1000')
        if not rows:
            break
        for x in rows:
            out[int(x['fundingTime']) // (H * 1000)] = float(x['fundingRate'])
        last = int(rows[-1]['fundingTime'])
        if len(rows) < 1000 or last >= F.END_S * 1000:
            break
        t = last + 1
    return out


def lt_candles(mid):
    out, t0 = {}, S0 * H
    while t0 < S1 * H:
        t1 = min(t0 + 500 * H, S1 * H)
        d = F.call(f'{LT}/candles?market_id={mid}&resolution=1h&start_timestamp={t0}'
                   f'&end_timestamp={t1}&count_back=500')
        for c in d.get('c') or []:
            out[int(c['t']) // (H * 1000)] = (float(c['c']), float(c['h']), float(c['l']))
        t0 = t1
    return out


def as_candles(sym):
    out, t = {}, F.START_S * 1000
    while t < F.END_S * 1000:
        rows = F.call(f'{AS}/klines?symbol={sym}&interval=1h&startTime={t}&limit=1000')
        if not rows:
            break
        for r in rows:
            out[int(r[0]) // (H * 1000)] = (float(r[4]), float(r[2]), float(r[3]))
        last = int(rows[-1][0])
        if len(rows) < 1000 or last >= F.END_S * 1000:
            break
        t = last + H * 1000
    return out


def read_base(coin):
    """Load existing HL/Kraken columns: hour -> (hl_f, kr_f)."""
    rows = {}
    with open(os.path.join(DATA, f'{coin}.csv')) as f:
        for r in csv.DictReader(f):
            hr = int(F.dt.datetime.strptime(r['hour_utc'], '%Y-%m-%dT%H:%MZ').replace(
                tzinfo=F.dt.timezone.utc).timestamp()) // H
            rows[hr] = (float(r['hl_funding']) if r['hl_funding'] else None,
                        float(r['kr_funding']) if r['kr_funding'] else None)
    return rows


def forecast_series(rates):
    """rates: list (len N_HOURS) of hourly-equivalent rate or None. Return signal list or None where
    the 168h history is incomplete. Signal = 0.5*mean24 + 0.3*mean168 + 0.2*latest (hourly fraction)."""
    n = len(rates)
    pre = [0.0] * (n + 1)
    cnt = [0] * (n + 1)
    for i, r in enumerate(rates):
        pre[i + 1] = pre[i] + (r or 0.0)
        cnt[i + 1] = cnt[i] + (1 if r is not None else 0)
    sig = [None] * n
    for i in range(WARM - 1, n):
        if rates[i] is None or cnt[i + 1] - cnt[i + 1 - WARM] < WARM:
            continue
        m24 = (pre[i + 1] - pre[i + 1 - 24]) / 24
        m168 = (pre[i + 1] - pre[i + 1 - WARM]) / WARM
        sig[i] = 0.5 * m24 + 0.3 * m168 + 0.2 * rates[i]
    return sig


def funding_ranking(coins_data):
    """coins_data: {coin: {venue: [hourly-equivalent rate or None]*N}}. Returns set of coins ever top-N."""
    ever = set()
    sigs = {c: {v: forecast_series(r) for v, r in vs.items()} for c, vs in coins_data.items()}
    for i in range(N_HOURS):
        edges = []
        for c, vs in sigs.items():
            vals = {v: s[i] for v, s in vs.items() if s[i] is not None}
            if len(vals) < 2:
                continue
            hi, lo = max(vals.values()), min(vals.values())
            edges.append((hi - lo, c))
        edges.sort(reverse=True)
        for _, c in edges[:TOPN]:
            ever.add(c)
    return ever


def pass1(coin, mid, asym):
    lt = lt_funding(mid) if mid is not None else {}
    au = as_funding(asym) if asym is not None else {}
    base = read_base(coin)
    path = os.path.join(DATA, f'{coin}_ext.csv')
    with open(path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['hour_utc', 'lt_rate', 'as_rate', 'lt_close', 'lt_high', 'lt_low',
                    'as_close', 'as_high', 'as_low'])
        for hr in range(S0, S1):
            w.writerow([dt.datetime.fromtimestamp(hr * H, dt.timezone.utc).strftime('%Y-%m-%dT%H:00Z'),
                        repr(lt[hr]) if hr in lt else '', repr(au[hr]) if hr in au else '', '', '', '', '', '', ''])
    return coin, {'lt_hours': len(lt), 'as_payouts': len(au), 'lt_symbol': mid, 'as_symbol': asym}


def pass2(coin, mid, asym):
    path = os.path.join(DATA, f'{coin}_ext.csv')
    with open(path) as f:
        rows = list(csv.reader(f))
    lc = lt_candles(mid) if mid is not None else {}
    ac = as_candles(asym) if asym is not None else {}
    for row in rows[1:]:
        hr = int(F.dt.datetime.strptime(row[0], '%Y-%m-%dT%H:%MZ').replace(
            tzinfo=F.dt.timezone.utc).timestamp()) // H
        for k, src in ((3, lc), (6, ac)):
            c = src.get(hr)
            row[k:k + 3] = [repr(x) for x in c] if c else ['', '', '']
    with open(path, 'w', newline='') as f:
        csv.writer(f).writerows(rows)
    return coin, {'lt_candles': len(lc), 'as_candles': len(ac)}


def main():
    meta = json.load(open(os.path.join(DATA, 'meta.json')))['coins']
    coins = [c for c, m in meta.items() if 'skipped' not in m]
    lm, am = lighter_markets(), aster_symbols()
    lt_map = {c: lm.get(c) for c in coins}
    as_map = {c: am.get(c) for c in coins}
    with ThreadPoolExecutor(6) as ex:
        p1 = list(ex.map(lambda c: pass1(c, lt_map[c], as_map[c]), coins))
    print('pass1 done', len(p1), flush=True)
    # funding-only ranking over the universe (HL, Kraken, Lighter, Aster) to pick coins for candles
    data = {}
    for c in coins:
        base = read_base(c)
        ext = {}
        with open(os.path.join(DATA, f'{c}_ext.csv')) as f:
            r = list(csv.DictReader(f))
        hl = [base.get(h, (None, None))[0] for h in range(S0, S1)]
        kr = [base.get(h, (None, None))[1] for h in range(S0, S1)]
        lt = [float(x['lt_rate']) if x['lt_rate'] else None for x in r]
        au = [float(x['as_rate']) / 8 if x['as_rate'] else None for x in r]
        # hourly-equivalent with Aster funding as its 8h rate divided by 8, carried flat between payouts
        au_h = []
        last = None
        for x in au:
            if x is not None:
                last = x
            au_h.append(last)
        data[c] = {'HL': hl, 'KR': kr, 'LT': lt, 'AS': au_h}
    selected = sorted(funding_ranking(data))
    print('selected for candles:', len(selected), selected, flush=True)
    with ThreadPoolExecutor(6) as ex:
        p2 = list(ex.map(lambda c: pass2(c, lt_map[c], as_map[c]), selected))
    with open(os.path.join(DATA, 'meta_ext.json'), 'w') as f:
        json.dump({'pass1': dict(p1), 'selected': selected, 'pass2': dict(p2),
                   'lighter_map': lt_map, 'aster_map': as_map}, f, indent=1)
    print('pass2 done', len(p2), flush=True)


if __name__ == '__main__':
    main()
