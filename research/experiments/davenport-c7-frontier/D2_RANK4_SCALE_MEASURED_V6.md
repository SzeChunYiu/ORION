# `D_2(C_5^4)` is out of reach of post-hoc deduplication — measured — V6

Status: **measured negative, with the technique that would change it named.** No new mathematical result.
Probe: `tools/probe_c54_scale_v6.c`. Priority CANNOT_CHECK.
Lane: `claude/orion-research-frontier-3ck9yt`.

## 1. The question

`D2_ALL_RANKS_V3.md` §5 leaves `D_2(C_5^4) ∈ {26,27}`, and task 9 of this packet asks to decide it by exhaustive search. Deciding it means settling whether a length-26 sequence `S` over `C_5^4` with `z(S) ≤ 1` exists.

Structure: take any atom `A ⊆ S`; then `S \ A` is zero-sum-free, so `|S \ A| ≤ D(C_5^4) − 1 = 16` and `|A| ≥ 10`. The binding sub-problem is therefore the enumeration of zero-sum-free sequences of length up to 16 over `C_5^4`.

## 2. The measurement

Zero-sum-free sequences containing `e_1,…,e_4` (the normalisation is legitimate: a zero-sum-free sequence of length 16 cannot lie in a hyperplane `C_5^3`, where the maximum such length is `D − 1 = 12`), carrying the subsum set as a 625-bit mask:

| target length | counted | exhaustive? |
|---|---|---|
| 12 | **198,116,979** | **no** — hit the 200,000,000-node cap in 155 s |
| 16 | — | not attempted; four levels deeper |

The rate is ~1.28 million leaves per second, and the count grows steeply with length. Length 16 is many orders of magnitude beyond the length-12 figure, which itself was not completed.

For contrast, the `p = 5`, rank-3 sweeps that decided `D_4(C_5^3)` topped out at 15.3 million distinct atoms and 44,111 orbits. This is a different regime, not a larger instance of the same one.

## 3. Why the `D_4(C_5^3)` trick does not carry over

The decisive move there was deduplication: 6.3 million enumerated objects collapsed to 3,325 `GL(3,5)`-orbits, turning a projected 114 hours into minutes. That worked because the enumeration itself was cheap and only the *downstream* work was redundant.

Here the enumeration is the bottleneck. `|GL(4,5)| ≈ 1.16 × 10^{11}` is enormous, so the orbit count may well be small — but post-hoc deduplication cannot help when the object list cannot be produced in the first place.

**The technique that would change this is orderly generation** (canonical construction path): extend only partial objects that are already canonical in their orbit, so representatives are produced directly and the redundant copies are never generated. That is a different algorithm, not a tuning of this one, and implementing it correctly for `GL(4,5)` is a substantial piece of work.

## 4. Recorded so the assertion is not repeated on faith

This packet has twice recorded a limit that dissolved on measurement — the flat-triple gap (a deduplication problem, not a compute problem) and the maximal-atom sweep (114 hours became three minutes). The claim here is therefore stated as a measurement with its cap and rate, not as a judgement: **at 1.28 M leaves/s, the length-12 sub-enumeration alone did not finish in 200 million nodes.** Anyone revisiting this should re-measure rather than trust the conclusion.

## Claim ceiling

A scale measurement on one host with one algorithm. It does not prove `D_2(C_5^4)` is undecidable by computer, and says nothing about `D_2(C_3^5)`, whose scale is unmeasured. It is evidence that the post-hoc-deduplication approach that worked at rank three does not extend to rank four.

---

## V6 addendum: re-measured after the 3.5× enumerator speedup (2026-09-05)

The `D_2(C_3^5)` sweep finished (`D2_C3_5_DECIDED_V6.md`) partly because
`tools/enum_rank_generic_v3.c` got 3.5× faster — the candidate test was hoisted out of the
extension loop. That raised the obvious question of whether `D_2(C_5^4)` had also come into
range. **It has not**, and this is the measurement rather than an assertion.

Deciding `D_2(C_5^4) ∈ [26,27]` means ruling out `|S| = 26` with `z(S) ≤ 1` over `C_5^4`. Here
`D(C_5^4) = 17`, so every block has length `≥ 26 − 16 = 10` and the prune is "no zero-sum of
length `≤ 9`"; `N = 5^4 = 625`.

    ./enumr 5 4 26 9 --shard 0 256 --progress

One shard of **256**, on the post-speedup binary:

| after | nodes | leaves | deepest depth |
|---|---|---|---|
| 155 s | 17,825,792 | 0 | **16** of 26 |

115K nodes/s, and after 17.8 million nodes the search has only reached depth 16 — ten levels
short of a leaf, in one two-hundred-and-fifty-sixth of the space. For contrast, the entire
`C_3^5` decision took 2.73×10⁹ nodes.

The shard did not finish, so this bounds the cost only from below; on the shape of the frontier a
full run is plausibly two orders of magnitude beyond the `C_3^5` sweep, i.e. days of continuous
four-core time. In an environment whose containers are reclaimed on idle, that is not a run that
completes.

So the earlier conclusion stands, now for a sharper reason: the obstacle is not deduplication
overhead but the raw size of the `s = 9`, `N = 625`, `L = 26` tree. The speedup that decided
`C_3^5` moves this by a constant, and a constant is not what is missing. What would change it is
the same thing named before — orderly generation / canonical construction, which prunes by
isomorphism rather than by re-deriving each branch — or an upper-bound theorem sharp enough to
close `[26,27]` without enumeration at all.
