#!/usr/bin/env python3
"""High-frequency order-book collector (REST polling, stdlib only).

Venues: OKX, Kraken Futures, Aster (bulk tickers every 2 s); Hyperliquid and Lighter
(per-coin book polls, round-robin with rate caps). Writes hourly-rotated gzip CSV to
hf/data/YYYYMMDD_HH.csv.gz (UTC). Runs DURATION seconds, then exits cleanly.
"""
import csv
import datetime as dt
import gzip
import json
import os
import re
import threading
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, 'data')
import os
DURATION = int(os.environ.get("HF_DURATION", 24 * 3600))
COINS = ('BTC ETH SOL XRP DOGE BNB HYPE ASTER WLFI SUI LINK AVAX PEPE KAS VVV PUMP JUP '
         'MORPHO ONDO CRO ENA TAO WLD LTC SKY').split()
VENUES = ['OKX', 'Kraken', 'Hyperliquid', 'Aster', 'Lighter']
OKX = 'https://www.okx.com/api/v5'
KRA = 'https://futures.kraken.com/derivatives/api/v3'
HL = 'https://api.hyperliquid.xyz/info'
ASTER = 'https://fapi.asterdex.com/fapi/v1'
LIGHTER = 'https://mainnet.zklighter.elliot.ai/api/v1'
UA = {'User-Agent': 'perp-research-collector/1.0', 'Accept': 'application/json'}
FIELDS = ['ts_ms', 'venue', 'coin', 'bid', 'ask', 'bid_sz', 'ask_sz',
          'bid_1k', 'ask_1k', 'bid_10k', 'ask_10k']
# per-coin pollers: (workers, seconds between requests per worker)
HL_WORKERS, HL_GAP = 4, 0.64      # ~6.25 req/s * weight 2 = ~750 weight/min (limit 1200)
LIT_WORKERS, LIT_GAP = 2, 0.5     # 4 req/s cap; backs off on 429

stop = threading.Event()
lock = threading.Lock()
counts = {v: 0 for v in VENUES}
last_err = {}


def now_ms():
    return int(time.time() * 1000)


def log(msg):
    print(f"{dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')} {msg}", flush=True)


def err(label, e):
    """Log an error, throttled to one line per label per 60 s."""
    t = time.time()
    with lock:
        prev = last_err.get(label)
        if prev and t - prev[0] < 60:
            prev[1] += 1
            return
        suppressed = prev[1] if prev else 0
        last_err[label] = [t, 0]
    log(f"ERR {label}: {type(e).__name__}: {str(e)[:150]} (suppressed={suppressed})")


def req(url, payload=None, timeout=10):
    body = json.dumps(payload).encode() if payload is not None else None
    h = dict(UA)
    if body is not None:
        h['Content-Type'] = 'application/json'
    with urllib.request.urlopen(urllib.request.Request(url, data=body, headers=h), timeout=timeout) as r:
        return json.loads(r.read().decode())


def norm(venue, base):
    """Venue base symbol -> (coin, factor). factor = coin units per venue price/qty unit."""
    if venue == 'Hyperliquid' and re.fullmatch(r'k[A-Z0-9]+', base):  # kPEPE = 1000 PEPE
        return base[1:].upper(), 1000
    b = base.upper()
    m = re.fullmatch(r'1000([A-Z0-9]+)', b)
    if m:
        return m.group(1), 1000
    if venue == 'Kraken' and b == 'XBT':
        return 'BTC', 1
    return b, 1


def resolve():
    """Map each venue's perp symbols for our coins from the live instrument lists."""
    M = {v: {} for v in VENUES}

    def keep(v, base, sym, ctv):
        c, f = norm(v, base)
        if c in COINS and c not in M[v]:
            M[v][c] = (sym, f, ctv)

    def okx(_):
        for i in req(f'{OKX}/public/instruments?instType=SWAP')['data']:
            if i.get('settleCcy') == 'USDT' and i.get('state') == 'live' and i['instId'].endswith('-USDT-SWAP'):
                keep('OKX', i['instId'].split('-')[0], i['instId'], float(i['ctVal']))

    def kra(_):
        for i in req(f'{KRA}/instruments')['instruments']:
            if i['symbol'].startswith('PF_') and i.get('tradeable') and not i.get('suspended') and not i.get('isExpired'):
                keep('Kraken', i['base'], i['symbol'], float(i.get('contractSize') or 1))

    def hl(_):
        for u in req(HL, {'type': 'metaAndAssetCtxs'})[0]['universe']:
            if not u.get('isDelisted'):
                keep('Hyperliquid', u['name'], u['name'], 1.0)

    def aster(_):
        for s in req(f'{ASTER}/exchangeInfo')['symbols']:
            if s.get('quoteAsset') == 'USDT' and s.get('status') == 'TRADING' and \
                    s.get('contractType', 'PERPETUAL') in ('PERPETUAL', '', None):
                keep('Aster', s['baseAsset'], s['symbol'], 1.0)

    def lit(_):
        for m in req(f'{LIGHTER}/orderBooks')['order_books']:
            if m.get('market_type') == 'perp' and m.get('status') == 'active':
                keep('Lighter', m['symbol'], m['market_id'], 1.0)

    for name, fn in [('OKX', okx), ('Kraken', kra), ('Hyperliquid', hl), ('Aster', aster), ('Lighter', lit)]:
        for attempt in range(4):
            try:
                fn(None)
                break
            except Exception as e:
                err(f'resolve {name}', e)
                time.sleep(10)
    return M


