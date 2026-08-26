# Engine B SAT completeness argument

## Scope

For one declared sequence `S=(g_0,...,g_{n-1})` of at most 31 elements of
`C_5^3` and one `k` in `{1,2,3,4}`, Engine B decides whether `S` contains `k`
pairwise disjoint, nonempty, zero-sum subsequences. The encoding is derived
only from primitive `C_5^3` addition. It has no orbit normalization, candidate
filter, learned pruning rule, or imported NQ transition table.

This argument proves completeness of the predicate encoding for each bound
input record. It does not prove that an external input stream is a complete
normalized census. That separate obligation is bound by an input-coverage
declaration and still requires a proof auditor.

## Variables

`x[i,b]` says that occurrence `i` is assigned to factor bin `b`. Pairwise
clauses allow an occurrence in at most one bin. A long clause requires every
bin to be nonempty. Unassigned occurrences are allowed.

For every bin, coordinate, prefix, and residue, `q[b,c,i,r]` says that the sum
of coordinate `c` among selected occurrences before prefix `i` is `r mod 5`.
Every prefix has exactly one state. The initial state is zero. Two transition
implications select either the unchanged residue or the residue obtained from
primitive `C_5^3` addition. The final state is constrained to zero.

## Soundness

Given any satisfying assignment, take the indices with true `x[i,b]` for each
bin. At-most-one clauses make the bins pairwise disjoint and the nonempty
clauses make every bin nonempty. Exact-one prefix states and transition clauses
inductively force each state to equal the actual componentwise prefix sum.
The final zero units therefore prove that every selected bin is zero-sum.

The emitted SAT certificate lists these occurrence indices. Its verifier
ignores SAT state variables and recomputes disjointness and all three sums from
primitive addition.

## Completeness

Given `k` pairwise disjoint nonempty zero-sum subsequences, set `x[i,b]` exactly
for their occurrence indices and leave every other occurrence unused. Assign
each `q` variable to the unique residue obtained by folding the selected
prefix with primitive addition. The bins satisfy at-most-one and nonempty
clauses. Every transition is satisfied by construction, and every final state
is zero because each factor is zero-sum. Thus every valid factorization maps to
a SAT model.

Together, Soundness and Completeness give an exact equivalence with no pruning
and no symmetry-breaking assumption that could remove a valid model.

## UNSAT certificates

The execution adapter requests a DRUP trace from the SAT solver and writes the
exact deterministic DIMACS CNF checked by that trace. UNSAT certificate V2
binds the CNF bytes, CNF semantic digest, proof bytes, sequence digest, subject
commit, and solver identity. Its verifier reconstructs the Engine-B CNF and
requires byte equality with the bound DIMACS file. An UNSAT result remains
`UNSAT_PROOF_EMITTED_REQUIRES_EXTERNAL_CHECK` until a separate proof checker
validates the trace. Merely hashing the trace is not a logical proof check.

## External DRUP engineering control

`EXTERNAL_DRUP_CHECKER_PROTOCOL.json` pins the external `drat-trim` source
commit and tree, license, build command, binary location, invocation, timeout,
and success marker. The fail-closed runner rejects a dirty tracked source tree,
wrong commit or tree, non-executable or out-of-tree binary, nonzero exit, or
missing exact `s VERIFIED` line. Its receipt binds the protocol, source and
binary identities, input record, V2 certificate, CNF, proof, stdout, and
stderr.

The materialized negative control checks exactly one small UNSAT fixture. It
does not execute either full census, audit normalization or partitions, check
all full-bundle UNSAT proofs, establish independent replay authority, or change
paper authority. Those fields remain `CANNOT_CHECK`/`NONE`, and
`D_4(C_5^3)` remains OPEN.

## Census and theorem boundary

The input-coverage declaration binds the generator, normalization identity,
record count, and a digest of its mathematical coverage argument. Engine B
checks those bindings but cannot manufacture a missing orbit-completeness
proof. Partial streams and resource exhaustion are `CANNOT_CHECK`, not
scientific negatives.

This predicate does not close `D_4(C_5^3)`, and neither does any partial stratum. That constant
remains OPEN unless every mathematical stratum is actually closed and the
whole reduction receives ordinary proof audit.
