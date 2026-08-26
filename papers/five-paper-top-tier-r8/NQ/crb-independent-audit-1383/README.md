# CR-B independent bundle audit

This additive subtree freezes a clean-room verifier for the CR-B aggregate
bundle contract. It does not import or reuse an aggregate producer's
normalizer, partition builder, manifest reader, or proof-checking wrapper.

## Frozen implementation hypothesis

The audit accepts a bundle only when all three independent checks agree:

1. each declared representative is the lexicographically minimal image found
   by enumerating every ordered independent anchor triple over `F5`, inverting
   the resulting `3 x 3` matrix, transforming every column, and sorting the
   transformed columns;
2. deterministic half-open partition ranges cover `[0, domain.size)` exactly,
   are nonempty and disjoint, bind unique IDs/range digests, and contain the
   exact consecutive record ordinals they declare; and
3. every `UNSAT` record binds one unique CNF/proof pair by path, byte count, and
   SHA-256, the declared proof directory contains no unlisted file, and the
   hash-pinned external DRAT/DRUP checker returns exit code zero for each pair.

The checker is invoked directly as `CHECKER CNF PROOF`; no shell is used.
Relative artifact paths must stay inside the bundle, and symlinks fail closed.

## Development packet

**Atomic questions.** Can normalization be recomputed without producer code?
Can interval coverage be established from first principles? Can every emitted
UNSAT proof be bound to one CNF and replayed by a separately pinned executable?

**Bounded saturation assessment.** The implementation is saturated only over
the explicit CR-B contract above: finite `F5^3` column sequences, half-open
ordinal ranges, SHA-256/byte bindings, and external DRAT/DRUP process replay.
It makes no claim about generator completeness outside the declared domain,
solver correctness for SAT records, novelty, publication readiness, or
external scientific independence.

**Challenge to the basis.** A producer could emit a self-consistent but
noncanonical representative, adjacent-looking partitions with a gap/overlap,
or a receipt for a proof that was missing, altered, reused, or never checked.
The hostile tests exercise each of these failure classes.

**Why a prior search could miss the defect.** Reusing producer helpers would
make shared normalization or partition bugs invisible. Trusting hashes without
running a proof checker would establish custody only, not proof validity.
Scanning only manifest entries would miss extra proof artifacts.

**Reopen triggers.** Reopen the contract rather than silently adapting if a
future bundle uses rank-deficient sequences, a different field/dimension,
nonconsecutive record ordinals, compressed/containerized proofs, another proof
format, or a checker whose success contract is not exit code zero.

The verifier and tests were frozen without opening or consuming an aggregate
result bundle. Aggregate values exposed incidentally in coordination metadata
were not used in the implementation or test fixtures.

## Run

```bash
python verify_crb_bundle_independent.py \
  /path/to/bundle/CRB_BUNDLE.json \
  --checker /path/to/hash-pinned/drat-checker \
  --checker-sha256 TRUSTED_CHECKER_SHA256
```

Success emits a compact JSON report with authority
`internal_conformance_only`. A pass is an internal conformance/replay receipt;
it is not novelty evidence, a D4 discharge, journal authority, or external
independence.