def mk(bids, asks, f, qmult):
    """Normalise raw levels to per-coin price and coin qty; bids desc, asks asc."""
    b = sorted(((float(p) / f, float(q) * qmult * f) for p, q in bids if float(q) > 0), key=lambda x: -x[0])
    a = sorted(((float(p) / f, float(q) * qmult * f) for p, q in asks if float(q) > 0), key=lambda x: x[0])
    return b, a


def walk(levels, target_usd):
    """Price of the last level needed to reach target_usd of cumulative notional; None if too thin."""
    cum = 0.0
    for p, q in levels:
        cum += p * q
        if cum >= target_usd:
            return p
    return None


def book_row(ts, venue, coin, bids, asks):
    if not bids or not asks:
        return None
    return [ts, venue, coin, bids[0][0], asks[0][0], bids[0][1], asks[0][1],
            walk(bids, 1000), walk(asks, 1000), walk(bids, 10000), walk(asks, 10000)]


def top_row(ts, venue, coin, bid, ask, bsz, asz):
    b, a = float(bid), float(ask)
    if not (b > 0 and a > 0):
        return None
    return [ts, venue, coin, b, a, float(bsz), float(asz), '', '', '', '']


class Writer:
    def __init__(self):
        self.key = None
        self.fh = None
        self.wr = None
        os.makedirs(DATA, exist_ok=True)

    def _rotate(self, key):
        if self.fh:
            self.fh.close()
        path = os.path.join(DATA, f'{key}.csv.gz')
        new = not os.path.exists(path) or os.path.getsize(path) == 0
        self.fh = gzip.open(path, 'at', newline='')
        self.wr = csv.writer(self.fh)
        if new:
            self.wr.writerow(FIELDS)
        self.key = key

    def write(self, rows):
        rows = [r for r in rows if r]
        if not rows:
            return
        with lock:
            key = dt.datetime.fromtimestamp(rows[0][0] / 1000, dt.timezone.utc).strftime('%Y%m%d_%H')
            if key != self.key:
                self._rotate(key)
            self.wr.writerows(rows)
            self.fh.flush()  # gzip sync-flush so the data survives a crash
            for r in rows:
                counts[r[1]] += 1

    def close(self):
        with lock:
            if self.fh:
                self.fh.close()
                self.fh = None


W = Writer()


def sleep_until(t):
    while not stop.is_set():
        d = t - time.time()
        if d <= 0:
            return
        stop.wait(min(d, 0.5))


def bulk_loop(venue, fetch, period):
    while not stop.is_set():
        t0 = time.time()
        try:
            W.write(fetch())
        except Exception as e:
            err(venue, e)
        sleep_until(t0 + period)


def okx_fetch(M):
    inv = {sym: (c, f, ctv) for c, (sym, f, ctv) in M['OKX'].items()}

    def f():
        data = req(f'{OKX}/market/tickers?instType=SWAP')['data']
        ts, out = now_ms(), []
        for t in data:
            e = inv.get(t.get('instId'))
            if e:
                c, fac, ctv = e
                r = top_row(ts, 'OKX', c, float(t['bidPx']) / fac, float(t['askPx']) / fac,
                            float(t['bidSz']) * ctv * fac, float(t['askSz']) * ctv * fac)
                out.append(r)
        return out
    return f


