#!/usr/bin/env python3
"""Live public perp data collector for a cross-venue arbitrage study (stdlib only).

Modes:
  universe  CoinGecko top-200 -> data/listings.csv, data/universe.json
  funding   current rate + 7d history per coin x venue -> data/funding.csv
  sample    30 samples x 60 s top-of-book -> data/samples.csv
            plus one full-depth snapshot in sample 0 -> data/depth.csv
            window -> data/window.json
"""
import csv
import datetime as dt
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

DATA = '/home/user/crevopunch/research/data'
UNI = os.path.join(DATA, 'universe.json')
VENUES = ['OKX', 'Kraken', 'Hyperliquid', 'Aster', 'Lighter', 'dYdX']
OKX = 'https://www.okx.com/api/v5'
KRA = 'https://futures.kraken.com/derivatives/api/v3'
HL = 'https://api.hyperliquid.xyz/info'
ASTER = 'https://fapi.asterdex.com/fapi/v1'
LIGHTER = 'https://mainnet.zklighter.elliot.ai/api/v1'
DYDX = 'https://indexer.dydx.trade/v4'
CG = 'https://api.coingecko.com/api/v3'
NOTIONALS = [100, 1000, 10000]
N_SAMPLES, PERIOD = 30, 60
EXCLUDE = {'USDT', 'USDC', 'DAI', 'USDE', 'FDUSD', 'TUSD', 'USDS', 'PYUSD', 'USD1', 'BUSD', 'USDD',
           'FRAX', 'LUSD', 'GUSD', 'USDP', 'EURC', 'SUSD', 'USDY', 'USDG', 'BSC-USD', 'WBTC', 'WETH',
           'STETH', 'WSTETH', 'WEETH', 'RETH', 'CBBTC', 'CBETH', 'WBETH', 'WBNB', 'WSOL', 'JITOSOL',
           'MSOL', 'BSOL', 'SUSDE', 'TBTC', 'LBTC', 'METH', 'EETH', 'LSETH', 'SWETH', 'RSETH',
           'FBTC', 'HBTC', 'SOLVBTC', 'BTCB', 'WRSETH'}
EXCLUDE_NAME = re.compile(r'wrapped|staked|bridged|liquid staking', re.I)
UA = {'User-Agent': 'perp-research-collector/1.0', 'Accept': 'application/json'}


def now_ts():
    return time.time()


def iso(t):
    return dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def log(msg):
    line = f'{iso(now_ts())} {msg}'
    with open(os.path.join(DATA, 'collect.log'), 'a') as f:
        f.write(line + '\n')
    print(line, flush=True)


def _req(url, payload=None, tries=3):
    body = json.dumps(payload).encode() if payload is not None else None
    last = None
    for i in range(tries):
        try:
            h = dict(UA)
            if body is not None:
                h['Content-Type'] = 'application/json'
            with urllib.request.urlopen(urllib.request.Request(url, data=body, headers=h), timeout=20) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            last = e
            if e.code != 429 and e.code < 500:
                break
            time.sleep(10 if e.code == 429 else 1 + i)
        except Exception as e:  # network / timeout / bad JSON
            last = e
            time.sleep(1 + i)
    raise last


def get(url):
    return _req(url)


def post(url, payload):
    return _req(url, payload)


def norm(venue, base):
    """Map venue base symbol -> (coin, factor). factor = coin units per venue price/qty unit."""
    if venue == 'Hyperliquid' and re.fullmatch(r'k[A-Z0-9]+', base):  # kPEPE etc = 1000 coins
        return base[1:].upper(), 1000
    b = base.upper()
    if re.fullmatch(r'1000[A-Z0-9]+', b):
        return b[4:], 1000
    if venue == 'Kraken' and b == 'XBT':
        return 'BTC', 1
    return b, 1


def mk(raw_bids, raw_asks, f, qmult):
    """Normalise raw levels to coin units: price/f, qty*qmult*f; bids desc, asks asc."""
    b = sorted(((float(p) / f, float(q) * qmult * f) for p, q in raw_bids if float(q) > 0), key=lambda x: -x[0])
    a = sorted(((float(p) / f, float(q) * qmult * f) for p, q in raw_asks if float(q) > 0), key=lambda x: x[0])
    return {'bids': b, 'asks': a}


