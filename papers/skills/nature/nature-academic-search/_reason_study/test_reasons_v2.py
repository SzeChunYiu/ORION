#!/usr/bin/env python3
"""
REASON STUDY v2 - rigorous reason tester.
Fixes: (a) correct shuffle null (permute direction -> recompute won+cost);
       (b) baseline control = incremental edge over R0 favorite-momentum on the
           OVERLAP; (c) residual-sign mechanism (does the reason predict the
           residual direction, beyond fav_move+ste?).
"""
import pandas as pd, numpy as np, os
from scipy import stats
OUT = os.path.expanduser("~/polymarket_crypto/research/study_reason_signals")
F = pd.read_parquet(f"{OUT}/entries_features.parquet")
F["day"]=pd.to_datetime(F.end_ts,unit="s").dt.date.astype(str)
days=sorted(F.day.unique()); half=len(days)//2
tr_days,te_days=set(days[:half]),set(days[half:])
SPREAD=0.015
print(f"{len(F)} entries, {len(days)} days")

P=F.partial_move_pct.values; FM=F.fav_move_kl.values; STE=F.ste.values
RES=F.residual_move_pct.values; FULL=F.full_move_pct.values
BTC30=F.btc_ret_30s.values;BTC60=F.btc_ret_60s.values;BTC120=F.btc_ret_120s.values;BTC180=F.btc_ret_180s.values;BTC300=F.btc_ret_300s.values
C30=F.ret_30s.values;C60=F.ret_60s.values;C120=F.ret_120s.values;C180=F.ret_180s.values;C300=F.ret_300s.values
ACCEL=F.accel.values;VOL=F.vol_spike_1m.values;TIMB=F.taker_imb_1m.values
DH=F.dist_high_30m.values;DL=F.dist_low_30m.values;RNG=F.rng_30m_pct.values;SIG=F.sigma.values
UPW=F.up_wins.values
sgn=lambda x: np.where(x>=0,"UP","DOWN")
upw_arr = UPW.copy()

def cost_of(is_fav, ask_sub): return np.where(is_fav, ask_sub, 1.0-ask_sub+SPREAD)

