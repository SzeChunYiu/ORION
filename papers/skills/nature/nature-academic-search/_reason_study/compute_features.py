#!/usr/bin/env python3
"""
REASON STUDY - foundational feature compute.

For each resolved PM entry, compute detectable-at-entry Binance features and the
RESIDUAL move (entry -> expiry). The residual is what determines whether a reason
beats the already-priced partial move.

Output: ~/polymarket_crypto/research/study_reason_signals/entries_features.parquet
"""
import pandas as pd, numpy as np, os, sys, json, time

EDGE = os.path.expanduser("~/polymarket_crypto/research/edge_loop")
OUT  = os.path.expanduser("~/polymarket_crypto/research/study_reason_signals")
os.makedirs(OUT, exist_ok=True)

COINS = ["BTCUSDT","ETHUSDT","SOLUSDT","XRPUSDT","DOGEUSDT"]

# ---- load klines (1m) for all coins, index by minute ----
kl = {}
for c in COINS:
    p = f"{EDGE}/binance_klines/{c}_1m.csv"
    if not os.path.exists(p):
        print(f"WARN no klines for {c}"); continue
    d = pd.read_csv(p)
    d["min_start"] = (d.open_ms//1000).astype(np.int64)      # epoch sec of minute start
    d["min_end"]   = (d.close_ms//1000).astype(np.int64)
    d["ret_pct"]   = (d.close - d.open) / d.open * 100.0       # intraminute return in %
    d = d.sort_values("min_start").drop_duplicates("min_start").reset_index(drop=True)
    kl[c] = d
    print(f"{c}: {len(d)} klines  {pd.to_datetime(d.min_start.iloc[0],unit='s')} -> {pd.to_datetime(d.min_start.iloc[-1],unit='s')}")

# fast lookup: per coin, minute_start -> row
kl_idx = {c: d.set_index("min_start") for c,d in kl.items()}

def min_start_of(ts_sec):
    return int(ts_sec // 60 * 60)

def kline_at(coin, ts_sec):
    """The 1m kline whose minute contains ts_sec (the most-recent CLOSED kline is the prior minute)."""
    ms = min_start_of(ts_sec)
    idx = kl_idx[coin]
    # use the kline that has CLOSED by ts_sec: minute start <= ts-60
    closed_ms = ms - 60 if (ts_sec % 60) < 1 else ms - 60
    # fall back: find largest min_start <= ts_sec - 1 (a closed candle)
    cand = idx.index[(idx.index <= ts_sec - 1)]
    if len(cand)==0: return None
    return idx.loc[cand[-1]]

def ret_over(coin, ts_sec, lookback_s):
    """Return (%) of coin over [ts-lookback, ts] using closed klines: close_now/close_then."""
    idx = kl_idx[coin]
    now_ms = min_start_of(ts_sec) - 60                      # last fully closed minute
    then_ms = min_start_of(ts_sec - lookback_s) - 60
    if now_ms not in idx.index or then_ms not in idx.index: return np.nan
    c0 = idx.loc[then_ms,"open"]; c1 = idx.loc[now_ms,"close"]
    return (c1-c0)/c0*100.0

def full_window_move(coin, end_ts, strike):
    """close at the minute of end_ts vs strike (window-start price)."""
    idx = kl_idx[coin]
    ms = min_start_of(end_ts)
    if ms not in idx.index:
        cand = idx.index[(idx.index <= end_ts)];
        if len(cand)==0: return np.nan
        ms = cand[-1]
    close = idx.loc[ms,"close"]
    return (close-strike)/strike*100.0

def feature_block(coin, ts_sec, lookbacks=(30,60,120,180,300)):
    out = {}
    for lb in lookbacks:
        out[f"ret_{lb}s"] = ret_over(coin, ts_sec, lb)
    # BTC co-movement (lead/lag)
    for lb in lookbacks:
        out[f"btc_ret_{lb}s"] = ret_over("BTCUSDT", ts_sec, lb)
    # volume spike: taker_buy_quote of last closed 1m vs rolling 20m mean
    idx = kl_idx.get(coin)
    if idx is not None:
        now_ms = min_start_of(ts_sec) - 60
        if now_ms in idx.index:
            pos = idx.index.get_loc(now_ms)
            win = idx.iloc[max(0,pos-20):pos+1]
            cur = idx.iloc[pos]
            roll_mean = win["taker_buy_quote"].mean()
            out["vol_spike_1m"] = cur["taker_buy_quote"]/roll_mean if roll_mean>0 else np.nan
            out["ntrades_1m"] = float(cur["n_trades"])
            # acceleration: this minute ret vs previous minute ret
            out["ret_1m_now"]  = cur["ret_pct"]
            out["ret_1m_prev"] = idx.iloc[pos-1]["ret_pct"] if pos>0 else np.nan
            out["accel"] = out["ret_1m_now"] - out["ret_1m_prev"] if pos>0 else np.nan
            # reversal: distance of close to rolling 30m high
            w30 = idx.iloc[max(0,pos-30):pos+1]
            hi = w30["high"].max(); lo = w30["low"].min()
            out["dist_high_30m"] = (cur["close"]-hi)/hi*100.0   # <=0; near 0 = at recent high
            out["dist_low_30m"]  = (cur["close"]-lo)/lo*100.0
            out["rng_30m_pct"]   = (hi-lo)/lo*100.0
            # directional taker pressure
            out["taker_imb_1m"] = (cur["taker_buy_quote"]*2 - cur["quote_vol"])/max(cur["quote_vol"],1e-9)
        else:
            for k in ["vol_spike_1m","ntrades_1m","ret_1m_now","ret_1m_prev","accel",
                      "dist_high_30m","dist_low_30m","rng_30m_pct","taker_imb_1m"]:
                out[k]=np.nan
    else:
        for k in ["vol_spike_1m","ntrades_1m","ret_1m_now","ret_1m_prev","accel",
                  "dist_high_30m","dist_low_30m","rng_30m_pct","taker_imb_1m"]:
            out[k]=np.nan
    return out

# ---- load entries ----
e = pd.read_csv(f"{EDGE}/iter07_entries_enriched.csv")
e = e[e.outcome_src=="resolved"].copy()
print(f"\nresolved entries: {len(e)}")
e["ts_int"] = e.ts.astype(int)
e["end_int"] = e.end_ts.astype(int)

t0=time.time()
rows=[]
miss=0
for _,r in e.iterrows():
    coin=r.symbol; ts=r.ts_int; end=r.end_int
    if coin not in kl_idx:
        miss+=1; continue
    f = feature_block(coin, ts)
    f.update(dict(
        symbol=coin, end_ts=r.end_ts, ts=r.ts, ste=r.ste, side=r.side,
        ask=r.ask, theta=r.theta, agreement=r.agreement,
        up_wins=bool(r.up_wins), won=bool(r.won),
        fav_move_kl=r.fav_move_kl, coin_move_kl=r.coin_move_kl,
        sigma=r.sigma_5m_ann, spot_entry=r.spot_entry_kl, strike=r.strike_kl,
        book_imb=r.book_imb, hour=r.hour_utc,
        partial_move_pct=r.coin_move_kl,                 # move start->entry (detectable)
        full_move_pct=full_window_move(coin, end, r.strike_kl),
    ))
    rows.append(f)
print(f"feature compute: {len(rows)} rows, {miss} misses, {time.time()-t0:.1f}s")

F = pd.DataFrame(rows)
F["residual_move_pct"] = F.full_move_pct - F.partial_move_pct
# reason-implied direction helpers
F["fav_side"] = np.where(F.partial_move_pct>=0,"UP","DOWN")
F["fav_won"]  = ((F.fav_side=="UP")&F.up_wins) | ((F.fav_side=="DOWN")&(~F.up_wins))

F.to_parquet(f"{OUT}/entries_features.parquet")
F.to_csv(f"{OUT}/entries_features.csv", index=False)
print(f"\nWROTE {OUT}/entries_features.parquet  ({len(F)} rows, {len(F.columns)} cols)")
print("residual_move_pct describe:", F.residual_move_pct.describe().round(4).to_dict())
print("full_move vs partial corr:", round(F.full_move_pct.corr(F.partial_move_pct),4))
print("residual vs partial corr:", round(F.residual_move_pct.corr(F.partial_move_pct),4))
print("fav_won rate:", round(F.fav_won.mean(),4), " n=", F.fav_won.size)
print("cols:", sorted(F.columns))
