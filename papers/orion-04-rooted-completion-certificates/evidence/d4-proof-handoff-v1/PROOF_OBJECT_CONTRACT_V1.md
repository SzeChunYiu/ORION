# ORION04.D4_PROOF_OBJECT_CONTRACT.v1

**Status:** `DESIGN_ONLY__NO_D4_OUTCOME_AUTHORITY`  
**Scientific authority delta:** `NONE`  
**Controlling present state:** `AWAITING_NEW_ONE_SHOT_AUTHORIZATION`; `d4_rounds_consumed: 0`.

## Purpose

Define, before any new authorized D4 execution, the minimum proof object that could support an exact claim `D_4(C_5^3)=30` without treating a solver terminal, a shared candidate stream, or a checksum as a mathematical proof.

This contract does **not** authorize execution and contains no D4 outcome.

## Required proof decomposition

An exact result has two logically independent halves.

### U — upper-bound construction (`D_4 <= 30`)

The packet must contain:

1. a canonical machine-readable description of one size-30 construction;
2. a standalone verifier derived from primitive `C_5^3` semantics, not from the search implementation;
3. a deterministic verification transcript enumerating every required rooted-completion predicate checked for that construction;
4. a digest binding the construction bytes, verifier source, environment lock and transcript.

A search program reporting `FOUND_30` is insufficient unless the emitted construction passes the standalone verifier.

### L — lower-bound impossibility (`D_4 >= 30`)

The packet must prove that every size-31 candidate violates the target property. It must contain **two independent proof routes**:

- **L-A, certificate route.** A declarative finite encoding plus a proof certificate whose checker is substantially simpler than the producing solver. If SAT/SMT is used, the packet must expose a checkable unsatisfiability certificate or an equivalently explicit derivation; a solver exit code alone is not evidence.
- **L-B, independently derived route.** A second implementation whose state representation and transition/constraint derivation are reconstructed from primitive `C_5^3` semantics and do not consume L-A's normalized candidate stream, learned clauses, orbit table or decision trace.

Both routes must bind the same mathematical proposition but need not share the same encoding.

## Symmetry/orbit evidence

Symmetry reduction may accelerate either route but is load-bearing only if the packet emits:

1. generators acting on the primitive object domain;
2. a verifier that each generator preserves the target predicate;
3. canonicalization rules;
4. orbit representatives and multiplicities or an equivalent coverage certificate;
5. an independently checked equality between the unreduced domain cardinality and the sum of represented orbit mass.

If any symmetry certificate is absent or fails, the exact claim must remain `CANNOT_CHECK_SYMMETRY_COVERAGE` unless a non-symmetry proof route closes the same obligation.

## Independence boundary

The following do **not** count as two independent routes:

- the same encoder with different random seeds;
- two solvers consuming the same generated CNF while the encoder is load-bearing;
- two executables importing the same candidate-normalization/orbit module;
- a second checker that merely replays the producer's accept/reject bits;
- duplicated containers or hosts under the same implementation path.

Allowed sharing is limited to a small, explicitly enumerated primitive-semantic specification and cryptographic/hash utilities whose correctness is not the mathematical claim under test.

## Failure-preserving terminals

The execution packet must distinguish at least:

- `EXACT_D4_30_PROVED` — U, L-A and L-B all pass and all authority/custody gates pass;
- `CONSTRUCTION_ONLY__LOWER_BOUND_OPEN`;
- `LOWER_BOUND_ONLY__CONSTRUCTION_OPEN`;
- `CANNOT_CHECK_CERTIFICATE_REPLAY`;
- `CANNOT_CHECK_INDEPENDENCE`;
- `CANNOT_CHECK_SYMMETRY_COVERAGE`;
- `CANNOT_CHECK_CUSTODY_OR_AUTHORIZATION`;
- `ADVERSE_ROUTE_DISAGREEMENT`.

Route disagreement is retained as an adverse result; it must not be resolved by majority vote or by deleting the dissenting route.

## Required hostile mutations

Before an `EXACT_D4_30_PROVED` terminal is accepted, the verification harness must demonstrate rejection of at least these mutations:

1. delete or alter one element of the size-30 construction;
2. change one primitive-semantic predicate used by a proof route;
3. delete or corrupt one load-bearing lower-bound certificate step;
4. perturb a symmetry generator or one orbit multiplicity;
5. substitute a mismatched source/environment digest;
6. reuse a consumed nonduplication key or omit the one-shot authorization record;
7. force L-A and L-B to disagree on at least one synthetic small control instance.

Each mutation must fail at the layer it targets; a global checksum failure alone does not establish semantic checker sensitivity.

## Small-instance calibration

Before D4 execution, both lower-bound routes and the construction verifier must be run on a frozen suite of smaller instances whose exact answers are already independently established. The suite must include:

- at least one satisfiable/constructible control;
- at least one impossible control;
- at least one symmetry-rich control;
- at least one intentionally malformed proof object.

The exact control identities and expected answers must be frozen before the D4 outcome is accessed.

## Publication claim rule

Only the conjunction of mathematical proof-object success **and** the repository's separate one-shot authorization/custody requirements may support an exact D4 manuscript upgrade. Mathematical correctness cannot waive custody; custody cannot substitute for mathematical correctness.