def eval_reason(mask, direction, name, baseline_mask=None):
    idx=np.where(mask)[0]
    if len(idx)<30: return None
    d=direction[idx]; sub=F.iloc[idx].copy()
    ask_sub=sub.ask.values
    fav_dir=np.where(sub.partial_move_pct.values>=0,"UP","DOWN")
    is_fav=(d==fav_dir)
    won=((d=="UP")&sub.up_wins.values)|((d=="DOWN")&(~sub.up_wins.values))
    cost=cost_of(is_fav,ask_sub)
    edge=(won.astype(float)-cost)*100
    me=edge.mean(); se=edge.std(ddof=1)/np.sqrt(len(edge)); z=me/se if se>0 else 0
    # ---- correct shuffle null: permute DIRECTION (recompute won + cost) ----
    rng=np.random.default_rng(42); nulls=np.empty(2000)
    fav_frac=is_fav.mean()
    for i in range(2000):
        dp=rng.permutation(d)
        isf=(dp==fav_dir)
        w=((dp=="UP")&sub.up_wins.values)|((dp=="DOWN")&(~sub.up_wins.values))
        ct=cost_of(isf,ask_sub)
        nulls[i]=(w.astype(float)-ct).mean()*100
    p=(np.abs(nulls)>=abs(me)).mean()
    # OOS
    sd=sub.day.values; intr=sd.astype(str).isin([str(x) for x in tr_days])
    etr=edge[intr].mean() if intr.any() else np.nan
    ete=edge[~intr].mean() if (~intr).any() else np.nan
    oos=(np.sign(etr)==np.sign(ete)) and (ete>0) if not np.isnan(ete) else False
    # residual-sign prediction: corr(direction_sign, residual)
    dsign=np.where(d=="UP",1,-1); ressub=RES[idx]
    resid_corr=np.corrcoef(dsign,ressub)[0,1] if np.std(ressub)>0 else 0
    out=dict(name=name,n=len(idx),wr=round(float(won.mean()),4),fav_frac=round(float(fav_frac),3),
             mean_cost=round(float(cost.mean()),4),net_c=round(float(me),3),se=round(float(se),3),z=round(float(z),2),
             shuf_p=round(float(p),4),etr=round(float(etr),2),ete=round(float(ete),2),oos=bool(oos),
             resid_corr=round(float(resid_corr),3))
    # ---- baseline control: incremental over R0 on the overlap ----
    if baseline_mask is not None:
        bo=np.where(mask & baseline_mask)[0]
        if len(bo)>=30:
            # within overlap, split by reason-direction vs not. Measure edge of this reason's
            # population (all overlap is R0-fav already); compare WR when reason fires vs R0-only.
            # Simpler: on overlap, does reason-direction (a subset choice) lift WR over always-fav?
            r0fav=np.where(F.partial_move_pct.values[bo]>=0,"UP","DOWN")
            r0won=((r0fav=="UP")&upw_arr[bo])|((r0fav=="DOWN")&(~upw_arr[bo]))
            ask_bo=F.ask.values[bo]
            r0cost=cost_of(np.ones(len(bo),bool),ask_bo); r0edge=(r0won.astype(float)-r0cost)*100
            db=direction[bo]; isfb=(db==r0fav)
            wonb=((db=="UP")&upw_arr[bo])|((db=="DOWN")&(~upw_arr[bo]))
            costb=cost_of(isfb,ask_bo); bedge=(wonb.astype(float)-costb)*100
            out["r0_overlap_n"]=len(bo); out["r0_edge_c"]=round(float(r0edge.mean()),3)
            out["reason_edge_on_overlap_c"]=round(float(bedge.mean()),3)
            out["increment_c"]=round(float(bedge.mean()-r0edge.mean()),3)
    return out

# R0 baseline: favorite momentum ste in [60,150], fav>=0.05
R0mask=(FM>=0.05)&(STE>=60)&(STE<=150)
print(f"R0 baseline n={R0mask.sum()}")

res=[]
# ---- R0 baseline characterization ----
res.append(eval_reason(R0mask,sgn(P),"R0_BASELINE_fm.05_ste60_150"))
# variations
for fm in [0.05,0.08,0.12]:
  for a,b in [(30,90),(60,120),(90,150),(120,210)]:
    m=(FM>=fm)&(STE>=a)&(STE<=b); r=eval_reason(m,sgn(P),f"R0_fm{fm}_ste{a}_{b}")
    if r: res.append(r)

# ---- R1 BTC lead/lag (follow BTC dir on coin) ----
for lb_name,lb in [("60",BTC60),("120",BTC120),("180",BTC180),("300",BTC300)]:
  for thr in [0.03,0.06,0.10,0.15]:
    m=(np.abs(lb)>=thr)&(~np.isnan(lb)); r=eval_reason(m,sgn(lb),f"R1_btclead{lb_name}_t{thr}",R0mask)
    if r: res.append(r)
# R1b gap: btc moved, coin lagged, bet coin in btc dir
for lb_name,btc,coi in [("60",BTC60,C60),("120",BTC120,C120),("180",BTC180,C180)]:
  for thr in [0.04,0.08,0.12]:
    gap=btc-coi; m=(btc>=thr)&(gap>=thr*0.4)&(~np.isnan(gap))
    r=eval_reason(m,sgn(btc),f"R1b_gap{lb_name}_t{thr}",R0mask)
    if r: res.append(r)
# R1c BTC lead REVERSAL test: does BTC opposite-coin predict coin reversal? (null check)
for thr in [0.06,0.10]:
    m=(np.abs(BTC120)>=thr)&(~np.isnan(BTC120))
    r=eval_reason(m,np.where(BTC120>=0,"DOWN","UP"),f"R1c_btcrev120_t{thr}",R0mask)
    if r: res.append(r)

