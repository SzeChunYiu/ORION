# ORION-10 V3 cap lift — findings

**Terminal: `CANNOT_CHECK_PREFIX_CONTROL_FAILED`.**
**Scientific authority delta: `NONE`.** The V2 terminal `FIBRE_CONSTANCY_REFUTED` is
untouched. **No envelope claim is made here in either direction**, which is what
`PROTOCOL_V3.md` pre-declared for this outcome.

## The run

LUNARC job 3561253, `cn128`, 48 threads, **`COMPLETED` exit `0:0`** in 02:02:54 of an
11-hour budget, at the outcome-free commit `9ad587938`. **13,401 instances** against V2's
740, and `hard_assertion_failures_verbatim: []` across the whole run. Fourth-regime
candidates rose from 64 to 567.

## What the falsifier appeared to do

`REVIVAL_PASS_V1.md` declared the falsifier before V3 was written: *any admitted instance
with `f_Bprime − C_Dxx > 3` refutes the lower envelope.*

```
offset distribution: {0: 8400, 1: 4485, 2: 302, 3: 205, 4: 8, 5: 1}
instances with offset > 3: 9        max offset observed: 5
```

Nine instances exceed the bound, in `H2_n3` (5) and `H4_n3` (4), all in `split` regime.
On every one of them `C_DP == C_Dxx` and `gap4 == 0`, so they satisfy the soundness
relation and carry no internal inconsistency.

## Why that is not reported as a refutation

**The pre-declared prefix control failed.** `PROTOCOL_V3.md` states that because the
enumeration order is unchanged, V2's rows must reappear as V3's prefix, and that *"if
V3's first 740 evaluated instances per panel do not reproduce V2's values, the generator
is not deterministic and no V3 conclusion may be drawn."*

Five of ten panels fail it:

| panel | V2 | V3 | prefix matches |
|---|---|---|---|
| H1_n3 | 120 | 2400 | yes |
| H2_n3 | 160 | 3200 | **no** |
| H3_n3 | 90 | 1800 | **no** |
| H4_n3 | 90 | 1800 | **no** |
| H5_n3 | 120 | 1001 | **no** |
| H1_n4 | 40 | 800 | yes |
| H2_n4 | 40 | 800 | **no** |
| H3_n4 | 24 | 480 | yes |
| H4_n4 | 32 | 640 | yes |
| H5_n4 | 24 | 480 | yes |

## Root cause, diagnosed not guessed

`run_full_census_v2.py:1060` creates **one** `dedupe: set = set()` and passes it into
every `run_panel` call. Instances are skipped on `canonical_key(tp, n)` membership in
that shared set.

So a cap is not merely a stopping point. Raising `H1_n3` from 120 to 2400 inserts roughly
2,280 additional keys before `H2_n3` runs, and `H2_n3` then skips instances it would
otherwise have evaluated. **The enumeration of every panel depends on the caps of the
panels before it in `PANEL_ORDER`.** `H1_n3` is first and matches; the panels following it
in the `n=3` block do not.

This is a real defect in the generator *for the purpose of cap-varying comparison*. It was
invisible at a single fixed cap, which is why V2 never exposed it, and it is exactly what
the prefix control existed to catch.

## What I am deliberately not doing

The nine instances look like a genuine refutation. They were produced by the frozen
grammar, they pass every hard assertion, and a universal claim needs only one
counterexample — enumeration *order* does not determine whether an instance is admissible.
So there is a real argument that the refutation survives on existence grounds
independently of the prefix comparison.

**I am not making that argument, because I would be making it after seeing the result.**
`PROTOCOL_V3.md` says `CANNOT_CHECK_PREFIX_CONTROL_FAILED` means no claim in either
direction. Reinterpreting my own pre-declared terminal once the outcome looks exciting is
precisely the move the pre-registration exists to prevent, and the fact that the
reinterpretation is *plausible* is what makes it dangerous rather than harmless.

The observation is recorded, with its status: **candidate refutation, pending a clean
run.**

## The clean run, specified

Per-panel dedupe. Each panel gets its own set, so its enumeration depends only on its own
cap and the prefix property holds by construction. That is a one-line change to a copy of
the generator under a new identity — V2 stays frozen and untouched.

If the prefix control then passes and any instance still exceeds offset 3, the envelope is
refuted and `REVIVAL_PASS_V1.md`'s one-sided bound must be withdrawn. If the violations
disappear under per-panel dedupe, they were an artifact of cross-panel skipping and the
envelope survives at 20× coverage — which is still not a proof, as `PROTOCOL_V3.md`
already states.

Either way the result is decided by the re-run, not by argument about this one.

## One incidental gain

`H5_n3` reports `cap_hit: false` at 1,001 of a possible 2,400 — the only panel to exhaust
its space. Its enumeration is therefore complete, and complete for the first time in this
lane. That fact is independent of the prefix failure, since exhausting a space does not
depend on the order in which it was walked.
