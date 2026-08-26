#!/usr/bin/env python3
"""
REASON STUDY - reason library tester.

Each REASON = (trigger mask, direction array). Generic evaluator reports:
  n, WR, gross-edge vs theta, net-edge vs ask (favorite) / approx-underdog-ask,
  shuffle-null p-value, walk-forward OOS sign-stability.

Benchmark = R0 favorite-momentum (known +6c sweet spot ste~90-120).
"""
import pandas as pd, numpy as np, os, json
from scipy import stats

OUT = os.path.expanduser("~/polymarket_crypto/research/study_reason_signals")
F = pd.read_parquet(f"{OUT}/entries_features.parquet")
F["day"] = pd.to_datetime(F.end_ts, unit="s").dt.date.astype(str)
SPREAD = 0.015   # approx 1.5c half-spread on PM 5m crypto
days = sorted(F.day.unique())
print(f"{len(F)} entries, {len(days)} days: {days[0]}..{days[-1]}")

# ---- direction -> cost + win ----
def reason_eval(F, mask, direction, name, bet_type="auto"):
    """direction: array of 'UP'/'DOWN' aligned to F. mask: bool trigger.
    bet_type: 'auto' uses each row's fav/dog; or explicit."""
    sub = F[mask].copy()
    if len(sub)==0: return dict(name=name,n=0)
    d = direction[mask]
    sub["dir"] = d
    sub["reason_won"] = ((d=="UP")&sub.up_wins) | ((d=="DOWN")&(~sub.up_wins))
    sub["fav_dir"] = np.where(sub.partial_move_pct>=0,"UP","DOWN")
    sub["is_fav_bet"] = (sub.dir==sub.fav_dir)
    # cost: favorite bet -> ask; underdog bet -> 1 - ask + SPREAD
    cost = np.where(sub.is_fav_bet, sub.ask, 1.0 - sub.ask + SPREAD)
    sub["cost"] = cost
    sub["edge_cents"] = (sub.reason_won.astype(float) - cost)*100.0
    wr = sub.reason_won.mean()
    mean_edge = sub.edge_cents.mean()
    se = sub.edge_cents.std(ddof=1)/np.sqrt(len(sub))
    z = mean_edge/se if se>0 else 0.0
    # shuffle null: permute direction within the triggered set, recompute edge, 1000x
    rng = np.random.default_rng(42)
    rw = sub.reason_won.values
    nulls = []
    for _ in range(1000):
        pcost = np.where(np.random.permutation(sub.is_fav_bet.values), sub.ask.values, 1.0-sub.ask.values+SPREAD)
        nulls.append((rw.astype(float)-pcost).mean()*100.0)
    nulls = np.array(nulls)
    p = (np.abs(nulls) >= abs(mean_edge)).mean()
    # walk-forward OOS: split days in half
    half = len(days)//2
    tr_days, te_days = set(days[:half]), set(days[half:])
    def half_edge(ds):
        s = sub[sub.day.isin(ds)]
        if len(s)==0: return np.nan, 0
        return s.edge_cents.mean(), len(s)
    e_tr,n_tr = half_edge(tr_days); e_te,n_te = half_edge(te_days)
    oos_stable = (np.sign(e_tr)==np.sign(e_te)) and (e_te>0) if not np.isnan(e_te) else False
    r = dict(name=name, n=int(len(sub)),
             wr=round(float(wr),4),
             fav_bet_frac=round(float(sub.is_fav_bet.mean()),3),
             mean_cost=round(float(cost.mean()),4),
             net_edge_c=round(float(mean_edge),3),
             se=round(float(se),3), z=round(float(z),2),
             shuffle_p=round(float(p),4),
             e_tr_c=round(float(e_tr),3) if not np.isnan(e_tr) else None,
             e_te_c=round(float(e_te),3) if not np.isnan(e_te) else None,
             n_tr=int(n_tr),n_te=int(n_te),
             oos_stable=bool(oos_stable))
    return r

# ===================== REASONS =====================
# Helper: reason registry. Each returns (mask, direction) over F.
P = F.partial_move_pct.values        # detectable move start->entry (%)
FM = F.fav_move_kl.values            # abs favorite move
STE = F.ste.values
BTC60 = F.btc_ret_60s.values; BTC120=F.btc_ret_120s.values; BTC30=F.btc_ret_30s.values
C60=F.ret_60s.values; C120=F.ret_120s.values; C30=F.ret_30s.values
ACCEL=F.accel.values; VOL=F.vol_spike_1m.values; TIMB=F.taker_imb_1m.values
DH=F.dist_high_30m.values; DL=F.dist_low_30m.values; RNG=F.rng_30m_pct.values
SIG=F.sigma.values

results=[]
def sgn(x): return np.where(x>=0,"UP","DOWN")