# ---- R2 rejection: at 30m high, dropped -> DOWN; at low, bounced -> UP ----
for dh in [-0.02,-0.05,-0.10]:
  for drop in [-0.02,-0.05,-0.10]:
    m=(DH>=dh)&(C60<=drop)&(~np.isnan(DH)); r=eval_reason(m,np.where(m,"DOWN","UP"),f"R2_rejHi_dh{dh}_d{drop}",R0mask)
    if r: res.append(r)
for dl in [0.02,0.05,0.10]:
  for bnc in [0.02,0.05,0.10]:
    m=(DL<=dl)&(C60>=bnc)&(~np.isnan(DL)); r=eval_reason(m,np.where(m,"UP","DOWN"),f"R2b_bncLo_dl{dl}_b{bnc}",R0mask)
    if r: res.append(r)

# ---- R3 acceleration ----
for acc in [0.01,0.03,0.05,0.08]:
    m=(np.abs(ACCEL)>=acc)&(np.sign(ACCEL)==np.sign(C60))&(~np.isnan(ACCEL))
    r=eval_reason(m,sgn(C60),f"R3_accel{acc}",R0mask)
    if r: res.append(r)

# ---- R4 volume spike + taker imbalance ----
for vs in [1.5,2.0,3.0]:
  for ti in [0.1,0.3,0.5]:
    m=(VOL>=vs)&(np.abs(TIMB)>=ti)&(~np.isnan(VOL)); r=eval_reason(m,sgn(TIMB),f"R4_vol{vs}_ti{ti}",R0mask)
    if r: res.append(r)

# ---- R5 range/rejection composite: tight 30m range + break ----
for rg in [0.1,0.2,0.4]:
  m=(RNG<=rg)&(np.abs(C60)>=0.03)&(~np.isnan(RNG)); r=eval_reason(m,sgn(C60),f"R5_rangebreak_rg{rg}",R0mask)
  if r: res.append(r)

# ---- R7 overextension reversal (bet dog) ----
for fm in [0.15,0.20,0.30,0.40]:
    m=(FM>=fm); dog=np.where(P>=0,"DOWN","UP"); r=eval_reason(m,dog,f"R7_overext_fm{fm}",R0mask)
    if r: res.append(r)

# ---- R8 vol regime x fav ----
for sg in [0.05,0.10,0.20,0.40]:
    m=(SIG<=sg)&(FM>=0.05)&(STE>=60)&(STE<=150); r=eval_reason(m,sgn(P),f"R8_LOWVOL_fav_sg{sg}",R0mask)
    if r: res.append(r)
for sg in [0.20,0.40,0.80]:
    m=(SIG>=sg)&(FM>=0.05)&(STE>=60)&(STE<=150); r=eval_reason(m,sgn(P),f"R8_HIVOL_fav_sg{sg}",R0mask)
    if r: res.append(r)

R=pd.DataFrame(res).dropna(subset=["net_c"]).sort_values("net_c",ascending=False)
R.to_csv(f"{OUT}/reason_results_t1_v2.csv",index=False)
pd.set_option("display.width",220,"display.max_columns",40)
print("\n=== TOP 20 by net edge (all reasons) ===")
print(R.head(20).to_string(index=False))
print("\n=== PASS GATE: shuf_p<0.05 & oos & n>=60 & net_c>0 ===")
g=R[(R.shuf_p<0.05)&(R.oos==True)&(R.n>=60)&(R.net_c>0)].sort_values("net_c",ascending=False)
print(g.to_string(index=False)); print("pass count:",len(g))
print("\n=== INCREMENTAL (over R0 overlap): increment_c > 0.5 & n_overlap>=60 ===")
inc=R[R.increment_c.notna()&(R.increment_c>0.5)&(R.r0_overlap_n>=60)].sort_values("increment_c",ascending=False)
print(inc[["name","n","net_c","r0_overlap_n","r0_edge_c","reason_edge_on_overlap_c","increment_c","shuf_p","oos","resid_corr"]].head(15).to_string(index=False))