def load_venues():
    vm = {v: {} for v in VENUES}
    for i in get(f'{OKX}/public/instruments?instType=SWAP')['data']:
        if i.get('settleCcy') == 'USDT' and i.get('state') == 'live' and i['instId'].endswith('-USDT-SWAP'):
            c, f = norm('OKX', i['instId'].split('-')[0])
            vm['OKX'][c] = dict(sym=i['instId'], f=f, ctv=float(i['ctVal']))
    for i in get(f'{KRA}/instruments')['instruments']:
        if i['symbol'].startswith('PF_') and i.get('tradeable') and not i.get('suspended') and not i.get('isExpired'):
            c, f = norm('Kraken', i['base'])
            vm['Kraken'][c] = dict(sym=i['symbol'], f=f, ctv=float(i.get('contractSize') or 1))
    meta, _ = post(HL, {'type': 'metaAndAssetCtxs'})
    for u in meta['universe']:
        if not u.get('isDelisted'):
            c, f = norm('Hyperliquid', u['name'])
            vm['Hyperliquid'][c] = dict(sym=u['name'], f=f, ctv=1.0)
    for s in get(f'{ASTER}/exchangeInfo')['symbols']:
        if s.get('quoteAsset') == 'USDT' and s.get('status') == 'TRADING' and s.get('contractType', 'PERPETUAL') in ('PERPETUAL', '', None):
            c, f = norm('Aster', s['baseAsset'])
            vm['Aster'][c] = dict(sym=s['symbol'], f=f, ctv=1.0)
    for m in get(f'{LIGHTER}/orderBooks')['order_books']:
        if m.get('market_type') == 'perp' and m.get('status') == 'active':
            c, f = norm('Lighter', m['symbol'])
            vm['Lighter'][c] = dict(sym=m['market_id'], f=f, ctv=1.0)
    for t, m in get(f'{DYDX}/perpetualMarkets')['markets'].items():
        if m.get('status') == 'ACTIVE':
            c, f = norm('dYdX', t.split('-')[0])
            vm['dYdX'][c] = dict(sym=t, f=f, ctv=1.0)
    return vm


