"""Size-dependent slippage, calibrated from research/data/depth.csv (stdlib only).

Slippage = VWAP vs mid including half-spread, one way, in bps. Per (coin, venue): mean of the ok buy/sell
rows at each notional (100, 1000, 10000). Between points: linear in log(N). Above 10k:
s(10k) * sqrt(N/10k), capped at 300 bps. Missing (coin, venue): the venue's median curve across coins.
Effective rate on a fill = max(old flat rate, size curve). mode='flat' returns the old flat rate only.
"""
import csv
import functools
import math
import statistics

DEPTH = '/home/user/crevopunch/research/data/depth.csv'
NOTIONALS = (100.0, 1000.0, 10000.0)
MAX_BPS = 300.0
VENUE_NAME = {'H': 'Hyperliquid', 'K': 'Kraken', 'HL': 'Hyperliquid', 'KR': 'Kraken', 'LT': 'Lighter', 'AS': 'Aster'}


def flat(coin):
    return 2e-4 if coin in ('BTC', 'ETH') else 5e-4


def _build():
    raw = {}
    names = set(VENUE_NAME.values())
    with open(DEPTH) as f:
        for r in csv.DictReader(f):
            if r['status'] != 'ok' or r['slippage_bps'] == '' or r['venue'] not in names:
                continue
            raw.setdefault((r['coin'], r['venue']), {}).setdefault(float(r['notional_usd']), []).append(
                float(r['slippage_bps']))
    pairs = {}
    for k, d in raw.items():
        pts = [(n, statistics.mean(d[n])) for n in NOTIONALS if n in d]
        if pts:
            pairs[k] = pts
    per_venue = {}
    for (c, v), pts in pairs.items():
        for n, s in pts:
            per_venue.setdefault(v, {}).setdefault(n, []).append(s)
    venue_med = {v: [(n, statistics.median(per_venue[v][n])) for n in NOTIONALS if n in per_venue.get(v, {})]
                 for v in names}
    return pairs, venue_med


PAIRS, VENUE_MED = _build()


def _interp(pts, N):
    if N <= pts[0][0]:
        return pts[0][1]
    for (n0, s0), (n1, s1) in zip(pts, pts[1:]):
        if N <= n1:
            w = (math.log(N) - math.log(n0)) / (math.log(n1) - math.log(n0))
            return s0 + w * (s1 - s0)
    s10k = pts[-1][1]
    return min(MAX_BPS, s10k * math.sqrt(N / pts[-1][0]))


def curve_bps(coin, venue, N):
    """Size curve in bps for a fill of notional N (USD) on venue (full name)."""
    pts = PAIRS.get((coin, venue))
    if pts is None:
        pts = VENUE_MED[venue]
    return _interp(pts, N)


@functools.lru_cache(maxsize=None)
def rate_fn(coin, venue, mode='size'):
    """Return f(notional_usd) -> one-way slippage as a fraction of notional."""
    fl = flat(coin)
    if mode == 'flat':
        return lambda N: fl
    return lambda N: max(fl, curve_bps(coin, venue, N) / 1e4)
