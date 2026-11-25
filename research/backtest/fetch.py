#!/usr/bin/env python3
"""Fetch hourly funding and prices for the cross-venue carry backtest (stdlib only).

Writes data/<COIN>.csv (one row per UTC hour in the window, blanks where missing)
and data/meta.json. Hyperliquid kPEPE prices are divided by 1000 so both legs are
quoted per PEPE. Funding is kept as the hourly fraction on both venues.
"""
import csv
import datetime as dt
import json
import os
import ssl
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor

BASE = '/home/user/crevopunch/research/backtest'
DATA = os.path.join(BASE, 'data')
LISTINGS = '/home/user/crevopunch/research/data/listings.csv'
HL_URL = 'https://api.hyperliquid.xyz/info'
KR = 'https://futures.kraken.com/derivatives/api/v3'
KR_CHART = 'https://futures.kraken.com/api/charts/v1/trade'
H = 3600
START_S = int(dt.datetime(2024, 11, 25, tzinfo=dt.timezone.utc).timestamp())
END_S = int(dt.datetime(2026, 11, 25, tzinfo=dt.timezone.utc).timestamp())
USER_COINS = ['BTC', 'ETH', 'SOL', 'XRP', 'DOGE', 'PEPE', 'KAS', 'SUI', 'LINK', 'AVAX']


def _ctx():
    for p in ('/root/.ccr/ca-bundle.crt', os.environ.get('SSL_CERT_FILE', '')):
        if p and os.path.exists(p):
            return ssl.create_default_context(cafile=p)
    return ssl.create_default_context()


CTX = _ctx()


def call(url, payload=None):
    body = None if payload is None else json.dumps(payload).encode()
    last = None
    for attempt in range(6):
        try:
            req = urllib.request.Request(
                url, data=body, method='GET' if body is None else 'POST',
                headers={'Content-Type': 'application/json', 'User-Agent': 'carry-backtest/1.0'})
            with urllib.request.urlopen(req, timeout=60, context=CTX) as r:
                return json.loads(r.read())
        except Exception as e:  # retry transient network / proxy errors
            last = e
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f'{url}: {last}')


def hl_universe():
    meta = call(HL_URL, {'type': 'meta'})
    return {u['name']: u for u in meta['universe'] if not u.get('isDelisted')}


def kr_symbols():
    d = call(f'{KR}/instruments')
    return {i['symbol'] for i in d['instruments']
            if i['symbol'].startswith('PF_') and i['symbol'].endswith('USD') and i.get('tradeable')}


def candidates():
    out = list(USER_COINS)
    with open(LISTINGS) as f:
        for r in csv.DictReader(f):
            if r['Hyperliquid'] == 'Y' and r['Kraken'] == 'Y' and r['coin'] not in out:
                out.append(r['coin'])
    return out


def hl_name(coin, uni):
    if coin in uni:
        return coin, 1.0
    if 'k' + coin in uni:
        return 'k' + coin, 1e-3  # kPEPE is 1000 PEPE; normalise prices to per-unit
    return None, None


