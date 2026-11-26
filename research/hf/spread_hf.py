#!/usr/bin/env python3
"""Cross-venue perp spread backtests on recorded order-book snapshots (2026-11-26, ~8h).

Pandas/numpy only. Reads hf/data/20261126_*.csv.gz and writes hf/results_hf.csv and
hf/summary_hf.md next to this file. Each coin is processed separately on a 1s grid with
as-of (forward-filled) quotes that must be <=8s old (<=12s for Lighter).
"""
import glob
import os
from collections import defaultdict
from itertools import combinations

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, 'data')
OUT_CSV = os.path.join(HERE, 'results_hf.csv')
OUT_MD = os.path.join(HERE, 'summary_hf.md')

VENUES = ['OKX', 'Kraken', 'Hyperliquid', 'Aster', 'Lighter']
SH = {'OKX': 'OKX', 'Kraken': 'KRK', 'Hyperliquid': 'HL', 'Aster': 'AST', 'Lighter': 'LTR'}
TAKER = {'OKX': 5.0, 'Kraken': 5.0, 'Hyperliquid': 4.5, 'Aster': 4.0, 'Lighter': 0.0}
MAKER = {'OKX': 2.0, 'Kraken': 2.0, 'Hyperliquid': 1.5, 'Aster': 0.0, 'Lighter': 0.0}
STALE_MS = {v: 8000 for v in VENUES}
STALE_MS['Lighter'] = 12000
DEPTH = {'Hyperliquid', 'Lighter'}          # only venues with *_1k / *_10k columns
SIZES = [100, 1000, 10000]
KS = {1000: '1k', 10000: '10k'}
TICK = 0.5e-4                                # fill-rule tick: 0.5 bp of price
DAY_MULT = 24 / 8                            # 8h sample -> per day
H4 = 4 * 3600                                # S1 timeout (s)
BIG = 10 ** 9                                # "no timeout" for S2
W_MAKER = 60                                 # maker order life for maker-maker variant (s)
W_FLAT = 1800                                # S3 flatten time (s)
BLOCK = 30                                   # S3 requote cadence (s)
TICK_LIMIT_BPS = 1.0                         # coins whose price tick exceeds this are flagged
NAN = float('nan')
COLS = ['ts_ms', 'bid', 'ask', 'bid_sz', 'ask_sz', 'bid_1k', 'ask_1k', 'bid_10k', 'ask_10k']

ROWS = []
LOG = []
SANITY = []
BASIS = []   # (coin, venue, median mid basis vs Lighter in bps)


# ----------------------------------------------------------------------------- data
def load():
    files = sorted(glob.glob(os.path.join(DATA, '20261126_*.csv.gz')))
    df = pd.concat((pd.read_csv(f) for f in files), ignore_index=True)
    n0 = len(df)
    df = df.drop_duplicates(['ts_ms', 'venue', 'coin'])
    good = (df.bid > 0) & (df.ask > 0) & (df.bid <= df.ask)
    df = df[good].sort_values('ts_ms')
    LOG.append(f'Input: {len(files)} files (20261126_01..09; 20261125_19 excluded), {n0:,} rows, '
               f'{len(df):,} kept after de-duplication and dropping zero or crossed quotes.')
    return df


def build(g, grid):
    """Forward-filled as-of quotes for one coin on the 1s grid, with staleness limits."""
    c = {'_cache': {}}
    for v in VENUES:
        q = g.loc[g.venue == v, COLS]
        if q.empty:
            continue
        m = pd.merge_asof(pd.DataFrame({'t': grid}), q, left_on='t', right_on='ts_ms',
                          direction='backward', tolerance=STALE_MS[v])
        c[v] = {'bid': m.bid.to_numpy(float), 'ask': m.ask.to_numpy(float),
                'bsz': m.bid_sz.to_numpy(float), 'asz': m.ask_sz.to_numpy(float),
                'bid_1k': m.bid_1k.to_numpy(float), 'ask_1k': m.ask_1k.to_numpy(float),
                'bid_10k': m.bid_10k.to_numpy(float), 'ask_10k': m.ask_10k.to_numpy(float),
                'qts': m.ts_ms.to_numpy(float), 'depth': v in DEPTH}
    return c


def finalize_mids(c):
    for v in VENUES:
        if v in c:
            c[v]['mid'] = (c[v]['bid'] + c[v]['ask']) / 2


