# ORION-10 B' fibre criterion V3 — cap lift

**Committed before the run, with no outcome in hand.**
**Scientific authority delta: `NONE`.** V3 is a successor under a new identity. It does
not modify, re-tune or re-interpret V2, whose terminal `FIBRE_CONSTANCY_REFUTED` stands
regardless of what V3 returns.

## The defect V3 exists to repair

V2's directory is named `...-full-census` and `FINDINGS_V2.md` calls its 740 rows "the
full census". They are not a census. `FULL_CENSUS_RESULTS_V2.json` records
`cap_hit: true` for **all ten panels**, and the spaces are far larger than the caps —
`H1_n3` alone reports `template_pair_space: 12800` against `evaluated: 120`. The 740
instances are an early prefix of the enumeration order, on the order of one percent of
what is reachable.

That does not touch V2's refutation: showing cost is *not* constant on `f_Bprime`-fibres
requires only exhibiting cost-mixed fibres, and a prefix that exhibits them settles it.
It does undermine the one-sided envelope observed in `REVIVAL_PASS_V1.md`, which is a
statement about a range and therefore about coverage.

## The single change

`CAPS` is multiplied by 20 in every panel, from 740 total to 14,800:

| panel | V2 cap | V3 cap |
|---|---|---|
| H1_n3 / H2_n3 / H3_n3 / H4_n3 / H5_n3 | 120 / 160 / 90 / 90 / 120 | 2400 / 3200 / 1800 / 1800 / 2400 |
| H1_n4 / H2_n4 / H3_n4 / H4_n4 / H5_n4 | 40 / 40 / 24 / 32 / 24 | 800 / 800 / 480 / 640 / 480 |

Nothing else moves. The grammar, route set, skeleton builders, enumeration order, regime
rule, dedupe, zero-target skip and terminal selection are byte-identical to
`run_full_census_v2.py`; the diff is 11 insertions and 5 deletions, of which six lines
are the comment explaining the lift and two are identity strings
(`schema_v3`, output filename). The multiplier was fixed before the run and is not tuned
against any outcome.

Because the enumeration order is unchanged, V2's 740 rows are a **prefix** of V3's rows.
That is the control: if V3's first 740 evaluated instances per panel do not reproduce
V2's values, the generator is not deterministic and no V3 conclusion may be drawn.

## The question, and the pre-declared falsifier

`REVIVAL_PASS_V1.md` records an observed one-sided envelope over V2's prefix:

```
C_Dxx >= f_Bprime - 3          (lower side, no proof)
C_Dxx <= f_Bprime              (upper side, the B'-soundness property, theorem-backed)
```

**The falsifier was declared before V3 was written and is unchanged: any admitted
instance with `f_Bprime − C_Dxx > 3` refutes the lower envelope.**

## Terminals, frozen here

- `ENVELOPE_REFUTED_AT_LIFTED_COVERAGE` — at least one instance has offset > 3. The
  envelope was an artifact of V2's truncation. Record the instance, its panel and its
  offset.
- `ENVELOPE_SURVIVES_20X_COVERAGE` — no instance exceeds offset 3 across 14,800
  instances. This is **not** a proof: it raises the coverage at which the envelope has
  been tested by a factor of twenty and no more. The bound remains unproven, and this
  terminal may not be quoted as establishing it.
- `CANNOT_CHECK_PREFIX_CONTROL_FAILED` — V3's first rows do not reproduce V2's values on
  the shared prefix. Determinism is violated, the comparison is void, and no envelope
  claim may be made in either direction.
- `CANNOT_CHECK_WALL_CLOCK` — the run does not complete within its SLURM limit. Partial
  coverage is reported as partial; a truncated V3 must not be presented as a census, which
  is the exact error V3 exists to correct.

## What V3 cannot do

It cannot rescue fibre constancy. `REVIVAL_PASS_V1.md` established that every candidate
enrichment among the recorded fields is inadmissible — `gap4`, `C_Dplus`, `C_DP` and
`regime` are cost-derived, `panel` is the instance label — and lifting caps records the
same fields on more instances. An admissible enrichment requires a Psi-side invariant
nobody has serialised yet, which is a different successor and is not attempted here.

It also cannot make V2 a census retrospectively. V2's rows stay frozen and its
`FINDINGS_V2.md` stays as written; the coverage qualification lives in
`REVIVAL_PASS_V1.md` and in this protocol.

## Execution

`lu48`, one node, 48 threads, account `lu2026-2-51`. Output
`CAP_LIFT_RESULTS_V3.json` beside this protocol, carrying the full per-panel table with
`cap_hit` per panel so a reader can see immediately whether V3 itself truncated.
