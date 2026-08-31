# Five-Paper Atomic Verification V6

> Historical fail-closed audit. Superseded by
> `FIVE_PAPER_ATOMIC_VERIFICATION_V7_2026-08-25.md` after the cited blockers
> were repaired or the affected claims were removed.

Date: 2026-08-25

## Control state

- Writing pipeline: `SzeChunYiu/academic-paper-skills` at merged `main` commit
  `fefc3f138e9ad30a56e35f50cc44f06850ccc89d` (PR #6).
- ORION branch: `codex/orion-publication-rewrite-20260825`.
- Closure constraint: `FORMAL_COMPONENTS_ONLY_NO_UNIFIED_CALCULUS`.
- Forbidden novelty claim: no unified or universal ORION calculus.
- Author: Sze Chun Yiu.
- Correspondence: `sze-chun.yiu@fysik.su.se`.
- Affiliation and ORCID: not supplied; no value has been inferred.
- Release rule: a manuscript is not cleared for public posting while any
  load-bearing row is `UNRESOLVED`, `BLOCKED`, or `NOT_ASSESSABLE`.

## Reconstructed handoff

| Paper | Canonical source | Branch/worktree | Provisional target | Current status |
|---|---|---|---|---|
| A | `papers/theory-A-multitag-constraint-rank/MANUSCRIPT_V3_PIPELINE.md` | this branch / this worktree | Quantum; QST or TQC fallback | `BLOCKED` pending a source-supported bridge from the abstract grammar to TARE and standalone finite-record verification |
| B | `papers/theory-B-certificate-complexity/MANUSCRIPT_V3_PIPELINE.md` | this branch / this worktree | ACM TQC or specialist theory venue | `BLOCKED` pending a standalone proof/certificate for the dependent-triple localization inequalities |
| C | `papers/theory-C-low-order-information/MANUSCRIPT_V3_PIPELINE.md` | this branch / this worktree | Quantum after a direct quantum bridge; QIP/TQC fallback | `BLOCKED` because the supplied exact implementations are not standalone and the quantum application is not source-grounded |
| D | `papers/theory-D-falsification-authority/MANUSCRIPT_V3_PIPELINE.md` | this branch / this worktree | Journal of Automated Reasoning | `BLOCKED` on target-fit depth, author declarations, and affiliation; executable semantics are locally reproducible |
| Non-quantum | `papers/nonquantum-c5cubed-davenport/MANUSCRIPT_V3_PIPELINE.md` | this branch / this worktree | Electronic Journal of Combinatorics; JNT alternative | `BLOCKED` because all principal bounds are conditional on unverified exact inputs and bounded searches lack clean-room replay |

## Atomic dispositions

### Paper A

| Atomic claim or surface | Disposition | Reason |
|---|---|---|
| Binary alphabet spanning `H` has deletion threshold equal to `rank(H)` | `VERIFIED` | A finite spanning alphabet contains a basis; linear dependence gives the reverse inequality. The earlier suggestion of a smaller threshold was removed. |
| Zero-sum deletion terminates at the alphabet-restricted threshold | `VERIFIED` | Each recomputed deletion strictly lowers total support. |
| General MultiTag ceiling is intrinsically sharp | `NOT_APPLICABLE` | The manuscript now expressly makes no such claim. |
| One-Tag finite record proves a general intrinsic theorem | `NOT_APPLICABLE` | The finite record is now calibration only. |
| Abstract grammar is an exact model of published TARE | `UNRESOLVED` | The manuscript cites TARE but does not yet give a source-supported equivalence map. |
| Submission surface | `BLOCKED` | No supplied affiliation; target fit remains unresolved. |

### Paper B

| Atomic claim or surface | Disposition | Reason |
| Abstract five-bit deletion complexity is five | `VERIFIED` | It is now defined directly on the standard basis of `F_2^5`; it is not asserted as a production lower bound. |
| Possibility of `zsf(H;A) < rank(H)` when `H=<A>` | `NOT_APPLICABLE` | The false possibility has been removed. |
| Dependent-triple compiler has intrinsic support one | `SUPPORTED_INTERNAL` | The manuscript states the full objective and local cases, but the supplied package does not provide a standalone checker for all localization inequalities. |
| `5t` versus `t` compares one common support invariant | `NOT_APPLICABLE` | The manuscript now labels this a numerical comparison between an abstract certificate budget and explicitly defined product support. |
| Direct enumeration ratio | `BOUNDED_INFERENCE` | Valid only for fixed `t` and the declared direct-support enumerator; no unrestricted lower bound is claimed. |
| Submission surface | `BLOCKED` | Main compiler theorem lacks a self-contained external verification path and the quantum-literature bridge is thin. |

### Paper C

| Atomic claim or surface | Disposition | Reason |
| Low-order parity instances agree on every proper labeled subset | `NOT_APPLICABLE` | Corrected to the proved range: labeled subsets of size at most `m-2`. |
| Mixed-gadget blocks can be removed without worsening the objective | `VERIFIED` | Replacing a negative-credit mixed block by singleton blocks gives zero credit and cannot increase maximum width. |
| Boolean-lattice kernel formula | `VERIFIED` | Follows by Möbius inversion under the stated marginal conditions. |
| Standalone reproducibility of exact implementations | `BLOCKED` | Current ancillary programs depend on repository modules/protocols not included in the public source package. |
| Quantum-journal fit | `UNRESOLVED` | The mathematical partition model is explicit, but its claimed quantum-compilation instantiation is not tied to primary quantum sources. |

### Paper D

| Atomic claim or surface | Disposition | Reason |
| Fair accumulating schedules reach the least fixed point | `VERIFIED` | The schedule now initializes seeds, excludes refuted heads, and unions only enabled nonempty transfers. |
| JSON Schema implements semantics | `NOT_APPLICABLE` | Corrected: the schema validates shape; the evaluator implements semantics. |
| Canonical typed retraction | `VERIFIED` | It is the unique proof-supported post-refutation assignment relative to declared seeds, rules, caps, and refutations. |
| Executable package | `VERIFIED` | Schema, evaluator, fixtures, and unit tests form a standalone surface. |
| JAR submission readiness | `BLOCKED` | Affiliation/declarations are missing and editorial significance beyond illustrative synthetic fixtures is not yet established. |

### Non-quantum paper

| Atomic claim or surface | Disposition | Reason |
| Width-one corridor | `BOUNDED_INFERENCE` | The derivation is valid only under the explicitly declared values and lower-line hypothesis. |
| Saturation removes multiplicity three | `BOUNDED_INFERENCE` | Valid for saturated obstructions, including support at least nine only under the declared length-32 inverse-theorem input. |
| Rank-forcing phase | `BOUNDED_INFERENCE` | Valid for saturated obstructions with `s >= 9` under `eta(C_5^2)=13`. |
| Support-through-ten exclusion | `SUPPORTED_INTERNAL` | Two related implementations agree, but no independent clean-room replay is present. |
| Support-through-22 exclusion | `SUPPORTED_INTERNAL` | Bounded computation only; it has no theorem authority. |
| Exact value of `D_4(C_5^3)` | `UNRESOLVED` | The manuscript correctly retains `{30,31}`. |
| Submission readiness | `BLOCKED` | Load-bearing source theorems need exact locators/verification and computation needs a public standalone replay surface. |

## Surface decisions

- Display mathematics was removed from all abstracts; equations there remain
  inline.
- Submission PDFs use precise title-derived filenames.
- Internal experiment labels such as `R6M`, `R6I`, `QG*`, and `ORION` do not
  appear in the five submission manuscripts.
- Data/code statements describe files present in this version and contain no
  promised future arXiv identifier.
- The updated conservative surface scanner reports punctuation errors inside
  LaTeX subscripts/indices (for example `P_{j0},P_{j1}`) and list-indentation
  spaces. Context review classifies these as scanner false positives rather
  than prose defects. Its remaining acronym/range items are standard terms or
  bibliography-style review items, not release placeholders.
- Public arXiv posting is not authorized by this report: the scientific gate is
  fail-closed, and arXiv account, license, category/endorsement, affiliation,
  and final author certification remain user-controlled steps.

## Terminal disposition

`BLOCKED_NO_PUBLIC_POSTING`

This is not a judgment that the manuscripts lack value. It means the new
pipeline correctly refuses to convert internally plausible work into a public
submission until every load-bearing claim has a reader-reproducible authority
path.
