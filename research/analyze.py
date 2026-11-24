#!/usr/bin/env python3
"""Analyse data/samples.csv and data/funding.csv -> data/summary.md and data/pairs_stats.csv (stdlib only)."""
import csv
import itertools
import json
import os
import statistics
from collections import defaultdict

DATA = '/home/user/crevopunch/research/data'
VENUES = ['OKX', 'Kraken', 'Hyperliquid', 'Aster', 'Lighter', 'dYdX']
THR = [0, 10, 20, 30]
MISMATCH_RATIO = 1.5  # coin-pairs whose mid ratio exceeds this are symbol/unit mismatches, excluded from rankings


def pct(xs, p):
    xs = sorted(xs)
    if not xs:
        return None
    k = (len(xs) - 1) * p
    lo, hi = int(k), min(int(k) + 1, len(xs) - 1)
    return xs[lo] + (xs[hi] - xs[lo]) * (k - lo)


def f2(x, d=2):
    return '' if x is None else f'{x:.{d}f}'


def fnum(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


q = defaultdict(dict)  # (coin, venue) -> {ts: (bid, ask)}
all_ts = set()
for r in csv.DictReader(open(os.path.join(DATA, 'samples.csv'))):
    q[(r['coin'], r['venue'])][r['ts']] = (float(r['bid']), float(r['ask']))
    all_ts.add(r['ts'])
fund = {(r['coin'], r['venue']): r for r in csv.DictReader(open(os.path.join(DATA, 'funding.csv')))}
win = json.load(open(os.path.join(DATA, 'window.json')))
coins = sorted({c for c, _ in q})

pairs, raw = [], {}  # raw[(coin, A, B)] = (gaps, execs)
for c in coins:
    for A, B in itertools.combinations(VENUES, 2):
        if (c, A) not in q or (c, B) not in q:
            continue
        common = sorted(set(q[(c, A)]) & set(q[(c, B)]))
        if not common:
            continue
        gaps, execs, ratios = [], [], []
        for t in common:
            bA, aA = q[(c, A)][t]
            bB, aB = q[(c, B)][t]
            mA, mB = (bA + aA) / 2, (bB + aB) / 2
            m = (mA + mB) / 2
            gaps.append(abs(mA - mB) / m * 1e4)
            execs.append(max(bA - aB, bB - aA) / m * 1e4)
            ratios.append(mA / mB)
        raw[(c, A, B)] = (gaps, execs)
        fA, fB = fund.get((c, A), {}), fund.get((c, B), {})
        mA_ann, mB_ann = fnum(fA.get('hist_mean_ann_pct')), fnum(fB.get('hist_mean_ann_pct'))
        fdiff = mA_ann - mB_ann if mA_ann is not None and mB_ann is not None else None
        side = '' if fdiff is None else (f'short {A} / long {B}' if fdiff > 0 else f'short {B} / long {A}')
        ratio = statistics.median(ratios)
        pairs.append(dict(
            coin=c, pair=f'{A}-{B}', A=A, B=B, n=len(common),
            gap_med=statistics.median(gaps), gap_p90=pct(gaps, 0.9),
            exec_med=statistics.median(execs), exec_p90=pct(execs, 0.9), exec_max=max(execs),
            **{f'gt{t}': 100 * sum(1 for x in execs if x > t) / len(execs) for t in THR},
            ratio=ratio, flag=(ratio > MISMATCH_RATIO or ratio < 1 / MISMATCH_RATIO),
            fA=mA_ann, fB=mB_ann, fdiff=fdiff, side=side))

ok = [p for p in pairs if not p['flag']]
with open(os.path.join(DATA, 'pairs_stats.csv'), 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['coin', 'pair', 'n', 'abs_gap_med_bps', 'abs_gap_p90_bps', 'exec_med_bps', 'exec_p90_bps',
                'exec_max_bps', 'pct_exec_gt0', 'pct_exec_gt10', 'pct_exec_gt20', 'pct_exec_gt30',
                'mid_ratio_med', 'flag_mismatch', 'fund_A_ann_pct_7d', 'fund_B_ann_pct_7d', 'fund_diff_A_minus_B_ann_pct', 'trade'])
    for p in pairs:
        w.writerow([p['coin'], p['pair'], p['n'], f2(p['gap_med'], 3), f2(p['gap_p90'], 3), f2(p['exec_med'], 3),
                    f2(p['exec_p90'], 3), f2(p['exec_max'], 3), f2(p['gt0'], 1), f2(p['gt10'], 1), f2(p['gt20'], 1),
                    f2(p['gt30'], 1), f2(p['ratio'], 4), 'Y' if p['flag'] else 'N', f2(p['fA'], 3), f2(p['fB'], 3),
                    f2(p['fdiff'], 3), p['side']])

L = []
A_ = L.append
ts_sorted = sorted(all_ts)
A_('# Cross-venue perp arbitrage: live sampling summary')
A_('')
A_(f'- Sampling window (UTC): **{win.get("start_utc")} to {win.get("end_utc", "in progress")}**; '
   f'first/last sample ts {ts_sorted[0]} / {ts_sorted[-1]}; {len(ts_sorted)} samples, 60 s apart.')
A_(f'- Coins: {len(coins)} with at least one sampled venue, top-50 by CoinGecko rank that list on 2+ venues. '
   f'Venues: {", ".join(VENUES)}. Coin-venue pairs compared: {len(pairs)} ({len(ok)} after mismatch filter).')
A_('- Mid gap = |mA - mB| / avg mid. Executable spread = max(bidA - askB, bidB - askA) / avg mid. Both in bps, gross of fees, '
   'top-of-book only, no transfer or funding-timing costs.')
A_('- Funding: annualised = rate x 8760 / interval_h x 100. Differential = 7d mean of per-period annualised rates. '
   'Positive A-B => short A, long B.')
A_('- Sign conventions: positive rate = longs pay shorts. Lighter history sign taken from `direction` (long = +).')
A_(f'- Mismatch filter: coin-pairs whose median mid ratio is outside 1/{MISMATCH_RATIO}..{MISMATCH_RATIO} are excluded from rankings '
   '(symbol identity or unit issue).')
A_('')
flagged = sorted({(p['coin'], p['pair'], round(p['ratio'], 3)) for p in pairs if p['flag']})
if flagged:
    A_('**Excluded as mismatched:** ' + '; '.join(f'{c} {pr} (mid ratio {r})' for c, pr, r in flagged))
    A_('')

A_('## Pooled by venue pair (all coins, ok pairs only)')
A_('')
A_('| pair | coin-pairs | samples | med abs gap | exec med | exec p90 | exec max | >0 % | >10 % | >20 % | >30 % |')
A_('|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|')
for A, B in itertools.combinations(VENUES, 2):
    rows = [p for p in ok if p['A'] == A and p['B'] == B]
    if not rows:
        continue
    keys = [(p['coin'], A, B) for p in rows]
    ex_pool = [x for k in keys for x in raw[k][1]]
    gap_pool = [x for k in keys for x in raw[k][0]]
    n_all = len(ex_pool)
    A_(f'| {A}-{B} | {len(rows)} | {n_all} | {f2(statistics.median(gap_pool), 1)} | {f2(statistics.median(ex_pool), 1)} | '
       f'{f2(pct(ex_pool, 0.9), 1)} | {f2(max(ex_pool), 1)} | ' +
       ' | '.join(f2(100 * sum(1 for x in ex_pool if x > t) / n_all, 1) for t in THR) + ' |')
A_('')
A_('(Pooled over all samples including flagged coin-pairs, so use the per-pair rows for ranking.)')
A_('')

hdr = ('| # | coin | pair | n | med abs gap | exec med | exec p90 | exec max | >0 % | >10 % | >20 % | >30 % | '
       'fund diff 7d (ann %) | trade |')
A_('## Top 25 by p90 executable spread (bps)')
A_('')
A_(hdr)
A_('|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|')
for i, p in enumerate(sorted(ok, key=lambda p: -p['exec_p90'])[:25], 1):
    A_(f'| {i} | {p["coin"]} | {p["pair"]} | {p["n"]} | {f2(p["gap_med"], 1)} | {f2(p["exec_med"], 1)} | '
       f'{f2(p["exec_p90"], 1)} | {f2(p["exec_max"], 1)} | {f2(p["gt0"], 0)} | {f2(p["gt10"], 0)} | '
       f'{f2(p["gt20"], 0)} | {f2(p["gt30"], 0)} | {f2(p["fdiff"], 2)} | {p["side"]} |')
A_('')
A_('## Top 25 by 7d funding differential (annualised %, absolute)')
A_('')
A_('| # | coin | pair | fund diff (ann %) | A ann mean | B ann mean | trade | exec p90 (bps) |')
A_('|---:|---|---|---:|---:|---:|---|---:|')
fund_rows = [p for p in ok if p['fdiff'] is not None]
for i, p in enumerate(sorted(fund_rows, key=lambda p: -abs(p['fdiff']))[:25], 1):
    A_(f'| {i} | {p["coin"]} | {p["pair"]} | {f2(p["fdiff"], 2)} | {f2(p["fA"], 2)} | {f2(p["fB"], 2)} | '
       f'{p["side"]} | {f2(p["exec_p90"], 1)} |')
A_('')
A_('Full per coin x venue-pair table (all metrics, incl. flagged rows): `data/pairs_stats.csv`. '
   'Raw data: `data/samples.csv`, `data/depth.csv`, `data/funding.csv`, `data/listings.csv`.')
open(os.path.join(DATA, 'summary.md'), 'w').write('\n'.join(L) + '\n')
print(f'summary.md: {len(L)} lines, {len(pairs)} pairs, {len(ok)} ok')
