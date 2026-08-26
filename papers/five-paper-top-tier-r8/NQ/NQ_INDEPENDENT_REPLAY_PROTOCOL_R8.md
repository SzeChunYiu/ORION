# NQ Independent Replay Protocol R8

## Objective

Promote the repository claims `D_2(C_5^3)=20`, `D_3(C_5^3)=25`, and the exact `s_{<=T}` spectrum from internal machine-checked candidates to a defensible computer-assisted proof package.

## Frozen claims

1. `s_{<=6}(C_5^3)=24`.
2. `s_{<=7}(C_5^3)=19` and the remaining registered spectrum through `T=12`.
3. `D_2(C_5^3)=20`.
4. exactly 98,622 normalized length-19 `D_2` extremal witnesses under the declared normalization.
5. `D_3(C_5^3)=25`.
6. exactly 230,983 length-25 candidates enter the final three-disjoint predicate and zero survive.

No `D_4` conclusion is part of this replay.

## Team separation

- **Primary team:** may read the current optimized implementation and protocol.
- **Clean-room team:** receives the mathematical specification, frozen input/output schema, and small controls, but not the primary algorithm or code.
- **Proof auditor:** checks the reduction from the mathematical claim to the enumerated state space.
- **Artifact auditor:** checks hashes, build determinism, and logs.

A single implementation rewritten in another language is not automatically independent if it copies the same state compression and pruning logic.

## Mathematical specification

The specification must define:

- canonical encoding of all 125 elements of `F_5^3`;
- multiset/sequence semantics;
- nonempty zero-sum predicate;
- two- and three-disjoint predicates;
- short-zero-sum cutoff predicate;
- normalization group and orbit coverage;
- complement and extension lemmas;
- exact acceptance and rejection states.

The specification, not the existing code, is the source of truth for the clean-room implementation.

## Phase 0 - artifact freeze

Record:

- Git commit and blob SHAs;
- every source and generated data file SHA-256;
- compilers/interpreters and versions;
- optimization and target-architecture flags;
- container digest;
- CPU/RAM and expected run time;
- deterministic seed policy;
- result schema.

Build with at least GCC and Clang where applicable. Run address, undefined-behavior, and integer sanitizers on reduced exhaustive domains.

## Phase 1 - primitive predicate validation

Exhaustively test small groups and short lengths where brute force is trivial:

- `C_2`, `C_3`, `C_2^2`, and bounded `C_5^2` panels;
- all single-element and empty edge cases;
- duplicate-heavy sequences;
- known positive and negative disjoint-zero-sum examples;
- permutation invariance;
- independent recomputation of group sums.

Require exact equality among:

- primary bitset/DP predicate;
- clean-room subset/partition predicate;
- a slow reference enumerator.

## Phase 2 - short-zero-sum spectrum

For each `T=6,...,12`:

1. freeze the search tree and normalization;
2. generate an extremal witness;
3. independently verify that its minimum zero-sum length exceeds `T`;
4. independently verify that no longer obstruction exists;
5. record node counts and terminal counts;
6. compare primary and clean-room results.

The upper proof must not depend on a pruning rule whose validity is inferred from the same result being proved.

## Phase 3 - `D_2`

### Route I

Replay the `s_{<=7}=19` proof and the human complement argument.

### Route II

Run a direct exact two-disjoint enumerator with a different state representation. Verify:

- maximum obstruction length 19;
- zero length-20 survivors;
- 98,622 normalized extremal records;
- every record is a true obstruction;
- no duplicate orbit under the declared normalization unless duplicates are expected and counted;
- the Freeze-Schmid witness is present.

Cross-check random unnormalized sequences by applying random `GL(3,5)` transformations and permutations.

## Phase 4 - `D_3`

1. regenerate every normalized length-19 core from the independently verified `D_2` archive;
2. generate all six-term zero-sum extensions satisfying the exact structural filters;
3. independently recompute the total 230,983 candidate count;
4. apply a clean-room three-disjoint predicate;
5. require zero survivors;
6. replay positive/negative controls, including a two-but-not-three case;
7. sample candidate traces and reconstruct all found zero-sum factors explicitly.

Any search filter must have a written lemma proving that it cannot remove a genuine obstruction.

## Phase 5 - proof integration

The paper proof must state:

- why every length-25 obstruction has the enumerated form;
- why normalization is orbit complete;
- why the final predicate is equivalent to three disjoint nonempty zero sums;
- why the short-zero-sum filters are necessary;
- how the lower witnesses establish equality.

The independent code cannot repair an incomplete mathematical reduction.

## Phase 6 - corridor

After Phases 2-4 pass, independently check the human induction yielding:

- `5k+10 <= D_k <= 5k+11` for all `k>=4`;
- `D_4 in {30,31}`;
- `D_4=30 => D_k=5k+10` for every `k>=2`.

A finite table through any maximum `k` is regression evidence only.

## Required outputs

- `SOURCE_MANIFEST.json`
- `ENVIRONMENT.json`
- `SMALL_DOMAIN_CONTROLS.json`
- `SHORT_SPECTRUM_RESULTS.json`
- `D2_PRIMARY_RESULTS.json`
- `D2_CLEANROOM_RESULTS.json`
- `D2_EXTREMALS.zst` or deterministic generator
- `D3_CANDIDATES.zst` or deterministic generator
- `D3_PRIMARY_RESULTS.json`
- `D3_CLEANROOM_RESULTS.json`
- `COUNT_AND_HASH_COMPARISON.json`
- complete stdout/stderr logs
- human `PROOF_AUDIT.md`
- archival DOI or immutable release identifier.

## Pass terminal

`NQ_D2_D3_INDEPENDENT_REPLAY_PASS` requires exact claim/count agreement, no unresolved sanitizer defect, full mathematical state-space coverage, and release of a replayable archive.

Any mismatch produces `CANNOT_PROMOTE` until explained and rerun under a new frozen version.
