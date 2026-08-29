# Move census, hidden-operation hostile control, and confluence — ORION01.MOVE_CENSUS_AND_CONFLUENCE.v1

`authority: MEASUREMENT_AND_PROOF_ONLY` · `scientific_authority_delta: NONE` ·
`submission_authority: false`. Extends `experiments/contextual-move-completeness-v1`; read-only
on every frozen artifact. Every number below comes from `check_move_census_and_confluence.py`
run on `/usr/bin/python3` 3.9.6.

## What the prior art already established (not re-claimed here)

`contextual-move-completeness-v1` froze a finite model — states `1..n`, declared candidate moves
the strictly resource-decreasing pairs `(s,t)` with `s>t`, a registry any subset — and proved, at
terminal `T1_QUOTIENT_REPAIRS_COMPLETENESS_ONLY`: **Theorem A**, `terminal_complexity(n,R)=1`
**iff** `R` is source-complete, both directions over all 33,866 registries (K2); **Theorem B**,
the source-complete count is `prod_{s=2}^{n}(2^(s-1)-1)`, matching the frozen
`REGISTRY_NONIDENTIFIABILITY_R12` histogram at complexity 1 (K1); **Claim C**, the optimizer
signature stays constant on the quotient, repairing completeness but **not** registry
identifiability. R12 also froze `same_optimizer_signature_for_every_registry: true`,
`one_unresolved_edge_changes_terminal_complexity: true` and 31 `hidden_edge_controls` rows; R11
froze the 12-move production registry at `CANNOT_CHECK_MOVE_COMPLETENESS`, all 12 single-move
omissions rejected. This packet reuses that model verbatim and adds the three stages the PR-1469
audit records as `false`: `omitted_move_hostile_control`, `interaction_joinability_verified`, and
the runtime side of the move census.

## Stage 1 — census

### Source side (pinned production registry)

12 declared moves, all reachable from the `full_reduce` entrypoint, none unreachable, all with
`exact_search_enabled`. By kind: `saturating_single_vertex` 4, `saturating_double_vertex` 2,
`whole_graph_batch` 2, `whole_graph_batch_double_vertex` 2, `whole_graph_cleanup` 1,
`whole_graph_normalization` 1. 16 public PyZX operations are excluded; the 3 hostile extension
symbols are disjoint from the registry and lie inside that excluded set. The frozen round terminal
is `CANNOT_CHECK_MOVE_COMPLETENESS`, over a 4,681-word input domain of which 74 words executed
before the fail-closed terminal.

**Eight independent frozen counts of the same object all equal 12** (C1): the source registry's
`registered_schemas` and `registered_symbol_order`; the R11 results' `discovered_count`,
`discovered_registered_symbols`, `hostile_single_omissions`, `hostile_omissions_rejected`; and the
post-review `mutated_registry_omissions` with its `_rejected` count. The five underlying *symbol
sets* are equal too, not just the cardinalities. Three independently recorded call graphs —
`control_call_graph`, R11 `observed_control_call_graph`, post-review `full_pinned_control_call_inventory` — reduce to the
same 12 symbols (C10) under a normalization recorded in `RESULT_V1.json`: strip one receiver
qualifier (`BaseGraph.remove_isolated_vertices` / `g.remove_isolated_vertices` /
`remove_isolated_vertices` are one move), drop the four control nodes, and subtract the frozen
`explicit_benign_nonmutating_calls`. Without it a naive set comparison reports a false mismatch.

### Runtime side (frozen abstract model) — exhaustive over all `2^E` registries, `n=2..6`

| n | moves | registries | source-complete | = closed form | = frozen R12 @1 | move occurrences | = `E·2^(E−1)` | live | dead |
|---|---|---|---|---|---|---|---|---|---|
| 2 | 1 | 2 | 1 | 1 | 1 | 1 | 1 | 1 | 0 |
| 3 | 3 | 8 | 3 | 3 | 3 | 12 | 12 | 10 | 2 |
| 4 | 6 | 64 | 21 | 21 | 21 | 192 | 192 | 148 | 44 |
| 5 | 10 | 1,024 | 315 | 315 | 315 | 5,120 | 5,120 | 3,832 | 1,288 |
| 6 | 15 | 32,768 | 9,765 | 9,765 | 9,765 | 245,760 | 245,760 | 182,928 | 62,832 |

A move occurrence is *live* when its source is reachable from top state `n`, so it can fire in a
run; otherwise *dead*. Reachability is computed twice — breadth-first closure and iterated
relational composition — agreeing everywhere (C8). Totals match `E·2^(E−1)` (C13); the
source-complete column reproduces the prior art and the frozen histogram (C2, C12).

## Stage 2 — hidden-operation hostile control

**Question.** Can an *undeclared* operation change the rewrite relation while the declared
observable does not move?