# R0 benchmark: favorite momentum sweet spot (known +6c)
for fm_lo, shi in [(0.05,1e9)]:
    m = (FM>=fm_lo) & (STE>=90)&(STE<=120)
    results.append(reason_eval(F,m,sgn(P),"R0_fav_mom_90_120"))

# R0b broader fav momentum bands
for fm_lo,shi in [(0.05,1e9),(0.08,1e9),(0.05,0.10)]:
    for slo,shi2 in [(60,120),(120,200),(30,90)]:
        m=(FM>=fm_lo)&(STE>=slo)&(STE<=shi2)
        results.append(reason_eval(F,m,sgn(P),f"R0b_fav_fm{fm_lo}_ste{slo}_{shi2}"))

# R1 BTC lead/lag: BTC moved >=T bps in 60-120s, follow BTC direction on the coin
for thr in [0.03,0.06,0.10,0.15]:
    for lb,lab in [(60,"60"),(120,"120")]:
        btc = BTC60 if lb==60 else BTC120
        m = (np.abs(btc)>=thr) & (~np.isnan(btc))
        results.append(reason_eval(F,m,sgn(btc),f"R1_btclead_{lab}s_t{thr}"))

# R1b lag GAP: BTC moved but coin hasn't (btc_ret - coin_ret large), bet coin in BTC dir
for thr in [0.04,0.08,0.12]:
    for lb,lab in [(60,"60"),(120,"120")]:
        btc = BTC60 if lb==60 else BTC120; coi = C60 if lb==60 else C120
        gap = btc - coi
        m = (btc>=thr) & (gap>=thr*0.5) & (~np.isnan(gap))
        results.append(reason_eval(F,m,sgn(btc),f"R1b_btcgap_{lab}s_t{thr}"))

# R2 rejection/reversal: at 30m high (dist_high near 0) AND dropped in last 60s -> bet DOWN (reversal)
for dh_hi in [-0.01,-0.03,-0.06]:
    for drop in [-0.02,-0.05,-0.10]:
        m = (DH>=dh_hi) & (C60<=drop) & (~np.isnan(DH))
        results.append(reason_eval(F,m,np.where(m,"DOWN","UP"),f"R2_rejectHi_dh{dh_hi}_drop{drop}"))
# R2b at 30m low AND bounced -> bet UP
for dl_lo in [0.01,0.03,0.06]:
    for bounce in [0.02,0.05,0.10]:
        m = (DL<=dl_lo) & (C60>=bounce) & (~np.isnan(DL))
        results.append(reason_eval(F,m,np.where(m,"UP","DOWN"),f"R2b_bounceLo_dl{dl_lo}_bnc{bounce}"))

# R3 momentum acceleration: accel same sign as recent move -> continue
for acc in [0.01,0.03,0.05]:
    m = (np.abs(ACCEL)>=acc) & (np.sign(ACCEL)==np.sign(C60)) & (~np.isnan(ACCEL))
    results.append(reason_eval(F,m,sgn(C60),f"R3_accel_{acc}"))

# R4 volume spike + directional taker imbalance
for vs in [1.5,2.0,3.0]:
    for ti in [0.1,0.3,0.5]:
        m = (VOL>=vs) & (np.abs(TIMB)>=ti) & (~np.isnan(VOL))
        results.append(reason_eval(F,m,sgn(TIMB),f"R4_volspike{vs}_timb{ti}"))

# R7 overextension reversal: large fav_move -> bet UNDERDOG (reversal)
for fm_hi in [0.15,0.20,0.30]:
    m = (FM>=fm_hi)
    dog = np.where(F.partial_move_pct>=0,"DOWN","UP")   # opposite = underdog
    results.append(reason_eval(F,m,dog,f"R7_overext_reversal_fm{fm_hi}"))

# R8 volatility regime x fav momentum
for sg in [0.10,0.20,0.40]:
    m = (SIG>=sg) & (FM>=0.05) & (STE>=60)&(STE<=150)
    results.append(reason_eval(F,m,sgn(P),f"R8_highvol_fav_sg{sg}"))

R = pd.DataFrame(results).sort_values("net_edge_c",ascending=False)
R.to_csv(f"{OUT}/reason_results_t1.csv",index=False)
pd.set_option("display.width",200,"display.max_columns",30)
print("\n=== TOP 25 by net edge ===")
print(R.head(25).to_string(index=False))
print("\n=== OOS-stable + shuffle_p<0.1 + n>=30 ===")
filt = R[(R.oos_stable==True)&(R.shuffle_p<0.1)&(R.n>=30)].sort_values("net_edge_c",ascending=False)
print(filt.to_string(index=False))
print(f"\nfiltered count: {len(filt)}")
