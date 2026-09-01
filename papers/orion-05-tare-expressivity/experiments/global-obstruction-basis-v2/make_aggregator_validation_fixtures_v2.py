import json, os, sys
SCHEMA = "ORION05.GLOBAL_OBSTRUCTION_BASIS.v2.stage1"
D = sys.argv[1]
def shard(case, start, end, positives=(), hist_fudge=0, stop="limit_reached"):
    proc = end - start
    hist = {"0": proc - len(positives) + hist_fudge}
    if positives: hist["1"] = len(positives)
    pos = [{"absolute_index_zero_based": i, "lex_index": i+1, "c1": c1, "c2": c2,
            "gap": c1-c2, "codes": [1,1,1,1,1,2], "targets": []} for i, c1, c2 in positives]
    d = {"schema": SCHEMA, "start": start, "absolute_end_exclusive": end,
         "processed_this_invocation": proc, "shard_positives": pos,
         "gap_histogram": hist, "stop_reason": stop}
    os.makedirs(f"{D}/{case}", exist_ok=True)
    json.dump(d, open(f"{D}/{case}/s{start}.json","w"), indent=2)
N = 33755
# 1: full coverage, zero positives
for a in range(0, N, 10000): shard("c1_full_nopos", a, min(a+10000, N))
# 2: gap at [500,600), positives after it
shard("c2_gap", 0, 500, [(10,5,4),(20,5,4)]); shard("c2_gap", 600, N, [(700,5,4)])
# 3: three positives inside gap-free prefix
shard("c3_found", 0, 5000, [(10,5,4),(20,5,4),(30,5,4)])
# 4: two shards disagree on the same index
shard("c4_disagree", 0, 100, [(10,5,4)]); shard("c4_disagree", 100, 200, [])
d = json.load(open(f"{D}/c4_disagree/s100.json"))
d["shard_positives"] = [{"absolute_index_zero_based": 10, "lex_index": 11, "c1": 9, "c2": 1,
                         "gap": 8, "codes": [], "targets": []}]
d["gap_histogram"] = {"0": 99, "1": 1}
json.dump(d, open(f"{D}/c4_disagree/s100.json","w"), indent=2)
# 5: histogram does not account for every solve
shard("c5_hist", 0, 1000, hist_fudge=-7)
# 6: positive reported outside the shard's covered range
shard("c6_outside", 0, 100, [(5000,5,4)])
print("built")