def hl_funding(name):
    out, t, t1 = {}, START_S * 1000, END_S * 1000
    while t < t1:
        rows = call(HL_URL, {'type': 'fundingHistory', 'coin': name, 'startTime': t, 'endTime': t1})
        if not rows:
            break
        for r in rows:
            out[int(r['time']) // (H * 1000)] = float(r['fundingRate'])
        last = int(rows[-1]['time'])
        if len(rows) < 500:
            break
        t = last + 1
    return out


def hl_candles(name, mult):
    out, t, t1 = {}, START_S * 1000, END_S * 1000
    while t < t1:
        rows = call(HL_URL, {'type': 'candleSnapshot',
                             'req': {'coin': name, 'interval': '1h', 'startTime': t, 'endTime': t1}})
        if not rows:
            break
        for r in rows:
            out[int(r['t']) // (H * 1000)] = (float(r['c']) * mult, float(r['h']) * mult, float(r['l']) * mult)
        last = int(rows[-1]['t'])
        if len(rows) < 5000:
            break
        t = last + H * 1000
    return out


def kr_funding(sym):
    d = call(f'{KR}/historical-funding-rates?symbol={sym}')
    out = {}
    for r in d['rates']:
        if r.get('relativeFundingRate') is None:
            continue
        ts = int(dt.datetime.fromisoformat(r['timestamp'].replace('Z', '+00:00')).timestamp())
        out[ts // H] = float(r['relativeFundingRate'])
    return out


def kr_candles(sym):
    out, frm = {}, START_S
    while frm < END_S:
        d = call(f'{KR_CHART}/{sym}/1h?from={frm}&to={END_S}')
        cs = d.get('candles') or []
        if not cs:
            break
        for c in cs:
            out[int(c['time']) // (H * 1000)] = (float(c['close']), float(c['high']), float(c['low']))
        last = int(cs[-1]['time']) // 1000
        if last + H >= END_S:
            break
        frm = last + H
    return out


def fetch_one(coin, hn, mult, ks, max_lev):
    hf, hc = hl_funding(hn), hl_candles(hn, mult)
    kf, kc = kr_funding(ks), kr_candles(ks)
    hours = range(START_S // H, END_S // H)
    path = os.path.join(DATA, f'{coin}.csv')
    n_full = 0
    first_full = None
    with open(path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['hour_utc', 'hl_close', 'hl_high', 'hl_low', 'hl_funding',
                    'kr_close', 'kr_high', 'kr_low', 'kr_funding'])
        for hr in hours:
            h = hc.get(hr)
            k = kc.get(hr)
            row = [hr]
            row += list(h) if h else ['', '', '']
            row += [hf.get(hr, '')]
            row += list(k) if k else ['', '', '']
            row += [kf.get(hr, '')]
            if all(x != '' for x in row[1:]):
                n_full += 1
                if first_full is None:
                    first_full = hr
            w.writerow([dt.datetime.fromtimestamp(hr * H, dt.timezone.utc).strftime('%Y-%m-%dT%H:00Z')] + row[1:])
    return coin, {
        'hl_name': hn, 'price_scale': mult, 'hl_max_leverage': max_lev, 'kraken_symbol': ks,
        'complete_hours': n_full,
        'first_complete_utc': (dt.datetime.fromtimestamp(first_full * H, dt.timezone.utc).strftime('%Y-%m-%dT%H:00Z')
                               if first_full is not None else None),
    }


def main():
    os.makedirs(DATA, exist_ok=True)
    uni, krs = hl_universe(), kr_symbols()
    meta, jobs = {}, []
    for c in candidates():
        hn, mult = hl_name(c, uni)
        ks = f'PF_{"XBT" if c == "BTC" else c}USD'
        if hn is None or ks not in krs:
            meta[c] = {'skipped': f'hl={hn} kraken_listed={ks in krs}'}
            continue
        jobs.append((c, hn, mult, ks, uni[hn]['maxLeverage']))
    with ThreadPoolExecutor(4) as ex:
        for coin, m in ex.map(lambda j: fetch_one(*j), jobs):
            meta[coin] = m
    with open(os.path.join(DATA, 'meta.json'), 'w') as f:
        json.dump({'window_start_utc': '2024-11-25T00:00Z', 'window_end_utc': '2026-11-25T00:00Z',
                   'coins': meta}, f, indent=1)
    print(f"{'coin':6}{'hl':8}{'maxLev':>7}{'kr_sym':>12}{'complete_h':>11}  first_complete")
    for c, m in meta.items():
        if 'skipped' in m:
            print(f'{c:6}SKIP {m["skipped"]}')
        else:
            print(f"{c:6}{m['hl_name']:8}{m['hl_max_leverage']:>7}{m['kraken_symbol']:>12}"
                  f"{m['complete_hours']:>11}  {m['first_complete_utc']}")


if __name__ == '__main__':
    main()