def cmd_universe():
    vm = load_venues()
    cg = []
    for page in (1, 2):
        cg += get(f'{CG}/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=100&page={page}')
        time.sleep(3)
    rows = []
    for c in cg:
        sym = c['symbol'].upper()
        if sym in EXCLUDE or EXCLUDE_NAME.search(c['name']):
            continue
        listed = {v: sym in vm[v] for v in VENUES}
        rows.append(dict(coin=sym, name=c['name'], rank=c['market_cap_rank'], mcap=c['market_cap'],
                         n=sum(listed.values()), listed=listed))
    selected = [r['coin'] for r in rows if r['n'] >= 2][:50]
    sel = set(selected)
    with open(os.path.join(DATA, 'listings.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['coin', 'name', 'cg_rank', 'market_cap_usd'] + VENUES + ['n_venues', 'selected'])
        for r in rows:
            w.writerow([r['coin'], r['name'], r['rank'], r['mcap']] +
                       ['Y' if r['listed'][v] else 'N' for v in VENUES] + [r['n'], 'Y' if r['coin'] in sel else 'N'])
    venues = {v: {c: vm[v][c] for c in selected if c in vm[v]} for v in VENUES}
    json.dump(dict(selected=selected, venues=venues, generated_utc=iso(now_ts())), open(UNI, 'w'), indent=1)
    log(f'universe: {len(rows)} candidates, {len(selected)} selected: {" ".join(selected)}')


def load_uni():
    return json.load(open(UNI))


def pool_map(fn, items, workers=4):
    with ThreadPoolExecutor(max_workers=workers) as ex:
        return list(ex.map(fn, items))


def cmd_funding():
    u = load_uni()
    V = u['venues']
    sel = u['selected']
    since = now_ts() - 7 * 86400
    cur = {}   # (coin, venue) -> (rate, interval_h)
    hist = {}  # (coin, venue) -> [(t, rate_per_period)]

    # ---- OKX: per-instrument current + history
    def okx_one(c):
        sym = V['OKX'][c]['sym']
        d = get(f'{OKX}/public/funding-rate?instId={sym}')['data'][0]
        ft, nft = int(d['fundingTime']), int(d['nextFundingTime'])
        ih = round((nft - ft) / 3600000 * 4) / 4 or 8.0
        h = get(f'{OKX}/public/funding-rate-history?instId={sym}&limit=100')['data']
        pts = [(int(x['fundingTime']) / 1000, float(x.get('realizedRate') or x['fundingRate'])) for x in h]
        return c, float(d['fundingRate']), ih, pts
    for c, r, ih, pts in pool_map(lambda c: safe(lambda: okx_one(c), ('OKX', c), (c, None, None, [])), [c for c in sel if c in V['OKX']]):
        if r is None: continue
        cur[(c, 'OKX')] = (r, ih); hist[(c, 'OKX')] = [p for p in pts if p[0] >= since]

    # ---- Kraken: bulk current relativeFundingRate (hourly fraction) + history
    kt = {t['symbol']: t for t in get(f'{KRA}/tickers')['tickers']}
    def kra_hist(c):
        rs = get(f"{KRA}/historical-funding-rates?symbol={V['Kraken'][c]['sym']}")['rates']
        out = []
        for x in rs:
            t = dt.datetime.fromisoformat(x['timestamp'].replace('Z', '+00:00')).timestamp()
            if t >= since and x.get('relativeFundingRate') is not None:
                out.append((t, float(x['relativeFundingRate'])))
        return out
    for c in V['Kraken']:
        if c in sel and V['Kraken'][c]['sym'] in kt and kt[V['Kraken'][c]['sym']].get('relativeFundingRate') is not None:
            cur[(c, 'Kraken')] = (float(kt[V['Kraken'][c]['sym']]['relativeFundingRate']), 1.0)
    for c, pts in pool_map(lambda c: (c, safe(lambda: kra_hist(c), ('Kraken', c), [])), [c for c in sel if (c, 'Kraken') in cur]):
        hist[(c, 'Kraken')] = pts

    # ---- Hyperliquid: current from metaAndAssetCtxs, history from fundingHistory
    meta, ctxs = post(HL, {'type': 'metaAndAssetCtxs'})
    hl_cur = {u_['name']: float(x['funding']) for u_, x in zip(meta['universe'], ctxs) if 'funding' in x}
    def hl_hist(c):
        rs = post(HL, {'type': 'fundingHistory', 'coin': V['Hyperliquid'][c]['sym'], 'startTime': int(since * 1000)})
        return [(x['time'] / 1000, float(x['fundingRate'])) for x in rs]
    for c in sel:
        if c in V['Hyperliquid'] and V['Hyperliquid'][c]['sym'] in hl_cur:
            cur[(c, 'Hyperliquid')] = (hl_cur[V['Hyperliquid'][c]['sym']], 1.0)
    for c, pts in pool_map(lambda c: (c, safe(lambda: hl_hist(c), ('HL', c), [])), [c for c in sel if (c, 'Hyperliquid') in cur]):
        hist[(c, 'Hyperliquid')] = pts

    # ---- Aster: premiumIndex (current), fundingInfo (interval), fundingRate (history)
    pi = {x['symbol']: x for x in get(f'{ASTER}/premiumIndex')}
    fi = {x['symbol']: float(x.get('fundingIntervalHours') or 8) for x in get(f'{ASTER}/fundingInfo')}
    def aster_hist(c):
        rs = get(f"{ASTER}/fundingRate?symbol={V['Aster'][c]['sym']}&startTime={int(since * 1000)}&limit=1000")
        return [(x['fundingTime'] / 1000, float(x['fundingRate'])) for x in rs]
    for c in sel:
        if c in V['Aster'] and V['Aster'][c]['sym'] in pi:
            s = V['Aster'][c]['sym']
            cur[(c, 'Aster')] = (float(pi[s]['lastFundingRate']), fi.get(s, 8.0))
    for c, pts in pool_map(lambda c: (c, safe(lambda: aster_hist(c), ('Aster', c), [])), [c for c in sel if (c, 'Aster') in cur]):
        hist[(c, 'Aster')] = pts

    # ---- Lighter: funding-rates (current, signed), fundings (history, 1h, direction -> sign)
    lr = {x['market_id']: float(x['rate']) for x in get(f'{LIGHTER}/funding-rates')['funding_rates'] if x['exchange'] == 'lighter'}
    def lit_hist(c):
        mid = V['Lighter'][c]['sym']
        rs = get(f'{LIGHTER}/fundings?market_id={mid}&resolution=1h&start_timestamp={int(since)}'
                 f'&end_timestamp={int(now_ts())}&count_back=200')['fundings']
        return [(x['timestamp'], float(x['rate']) * (1 if x.get('direction') == 'long' else -1)) for x in rs]
    for c in sel:
        if c in V['Lighter'] and V['Lighter'][c]['sym'] in lr:
            cur[(c, 'Lighter')] = (lr[V['Lighter'][c]['sym']], 1.0)
    for c, pts in pool_map(lambda c: (c, safe(lambda: lit_hist(c), ('Lighter', c), [])), [c for c in sel if (c, 'Lighter') in cur]):
        hist[(c, 'Lighter')] = pts

    # ---- dYdX: perpetualMarkets nextFundingRate (hourly), historicalFunding
    dm = get(f'{DYDX}/perpetualMarkets')['markets']
    def dy_hist(c):
        rs = get(f"{DYDX}/historicalFunding/{V['dYdX'][c]['sym']}?limit=1000")['historicalFunding']
        out = []
        for x in rs:
            t = dt.datetime.fromisoformat(x['effectiveAt'].replace('Z', '+00:00')).timestamp()
            if t >= since:
                out.append((t, float(x['rate'])))
        return out
    for c in sel:
        if c in V['dYdX'] and V['dYdX'][c]['sym'] in dm and dm[V['dYdX'][c]['sym']].get('nextFundingRate') is not None:
            cur[(c, 'dYdX')] = (float(dm[V['dYdX'][c]['sym']]['nextFundingRate']), 1.0)
    for c, pts in pool_map(lambda c: (c, safe(lambda: dy_hist(c), ('dYdX', c), [])), [c for c in sel if (c, 'dYdX') in cur]):
        hist[(c, 'dYdX')] = pts

    # ---- write
    with open(os.path.join(DATA, 'funding.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['coin', 'venue', 'symbol', 'interval_h', 'current_rate', 'current_ann_pct', 'hist_n',
                    'hist_mean_ann_pct', 'hist_std_ann_pct', 'hist_pct_positive', 'hist_from_utc', 'hist_to_utc'])
        for c in sel:
            for v in VENUES:
                if (c, v) not in cur:
                    continue
                r, ih = cur[(c, v)]
                ann = lambda x: x * 8760 / ih * 100
                pts = sorted(hist.get((c, v), []))
                anns = [ann(x[1]) for x in pts]
                n = len(anns)
                mean = sum(anns) / n if n else ''
                std = (__import__('statistics').stdev(anns) if n > 1 else '') if n else ''
                pos = 100 * sum(1 for x in pts if x[1] > 0) / n if n else ''
                w.writerow([c, v, V[v][c]['sym'], ih, f'{r:.10g}', f'{ann(r):.4f}', n,
                            f'{mean:.4f}' if n else '', f'{std:.4f}' if n > 1 else '',
                            f'{pos:.1f}' if n else '',
                            iso(pts[0][0]) if n else '', iso(pts[-1][0]) if n else ''])
    log(f'funding: {len(cur)} coin-venue current rates written to funding.csv')


def safe(fn, label, default=None):
    try:
        return fn()
    except Exception as e:
        log(f'ERR {label}: {type(e).__name__}: {str(e)[:120]}')
        return default


# ---------------- sampling ----------------
def book_fetchers(V):
    def okx(c):
        d = get(f"{OKX}/market/books?instId={V['OKX'][c]['sym']}&sz=400")['data'][0]
        i = V['OKX'][c]
        return mk([(b[0], b[1]) for b in d['bids']], [(a[0], a[1]) for a in d['asks']], i['f'], i['ctv'])

    def kraken(c):
        i = V['Kraken'][c]
        d = get(f"{KRA}/orderbook?symbol={i['sym']}")['orderBook']
        return mk(d['bids'], d['asks'], i['f'], i['ctv'])

    def aster(c):
        i = V['Aster'][c]
        d = get(f"{ASTER}/depth?symbol={i['sym']}&limit=100")
        return mk(d['bids'], d['asks'], i['f'], 1)

    def hl(c):
        i = V['Hyperliquid'][c]
        d = post(HL, {'type': 'l2Book', 'coin': i['sym']})
        lv = d['levels']
        return mk([(x['px'], x['sz']) for x in lv[0]], [(x['px'], x['sz']) for x in lv[1]], i['f'], 1)

    def dydx(c):
        i = V['dYdX'][c]
        d = get(f"{DYDX}/orderbooks/perpetualMarket/{i['sym']}")
        return mk([(x['price'], x['size']) for x in d['bids']], [(x['price'], x['size']) for x in d['asks']], i['f'], 1)

    def lighter(c):
        i = V['Lighter'][c]
        d = get(f"{LIGHTER}/orderBookOrders?market_id={i['sym']}&limit=100")
        return mk([(x['price'], x['remaining_base_amount']) for x in d['bids']],
                  [(x['price'], x['remaining_base_amount']) for x in d['asks']], i['f'], 1)

    return {'OKX': okx, 'Kraken': kraken, 'Aster': aster, 'Hyperliquid': hl, 'dYdX': dydx, 'Lighter': lighter}


def walk(book, notional, side):
    """VWAP slippage in bps vs mid for a market order of `notional` USD. None if the book cannot fill it."""
    lv = book['asks'] if side == 'buy' else book['bids']
    rem, cost, qty = notional, 0.0, 0.0
    for px, q in lv:
        n = px * q
        if n >= rem:
            cost += rem
            qty += rem / px
            rem = 0.0
            break
        cost += n
        qty += q
        rem -= n
    if rem > 1e-9 or qty <= 0:
        return None
    vwap = cost / qty
    mid = (book['bids'][0][0] + book['asks'][0][0]) / 2
    return (vwap / mid - 1) * 1e4 if side == 'buy' else (1 - vwap / mid) * 1e4


def depth_rows(full):
    rows = []
    for (c, v), bk in sorted(full.items()):
        if not bk['bids'] or not bk['asks']:
            continue
        bb, ba = bk['bids'][0][0], bk['asks'][0][0]
        mid = (bb + ba) / 2
        bid_depth = sum(p * q for p, q in bk['bids'])
        ask_depth = sum(p * q for p, q in bk['asks'])
        for side in ('buy', 'sell'):
            for N in NOTIONALS:
                s = walk(bk, N, side)
                rows.append([c, v, side, N, f'{mid:.10g}', f'{(ba - bb) / mid * 1e4:.3f}',
                             'insufficient_depth' if s is None else 'ok',
                             '' if s is None else f'{s:.3f}', f'{bid_depth:.0f}', f'{ask_depth:.0f}'])
    return rows


def cmd_sample():
    u = load_uni()
    V, sel = u['venues'], u['selected']
    F = book_fetchers(V)
    sym2 = {}
    for v in ('OKX', 'Kraken', 'Aster', 'Hyperliquid', 'dYdX', 'Lighter'):
        sym2[v] = {V[v][c]['sym']: c for c in V[v]}
    win = {'start_utc': iso(now_ts()), 'period_s': PERIOD, 'n_samples': N_SAMPLES}
    json.dump(win, open(os.path.join(DATA, 'window.json'), 'w'), indent=1)
    sp = open(os.path.join(DATA, 'samples.csv'), 'w', newline='')
    sw = csv.writer(sp)
    sw.writerow(['ts', 'coin', 'venue', 'bid', 'ask'])
    depth_done = False
    t_start = now_ts()
    for i in range(N_SAMPLES):
        t0 = now_ts()
        ts = iso(t0)
        quotes = {}
        full = {}
        # bulk top-of-book: OKX, Kraken, Aster
        try:
            for t in get(f'{OKX}/market/tickers?instType=SWAP')['data']:
                c = sym2['OKX'].get(t['instId'])
                if c and t['bidPx'] and t['askPx']:
                    f = V['OKX'][c]['f']
                    quotes[(c, 'OKX')] = (float(t['bidPx']) / f, float(t['askPx']) / f)
        except Exception as e:
            log(f'ERR s{i} OKX bulk: {e}')
        try:
            for t in get(f'{KRA}/tickers')['tickers']:
                c = sym2['Kraken'].get(t['symbol'])
                if c and t.get('bid') and t.get('ask'):
                    f = V['Kraken'][c]['f']
                    quotes[(c, 'Kraken')] = (float(t['bid']) / f, float(t['ask']) / f)
        except Exception as e:
            log(f'ERR s{i} Kraken bulk: {e}')
        try:
            for t in get(f'{ASTER}/ticker/bookTicker'):
                c = sym2['Aster'].get(t['symbol'])
                if c:
                    f = V['Aster'][c]['f']
                    quotes[(c, 'Aster')] = (float(t['bidPrice']) / f, float(t['askPrice']) / f)
        except Exception as e:
            log(f'ERR s{i} Aster bulk: {e}')
        # per-coin books (no bulk endpoint): HL, dYdX, Lighter; depth snapshot also takes OKX/Kraken/Aster books
        tasks = [(c, v) for c in sel for v in ('Hyperliquid', 'dYdX', 'Lighter') if c in V[v]]
        if not depth_done:
            tasks += [(c, v) for c in sel for v in ('OKX', 'Kraken', 'Aster') if c in V[v]]

        def run(task):
            c, v = task
            try:
                return task, F[v](c)
            except Exception as e:
                log(f'ERR s{i} {v} {c}: {type(e).__name__}: {str(e)[:100]}')
                return task, None
        for (c, v), bk in pool_map(run, tasks):
            if bk is None:
                continue
            if bk['bids'] and bk['asks'] and (v in ('Hyperliquid', 'dYdX', 'Lighter')):
                quotes[(c, v)] = (bk['bids'][0][0], bk['asks'][0][0])
            if not depth_done:
                full[(c, v)] = bk
        for (c, v), (b, a) in quotes.items():
            sw.writerow([ts, c, v, f'{b:.10g}', f'{a:.10g}'])
        sp.flush()
        if not depth_done:
            # full books for HL/dYdX/Lighter reuse the tasks above; OKX/Kraken/Aster books fetched in same pool
            with open(os.path.join(DATA, 'depth.csv'), 'w', newline='') as df:
                dw = csv.writer(df)
                dw.writerow(['coin', 'venue', 'side', 'notional_usd', 'mid', 'spread_bps', 'status',
                             'slippage_bps', 'bid_depth_usd_total', 'ask_depth_usd_total'])
                dw.writerows(depth_rows(full))
            depth_done = True
            log(f'depth snapshot written: {len(full)} coin-venue books')
            # unit sanity: cross-venue mid spread per coin; big ratios point to a 1000x mismatch
            mids = {}
            for (c, v), (b, a) in quotes.items():
                mids.setdefault(c, []).append((v, (b + a) / 2))
            for c, lst in mids.items():
                if len(lst) >= 2:
                    ps = [m for _, m in lst]
                    if max(ps) / min(ps) > 1.5:
                        log(f'CHECK units {c}: ' + ', '.join(f'{v}={m:.6g}' for v, m in lst))
        log(f'sample {i + 1}/{N_SAMPLES} ts={ts} quotes={len(quotes)} ({now_ts() - t0:.1f}s)')
        if i < N_SAMPLES - 1:
            time.sleep(max(0.0, PERIOD - (now_ts() - t0)))
    sp.close()
    win['end_utc'] = iso(now_ts())
    json.dump(win, open(os.path.join(DATA, 'window.json'), 'w'), indent=1)
    log('sampling complete')


if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else ''
    {'universe': cmd_universe, 'funding': cmd_funding, 'sample': cmd_sample}.get(
        mode, lambda: (print(__doc__), sys.exit(2)))()
