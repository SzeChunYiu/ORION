#!/usr/bin/env python3
"""H4 parity gate for the streaming combine: run the full H4 fold with
streaming_combine_frontiers installed (accel attr replaced BEFORE the
chunker imports it, so run_chunk's own install lands the streaming form)
and require the SubjectFast.v1 result to equal the committed H4 parity
receipt's result field-for-field, modulo per-window wall_s timing.

ORIONQ_R5H_STREAM_ROWS is forced SMALL (default here 50000 vs the 2M
production default) so the mid-stream dict prune fires many times per
window on H4's 4-5k frontier -- the exact code path N2 will hammer at
50x the frontier size.

Usage: python3 r5h_h4_stream_parity.py <committed_receipt.json>
"""
import json
import os
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

receipt = json.loads(Path(sys.argv[1]).read_text())
ref = receipt["payload"]["result"]

stream_rows = os.environ.get("ORIONQ_R5H_STREAM_ROWS", "50000")
os.environ["ORIONQ_R5H_STREAM_ROWS"] = stream_rows

import max_r5h_mixed_cardinality_development_fast as accel  # noqa: E402
import max_r5h_streaming_combine as stream  # noqa: E402

accel.fast_combine_frontiers = stream.streaming_combine_frontiers

import max_r5h_subject_chunked as ch  # noqa: E402

with tempfile.TemporaryDirectory() as td:
    ck = Path(td)
    ch.run_chunk("H4", "donor", ck, 23, 200000)
    ch.run_chunk("H4", "mixed", ck, 23, 200000)
    out = ch.finalize(ck, "H4")

got = out["result"]


def strip_wall(meta):
    return [{k: v for k, v in w.items() if k != "wall_s"} for w in meta]


diffs = [k for k in ref
         if (strip_wall(ref[k]) != strip_wall(got[k])
             if k in ("donor_window_meta", "mixed_window_meta")
             else ref[k] != got[k])]
extra = sorted(set(got) - set(ref))
if diffs or extra:
    print(f"H4_STREAM_PARITY=FAIL diffs={diffs} extra={extra}")
    for k in diffs[:3]:
        print(f"  {k} ref={str(ref[k])[:300]}", file=sys.stderr)
        print(f"  {k} got={str(got[k])[:300]}", file=sys.stderr)
    raise SystemExit(1)
print(f"H4_STREAM_PARITY=PASS stream_rows={stream_rows} "
      f"frontiers={got['donor_direct_frontier_size']}/{got['mixed_frontier_size']} "
      f"named_B3={sorted(got['B3_mixed_named'])}")
