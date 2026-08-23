# P9-U-T3 / P9-U-T4 receipt: the grid is declared, and one of the two attacks landed

- **Date**: 2026-08-21
- **Gates addressed**: `P9-U-T3`, `P9-U-T4` (issue #662)
- **Authority**: `NO_SCIENTIFIC_AUTHORITY_HOSTILE_AUDIT_ONLY`. Neither gate is discharged by this
  work. Both remain **BLOCKED**.
- **Artifacts**
  - freeze `protocol/P9_U_T4_HOSTILE_REPRESENTATION_ATTACK_FREEZE_2026-08-21.md` + `.json`
    (`parameters_sha256 sha256:3a4c8a1e4211e8032ab3bbee0f9bb16f0d1f626b42f9c96c6b40cf0f115e18eb`)
  - freeze `protocol/P9_U_T3_FRONTIER_GRID_FREEZE_2026-08-21.md` + `.json`
    (`parameters_sha256 sha256:33138930449fda9a77c99a325f6c9ca2c13b58291218beb94704ea045334fe8c`)
  - result `evidence/P9_U_T4_HOSTILE_ATTACK_RESULT_2026-08-21.json` (exit 3, `FAIL`)
  - status `evidence/P9_U_T3_FRONTIER_GRID_STATUS_2026-08-21.json` (exit 4, `CANNOT_CHECK`)
  - instruments `src/orion/study/p9/hostile_representation_attacks.py`,
    `src/orion/study/p9/frontier_grid.py`
- **No existing P9 result, receipt, protocol or evidence artifact is modified.** Only new files.

---

## P9-U-T4 — the attacks were named and had never been run. They have now been run.

The two hostile alternatives appear in exactly one place in the repository,
`successor/P9_U_MANUSCRIPT.tex` ("Equal-token/length controls, order/symbol reminting,
semantic-orbit controls and exact information checks are mandatory"; hypothesis H4). No runner, arm,
fixture or result for any of them existed.

They cannot be run against the result they were written for: the frozen Qwen2.5 0.5B/1.5B/3B
successor run of issue #618 has no outcome, no checkpoint here, and no reachable provider from this
environment. They were therefore run against the one representation contrast P9 publishes: **D1
v1.2**, regenerated locally to the shipped `dataset_manifest_digest sha256:27752984…`.

### Verdict: `T4_ATTACK_SUCCEEDED` / `FAIL`

| attack | components | outcome |
|---|---|---|
| **representation-length (`H_LEN`)** | RL-1, RL-2, RL-3 | **did not succeed**, each over 128 protected cases |
| **format-prior (`H_FMT`)** | FP-2 semantic orbit on `TYPED_SERIALIZED_BAG` | **succeeded**, 32 violations / 128 opportunities |
| format-prior, other components | FP-1a, FP-1b, FP-2 on 7 other arms, FP-3 on 8 arms | did not succeed; 14 of 21 components are `CANNOT_CHECK` with a stated zero denominator |

### The length attack does not explain D1

On the frozen protected split, a view carrying only per-side presence and cardinality scores
`0.75`, and a view carrying only cross-side agreement of presence and cardinality scores `0.875`,
against `TYPED_RELATIONAL`'s `1.0`. On the **equal-token/length control** — a regenerated dataset in
which every corruption preserves every coordinate's cardinality and presence (192 corrupted
instances, 1536 coordinate-side comparisons, 0 mismatches, 0 of 512 gold labels moved) —
`TYPED_RELATIONAL` still scores `1.0`, while `UNTYPED_PAIR` falls from `0.90625` to `0.609375` and
`LENGTH_RELATIONAL` from `0.875` to `0.75`.

That is a real result, and its direction is worth stating precisely: **most of the responsive
comparator's score was length; the typed arm's was not.**

### The format-prior attack succeeds against the same-information serialized arm

Apply one bijection to every atomic value in the eight comparison coordinates (220 atoms, 220
distinct images), leaving structure, mechanics, dependency topology, surfaces and splits untouched.
All 512 gold labels are preserved, verified instance by instance. Then:

```
TYPED_SERIALIZED_BAG   base   accuracy 0.75   2 distinct predictions   informedness 0.5
TYPED_SERIALIZED_BAG   orbit  accuracy 0.50   1 distinct prediction    informedness 0.0
                              32 of 128 protected answers changed
```

The transform is an *exact renaming of that arm's feature keys*: 279 distinct keys before and after,
150 train keys, 26 surviving in-vocabulary protected keys, and the same seven distinct protected
rows with the same multiplicities `[48, 32, 15, 14, 11, 4, 4]`. Nothing about the arm's input changed
except the names of its columns, and a whole 32-case group changed its answer.

Its orbit contains the officially shipped value: `0.50` with a single label on all 128 cases is one
point of it, `0.75` with two labels is another. `typed_minus_same_information_serialized` is
`+0.50`, `+0.25` or `CANNOT_CHECK` depending only on which symbols the coordinate values were
written with.

The six arms whose features are functions of equality, presence and cardinality —
`TRANSCRIPT_BAG`, `UNTYPED_PAIR`, `TYPED_RELATIONAL`, `LENGTH_ONLY`, `LENGTH_RELATIONAL`,
`SERIALIZED_PATHONLY` — present `0` of `128` changed feature dicts under the orbit. Those components
are reported `CANNOT_CHECK / NEVER_EXERCISED`, not `PASS`: the arms are invariant by construction,
and a guard with no opportunity has not held. `SERIALIZED_INDEXED`, the reversible-index reformat,
is the one arm the orbit reaches and does not move: `0` violations over `128` opportunities, `PASS`.

### Two things the unblock asked for that turn out to have no denominator on D1

- **Order reminting is vacuous by construction.** `build_method_realization` passes every sequence
  coordinate through `tuple(sorted(set(...)))`, so a permuted dataset reproduces the base manifest
  digest byte for byte and `0` of `128` feature dicts change for **every** arm. All 8 FP-3
  components are `CANNOT_CHECK`. This was declared in the freeze before the measurement and is
  reported as an absent measurement, never as a control that held.
- **`typed_minus_transcript` is not eligible to be attacked.** Its comparator answers `ALIGNED` on
  all 128 protected cases, so `measure_contrast_margin` returns `CANNOT_CHECK / COMPARATOR_CONSTANT`
  and the `+0.75` is `1 − prior(ALIGNED)`. An attack cannot fail against a margin that was never
  measured.

### Same-information round trip: checked for the first time, and it holds

D1's protocol asserts that `TYPED_SERIALIZED_BAG` carries the same information as `TYPED_RELATIONAL`.
All 512 instances' serialized token lists decode back to their typed payload exactly. The assertion
is true. What the orbit result shows is that carrying the same information is not the same as
*answering from* it.

---

## P9-U-T3 — the grid is declared, and it has no outcomes

`T3_GRID_DECLARED_NO_CELL_EXECUTED` / `CANNOT_CHECK`, denominator **0 of 1344**.

`k ∈ {1,2,4,8}` × 7 representation families × `{QWEN2_5: 0.5B/1.5B/3B/7B, LLAMA3_2: 1B/3B}` ×
`C ∈ {1,4,16,64}` × `{FORMAL_RELATIONAL, NON_FORMAL_PROCEDURAL}`, read at `q ∈ {0.70, 0.85, 0.95}`,
with `N` fixed at 4 and `N*` declared out of scope. `S*` and `C*` are the first declared ladder point
reaching `q`, or `RIGHT_CENSORED`; no interpolation, no extrapolation, no fitted exponent anywhere in
their definition. A cell missing from an outcome file makes the whole grid `CANNOT_CHECK`. A fully
executed grid in which no crossing test has two uncensored frontiers is `CANNOT_CHECK`, not `PASS`.

The grid is not executed here and no surrogate is substituted for it: no open-weight checkpoint is
present in this repository and the environment's proxy returns `403` to `CONNECT` for external
providers. A classical-learner capacity ladder is not a model-scale ladder, and naming one `S*`
would be a weaker proxy wearing the measurement's name.

---

## What this licenses, and what it does not

**Does not license.** Nothing here discharges `P9-U-T3` or `P9-U-T4`. Both gates guard the successor
direct-LLM result, which has no outcome. `P9-U-T1` is still blocked on it.

**Licenses, and only this.**

1. The two attacks now exist as runnable gates with stated denominators, and one of them lands.
2. On D1, the representation-length alternative does not account for `TYPED_RELATIONAL`'s decision;
   it does account for most of `UNTYPED_PAIR`'s.
3. On D1, the format-prior alternative *does* account for the same-information serialized arm's
   published number. `main.tex`'s sentence — "explicit relational comparison makes those fields more
   useful" — cannot rest on `\DOneTypedMinusSerialized`, because that comparator's protected answers
   move under a renaming that changes no meaning.
4. The one D1 margin that survives is the one the existing failure record already identified:
   `TYPED_RELATIONAL − UNTYPED_PAIR = +0.09375`, against a comparator that departed from its modal
   answer on 76 of 128 cases, and whose two arms are both structurally invariant under the orbit.