Two observables are separated. The **weak** one is the R12 optimizer signature `{n, 1, 1}`, marked
`VACUOUS_BY_CONSTRUCTION`: R12 froze `same_optimizer_signature_for_every_registry: true`, so it is
blind to every change, declared or hidden, and mimicry against it would restate prior art as a new
result. The weight is on the **strong** observable, `terminal_complexity`, which R12 shows *is*
sensitive; as control C6 all **31/31** frozen `hidden_edge_controls` rows (`n=2..32`) reproduce
from the model, 0 mismatches. Ground truth is the normal-form map `s ↦ NF(s)`. Over `n=2..6`, all
registries and three undeclared operation classes, 778,502 pairs were classified:

| class | count | meaning |
|---|---|---|
| `BENIGN` | 374,240 | relation unchanged and metric unchanged |
| `MIMIC` | 250,683 | **relation changed, metric did not move at all** |
| `HONESTLY_DETECTED` | 67,886 | relation changed and metric moved |
| `OBSERVABLE_UNDEFINED` | 60,260 | no state terminal; the declared metric is undefined |
| `FALSE_IMPROVEMENT` | 25,433 | **metric falls to 1 while a state loses its normal form** |

`FALSE_IMPROVEMENT` is the strict `→1` subset, so 25,433 is a **lower bound**: a hidden op driving
`terminal_complexity` 6→2 while destroying a normal form counts `HONESTLY_DETECTED` — it moved.

**A mimicking witness exists.** Two, of different kinds, both maximally sharp at `n=6`:

- **`FALSE_IMPROVEMENT`** — declared registry `{(2,1),(3,1),(4,1),(5,1)}`, hidden self-loop
  `(6,6)`. `terminal_complexity` falls **6 → 1**, reading *perfectly complete*, while `NF(6)` goes
  from `{6}` to `∅`: state 6 never reduces at all. The metric moves from its worst value to its
  best while the system gets strictly worse.
- **`MIMIC`** — same registry, hidden self-loop `(1,1)`. `terminal_complexity` stays **6**, wholly
  unmoved, while five of six states silently lose their normal form.

**The control discriminates** (C7). `TRANSITIVE_COMPOSITE` — adding `(s,t)` when `t` is already
reachable from `s` — is `BENIGN` in **74,320 of 74,320** cases, never any other class. A control
flagging every hidden operation would prove nothing; this one passes the redundant class.

**Not an artifact of stepping outside the model.** The objection is that registries are
*defined* as sets of strictly-descending edges, so a self-loop is outside the model. But the vulnerable
shape — guard accepts, effect is the identity — is present in the pinned registry *by kind*:
`to_gh` (`whole_graph_normalization`, idempotent), `remove_isolated_vertices`
(`whole_graph_cleanup`, vacuous when nothing is isolated) and the six `saturating_*` moves, whose
last application is a no-op by construction. Established: **the declared completeness metric is
not invariant under a semantically null operation**, and the registry declares such move kinds.

## The separation: confluence is strictly weaker than completeness

Source-completeness and confluence are not the same property, and the gap is large and grows.

- **Source-complete ⟹ confluent.** Measured, not assumed: at every `n`, all source-complete
  registries are confluent and **0** non-joinable pairs occur in any of them (C9).
- **Confluent ⇏ source-complete.** Counts of confluent-but-not-source-complete registries:
  **1, 4, 22, 191, 2,926** for `n=2..6`. The `n=6` witness is not degenerate — it holds 10 of the
  15 declared moves (the complete descending graph on states `1..5`, state 6 isolated). Every
  state `1..5` reduces confluently to 1, so the system is fully confluent, yet
  `terminal_complexity = 6`, the worst possible value.

So confluence recovers neither the completeness value (Theorem A ties that to source-completeness)
nor, by R12's frozen signature constancy, registry identifiability — extending Theorem A, not
duplicating it.

## Stage 3 — critical pairs and confluence

This system has no terms and no left-hand-side overlap, so the Knuth–Bendix critical-pair
construction does not apply literally. Every divergence is a **local peak** `t₁ ← s → t₂` at a
single source state; those are enumerated, counted **unordered**, and are what "critical pair"
denotes below.

| n | critical pairs | = closed form `C(n,3)·2^(E−2)` | joining | non-joinable | in source-complete | locally confluent | confluent | = recursion |
|---|---|---|---|---|---|---|---|---|
| 2 | 0 | 0 | 0 | 0 | 0 | 2 | 2 | 2 |
| 3 | 2 | 2 | 1 | **1** | 0 | 7 | 7 | 7 |
| 4 | 64 | 64 | 36 | **28** | 0 | 43 | 43 | 43 |
| 5 | 2,560 | 2,560 | 1,592 | **968** | 0 | 506 | 506 | 506 |
| 6 | 163,840 | 163,840 | 110,704 | **53,136** | 0 | 12,691 | 12,691 | 12,691 |

