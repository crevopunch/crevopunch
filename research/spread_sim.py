"""Hindsight-optimistic spread-trade simulation on the 30 live samples.
For each coin x venue pair and direction: enter at the sample with the best executable entry spread
(sell rich venue bid, buy cheap venue ask), exit at the BEST later sample (buy back rich ask, sell cheap bid).
gross = entry_edge + exit_edge (bps of mid); net = gross - 2*(takerA+takerB). Top-of-book only (=$100-1k size)."""
import csv,collections as c,itertools as it
FEE={'OKX':5.0,'Kraken':5.0,'Hyperliquid':4.5,'Aster':4.0,'Lighter':0.0,'dYdX':5.0}
B=c.defaultdict(dict)
for r in csv.DictReader(open('data/samples.csv')):
    try: b,a=float(r['bid']),float(r['ask'])
    except: continue
    if b>0 and a>0: B[(r['coin'],r['venue'])][r['ts']]=(b,a)
coins={k[0] for k in B}; res=[]
for co in coins:
  vs=[v for v in FEE if (co,v) in B]
  for x,y in it.permutations(vs,2):   # short x (rich), long y (cheap)
    ts=sorted(set(B[(co,x)])&set(B[(co,y)]))
    if len(ts)<10: continue
    m=lambda t:(sum(B[(co,x)][t])+sum(B[(co,y)][t]))/4
    if not 0.67<B[(co,x)][ts[0]][0]/B[(co,y)][ts[0]][0]<1.5: continue
    ent=[(B[(co,x)][t][0]-B[(co,y)][t][1])/m(t)*1e4 for t in ts]
    ex=[(B[(co,y)][t][0]-B[(co,x)][t][1])/m(t)*1e4 for t in ts]
    best=max((ent[i]+max(ex[i+1:]),i) for i in range(len(ts)-1))
    fee=2*(FEE[x]+FEE[y])
    res.append((round(best[0]-fee,1),round(best[0],1),fee,co,'short '+x,'long '+y))
res.sort(reverse=True)
pos=[r for r in res if r[0]>0]
print(f'{len(res)} directional coin-pairs; {len(pos)} positive net even with perfect hindsight')
for r in res[:15]: print(r)
nd=[r for r in res if 'dYdX' not in r[4]+r[5]]
import statistics as s; print('median hindsight gross (excl dYdX) %.1f bps'%s.median([r[1] for r in nd]))
