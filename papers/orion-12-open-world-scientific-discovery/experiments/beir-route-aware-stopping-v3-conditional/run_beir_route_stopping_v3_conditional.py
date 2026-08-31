#!/usr/bin/env python3
"""ORION-12 route-aware stopping on BEIR. Protocol: beir-route-aware-stopping-v1.

Cost is the number of distinct documents EXAMINED for relevance. Examining a
document reveals its relevance; that is what active retrieval means and it is why
cost is counted in documents rather than in queries. No arm except the oracle
sees the relevance of a document it has not examined.
"""
from __future__ import annotations
import gzip, hashlib, json, math, os, re, sys, time
from collections import defaultdict

BEIR = os.path.expanduser("~/beir")
CORPORA = ["scifact", "nfcorpus", "arguana"]
DEPTHS = [10, 20, 50, 100, 200]
ROUTE_ORDER = ["bm25_full", "bm25_title", "bm25_text", "tfidf_word", "tfidf_char"]
RRF_K = 60
PATIENCE = 2           # generic_active: consecutive routes adding no new relevant
TAU = 1.0              # route_aware_stop: literal "expected < one new relevant"
SPLIT_SEED = 20260830
STOP = set("""a an and are as at be by for from has he in is it its of on that the
to was were will with this these those which who whom what when where how why not
no or but if then than so such can could may might must shall should would do does
did done have had having i you your we our they them their his her hers him she""".split())

TOK = re.compile(r"[a-z0-9]+")
def toks(s): return [t for t in TOK.findall(s.lower()) if t not in STOP and len(t) > 1]

def load(name):
    d = os.path.join(BEIR, name)
    corpus = {}
    with open(os.path.join(d, "corpus.jsonl"), encoding="utf-8") as fh:
        for ln in fh:
            o = json.loads(ln)
            corpus[o["_id"]] = (o.get("title", "") or "", o.get("text", "") or "")
    queries = {}
    with open(os.path.join(d, "queries.jsonl"), encoding="utf-8") as fh:
        for ln in fh:
            o = json.loads(ln)
            queries[o["_id"]] = o.get("text", "") or ""
    qrels = defaultdict(set)
    qp = os.path.join(d, "qrels", "test.tsv")
    with open(qp, encoding="utf-8") as fh:
        head = fh.readline()
        for ln in fh:
            p = ln.rstrip("\n").split("\t")
            if len(p) < 3: continue
            try: sc = float(p[2])
            except ValueError: continue
            if sc > 0: qrels[p[0]].add(p[1])
    qrels = {q: v for q, v in qrels.items() if q in queries and v}
    return corpus, queries, qrels

class BM25:
    def __init__(self, docs, k1=0.9, b=0.4):
        self.k1, self.b = k1, b
        self.ids = list(docs.keys())
        self.inv = defaultdict(list); self.dl = {}
        for did in self.ids:
            tf = defaultdict(int)
            for t in docs[did]: tf[t] += 1
            self.dl[did] = len(docs[did])
            for t, c in tf.items(): self.inv[t].append((did, c))
        N = len(self.ids)
        self.avgdl = (sum(self.dl.values()) / N) if N else 1.0
        self.idf = {t: math.log(1 + (N - len(p) + 0.5) / (len(p) + 0.5)) for t, p in self.inv.items()}
        self.empty = self.avgdl == 0
    def search(self, q, k):
        if self.empty: return []
        sc = defaultdict(float)
        for t in q:
            if t not in self.inv: continue
            idf = self.idf[t]
            for did, c in self.inv[t]:
                dn = c * (self.k1 + 1)
                dd = c + self.k1 * (1 - self.b + self.b * self.dl[did] / self.avgdl)
                sc[did] += idf * dn / dd
        return [d for d, _ in sorted(sc.items(), key=lambda x: (-x[1], x[0]))[:k]]

class TFIDF:
    def __init__(self, docs):
        self.ids = list(docs.keys())
        self.inv = defaultdict(list); N = len(self.ids)
        df = defaultdict(int); tfs = {}
        for did in self.ids:
            tf = defaultdict(int)
            for t in docs[did]: tf[t] += 1
            tfs[did] = tf
            for t in tf: df[t] += 1
        self.idf = {t: math.log(N / (1 + c)) + 1 for t, c in df.items()}
        for did, tf in tfs.items():
            v = {t: (1 + math.log(c)) * self.idf[t] for t, c in tf.items()}
            nrm = math.sqrt(sum(x * x for x in v.values())) or 1.0
            for t, x in v.items(): self.inv[t].append((did, x / nrm))
        self.empty = N == 0 or not df
    def search(self, q, k):
        if self.empty: return []
        tf = defaultdict(int)
        for t in q: tf[t] += 1
        qv = {t: (1 + math.log(c)) * self.idf.get(t, 0.0) for t, c in tf.items()}
        nrm = math.sqrt(sum(x * x for x in qv.values())) or 1.0
        sc = defaultdict(float)
        for t, x in qv.items():
            if x == 0 or t not in self.inv: continue
            w = x / nrm
            for did, y in self.inv[t]: sc[did] += w * y
        return [d for d, _ in sorted(sc.items(), key=lambda x: (-x[1], x[0]))[:k]]