def sanity(coin, c):
    """Drop or rescale venue/coin pairs whose median mid is >2% off the cross-venue median."""
    def meds():
        return {v: float(np.nanmedian((c[v]['bid'] + c[v]['ask']) / 2)) for v in VENUES
                if v in c and np.isfinite(c[v]['bid']).sum() > 60}

    m = meds()
    if len(m) >= 2:
        cross = float(np.median(list(m.values())))
        for v in list(m):
            r = m[v] / cross
            if abs(r - 1) <= 0.02:
                continue
            f = None
            for k in (10, 100, 1000):
                if abs(r / k - 1) <= 0.02:
                    f = 1.0 / k
                    break
                if abs(r * k - 1) <= 0.02:
                    f = float(k)
                    break
            if f is None:
                SANITY.append(f'{coin} {v}: median mid {100 * (r - 1):+.1f}% vs cross-venue, no clean factor -> dropped')
                del c[v]
            else:
                for key in ('bid', 'ask', 'bid_1k', 'ask_1k', 'bid_10k', 'ask_10k'):
                    c[v][key] = c[v][key] * f
                for key in ('bsz', 'asz'):          # keep notional invariant
                    c[v][key] = c[v][key] / f
                SANITY.append(f'{coin} {v}: median mid {100 * (r - 1):+.1f}% vs cross-venue -> rescaled prices x{f:g}')
    m = meds()
    if len(m) >= 2:
        cross = float(np.median(list(m.values())))
        for v in list(m):
            if abs(m[v] / cross - 1) > 0.02:
                SANITY.append(f'{coin} {v}: still off after rescale -> dropped')
                del c[v]
    finalize_mids(c)
    return c


def tick_bps(c):
    """Median (over venues) of the smallest observed price step, in bps of price."""
    vals = []
    for v in VENUES:
        if v not in c:
            continue
        b = c[v]['bid']
        b = b[np.isfinite(b)]
        if b.size < 2:
            continue
        u = np.unique(np.round(b / np.median(b), 9))
        d = np.diff(u)
        d = d[d > 1e-7]
        if d.size:
            vals.append(1e4 * d.min())
    return float(np.median(vals)) if vals else NAN


def ex(c, v, side, s):
    """Executable price for selling ('b') or buying ('a') $s on venue v (NaN if unavailable)."""
    key = (v, side, s)
    cache = c['_cache']
    if key in cache:
        return cache[key]
    d = c[v]
    if d['depth'] and s > 100:
        out = d[('bid_' if side == 'b' else 'ask_') + KS[s]]
    else:
        p = d['bid' if side == 'b' else 'ask']
        sz = d['bsz' if side == 'b' else 'asz']
        if d['depth']:
            out = p                                    # $100 at top of book
        else:
            # no depth recorded: top-of-book price, only if top notional covers the size
            with np.errstate(invalid='ignore'):
                out = np.where(p * sz >= s, p, NAN)
    cache[key] = out
    return out


# ----------------------------------------------------------------------------- helpers
def first_true(seg, start):
    k = np.flatnonzero(seg)
    return start + int(k[0]) if k.size else None


def taker_px(arr, idx, N):
    """First finite value of arr at or after idx (within 60s). Returns (index, price)."""
    if idx >= N:
        return None, NAN
    seg = arr[idx:min(idx + 60, N)]
    k = np.flatnonzero(np.isfinite(seg))
    if k.size == 0:
        return None, NAN
    return idx + int(k[0]), float(seg[k[0]])


def exit_index(i, H, N, condfn, validfn):
    """First index j>i where condfn & validfn holds, else the timeout (first valid at i+H), else sample end."""
    end = min(i + H, N - 1)
    if end > i:
        seg = condfn(i + 1, end + 1) & validfn(i + 1, end + 1)
        k = np.flatnonzero(seg)
        if k.size:
            return i + 1 + int(k[0])
    if i + H <= N - 1:
        k = np.flatnonzero(validfn(i + H, min(i + H + 300, N)))
        return i + H + int(k[0]) if k.size else None
    k = np.flatnonzero(validfn(i + 1, N))
    return i + 1 + int(k[-1]) if k.size else None


def zc(a, b):
    return np.zeros(b - a, dtype=bool)


def slicer(arr):
    return lambda a, b: np.asarray(arr[a:b], dtype=bool)


def zscore(g, win=1800, minp=600):
    s = pd.Series(g)
    mu = s.rolling(win, min_periods=minp).mean()
    sd = s.rolling(win, min_periods=minp).std()
    return ((s - mu) / sd.where(sd > 0)).to_numpy(float)


def add_row(strategy, params, pair, coin, size, trades, net, pnl, tk):
    ROWS.append({'strategy': strategy, 'params': params, 'pair': pair, 'coin': coin, 'size': size,
                 'trades': int(trades), 'net_bps_per_trade': float(net) if trades else NAN,
                 'pnl_usd': float(pnl), 'pnl_per_day_usd': float(pnl) * DAY_MULT, 'tick_bps': tk})


def add_nets(strategy, params, pair, coin, size, nets, tk):
    nets = np.asarray(nets, float)
    n = nets.size
    pnl = float(np.sum(size * nets / 1e4)) if n else 0.0
    add_row(strategy, params, pair, coin, size, n, nets.mean() if n else NAN, pnl, tk)


