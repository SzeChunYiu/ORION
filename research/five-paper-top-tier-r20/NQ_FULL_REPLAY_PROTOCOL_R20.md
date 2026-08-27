# NQ R20 — proof-clean full CR-B replay protocol

Status: `PROTOCOL_FROZEN__EXECUTION_OR_COMPLETE_RESULT_REQUIRED`

## Subject

The replay targets the registered complete `C_5^3` matrix/orbit subject and its D2/D3 proof bundle. It must not read any source or receipt whose name or content encodes the claimed numerical outcomes, rooted completion, factorization, invariant-kernel specialization, or `D_3(C_5^3)=25` before its generator, normalizer, solver, proof checker, acceptance rule, and denominators are committed.

## Frozen denominators

- normalized matrix/orbit rows: 98,622;
- registered candidate objects: 230,983;
- every partition bucket, duplicate class, excluded row, and invalid candidate must have an exact count whose sum recovers the denominator;
- the replay must fail on the first missing, duplicate, multiply normalized, or unclassified object.

## Independent implementation

The replay must use a language and data representation structurally distinct from the owning computation. It must independently implement:

1. group arithmetic and sequence normalization;
2. orbit/canonical representative generation;
3. zero-sum atom enumeration;
4. the D2/D3 packing predicate;
5. positive-witness evaluation;
6. clause or proof-object generation;
7. source-pinned external proof checking;
8. denominator and partition reconciliation.

Multiple SAT solvers over one generated clause set are not independent generation.

## Noncircularity

The executable replay may not import, read, or branch on:

- `D2` or `D3` result files;
- `D3_25` constants;
- completion/factorization specializations;
- invariant-kernel consequences;
- generalized-Noether numerical translations;
- acceptance whitelists derived from the claimed terminal.

After the typed replay terminal is fixed, those objects may be checked as consequences.

## Required receipt

The complete result must bind:

- source commit and tree;
- compiler/interpreter and dependency versions;
- exact commands;
- CPU, memory, wall time, scheduler identity and exit status;
- input and output digests;
- all denominator counts;
- every proof-checker command and exit;
- every positive witness;
- first disagreement or typed PASS terminal.

Allowed terminals:

- `NQ_CR_B_FULL_REPLAY_PASS`;
- `NQ_CR_B_FIRST_DISAGREEMENT`;
- `NQ_CR_B_PROOF_CHECK_FAILURE`;
- `NQ_CR_B_DENOMINATOR_MISMATCH`;
- `CANNOT_CHECK_RESOURCE_BOUND`.

## Authority

A same-owner clean-room PASS grants internal numerical corroboration for D2/D3 only. `D4`, novelty, external independence, and journal authority remain open. A small-group control, partial prefix, engineering pilot, or proof checker over owner-generated clauses does not satisfy this protocol.