def kraken_fetch(M):
    inv = {sym: (c, f, ctv) for c, (sym, f, ctv) in M['Kraken'].items()}

    def f():
        data = req(f'{KRA}/tickers')['tickers']
        ts, out = now_ms(), []
        for t in data:
            e = inv.get(t.get('symbol'))
            if e:
                c, fac, ctv = e
                out.append(top_row(ts, 'Kraken', c, float(t['bid']) / fac, float(t['ask']) / fac,
                                   float(t['bidSize']) * ctv * fac, float(t['askSize']) * ctv * fac))
        return out
    return f


def aster_fetch(M):
    inv = {sym: (c, f) for c, (sym, f, _) in M['Aster'].items()}

    def f():
        data = req(f'{ASTER}/ticker/bookTicker')
        ts, out = now_ms(), []
        for t in data:
            e = inv.get(t.get('symbol'))
            if e:
                c, fac = e
                out.append(top_row(ts, 'Aster', c, float(t['bidPrice']) / fac, float(t['askPrice']) / fac,
                                   float(t['bidQty']) * fac, float(t['askQty']) * fac))
        return out
    return f


def hl_one(coin, sym, f):
    d = req(HL, {'type': 'l2Book', 'coin': sym})
    lv = d['levels']
    bids, asks = mk([(x['px'], x['sz']) for x in lv[0]], [(x['px'], x['sz']) for x in lv[1]], f, 1)
    return book_row(now_ms(), 'Hyperliquid', coin, bids, asks)


def lit_one(coin, mid, f):
    d = req(f'{LIGHTER}/orderBookOrders?market_id={mid}&limit=20')
    bids, asks = mk([(x['price'], x['remaining_base_amount']) for x in d['bids']],
                    [(x['price'], x['remaining_base_amount']) for x in d['asks']], f, 1)
    return book_row(now_ms(), 'Lighter', coin, bids, asks)


def cycle_worker(venue, items, gap, one):
    """Round-robin over items, one request per `gap` seconds; backs off on 429."""
    i, backoff = 0, 0.0
    nxt = time.time()
    while not stop.is_set():
        coin, sym, f = items[i % len(items)]
        i += 1
        try:
            W.write([one(coin, sym, f)])
            backoff = 0.0
        except urllib.error.HTTPError as e:
            if e.code == 429:
                backoff = min(60.0, max(5.0, backoff * 2))
                err(f'{venue} 429', e)
            else:
                err(f'{venue} {coin}', e)
        except Exception as e:
            err(f'{venue} {coin}', e)
        if backoff:
            sleep_until(time.time() + backoff)
            nxt = time.time()
        else:
            nxt += gap
            if nxt < time.time() - 1:
                nxt = time.time()
            sleep_until(nxt)


def main():
    t_end = time.time() + DURATION
    M = resolve()
    cnt = {c: sum(c in M[v] for v in VENUES) for c in COINS}
    KEEP = [c for c in COINS if cnt[c] >= 2]
    log('venue coverage: ' + ' '.join(f'{v}={len(M[v])}' for v in VENUES))
    log(f'coins kept ({len(KEEP)}): ' + ' '.join(KEEP))
    M = {v: {c: x for c, x in M[v].items() if c in KEEP} for v in VENUES}

    threads = []

    def start(name, target, *args):
        t = threading.Thread(target=target, args=args, name=name, daemon=True)
        t.start()
        threads.append(t)

    for v, fetcher in [('OKX', okx_fetch), ('Kraken', kraken_fetch), ('Aster', aster_fetch)]:
        if M[v]:
            start(v, bulk_loop, v, fetcher(M), 2.0)
    hl_items = [(c, sym, f) for c, (sym, f, _) in M['Hyperliquid'].items()]
    lit_items = [(c, mid, f) for c, (mid, f, _) in M['Lighter'].items()]
    for k in range(HL_WORKERS):
        if hl_items[k::HL_WORKERS]:
            start(f'HL{k}', cycle_worker, 'Hyperliquid', hl_items[k::HL_WORKERS], HL_GAP, hl_one)
    for k in range(LIT_WORKERS):
        if lit_items[k::LIT_WORKERS]:
            start(f'LIT{k}', cycle_worker, 'Lighter', lit_items[k::LIT_WORKERS], LIT_GAP, lit_one)

    last_hb = 0.0
    while time.time() < t_end and not stop.is_set():
        stop.wait(5)
        if time.time() - last_hb >= 300:
            last_hb = time.time()
            with lock:
                c = dict(counts)
            log('HB rows ' + ' '.join(f'{k}={v}' for k, v in c.items()))
    stop.set()
    for t in threads:
        t.join(timeout=15)
    W.close()
    log('finished 24h run, exiting')


if __name__ == '__main__':
    main()