# ----------------------------------------------------------------------------- taker-taker engine
def taker_pairs(c, S, L, s, cand, cfac, H, N):
    """Short S (sell at bid), long L (buy at ask); exits buy S at ask and sell L at bid.
    Returns net bps per trade (fees: taker on both legs, entry and exit)."""
    bS, aS = ex(c, S, 'b', s), ex(c, S, 'a', s)
    bL, aL = ex(c, L, 'b', s), ex(c, L, 'a', s)
    ok = np.isfinite(bS) & np.isfinite(aL)
    cand = cand[ok[cand]]
    RT = 2 * (TAKER[S] + TAKER[L])

    def vf(a, b):
        return np.isfinite(aS[a:b]) & np.isfinite(bL[a:b])

    out = []
    p, n = 0, len(cand)
    while p < n:
        i = int(cand[p])
        pS0, pL0 = bS[i], aL[i]
        j = exit_index(i, H, N, cfac(i, pS0, pL0, aS, bL), vf)
        if j is None:
            p += 1
            continue
        out.append(1e4 * ((pS0 - aS[j]) / pS0 + (bL[j] - pL0) / pL0) - RT)
        p = int(np.searchsorted(cand, j + 1))
    return np.asarray(out, float)


def cf_s1(i, pS0, pL0, aS, bL):
    # S1 exit: closing now at executable prices has non-negative combined price change
    return lambda a, b: ((pS0 - aS[a:b]) + (bL[a:b] - pL0)) >= 0


def cf_z(z, side):
    # S2 exit: z crosses zero (sign flips or hits 0) relative to the entry side
    def factory(i, pS0, pL0, aS, bL):
        return lambda a, b: (z[a:b] * side) <= 0
    return factory


def maker_pairs(c, A, B, z, thr, N):
    """S2 maker-maker variant: limit orders at mid, filled by the trade-through rule within 60s;
    exit at z zero-cross with the same rule, falling back to a taker fill after 60s."""
    mA, mB = c[A]['mid'], c[B]['mid']
    cand = np.flatnonzero(np.abs(z) > thr)
    cand = cand[np.isfinite(mA[cand]) & np.isfinite(mB[cand])]
    out = []
    p, n = 0, len(cand)
    while p < n:
        i = int(cand[p])
        side = 1 if z[i] > 0 else -1
        S, L = (A, B) if side > 0 else (B, A)
        mS, mL = c[S]['mid'], c[L]['mid']
        bS, aS = c[S]['bid'], c[S]['ask']
        bL, aL = c[L]['bid'], c[L]['ask']
        PS, PL = mS[i], mL[i]
        a, b = i + 1, min(i + 1 + W_MAKER, N)
        fS = first_true(bS[a:b] >= PS * (1 + TICK), a)     # sell S at PS: bid trades through
        fL = first_true(aL[a:b] <= PL * (1 - TICK), a)     # buy L at PL: ask trades through
        if fS is None or fL is None:
            p += 1
            continue
        te = max(fS, fL)
        cross = np.flatnonzero(z[te + 1:] * side <= 0)
        j = te + 1 + int(cross[0]) if cross.size else N - 1
        qSm, qLm = mS[j], mL[j]
        a, b = j + 1, min(j + 1 + W_MAKER, N)
        fS2 = first_true(aS[a:b] <= qSm * (1 - TICK), a)   # buy back S at mid
        fL2 = first_true(bL[a:b] >= qLm * (1 + TICK), a)   # sell L at mid
        jf = min(j + W_MAKER, N - 1)
        if fS2 is not None:
            qS, feeS = qSm, MAKER[S]
        else:
            _, qS = taker_px(aS, jf, N)
            qS, feeS = (qS if np.isfinite(qS) else qSm), TAKER[S]
        if fL2 is not None:
            qL, feeL = qLm, MAKER[L]
        else:
            _, qL = taker_px(bL, jf, N)
            qL, feeL = (qL if np.isfinite(qL) else qLm), TAKER[L]
        out.append(1e4 * ((PS - qS) / PS + (qL - PL) / PL) - (MAKER[S] + MAKER[L] + feeS + feeL))
        p = int(np.searchsorted(cand, j + 1))
    return np.asarray(out, float)


