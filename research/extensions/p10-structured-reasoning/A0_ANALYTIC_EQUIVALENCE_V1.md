# P10 A0 analytic equivalence V1 — pre-outcome

This note derives the A0 donor-composed controller result from the frozen case definitions without executing the implementation. It is a finite proof at the registered A0 resolution, not a general theorem about agents.

## Frozen structural predicates

Write:

- `E` = evidence complete;
- `Q` = an admitted observation exists and discriminates live alternatives;
- `P` = local action's execution gate passes;
- `R` = a narrow repair is available and restores admissibility;
- `F` = a representation/frame transform is available and restores admissibility;
- `H` = an active compatible failure blocks the otherwise local action.

The five A0 responsibility families are constructed as:

| Responsibility | Frozen predicates |
|---|---|
| `LOCAL_ACTION` | `E ∧ P ∧ ¬H` |
| `NEED_EVIDENCE` | `¬E ∧ Q` |
| `LOCAL_REPAIR` | `E ∧ ¬P ∧ R` with interface-local block |
| `REFRAME_REPRESENTATION` | `E ∧ ¬P ∧ F` with frame-level block |
| `UNRESOLVED` | `¬E ∧ ¬Q` (and no admitted repair/reframe can discharge the obligation) |

The candidate packet is identical in kind space for every case:

`ACT, ACQUIRE_EVIDENCE, LOCAL_REPAIR, REFRAME_REPRESENTATION, UNRESOLVED`.

## ORION responsibility controller

By frozen definition:

1. if `¬E ∧ Q`, choose `ACQUIRE_EVIDENCE`;
2. if `¬E ∧ ¬Q`, choose `UNRESOLVED`;
3. if `E ∧ P ∧ ¬H`, choose `ACT`;
4. if interface-local blocked and `R`, choose `LOCAL_REPAIR`;
5. if frame-blocked and `F`, choose `REFRAME_REPRESENTATION`;
6. otherwise choose `UNRESOLVED`.

## Donor-composed controller

The donor-composed control is intentionally built only from parent-owned mechanisms:

1. dependency/support/evidence-sufficiency control handles incomplete evidence:
   - `¬E ∧ Q -> ACQUIRE_EVIDENCE`;
   - `¬E ∧ ¬Q -> UNRESOLVED`;
2. symbolic-feasibility/minimal-intervention control handles complete evidence:
   - `E ∧ P ∧ ¬H -> ACT`;
   - interface-local block with restoring `R -> LOCAL_REPAIR`;
   - frame-level block with restoring `F -> REFRAME_REPRESENTATION`;
   - otherwise `UNRESOLVED`.

## Case-by-case equality

| Family | ORION | Donor-composed |
|---|---|---|
| `LOCAL_ACTION` | `ACT` | `ACT` |
| `NEED_EVIDENCE` | `ACQUIRE_EVIDENCE` | `ACQUIRE_EVIDENCE` |
| `LOCAL_REPAIR` | `LOCAL_REPAIR` | `LOCAL_REPAIR` |
| `REFRAME_REPRESENTATION` | `REFRAME_REPRESENTATION` | `REFRAME_REPRESENTATION` |
| `UNRESOLVED` | `UNRESOLVED` | `UNRESOLVED` |

Therefore on the frozen A0 support:

`ORION_RESPONSIBILITY_CONTROL(case) = DONOR_COMPOSED_CONTROL(case)`

for every registered case.

Because the five families are balanced, both controllers have expected A0 accuracy `1.0`, false-closure rate `0`, unnecessary-reframe rate `0`, and identical mean decision cost `9/5 = 1.8` units.

## Scientific consequence

If the official V1.1 execution disagrees with this finite equality, the disagreement is an implementation/evaluator defect or a violation of the frozen case contract and must block promotion.

If execution agrees, A0 establishes a **negative unification result**: the proposed P10 responsibility controller has no residual over the admitted donor composition at this resolution. It does not show that all future epistemic control is solved; it shows only that these five action classes do not justify a new P10 controller claim.

This proof was frozen before the official A0 V1.1 workflow outcome and grants no live-LLM escalation or standalone-paper authority.
