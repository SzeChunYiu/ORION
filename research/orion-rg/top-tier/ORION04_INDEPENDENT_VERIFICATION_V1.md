# ORION-04 handoff: independent verification of the materialized packet

Run against the committed in-tree packet, not the archive. The packet's bytes were
verified identical to `orion_top_tier_promotion_bundle.zip`
(SHA-256 `fcca596d9c7a2b42e50358386b6fa076bac6ed676a09a24b2cc959fe67ed17f0`)
file by file before this ran: **0 of 30 files differ**.

## The three independent checkers

| checker | exit | decision | digest |
|---|---|---|---|
| `check_result.py` | 0 | `ACCEPT_ORION04_C0_31_D4_30` | `2d055d37…ece842` |
| `check_static.py` | 0 | `STATIC_COVER_ACCEPT` | `104dc214…c026fe` |
| `check_full_cover.py` | 0 | `FULL_COVER_ACCEPT` | `813c5480…d66fa5` |

`tests/research/test_orion04_global_obstruction.py`: 1 passed.

## Every claimed count, checked against `RESULT.json` directly

Not taken from the checkers' verdicts — recomputed from the record:

| claim | stated | measured | |
|---|---|---|---|
| complete rank/plane branches | 78 | 78 | ✓ |
| exact executions | 156 | 156 | ✓ |
| executions per branch | dual-engine | 2.0, engines `avx` + `u128` | ✓ |
| multiplicity patterns | 60 | 60 | ✓ |
| support range | 14–31 | 14–31 | ✓ |
| survivors | 0 | 0 branches with `solutions > 0` | ✓ |
| internal checks | all | 9 of 9 true | ✓ |
| exact stdout agreement | all branches | 78 of 78 | ✓ |
| largest branch nodes per engine | 1,009,511,446 | 1,009,511,446 | ✓ |

The largest branch is `s31:a31:b0:c0:ALL_SINGLETON_FULL_BASIS`, support 31, pattern
`[31, 0, 0]` — thirty-one multiplicity-one elements — with
`nodes=1009511446 leaves=0 solutions=0`, and **both engines report that same node
count**, which is the part that makes the agreement non-trivial.

The resource receipt records 78 branches and 156 engine runs, with elapsed times
marked observational and deliberately excluded from the deterministic result
digest (avx max 496.7 s, u128 max 673.9 s).

## The checkers were falsification-tested, not just run

Injecting a single survivor into a copy of the packet — `branches[0].solutions`
from `0` to `1` — flips `check_result.py` to exit 1,
`REJECT_ORION04_GLOBAL_RESULT`.

`check_static.py` and `check_full_cover.py` still accept that corrupted copy, and
that is **correct rather than a weakness**: they verify the branch cover's
structure, not the execution results. The three checkers are not three opinions on
one object; they check three different objects, and only one of them is sensitive
to result bytes. Anyone reading "all three checkers pass" as triple redundancy on
the theorem would be wrong, so it is recorded here.

## Authority

Unchanged and unedited. The packet's own fields say `finite_theorem_authority:
true`, `novelty_authority: false`,
`external_independent_replay_complete: false`.

This verification establishes that the packet is internally consistent, that its
stated counts are the counts its record contains, and that its result checker
detects a corrupted result. It does **not** constitute external clean-room
replay — the engines were not rebuilt and re-executed here — and it makes no
novelty claim. `D_4(C_5^3) = 30` follows from `C_0 = 31` inside this packet's
formalisation; the 1.009-billion-node branch is far beyond re-derivation by
inspection, which is exactly why the dual-engine agreement and the certificate
interface carry the weight.