# ----------------------------------------------------------------------------- S3 maker-hedge
def s3(c, M, o, s, N, grid):
    """Maker quotes on venue M at Lighter mid +/- o bps; hedge on Lighter at the next Lighter
    quote after each fill; one unit of inventory; close on opposite maker fill or flatten after
    30 min at taker on both. Returns (per-cycle net bps, number of hedge fallbacks to mid)."""
    midL = c['Lighter']['mid']
    bMt, aMt = c[M]['bid'], c[M]['ask']
    bMx, aMx = ex(c, M, 'b', s), ex(c, M, 'a', s)
    bL, aL = ex(c, 'Lighter', 'b', s), ex(c, 'Lighter', 'a', s)
    qts = c['Lighter']['qts']
    qmono = np.maximum.accumulate(np.where(np.isfinite(qts), qts, -1.0))
    fM, tM = MAKER[M], TAKER[M]
    of = o / 1e4
    fallback = [0]

    def hedge(tau, buy):
        k = int(np.searchsorted(qmono, grid[tau], side='right'))   # first grid point showing a newer quote
        _, px = (taker_px(aL if buy else bL, k, N) if k < N else (None, NAN))
        if not np.isfinite(px):
            fallback[0] += 1
            px = midL[min(tau, N - 1)]
        return px

    cyc = []
    pos = 0
    P_o = H_o = 0.0
    t_o = 0
    for t0 in range(0, N - 1, BLOCK):
        t1 = min(t0 + BLOCK, N - 1)
        w0, w1 = t0 + 1, t1 + 1
        fair = midL[t0]
        if pos == 0:
            if not np.isfinite(fair):
                continue
            bq, aq = fair * (1 - of), fair * (1 + of)
            fb = first_true(aMt[w0:w1] <= bq * (1 - TICK), w0)      # bid filled: ask traded through
            fsl = first_true(bMt[w0:w1] >= aq * (1 + TICK), w0)     # ask filled: bid traded through
            opts = [(t, sd, P) for t, sd, P in ((fb, 1, bq), (fsl, -1, aq)) if t is not None]
            if not opts:
                continue
            tau, sd, P = min(opts)
            H = hedge(tau, buy=(sd < 0))           # long maker -> sell Lighter at bid
            pos, t_o, P_o, H_o = sd, tau, P, H
            continue
        tf = t_o + W_FLAT
        aq = fair * (1 + of) if pos > 0 else fair * (1 - of)
        tc = None
        if np.isfinite(fair):
            if pos > 0:
                tc = first_true(bMt[w0:w1] >= aq * (1 + TICK), w0)
            else:
                tc = first_true(aMt[w0:w1] <= aq * (1 - TICK), w0)
        if tc is not None and tc < tf:
            tau, P_c, f_c = tc, aq, fM
        elif tf < w1:
            tau, px = taker_px(bMx if pos > 0 else aMx, max(tf, w0), N)
            if tau is None:
                continue
            P_c, f_c = px, tM
        else:
            continue
        H_c = hedge(tau, buy=(pos > 0))            # closing long -> buy back Lighter at ask
        cyc.append(1e4 * pos * ((P_c - P_o) / P_o - (H_c - H_o) / H_o) - (fM + f_c))
        pos = 0
    if pos != 0:                                    # force-close at sample end
        arr = bMx if pos > 0 else aMx
        fin = np.flatnonzero(np.isfinite(arr))
        P_c = float(arr[fin[-1]]) if fin.size else P_o
        H_c = float(midL[-1])
        cyc.append(1e4 * pos * ((P_c - P_o) / P_o - (H_c - H_o) / H_o) - (fM + tM))
    return np.asarray(cyc, float), fallback[0]


# ----------------------------------------------------------------------------- strategy runners
def run_s1(c, coin, N, tk):
    pres = [v for v in VENUES if v in c]
    for A in pres:
        for B in pres:
            if A == B:
                continue
            RT = 2 * (TAKER[A] + TAKER[B])
            for s in SIZES:
                bA = ex(c, A, 'b', s)
                aB = ex(c, B, 'a', s)
                with np.errstate(invalid='ignore', divide='ignore'):
                    sp = 1e4 * (bA - aB) / ((c[A]['mid'] + c[B]['mid']) / 2)
                for X in (0, 2, 5):
                    cand = np.flatnonzero(sp > RT + X)
                    nets = taker_pairs(c, A, B, s, cand, cf_s1, H4, N)
                    add_nets('S1', f'X={X}bps; enter spread>RT+X; exit reverse>=0; 4h timeout; taker',
                             f'{SH[A]}>{SH[B]}', coin, s, nets, tk)


def run_s2(c, coin, N, tk):
    pres = [v for v in VENUES if v in c]
    for A, B in combinations(pres, 2):
        mA, mB = c[A]['mid'], c[B]['mid']
        with np.errstate(invalid='ignore', divide='ignore'):
            g = (mA - mB) / ((mA + mB) / 2)
        z = zscore(g)
        pair = f'{SH[A]}|{SH[B]}'
        for thr in (2, 3):
            for s in SIZES:
                parts = []
                for side in (1, -1):
                    S, L = (A, B) if side > 0 else (B, A)
                    cand = np.flatnonzero(side * z > thr)
                    parts.append(taker_pairs(c, S, L, s, cand, cf_z(z, side), BIG, N))
                add_nets('S2', f'|z|>{thr} (30m roll); exit z=0 cross; taker both', pair, coin, s,
                         np.concatenate(parts), tk)
            nets = maker_pairs(c, A, B, z, thr, N)
            add_nets('S2', f'|z|>{thr} (30m roll); exit z=0 cross; maker both (limit at mid, 60s, fill rule; size-invariant)',
                     pair, coin, 100, nets, tk)