Three independent derivations agree at every `n`. The closed form `C(n,3)·2^(E−2)` follows from
`Σ_d C(m,d)C(d,2) = C(m,2)2^(m−2)` and the hockey-stick identity (C3). The confluent-registry count
is reproduced by a recursion that never enumerates a registry — it tracks only the partition of
built states into normal-form classes, a new state taking either an empty target set or a nonempty
subset of exactly one class (C5). Local confluence equals confluence at every `n` (C4), as
Newman's lemma requires for a terminating system; scoped to the declared system, since the hostile
stage deliberately breaks termination. **Non-joinable pairs exist — a preserved negative.** The minimal witness, embedded at every `n≥3`:
registry `{(3,1),(3,2)}`, peak at state 3 with targets 1 and 2. Descendants of 1 are `{1}`, of 2
are `{2}`; disjoint, so the peak does not join. 32.4% of all critical pairs at `n=6` are
non-joinable, none in a source-complete registry.

## CANNOT_CHECK — declared and not conflated with a pass

The full run exits **4** (`measured, with declared CANNOT_CHECK sub-stages`), never 0, so a
partial result cannot be read as a clean pass; exit 3 is reserved for a control failure.

1. **`S3b_live_production_confluence` — CANNOT_CHECK.** Confluence of the 12 pinned PyZX macro
   operations on real ZX graphs is not decided: this packet is standard-library only by protocol,
   and `import pyzx` fails on all three interpreters on this host (`/usr/bin/python3` 3.9.6,
   miniforge 3.13.12, homebrew 3.14.6). Stage 3 covers the abstract move system only.
2. **`S2b_hidden_operation_in_production` — CANNOT_CHECK.** Whether the pinned PyZX build
   actually contains an operation of the mimicking shape is not decided. What is decided is that
   the frozen model admits the witness and that the registry declares move kinds of that shape.
3. Smoke mode (`--smoke`) cross-checks only histogram rows `n=2..4`; the full run covers `n=2..6`.
   The checker resolves its five frozen inputs by path, so `RESULT_V1.json` records their SHA-256
under `input_bindings` and **C14** compares three against digests recorded independently *inside
other frozen artifacts* when those were sealed (`frozen_registry_sha256`, `raw_result_sha256` in
the R11 post-review audit; `json_receipts[0].sha256` in the PR-1469 audit). All three match, so
the bytes measured are the bytes frozen; all five also match the blobs at `344c1225c`.
## Checker validation — exit codes actually obtained

`--self-test` exercises each failure path against perturbed input **and** asserts the no-alarm
case on unperturbed input. Full run **exit 0, 12/12 detected**; smoke run **exit 0**.

| perturbation | expected | alarms (full) | detected |
|---|---|---|---|
| P0 unperturbed panel | no alarms | 0 | yes |
| P1 frozen histogram off by one | C2 fires | 1 | yes |
| P2 critical-pair closed form off by one | C3 fires | 5 | yes |
| P3 confluent recursion off by one | C5 fires | 5 | yes |
| P4 injected fake non-joinable pair | C4 fires | 8 | yes |
| P5 second reachability method corrupted | C8 fires | 5 | yes |
| P6 frozen hidden-edge row tampered | C6 mismatch | 1 | yes |
| P7 frozen hidden-edge rows unperturbed | no mismatch | 0 | yes |
| P8 source-census symbol dropped | C1 fires | 2 | yes |
| P9 source census unperturbed | no alarms | 0 | yes |
| P10 frozen receipt digest tampered | C14 mismatch | 1 | yes |
| P11 frozen receipts unperturbed | no mismatch | 0 | yes |

The first version of this self-test returned **exit 5**: P1 corrupted histogram row `n=6` while
smoke mode enumerates only `n=2..4`, so nothing could fire. That was a defect in the test, not in
the checker, recorded because it is the evidence that the self-test catches undetectable
perturbations rather than rubber-stamping them. All 14 controls (C1–C14) pass on the full run
with an empty `alarms` list; terminal
`T1_CENSUS_COMPLETE__HIDDEN_OP_WITNESS_FOUND__CONFLUENCE_PARTIAL`.

## Limits

The model is the frozen finite one, `n=2..6`; closed forms are proved for all `n` but checked on
that range. Nothing here speaks to real ZX graphs, PyZX behaviour, or registries outside the
model. No frozen record is edited: R12's authority fields (including its `external_independence`
and `novelty` `CANNOT_CHECK` fields), R11's `CANNOT_CHECK_MOVE_COMPLETENESS`, and
`production_transfer: false` stand as frozen — the witness is a reason they should.
