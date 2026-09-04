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