def run_s3(c, coin, N, tk, grid):
    if 'Lighter' not in c:
        return
    for M in [v for v in VENUES if v in c and v != 'Lighter']:
        for o in (3, 5, 10):
            for s in SIZES:
                cyc, fb = s3(c, M, o, s, N, grid)
                trades = 2 * cyc.size
                net = cyc.sum() / trades if trades else NAN
                pnl = float(s * cyc.sum() / 1e4)
                add_row('S3', f'offset={o}bps; quote at Lighter mid; fill=0.5bp trade-through; hedge next LTR quote; flatten 30m taker',
                        f'{SH[M]}-maker/LTR-hedge', coin, s, trades, net, pnl, tk)
                if fb:
                    LOG.append(f'S3 {coin} {SH[M]} o={o} ${s}: {fb} hedge prices fell back to mid')


def run_s4(c, coin, N, tk):
    if 'OKX' not in c:
        return
    mO = c['OKX']['mid']
    m5 = np.full(N, NAN)
    with np.errstate(invalid='ignore', divide='ignore'):
        m5[5:] = 1e4 * (mO[5:] / mO[:-5] - 1)
    for V in [v for v in VENUES if v in c and v != 'OKX']:
        f = TAKER[V]
        for s in SIZES:
            bV, aV = ex(c, V, 'b', s), ex(c, V, 'a', s)
            vb, va = np.isfinite(bV), np.isfinite(aV)
            for X in (5, 10):
                up = (m5 > X) & va
                dn = (m5 < -X) & vb
                cand = np.flatnonzero(up | dn)
                for T in (10, 30, 60):
                    nets = []
                    p, n = 0, len(cand)
                    while p < n:
                        i = int(cand[p])
                        d = 1 if up[i] else -1
                        j = exit_index(i, T, N, zc, slicer(vb if d > 0 else va))
                        if j is None:
                            p += 1
                            continue
                        if d > 0:
                            nets.append(1e4 * (bV[j] - aV[i]) / aV[i] - 2 * f)
                        else:
                            nets.append(1e4 * (bV[i] - aV[j]) / bV[i] - 2 * f)
                        p = int(np.searchsorted(cand, j + 1))
                    add_nets('S4', f'OKX mid move >{X}bps within 5s -> take lagging venue; exit after {T}s; taker both',
                             f'OKX->{SH[V]}', coin, s, np.asarray(nets), tk)


def xcorr_acc(c, N, xacc):
    if 'OKX' not in c:
        return
    mO = c['OKX']['mid']
    with np.errstate(invalid='ignore', divide='ignore'):
        rO = np.diff(mO) / mO[:-1]
    M = len(rO)
    for V in VENUES:
        if V == 'OKX' or V not in c:
            continue
        mV = c[V]['mid']
        with np.errstate(invalid='ignore', divide='ignore'):
            rV = np.diff(mV) / mV[:-1]
        for k in range(-10, 11):
            if k >= 0:
                x, y = rO[:M - k], rV[k:]
            else:
                x, y = rO[-k:], rV[:M + k]
            ok = np.isfinite(x) & np.isfinite(y)
            xs, ys = x[ok], y[ok]
            xacc[(V, k)] += [xs.size, xs.sum(), ys.sum(), (xs * xs).sum(), (ys * ys).sum(), (xs * ys).sum()]


def s5_acc(c, N, grid, s5):
    t = grid // 1000
    hl = ((t % 3600) <= 300) | ((t % 3600) >= 3300)          # +/-5 min around every full hour (HL)
    f8 = ((t % 28800) <= 300) | ((t % 28800) >= 28500)       # +/-5 min around 00/08/16 UTC (OKX, Aster)
    pres = [v for v in VENUES if v in c]
    for A, B in combinations(pres, 2):
        bA, aA = ex(c, A, 'b', 100), ex(c, A, 'a', 100)
        bB, aB = ex(c, B, 'b', 100), ex(c, B, 'a', 100)
        with np.errstate(invalid='ignore', divide='ignore'):
            e = 1e4 * np.maximum(bA - aB, bB - aA) / ((c[A]['mid'] + c[B]['mid']) / 2)
        ok = np.isfinite(e)
        key = f'{SH[A]}|{SH[B]}'
        for fam, m in (('HL hourly', hl), ('OKX/AST 00-08-16', f8)):
            for w, mask in (('in', m), ('out', ~m)):
                sel = ok & mask
                ev = e[sel]
                s5[(fam, key, w)] += [ev.sum(), np.maximum(ev, 0).sum(), ev.size, (ev > 0).sum()]


