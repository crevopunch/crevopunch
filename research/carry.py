"""Funding-carry economics per coin x venue pair (excl. dYdX: books too thin).
Cost = 2 x (taker fee A + taker fee B) + 2 x (VWAP slippage vs mid, A and B) at given size.
Fees (bps, base tier): verified HL 4.5, Aster 4.0, Lighter Std 0; CEX OKX 5.0 / Kraken 5.0 UNVERIFIED (standard published base rates)."""
import csv,collections as c
FEE={'OKX':5.0,'Kraken':5.0,'Hyperliquid':4.5,'Aster':4.0,'Lighter':0.0}
F={(r['coin'],r['venue']):r for r in csv.DictReader(open('data/funding.csv'))}
S=c.defaultdict(dict)
for r in csv.DictReader(open('data/depth.csv')):
    if r['status']=='ok': S[(r['coin'],r['venue'])].setdefault(float(r['notional_usd']),[]).append(float(r['slippage_bps']))
V=list(FEE);rows=[]
coins=sorted({k[0] for k in F})
for co in coins:
  for i,a in enumerate(V):
    for b in V[i+1:]:
      fa,fb=F.get((co,a)),F.get((co,b))
      if not fa or not fb or not fa['hist_mean_ann_pct'] or not fb['hist_mean_ann_pct']: continue
      ma,mb=float(fa['hist_mean_ann_pct']),float(fb['hist_mean_ann_pct'])
      sa,sb=float(fa['hist_std_ann_pct']),float(fb['hist_std_ann_pct'])
      diff=abs(ma-mb)
      if diff<15 or max(sa,sb)>300: continue  # drop spikes (e.g. MNT Kraken std 2050%)
      short,long_=(a,b) if ma>mb else (b,a)
      out={'coin':co,'short':short,'long':long_,'diff_ann':round(diff,1),'std_max':round(max(sa,sb),1),
           'cur_diff_ann':round(abs(float(F[(co,short)]['current_ann_pct'])-float(F[(co,long_)]['current_ann_pct'])),1) if True else 0,
           'cur_same_sign':(float(F[(co,short)]['current_ann_pct'])-float(F[(co,long_)]['current_ann_pct']))>0}
      daily=diff/365*100  # bps/day
      out['bps_day']=round(daily,1)
      for n in (1000.0,10000.0):
        try: slip=sum(sum(S[(co,v)][n])/len(S[(co,v)][n]) for v in (a,b))
        except KeyError: slip=None
        if slip is None: continue
        cost=2*(FEE[a]+FEE[b])+2*slip
        out[f'cost_bps_{int(n)}']=round(cost,1); out[f'be_days_{int(n)}']=round(cost/daily,1)
        out[f'net7d_usd_{int(n)}']=round(n*(7*daily-cost)/1e4,2); out[f'net30d_usd_{int(n)}']=round(n*(30*daily-cost)/1e4,2)
      rows.append(out)
rows.sort(key=lambda r:-r.get('net30d_usd_10000',-1e9))
k=list(rows[0].keys()); 
with open('data/carry.csv','w') as f:
  w=csv.DictWriter(f,fieldnames=sorted({x for r in rows for x in r},key=lambda x:(k+[x]).index(x)));w.writeheader();w.writerows(rows)
for r in rows[:22]: print(r)
