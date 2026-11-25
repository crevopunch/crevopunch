#!/bin/bash
# Rows per venue over the last 5 minutes, and the last 5 errors from the collector log.
D="$(cd "$(dirname "$0")" && pwd)"
python3 -I - "$D" <<'PY'
import csv, glob, gzip, os, sys, time, collections
D = sys.argv[1]
cut = time.time() * 1000 - 300_000
cnt = collections.Counter()
for p in sorted(glob.glob(os.path.join(D, 'data', '*.csv.gz')))[-2:]:
    try:
        with gzip.open(p, 'rt') as f:
            for r in csv.DictReader(f):
                try:
                    if float(r['ts_ms']) >= cut:
                        cnt[r['venue']] += 1
                except (ValueError, KeyError):
                    pass
    except (EOFError, OSError) as e:  # file still being written
        pass
print('rows last 5 min:')
for v in ['OKX', 'Kraken', 'Hyperliquid', 'Aster', 'Lighter']:
    print(f'  {v:<12} {cnt[v]}')
PY
echo "last 5 errors:"
grep ' ERR ' "$D/collect.log" 2>/dev/null | tail -5 | cut -c1-220