def chargrams(s, lo=3, hi=5):
    s = re.sub(r"\s+", " ", s.lower())
    out = []
    for n in range(lo, hi + 1):
        out.extend(s[i:i+n] for i in range(max(0, len(s) - n + 1)))
    return out

def build_routes(corpus):
    full = {d: toks(t + " " + b) for d, (t, b) in corpus.items()}
    title = {d: toks(t) for d, (t, _) in corpus.items()}
    text = {d: toks(b) for d, (_, b) in corpus.items()}
    # bm25_title stays in the denominator even when every title is empty.
    title_nonempty = sum(1 for v in title.values() if v)
    cg = {d: chargrams((t + " " + b)[:600]) for d, (t, b) in corpus.items()}
    R = {
        "bm25_full":  (BM25(full),  toks),
        "bm25_title": (BM25(title), toks),
        "bm25_text":  (BM25(text),  toks),
        "tfidf_word": (TFIDF(full), toks),
        "tfidf_char": (TFIDF(cg),   lambda s: chargrams(s[:600])),
    }
    return R, title_nonempty

def run_corpus(name, log):
    t0 = time.time()
    corpus, queries, qrels = load(name)
    log(f"[{name}] {len(corpus)} docs, {len(qrels)} scored queries")
    R, title_nonempty = build_routes(corpus)
    log(f"[{name}] routes built in {time.time()-t0:.0f}s; nonempty titles={title_nonempty}")

    qids = sorted(qrels)
    import random
    rnd = random.Random(SPLIT_SEED)
    shuf = qids[:]; rnd.shuffle(shuf)
    half = len(shuf) // 2
    dev, held = sorted(shuf[:half]), sorted(shuf[half:])

    maxd = max(DEPTHS)
    lists = {}   # qid -> route -> ranked ids (maxd)
    for qid in qids:
        qt = queries[qid]
        lists[qid] = {r: eng.search(tk(qt), maxd) for r, (eng, tk) in R.items()}

    def rel(qid): return qrels[qid]

    # ---- route heterogeneity (for the CANNOT_CHECK terminal) ----
    jac = []
    for qid in held:
        s = [set(lists[qid][r][:100]) for r in ROUTE_ORDER if lists[qid][r]]
        for i in range(len(s)):
            for j in range(i + 1, len(s)):
                u = len(s[i] | s[j])
                if u: jac.append(len(s[i] & s[j]) / u)
    mean_jac = sum(jac) / len(jac) if jac else 1.0

    # ---- dev marginals for route_aware_stop ----
    # prefix i (routes ROUTE_ORDER[:i] examined) -> remaining route -> mean new relevant
    marg = {}
    for i in range(len(ROUTE_ORDER)):
        marg[i] = {}
        for r in ROUTE_ORDER[i:]:
            tot = 0.0
            for qid in dev:
                seen = set()
                for rr in ROUTE_ORDER[:i]: seen |= set(lists[qid][rr][:100])
                new = set(lists[qid][r][:100]) - seen
                tot += len(new & rel(qid))
            marg[i][r] = tot / max(len(dev), 1)

    # ---- best_single chosen on dev ----
    dev_rec = {}
    for r in ROUTE_ORDER:
        tot = 0.0
        for qid in dev:
            g = rel(qid)
            tot += len(set(lists[qid][r][:100]) & g) / len(g)
        dev_rec[r] = tot / max(len(dev), 1)
    best_route = max(ROUTE_ORDER, key=lambda r: (dev_rec[r], r))

    # ---- V3: dev-mean unseen count per (prefix, route, depth), dev half only ----
    dev_unseen = {}
    for i in range(len(ROUTE_ORDER)):
        dev_unseen[i] = {}
        for r in ROUTE_ORDER[i:]:
            dev_unseen[i][r] = {}
            for dd in DEPTHS:
                t = 0.0
                for qid in dev:
                    sn = set()
                    for rr in ROUTE_ORDER[:i]: sn |= set(lists[qid][rr][:dd])
                    t += len(set(lists[qid][r][:dd]) - sn)
                dev_unseen[i][r][dd] = t / max(len(dev), 1)

    def rrf(qid, d):
        sc = defaultdict(float)
        for r in ROUTE_ORDER:
            for rank, did in enumerate(lists[qid][r]):
                sc[did] += 1.0 / (RRF_K + rank + 1)
        return [x for x, _ in sorted(sc.items(), key=lambda y: (-y[1], y[0]))[:d]]

    out = {"corpus": name, "docs": len(corpus), "queries_scored": len(qids),
           "dev": len(dev), "held": len(held), "best_single_route": best_route,
           "dev_recall_at100": dev_rec, "mean_pairwise_jaccard_at100": round(mean_jac, 4),
           "nonempty_titles": title_nonempty, "dev_marginals": marg, "by_depth": {}}

    for d in DEPTHS:
        agg = {}
        for arm in ("best_single", "fusion", "generic_active", "route_aware_stop", "oracle"):
            recs, costs, fc, fc_n = [], [], 0, 0
            for qid in held:
                g = rel(qid)
                if arm == "best_single":
                    ex = list(lists[qid][best_route][:d]); stopped = None
                elif arm == "fusion":
                    ex = rrf(qid, d); stopped = None
                elif arm == "oracle":
                    seen = []
                    for r in ROUTE_ORDER:
                        for x in lists[qid][r][:d]:
                            if x not in seen: seen.append(x)
                    ex = seen; stopped = None
                else:
                    seen, misses, i = [], 0, 0
                    for i, r in enumerate(ROUTE_ORDER):
                        if arm == "route_aware_stop" and i > 0:
                            rem = {}
                            for rr in ROUTE_ORDER[i:]:
                                unseen_q = len(set(lists[qid][rr][:d]) - set(seen))
                                base = dev_unseen[i][rr].get(d, 0.0)
                                ratio = (unseen_q / base) if base > 1e-9 else 1.0
                                rem[rr] = marg[i].get(rr, 0.0) * ratio
                            if rem and max(rem.values()) < TAU:
                                break
                        before = len(set(seen) & g)
                        for x in lists[qid][r][:d]:
                            if x not in seen: seen.append(x)
                        after = len(set(seen) & g)
                        if arm == "generic_active":
                            misses = 0 if after > before else misses + 1
                            if misses >= PATIENCE: i += 1; break
                    else:
                        i = len(ROUTE_ORDER)
                    ex = seen; stopped = i
                got = set(ex) & g
                recs.append(len(got) / len(g)); costs.append(len(ex))
                if stopped is not None:
                    fc_n += 1
                    remaining = set()
                    for r in ROUTE_ORDER[stopped:]: remaining |= set(lists[qid][r][:d])
                    if (remaining - set(ex)) & g: fc += 1
            agg[arm] = {
                "recall": round(sum(recs) / len(recs), 4),
                "cost": round(sum(costs) / len(costs), 2),
                "false_complete_rate": (round(fc / fc_n, 4) if fc_n else None),
                "false_complete_applicable": fc_n > 0,
            }
        out["by_depth"][str(d)] = agg
        log(f"[{name}] d={d} " + " ".join(
            f"{a}:r={v['recall']:.3f}/c={v['cost']:.0f}" for a, v in agg.items()))
    out["elapsed_s"] = round(time.time() - t0, 1)
    return out

def main():
    logf = open(os.path.expanduser("~/beir/run_v3.log"), "a", buffering=1)
    def log(m):
        print(m, flush=True); logf.write(m + "\n")
    digests = {}
    for c in CORPORA:
        p = os.path.join(BEIR, f"{c}.zip")
        h = hashlib.sha256()
        with open(p, "rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b""): h.update(chunk)
        digests[c] = h.hexdigest()
    res = {"schema": "ORION12.BEIR_ROUTE_AWARE_STOPPING_CONDITIONAL.v3",
           "zip_sha256": digests, "route_order": ROUTE_ORDER, "depths": DEPTHS,
           "rrf_k": RRF_K, "patience": PATIENCE, "tau": TAU, "split_seed": SPLIT_SEED,
           "corpora": {}}
    for c in CORPORA:
        res["corpora"][c] = run_corpus(c, log)
        with open(os.path.expanduser("~/beir/RESULTS_V3_CONDITIONAL.json"), "w") as fh:
            json.dump(res, fh, indent=1, sort_keys=True)
    log("ALL_DONE")

if __name__ == "__main__":
    sys.exit(main())