# ----------------------------------------------------------------------------- main
def main():
    df = load()
    t0 = int(df.ts_ms.min() // 1000 * 1000)
    t1 = int(df.ts_ms.max())
    grid = np.arange(t0, t1 + 1, 1000, dtype=np.int64)
    N = len(grid)
    LOG.append(f'Grid: {N} points at 1s, {pd.to_datetime(t0, unit="ms")} to {pd.to_datetime(t1, unit="ms")} UTC.')
    xacc = defaultdict(lambda: np.zeros(6))
    s5 = defaultdict(lambda: np.zeros(4))
    coin_info = []
    with np.errstate(invalid='ignore', divide='ignore'):
        for coin, g in df.groupby('coin', sort=True):
            c = build(g, grid)
            c = sanity(coin, c)
            pres = [v for v in VENUES if v in c]
            if len(pres) < 2:
                LOG.append(f'{coin}: fewer than 2 venues after sanity, skipped')
                continue
            tk = tick_bps(c)
            cross = float(np.nanmedian([np.nanmedian(c[v]['mid']) for v in pres]))
            coin_info.append((coin, pres, tk, cross))
            if 'Lighter' in c:
                mL = c['Lighter']['mid']
                for v in pres:
                    if v != 'Lighter':
                        BASIS.append((coin, v, float(np.nanmedian(1e4 * (c[v]['mid'] - mL) / mL))))
            print(f'{coin:<6} venues={",".join(SH[v] for v in pres):<22} tick={tk:9.2f} bps', flush=True)
            run_s1(c, coin, N, tk)
            run_s2(c, coin, N, tk)
            run_s3(c, coin, N, tk, grid)
            run_s4(c, coin, N, tk)
            xcorr_acc(c, N, xacc)
            s5_acc(c, N, grid, s5)
            del c, g

    # S5 rows (summary statistics in params; trades = number of 1s samples in window)
    for (fam, pair, w), v in sorted(s5.items()):
        if w != 'in':
            continue
        out_v = s5[(fam, pair, 'out')]
        mi, mo = v[0] / max(v[2], 1), out_v[0] / max(out_v[2], 1)
        ROWS.append({'strategy': 'S5', 'params': f'window={fam} (+/-5min); mean exec spread bps in={mi:.3f} out={mo:.3f}; '
                     f'mean max(spread,0) in={v[1] / max(v[2], 1):.3f} out={out_v[1] / max(out_v[2], 1):.3f}; $100 top of book',
                     'pair': pair, 'coin': 'ALL', 'size': 100, 'trades': int(v[2]), 'net_bps_per_trade': mi,
                     'pnl_usd': NAN, 'pnl_per_day_usd': NAN, 'tick_bps': NAN})

    out = pd.DataFrame(ROWS)
    cols = ['strategy', 'params', 'pair', 'coin', 'size', 'trades', 'net_bps_per_trade', 'pnl_usd',
            'pnl_per_day_usd', 'tick_bps']
    out[cols].to_csv(OUT_CSV, index=False, float_format='%.6g')
    print(f'wrote {OUT_CSV} ({len(out)} rows)', flush=True)

    write_summary(out, coin_info, xacc, s5)


# ----------------------------------------------------------------------------- summary
def fmt(x, nd=2):
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return 'n/a'
    return f'{x:,.{nd}f}'


def md_table(header, rows):
    lines = ['| ' + ' | '.join(header) + ' |', '|' + '|'.join(['---'] * len(header)) + '|']
    for r in rows:
        lines.append('| ' + ' | '.join(str(x).replace('|', '\\|') for x in r) + ' |')
    return '\n'.join(lines)


def write_summary(out, coin_info, xacc, s5):
    t = out[out.strategy.isin(['S1', 'S2', 'S3', 'S4'])].copy()
    t['nt'] = t.trades * t.net_bps_per_trade.fillna(0.0)
    t['day_ok'] = np.where(t.tick_bps > TICK_LIMIT_BPS, 0.0, t.pnl_per_day_usd)
    a = t.groupby(['strategy', 'params', 'pair', 'size'], sort=False).agg(
        coins=('coin', 'nunique'), trades=('trades', 'sum'), med_trades=('trades', 'median'),
        nt=('nt', 'sum'), day=('pnl_per_day_usd', 'sum'), day_ok=('day_ok', 'sum')).reset_index()
    a['net_bps'] = a.nt / a.trades.replace(0, np.nan)

    L = []
    L.append('# Cross-venue perp spread backtests: 2026-11-26 order-book sample\n')
    L.append('Script: `hf/spread_hf.py`. Rows: `hf/results_hf.csv`. Per-day figures = 8h sample x 24/8 (x3).\n')
    L.append('Net bps are per trade on one leg notional (size $), after taker or maker fees per side. '
             'pnl_usd = sum over trades of size x net bps / 1e4. Pair labels: `X>Y` = sell X, buy Y (S1, S4 = OKX-led); '
             '`X|Y` = both directions of the pair (S2); `M-maker/LTR-hedge` = S3.\n')
    L.append('## Data and method\n')
    for line in LOG:
        L.append(f'- {line}')
    L.append('- Venues: OKX, Kraken, Hyperliquid, Aster, Lighter. Depth columns (*_1k, *_10k) exist only for '
             'Hyperliquid and Lighter. For OKX, Kraken and Aster, $1k and $10k trades use top-of-book price and '
             'are taken only if top-of-book notional covers the size.')
    L.append('- Sanity filter: venue medians vs cross-venue median; clean 10/100/1000 factors rescaled, others dropped.')
    for line in SANITY:
        L.append(f'  - {line}')
    if not SANITY:
        L.append('  - No venue/coin pairs needed rescaling or dropping.')
    L.append('')
    rows = []
    for coin, pres, tk, cross in coin_info:
        flag = 'TICK-LIMITED' if np.isfinite(tk) and tk > TICK_LIMIT_BPS else ''
        rows.append([coin, ','.join(SH[v] for v in pres), fmt(cross, 6), fmt(tk, 2), flag])
    L.append('## Coins (price tick in bps; coins with tick > 1 bp are flagged as quantisation-limited)\n')
    L.append(md_table(['coin', 'venues used', 'cross-venue mid', 'tick bps', 'flag'], rows))
    L.append('')

    L.append('## Venue basis vs Lighter mid (median over time, bps; median across coins)\n')
    L.append('S3 quotes are centred on Lighter mid, so a persistent venue basis shifts every maker quote. '
             'S2 and S1 are mostly basis-neutral.\n')
    rows = []
    for v in ['OKX', 'Kraken', 'Hyperliquid', 'Aster']:
        vals = [b for _, vv, b in BASIS if vv == v]
        if vals:
            rows.append([SH[v], len(vals), fmt(float(np.median(vals)), 2), fmt(float(np.min(vals)), 2),
                         fmt(float(np.max(vals)), 2)])
    L.append(md_table(['venue', 'coins', 'median basis', 'min across coins', 'max across coins'], rows))
    L.append('')

    L.append('## Best config per strategy and size (by $/day summed over coins)\n')
    best = a.loc[a.groupby(['strategy', 'size'])['day'].idxmax()]
    rows = []
    for strat in ['S1', 'S2', 'S3', 'S4']:
        cells = [strat]
        for s in SIZES:
            r = best[(best.strategy == strat) & (best['size'] == s)]
            if len(r):
                r = r.iloc[0]
                cells.append(f'{fmt(r.day)} ({r.params.split(";")[0]}, {r.pair})')
            else:
                cells.append('n/a')
        rows.append(cells)
    L.append(md_table(['strategy', '$100', '$1k', '$10k'], rows))
    L.append('')

    for s in SIZES:
        L.append(f'## Top 15 configs by $/day at ${s:,}\n')
        top = a[a['size'] == s].sort_values('day', ascending=False).head(15)
        rows = []
        for k, (_, r) in enumerate(top.iterrows(), 1):
            rows.append([k, r.strategy, r.params, r.pair, fmt(r.day), fmt(r.day_ok), fmt(r.med_trades, 0),
                         fmt(r.trades, 0), fmt(r.net_bps)])
        L.append(md_table(['#', 'strategy', 'params', 'pair', '$/day (all coins)', '$/day (ex tick-limited)',
                           'median trades/coin', 'total trades', 'net bps/trade (pooled)'], rows))
        L.append('')

    L.append('## S4 lead-lag: Pearson corr of 1s returns, OKX_t vs venue_{t+k} (pooled over coins)\n')
    L.append('Positive k: venue lags OKX. Negative k: venue leads OKX. Returns use forward-filled quotes.\n')
    lags = [-10, -5, -3, -1, 0, 1, 2, 3, 5, 7, 10]
    rows = []
    for V in ['Kraken', 'Hyperliquid', 'Aster', 'Lighter']:
        cells = [SH[V]]
        best_k, best_r = None, -9
        for k in range(-10, 11):
            v = xacc.get((V, k))
            if v is None:
                continue
            n, sx, sy, sxx, syy, sxy = v
            num = n * sxy - sx * sy
            den = np.sqrt((n * sxx - sx * sx) * (n * syy - sy * sy))
            r = num / den if den > 0 else NAN
            if np.isfinite(r) and k >= 0 and r > best_r:
                best_k, best_r = k, r
            if k in lags:
                cells.append(f'{r:.3f}')
        cells.append(f'lag {best_k}s ({best_r:.3f})' if best_k is not None else 'n/a')
        rows.append(cells)
    L.append(md_table(['venue'] + [f'k={k}' for k in lags] + ['max over k>=0'], rows))
    L.append('')
    L.append('Most correlation sits at k=0 and k=1 to 2. On a 1s grid with forward-filled quotes this reflects '
             'near-simultaneous moves and poll timing, so it cannot resolve sub-second lead-lag or prove that OKX leads.\n')

    L.append('## S5 funding windows: executable spread (bps, $100 top of book), in-window vs out\n')
    rows = []
    for (fam, pair, w), v in sorted(s5.items()):
        if w != 'in':
            continue
        o = s5[(fam, pair, 'out')]
        rows.append([fam, pair, int(v[2]), fmt(v[0] / max(v[2], 1), 3), fmt(o[0] / max(o[2], 1), 3),
                     fmt(v[1] / max(v[2], 1), 3), fmt(o[1] / max(o[2], 1), 3)])
    L.append(md_table(['window', 'pair', 'in-window samples (s)', 'mean in', 'mean out', 'mean max(.,0) in',
                       'mean max(.,0) out'], rows))
    L.append('')
    L.append('Only one 00/08/16 UTC event (08:00) falls in the sample, so the OKX/AST window statistics rest on '
             'about 10 minutes of data. The HL hourly family has 8 events (02:00 to 09:00 UTC).\n')

    L.append('## Caveats\n')
    L.append('- 8h sample (01:11 to 09:05 UTC, one day). Results are not a multi-day estimate; per-day numbers are an '
             'extrapolation of 8h x 3, and intraday regimes differ.')
    L.append('- Polling gaps: Hyperliquid was rate-limited (HTTP 429) during collection (see collect.log), and quote '
             'staleness limits (8s, 12s Lighter) drop periods where a venue is silent. Entries are skipped in those periods.')
    L.append('- Price precision: many low-priced coins are quoted to 4 to 6 decimals, so one tick is several bps '
             '(PEPE about 2500 bps). Tick-limited coins (> 1 bp) produce meaningless bps and are excluded from the '
             '"ex tick-limited" column. The all-coins column is still shown as requested.')
    L.append('- Depth: only Hyperliquid and Lighter have $1k and $10k depth. OKX, Kraken and Aster use top-of-book '
             'prices with a notional check, so their $1k and $10k fills are optimistic (no walking the book) and '
             'many larger trades are skipped.')
    L.append('- No queue position. Maker fills use the trade-through rule: a bid fills only when a later ask prints '
             '0.5 bp through the quote, and an ask only when a later bid prints 0.5 bp through it. This is a conservative '
             'approximation, not a fill model. It ignores queue position, partial fills and cancel latency. S2 maker-maker '
             'uses limits at mid with a 60s life and taker fallback. It is size-invariant (top of book).')
    L.append('- Hedge latency: S3 hedges at the next Lighter quote after the fill. Adverse selection is captured by '
             'the price move to that quote. Inventory is limited to one unit.')
    L.append('- Not modelled: perp funding payments (S1, S2 and S3 hold for up to 4h or 30min), borrow for short legs, '
             'margin and liquidation, withdrawal or transfer costs, and fees beyond the stated schedule.')
    L.append('- Taker S1 and S2 exits: S1 exits when closing now is non-negative in gross price terms (4h timeout). S2 '
             'holds until z crosses zero, with no timeout, so trades can be long. These are the stated rules, and '
             'they are not optimised.')
    L.append('- S3 result is driven partly by venue basis, not only by fills. Kraken trades a median of about 2.5 bps below '
             'Lighter across coins (BTC about 7.6 bps below), with a per-coin range of roughly -11 to +10 bps. The maker '
             'quote is centred on Lighter mid, so the basis shifts it against the maker venue. A basis-adjusted fair value '
             'was not tested.')
    L.append('- S4 is directional on the lagging venue: no hedge, shorts on Kraken, Aster, HL and Lighter are assumed '
             'borrowable, and round-trip taker fees are charged on that single leg.')
    L.append('- Lead-lag correlations use forward-filled quotes, so update cadence (2s, 4s, 6s) can create lag structure '
             'that is not real lead-lag. Pearson is also sensitive to outlier 1s returns.')
    L.append('- Trades are not independent across coins. S4 signals fire together when OKX moves market-wide, so per-coin '
             'counts overstate the number of independent bets. The pooled $/day figures are dominated by a few '
             'high-volatility windows.')
    L.append('- Sample size: many configs have few trades. The top-15 ranking is noisy and should not be read as a '
             'selected edge without out-of-sample confirmation.')
    L.append('- S5 uses top-of-book executable spreads only and tests three-window samples, which is too thin for a conclusion.')
    with open(OUT_MD, 'w') as f:
        f.write('\n'.join(L) + '\n')
    print(f'wrote {OUT_MD}', flush=True)

    print('\nBest per strategy (summed $/day):')
    for _, r in best.sort_values(['strategy', 'size']).iterrows():
        print(f'  {r.strategy} ${r["size"]:>6} {r.day:12.2f} $/day  {r.params.split(";")[0]} | {r.pair} | trades={int(r.trades)} | net={r.net_bps:.2f} bps')


if __name__ == '__main__':
    with np.errstate(all='ignore'):
        main()
