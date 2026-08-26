# Q1-C1 dual-harness proof and article challenge protocol

Protocol identifier: `Q1-C1`

Protocol version: `1.0`

`EXECUTION_STATUS=NOT_STARTED`

Freeze date: 2026-08-22

Candidate ref: `158fcb08b612ffc82f5a5d2bed4917409084ded8`

This protocol is a prospective challenge of the Q1 theorem and its article
presentation. It does not promote the candidate, rescore an old run, alter a
historical receipt, or grant novelty, physical-resource, performance, merge,
or submission authority.

## Frozen article claim

For every integer `n >= 1` and every instance in the exactly defined
three-block shared-Tag grammar under the exactly defined raw-support objective,
there exists a minimum-cost feasible configuration in which every frame Pauli
has support at most two. The support-one restriction is not sufficient: an
independently verified exact instance has unrestricted cost 5 and support-one
cost 6.

The theorem is not about all Tag-and-Restore Encoding (TARE) constructions,
all Tag ranks, hardware-aware costs, circuit depth, fault-tolerant cost,
runtime, or quantum advantage.

## Terminology and notation freeze

| Canonical term | Meaning | Forbidden drift |
|---|---|---|
| TARE | Tag-and-Restore Encoding | no internal programme name in the article title or theorem |
| auxiliary frame Pauli `R_jk` | branch `k` auxiliary frame in block `j` | never shorten the headline, theorem, or figure-caption term in a way that could be confused with target-string localization |
| partner `R_j,1-k` | the other frame in the same block | no cross-block partner constraint |
| shared Tag `S` | one Pauli imposing the common branch labels | not a general multi-Tag construction |
| target `P_j,pi_j(k)` | target Pauli assigned to branch `k` | target order must state the relative permutation |
| transformed letter `T_jk` | `P_j,pi_j(k) R_jk` modulo phase | not a physical gate-count quantity |
| unrestricted optimum `C_DP` | minimum over the frozen full grammar | not a universal TARE optimum |
| support-two optimum `C_2` | minimum over the same grammar with every `w(R_jk) <= 2` | article notation; implementation name `D++` is supplementary only |
| support-one optimum `C_1` | minimum with every `w(R_jk) <= 1` and otherwise identical freedom | implementation names `D` and `D+` must be distinguished |
| `F_3` | declared per-qubit three-string Restore-factor cost | no unstated donor or hardware cost interpretation |

## Frozen mathematical object

Local Pauli letters are `I,X,Y,Z` modulo phase. Multiplication is bitwise Pauli
multiplication modulo phase, local support is zero for `I` and one otherwise,
and the local symplectic form is the standard binary Pauli form.

For `j in {A,B,C}` and `k in {0,1}`, the six frame Paulis are nonzero and
satisfy only

```text
symp(R_j0,R_j1)=1.
```

There are no cross-block frame constraints. Common labels `l0 != l1` and a
single Tag `S` satisfy

```text
symp(S,R_j0)=l0,
symp(S,R_j1)=l1
```

for all three blocks. For fixed relative target permutations and central bits,

```text
T_jk = P_j,pi_j(k) R_jk,

F_3(a,b,c) = 1                       if a=b=c!=I,
               w(a)+w(b)+w(c)       otherwise,

C = sum_j [4 w(R_j,nc) + 2 w(R_j,c)] - 18 + 2 w(S)
    + sum_{k in {0,1}} sum_q F_3(T_Ak[q],T_Bk[q],T_Ck[q]).
```

The baseline `-18`, central/non-central coefficients, Tag coefficient, branch
assignment, and `F_3` rule are load-bearing. No implementation is allowed to
change them silently.

## Immutable input corpus

The challenge extracts the candidate ref with `git archive`; it never executes
inside another lane's mutable worktree. SHA-256 digests are:

| SHA-256 | Fixed-ref path |
|---|---|
| `6fad2d4f8f97b0a1b76428bff4fdd83dda18f9e3a49cdab7732391d4bcf3d41d` | `research/extensions/orion-q/max_r6s_all_n_composition.py` |
| `b6d72913c3bd42d9c822eace19563378c046e620d7b9641ec7d818fbcc6b9875` | `research/extensions/orion-q/MAX_R6S_ALL_N_COMPOSITION_RESULTS.json` |
| `1006ab0293727ebb994b1202118bc60e779eb5432f820222c6ffbf22304d5965` | `research/extensions/orion-q/max_r6p_weight2_frame_donor_closure.py` |
| `3eef07d16353b606a133d7fb977d5039ad1c639c7a531a47ae82be4be9051190` | `research/extensions/orion-q/MAX_R6P_WEIGHT2_FRAME_DONOR_CLOSURE_RESULTS.json` |
| `7c6579db5f4afbc1738e8b3d96aa3730023bc3831d1fc4950ab34e071c0e3d90` | `research/extensions/orion-q/max_r6m_exact_three_tare2_shared_factor_dp.py` |
| `37cfd64201312e4c7e670e2beefede0961c7dd6a4cd1e3bb2f1fb74afbdf8c17` | `research/extensions/orion-q/max_r6o_enlarged_tag_donor_closure.py` |
| `e40e7a948061b9e4b647ba091c04a73b39cffa619ca829bbf4cef4beacdad352` | `research/extensions/orion-q/MAX_R6O_ENLARGED_TAG_DONOR_RESULTS.json` |
| `bb8a9d32176c5e13c4ce270b1f83a091b57ed6e00fe55e851bc6dee10027c602` | `development/orion-q-max-r0/MAX_R6S_ALL_N_COMPOSITION_PROTOCOL.md` |
| `b44c8b39363cdde2604c5cba7e8998bc34621623639a78007e78a856659ed171` | `papers/archive/2026-08-pre-unification/Q-paper-01-tare-expressivity/MANUSCRIPT_V3.md` |
| `3e9494a68ded5b482d17fc0738c9b4bbd54df389a29de95bfec341e17b6b5ed1` | `papers/orion-05-tare-expressivity/PROOF_AND_EVIDENCE_MAP_V2.md` |
| `94e07f841b58a0274c2503d89b011b117636f2e534c2439bd9f00a6aebd368f3` | `papers/orion-05-tare-expressivity/CLAIM_LEDGER_V2.md` |
| `bfe497e0c16cde06431799a5a7f1e260757c9744402f40b16c2cff76643dcec7` | `packages/orion-research-harness/pyproject.toml` |
| `62c5d787f3b411f54def8ec61584a8ec3a182003c0fbc013e1e396f37735a465` | `uv.lock` |

An input mismatch is `INVALID`, not a theorem failure and not permission to use
a convenient replacement.

The only serialized sharpness corpus Lane B may read is
`MAX_R6P_WEIGHT2_FRAME_DONOR_CLOSURE_RESULTS.json` at the digest above. It must
read exactly JSON Pointer `/domains/random_panel/critical_witness_samples/8`,
whose canonical-JSON SHA-256 is
`ed22ef40e960361cb2cc7ee3987284e15ba9334d4197b33d4d8eff3fa9e09d8e` and
whose selector fields are `n=2`, `index=23`, targets
`[[3,1],[1,0],[2,0],[3,3],[2,0],[2,2]]`, `C_unrestricted_dp=5`, and
`C_Dplus=6`. It copies only that object into a new canonical fixture and then
recomputes the result without importing or reading donor code or donor stdout.
Any second match, pointer/digest mismatch, or undeclared result read is
`INVALID`.

## Frozen implementation and chronology contract

Post-protocol files have these exact paths:

| Purpose | Required path |
|---|---|
| dual-lane coordinator | `development/q1-q4-publication-closure-2026-08-22/q1-cycle-01/harness/run_q1_c1_dual_harness.py` |
| Lane A wrapper | `development/q1-q4-publication-closure-2026-08-22/q1-cycle-01/harness/lane_a_r6s_replay.py` |
| Lane A production adapter | `development/q1-q4-publication-closure-2026-08-22/q1-cycle-01/harness/lane_a_author_stack_adapter.py` |
| Lane A campaign | `development/q1-q4-publication-closure-2026-08-22/q1-cycle-01/harness/lane_a_campaign.json` |
| Lane B verifier | `development/q1-q4-publication-closure-2026-08-22/q1-cycle-01/harness/lane_b_independent_challenge.py` |
| Lane B campaign | `development/q1-q4-publication-closure-2026-08-22/q1-cycle-01/harness/lane_b_campaign.json` |
| frozen small-domain fixtures | `development/q1-q4-publication-closure-2026-08-22/q1-cycle-01/harness/fixtures/q1_c1_small_domains.json` |
| mutation registry | `development/q1-q4-publication-closure-2026-08-22/q1-cycle-01/harness/q1_c1_mutations.json` |
| arbitrary-support proof certificate | `development/q1-q4-publication-closure-2026-08-22/q1-cycle-01/harness/proofs/q1_c1_zero_sum.proof.json` |
| proof-certificate schema | `development/q1-q4-publication-closure-2026-08-22/q1-cycle-01/harness/q1_c1_proof_certificate.schema.json` |
| TeX mutation registry | `development/q1-q4-publication-closure-2026-08-22/q1-cycle-01/harness/q1_c1_tex_mutations.json` |
| typed result schema | `development/q1-q4-publication-closure-2026-08-22/q1-cycle-01/harness/q1_c1_result.schema.json` |
| immutable terminals | `development/q1-q4-publication-closure-2026-08-22/q1-cycle-01/results/lane_a/` and `development/q1-q4-publication-closure-2026-08-22/q1-cycle-01/results/lane_b/` |

Every campaign, result, and TeX manifest records `protocol_commit`, its own
`artifact_commit`, and `artifact_commit_parent`; source/fixture commit fields
are read from Git rather than embedded self-referentially in their own bytes.
Each `artifact_commit_parent` must contain the protocol commit as a strict
ancestor. The small-domain fixture, mutation registry, proof certificate,
proof-certificate schema, TeX-mutation registry, and typed-result-schema
commits must all be immutable strict ancestors of both lane runners, both
campaigns, the checker/coordinator, and every result that consumes them.
Their exact artifact digests are copied into each consuming campaign and
result, including a mandatory `result_schema_digest`. A result commit must likewise descend strictly from its runner and
campaign commits. Each invocation records
`worktree_dirty=false`; a dirty worktree or missing parent field is `INVALID`.

Lane A uses the absolute interpreter
`/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python`,
Python `3.12.13`, and NumPy `2.3.5`. Its `PYTHON` capability request is only a
bootstrap: it executes the frozen wrapper with `-I` under a cleared environment
whose allowlist is `PATH`, `LANG=C.UTF-8`, `LC_ALL=C.UTF-8`,
`PYTHONHASHSEED=0`, and `TZ=UTC`. Extraction and output paths are passed only
as positional `argv` values named `ARCHIVE_ROOT`, `STDOUT_PATH`,
`STDERR_PATH`, and `RESULT_PATH`; they are not environment variables. The
wrapper changes to the immutable archive root, redirects complete stdout and
stderr to files, and returns only their hashes, byte counts, exit status, and
the frozen semantic projection. Timeout is 120 seconds. Capability output
truncation is forbidden; the out-of-band files are authoritative.

The wrapper installs a socket-denying Python audit hook before `runpy` and is
run under an OS network-syscall trace. A negative control must fail an attempted
`AF_INET` socket, and the scientific execution trace must contain no network
syscall. Namespace isolation, if unavailable, must be reported truthfully; it
must never be recorded as sandboxed. Lane B is separately model-free and
network-free and must satisfy the same negative control. The wrapper source,
bootstrap string, trace command, interpreter, environment allowlist, timeout,
and stdout/stderr capture logic are immutable campaign fields and are hashed
before execution.

The archive's `uv.lock` remains an input binding, but it is not silently
declared reproduced by an environment with different installed packages.
Before a release PASS, `uv --frozen --offline` must close against a hashed
wheelhouse/container matching the lock. The currently observed absence of the
locked `cryptography==50.0.0` distribution is `BLOCKED` until that dependency
closure is supplied; a run with `cryptography==46.0.0` is diagnostic only.

## Dual-harness separation

### Lane A: generic receipt-replay lane

Lane A initializes a fresh `ResearchWorkspace` with the immutable archive as
project root and process tools explicitly enabled. A local `PYTHON` capability
executes the fixed R6S program, with stdout, stderr, exit code, request, result,
environment, source hashes, and regenerated result hash retained. Lane A must
recover the exact scientific fields. The frozen semantic projection is the
canonical JSON result after removing exactly the JSON Pointer
`/runtime_seconds`. There are no wildcard or pattern removals. Wrapper timing,
absolute paths, and capture metadata live outside the scientific-result object
and are never projected from it. No theorem terminal, count, Boolean, witness,
seed, panel size, failure row, equality row, or source digest may be ignored.
The comparator emits a JSON Pointer diff for every mismatch.

Lane A is corroborative routing/replay evidence only. It may not grant proof
authority merely because the historical program emits
`THEOREM_MACHINE_CHECKED`.

Lane A also runs the content-addressed author-stack adapter against exactly the
same frozen `n=1` and `n=2` fixtures consumed by Lane B. The adapter may import
the fixed-ref R6M and R6P modules and records production `C_DP`, `C_2`, and
`C_1` outputs plus witness/cost fields in a separate immutable terminal. It may
not read Lane B output. After both lane terminals are immutable, the
coordinator performs an exact fieldwise comparison of adapter outputs with
Lane B's independent outputs. A mathematical-output mismatch is a
`COUNTEREXAMPLE` to the claimed implementation equivalence; adapter custody,
schema, or input mismatch is `INVALID`. Q1-C1 PASS requires this post-terminal
comparison in addition to R6S receipt replay.

This adapter comparison establishes production R6M/R6P agreement only on the
frozen adapter fixture corpus (`n=1` and the 65 declared `n=2` rows). It does
not establish arbitrary-`n` production implementation equivalence. The
arbitrary-`n` authority in Q1-C1 comes from the written mathematical theorem
and Lane B's typed algorithm/proof contract, not from finite code comparison.
A later source-to-spec proof cycle must bind the production DP invariant,
support-two enumeration, transforms, pruning, and surjectivity for arbitrary
`n` before the repository may claim all-`n` production-code equivalence.

### Lane B: native typed independent-challenge lane

Lane B uses a separate workspace and a frozen native campaign manifest. It is
model-free and network-free. Its verifier must not import, execute, paste, or
read R6S, R6M, or R6O output, or any R6P output other than the single declared,
digested `MAX_R6P_WEIGHT2_FRAME_DONOR_CLOSURE_RESULTS.json` sharpness corpus.
It may read the fixed protocol, manuscript, and that serialized witness corpus
only through declared paths. Its import allowlist is Python standard library only. Its open/read
allowlist is the protocol, manuscript/ledger/map, the single declared R6P JSON
fixture, its own campaign/fixtures/mutation registry/schema, the frozen proof
certificate and proof-certificate schema, and its output directory. An audit
hook serializes every import and file open; an undeclared
read/import is `INVALID`. It independently implements the local Pauli algebra,
feasibility bits, objective, enumerators, proof-contract checks, and mutation
controls.

Lane B runs without access to Lane A's workspace or outputs. Its typed outcome
space is `PASS`, `COUNTEREXAMPLE`, `INVALID`, or `BLOCKED`. Free-text reasoning
is not an input to its decision.

### Comparison

The lanes are compared only after both terminals are immutable. Agreement is
recorded, but agreement cannot repair a shared omission. Lane B controls the
mathematical terminal because it is the independent challenge. A valid Lane B
counterexample remains `COUNTEREXAMPLE` even when Lane A says PASS. An input,
schema, custody, separation, or semantic-comparator mismatch is `INVALID`.
Other scientific disagreement produces coordinator terminal `BLOCKED` with a
required typed `disagreement` record containing both immutable terminals and a
field-level diff. `DISAGREEMENT` is not a fifth lane or coordinator terminal
and is never misclassified as a custody failure.

## Sixteen proof and implementation obligations

Each obligation has an independently serialized boolean, evidence pointer, and
negative-control result.

1. **Domain and existence.** State `n` as an integer with `n >= 1`; construct a
   feasible configuration for every such `n`; establish that the feasible set
   is finite and nonempty.
2. **Pauli algebra.** Exhaustively bind independent multiplication, support,
   and symplectic truth tables to the article definitions.
3. **Feasibility bits.** Independently derive the nine acceptance bits and
   prove their accepting states are equivalent to three within-block
   anticommutation bits, four cross-block label-equality bits, two label-value
   bits, and the accepting-state requirement `l0 != l1`. The four equality
   bits and two value bits jointly encode the six common-label equations; they
   are not six additional state bits.
4. **Objective binding.** Bind every coefficient, the `-18` baseline, both
   branches, target permutations, central choices, Tag support, and `F_3` to
   the written objective for every local letter tuple.
5. **Exchange locality.** Show that zeroing `Q` changes only the selected frame
   support and the selected branch's `F_3` terms; Tag, partner, other blocks,
   other branch, other qubits, labels, matching, permutations, and centrals are
   unchanged.
6. **Arbitrary-support subset lemma.** Carry a written, arbitrary-`w`
   certificate: a `(0,0)` singleton or equal-class pair exists for every
   odd-alpha multiset of size at least three. Finite enumeration is
   corroboration only. Lane B parses a typed proof certificate with premises,
   exhaustive class partition, contradiction branch, subset constructor, and
   properness conclusion; it checks each inference rule against an explicit
   finite `F_2^2` semantics. Free prose or a larger finite cutoff cannot set
   this obligation true.

   The certificate at the frozen path validates against the frozen schema, has
   SHA-256
   `5cf8462e1ea00a39b9d3992d7183cea3a0e248a5a45e3de8d5b80628ae6dc351`
   and size 1,310 bytes, and is a mandatory Lane B campaign/result digest. It
   may use only inference IDs `P1_F2_SQUARED_DOMAIN`, `P2_ODD_ALPHA_TOTAL`,
   `R1_ZERO_CLASS_SINGLETON`, `R2_REPEATED_CLASS_PAIR`,
   `R3_DISTINCT_NONZERO_EXHAUSTION`, `R4_NONZERO_TRIPLE_ALPHA_EVEN`,
   `R5_ODD_ALPHA_CONTRADICTION`, `R6_NONEMPTY_PROPER_BOUND`, and
   `R7_ZERO_SUM_SUBSET_CONCLUSION`. The checker evaluates these rules directly
   over the four elements of `F_2^2`; undeclared axioms or inference IDs are
   `INVALID`. Mutant `M23_PROOF_CERTIFICATE_RULE` deletes or reverses one used
   rule application and must be rejected by this schema/semantics checker.
7. **Proper-subset feasibility.** Prove `Q` is nonempty and proper, the modified
   frame remains nonzero, partner anticommutation stays one, and the common Tag
   label is preserved without Tag repair.
8. **Local cost lemma.** Independently enumerate the complete 18,432-case
   domain; require zero positive deltas and bind the equality cases to
   multiplier two.
9. **Well-founded descent.** Prove that a lexicographic minimum of
   `(C,total frame support)` exists and that each exchange strictly reduces it
   without increasing `C`, yielding finite termination at support at most two.
10. **Unrestricted DP equivalence.** Independently verify that the XOR-DP state,
   transition, acceptance, baseline, and minimization cover exactly the full
   mathematical grammar, with no dropped or added feasible configuration.
11. **Support-two surjectivity.** Verify that every mathematical support-two
    configuration maps to an enumerated support-two tuple and every enumerated
    tuple is feasible in the mathematical grammar.
12. **Support-two optimizer soundness.** Verify minimum-Tag relaxation,
   pattern transform, central reduction, tie handling, and pruning lower bound;
   compare direct enumeration and the independent DP on the frozen domains:
   all `4^6=4096` one-qubit ordered target-letter tuples (`n=1`), and exactly
   the sharpness row plus 64 adversarial/seeded two-qubit target six-tuples
   generated by Python standard-library `random.Random(20260822)` and, for
   each of 64 rows in order, six consecutive Pauli strings
   `tuple(rng.randrange(4) for _ in range(2))` (`n=2`). The generator records
   Python `3.12.13`, the algorithm above, row order, and canonical fixture
   digest; no NumPy or implementation donor RNG is allowed. No exhaustive claim is made for
   `n>=2`; `n=3,4` checks are invariant/property tests only.

   The exact UTF-8 generator body (final LF included) is
   `rng=random.Random(20260822)\nrows=[[[rng.randrange(4) for _ in range(2)] for _ in range(6)] for _ in range(64)]\n`,
   with SHA-256
   `ef026dd09819d602746a3dec95410bc8f33ae9e6574a4abc15efc9717df3d88c`
   and size 111 bytes. The serialized 65-row fixture is committed and hashed
   before either runner or campaign is committed.
13. **Support-one equivalence.** Bind the article's `C_1` to the complete
   support-one family with arbitrary anchors and minimum feasible shared Tag;
   prove that every nonzero anticommuting support-one pair shares an anchor and
   uses two distinct nonidentity letters. This establishes `C_1` equals the
   arbitrary-anchor implementation family `D+`; the common-anchor family `D`
   is a distinct strict subfamily and is never substituted.
14. **Sharpness witness.** Independently recompute a serialized exact
    `C_DP=5 < 6=C_1` witness, exhaustively cover all support-one competitors,
    and verify every feasibility and cost term.
15. **Custody and replay.** Bind ref, protocol ancestry, all inputs, environment,
    commands, outputs, certificates, and hashes; require repeat-run semantic
    identity and explicitly classify runtime/last-bit non-scientific fields.
16. **Mutation adequacy.** Each acceptance bit, distinct-label test, nonzero
    condition, central multiplier, frame/Tag coefficient, baseline, `F_3`
    special case, branch assignment, target permutation, minimum-Tag rule,
   pattern transform, pruning bound, and support ceiling receives a seeded
   single-fault mutant. Every mutant must cause `COUNTEREXAMPLE` or `INVALID`;
   a surviving mutant blocks PASS.

The frozen mutation registry uses IDs `M01_B0` through `M09_B8` for the nine
acceptance bits, `M10_LABEL_DISTINCT`, `M11_FRAME_NONZERO`,
`M12_CENTRAL_MULTIPLIER`, `M13_FRAME_COEFFICIENT`, `M14_TAG_COEFFICIENT`,
`M15_BASELINE`, `M16_F3_SPECIAL`, `M17_BRANCH_ASSIGNMENT`,
`M18_TARGET_PERMUTATION`, `M19_MIN_TAG`, `M20_PATTERN_TRANSFORM`,
`M21_PRUNING_BOUND`, `M22_SUPPORT_CEILING`, and
`M23_PROOF_CERTIFICATE_RULE`. The registry records seed, exact edit/operator,
target obligation, expected fixture, and expected terminal. Before kill-rate
calculation, each mutant must be proved non-equivalent by a prespecified
distinguishing fixture; an equivalent mutant is `INVALID`, never a kill.

Every lane result validates against the typed schema and contains at least:
`schema_version`, `protocol_id`, `protocol_version`, `candidate_ref`,
`protocol_commit`, `artifact_commit`, `artifact_commit_parent`, `lane`,
`campaign_digest`, `runner_digest`, `result_schema_digest`, `fixture_digests`, `input_digests`,
`interpreter`, `dependency_inventory_digest`, `cwd`, `environment_allowlist`,
`network_control`, `command`, `started_at`, `finished_at`, `exit_code`,
`stdout_path`, `stdout_sha256`, `stdout_bytes`, `stderr_path`,
`stderr_sha256`, `stderr_bytes`, `output_truncated=false`,
`worktree_dirty=false`, sixteen typed obligation records, mutation records,
semantic projection/diff, and terminal. A missing field is `INVALID`.

## Prespecified outcomes

- `PASS`: both lanes complete; Lane A scientific fields recover; Lane B passes
  all sixteen obligations and all mutations are killed. This supports only the
  exact mathematical theorem, Lane B's mathematical algorithm binding, and
  production implementation agreement on the explicitly finite adapter
  corpus. It grants no arbitrary-`n` production-code-equivalence claim.
- `COUNTEREXAMPLE`: an independently checked mathematical obligation is false
  or a valid configuration violates the theorem/sharpness statement. Preserve
  the case verbatim and reopen the theorem.
- `INVALID`: input, chronology, lane separation, implementation binding,
  mutation adequacy, result contract, or custody fails. No mathematical outcome
  is inferred.
- `BLOCKED`: declared resource limits prevent completion. Partial checks are
  retained but grant no closure. `BLOCKED` also covers unresolved scientific
  disagreement between two otherwise valid immutable lane terminals and must
  then include the typed `disagreement` record required above.

No outcome authorizes novelty or top-tier readiness. Those require the separate
primary-literature and article-review gates.

## Article and PDF gates

The rebuilt article must be independent of repository programme names and use
one TeX file per chapter. The main article, not only a development protocol,
must contain the definitions, arbitrary-`w` lemma proof, feasibility exchange,
local-cost certificate, descent theorem, support-two equivalence, and sharpness
witness. Supplementary files may contain exhaustive tables and receipts but may
not carry a missing logical step.

The build freezes document class/style, bibliography backend, TeX engine, and
dependency versions. Release requires:

1. clean chaptered source and bibliography;
2. zero placeholders, undefined references/citations, or missing glyphs;
3. successful clean build from a fresh archive;
4. rendered-page inspection of every page;
5. source/PDF claim and notation consistency audit;
6. artifact manifest with source, bibliography, log, PDF, and page-render
   hashes;
7. reference metadata verification and a fresh strongest-donor search;
8. three independent reviewer-emphasis reports with no unresolved P0.

The TeX mutation suite must also kill `T01_UNDEFINED_TIGHTLIST`,
`T02_UNSUPPORTED_UNICODE_MATH`, `T03_UNDEFINED_REFERENCE`, and
`T04_UNDEFINED_CITATION`. The current Pandoc-derived `\tightlist` failure and
raw Unicode-math failure are retained fixtures, not silently edited logs.

The clean TeX gate fixture paths are
`development/q1-q4-publication-closure-2026-08-22/q1-cycle-01/harness/fixtures/tex/base.tex` (SHA-256
`b70a93bf653d147dcf911ec4e44bdc985437e49f6e43326000685571e8b8e402`;
262 bytes) and
`development/q1-q4-publication-closure-2026-08-22/q1-cycle-01/harness/fixtures/tex/fixture.bib` (SHA-256
`f7685a5ef4c402af0757f020ea0a2ce345ce2587279d3e837ccd40d8a5604515`;
142 bytes). Their exact UTF-8 contents are:

```tex
\documentclass{article}
\usepackage[utf8]{inputenc}
\newcommand{\tightlist}{}
\begin{document}
\tightlist
\section{Gate fixture}\label{sec:gate}
See Section~\ref{sec:gate}. Citation~\cite{fixture}.
\bibliographystyle{plain}
\bibliography{fixture}
\end{document}
```

```bibtex
@article{fixture,
  author = {Ada Example},
  title = {A Reproducibility Fixture},
  journal = {Journal of Test Artifacts},
  year = {2026}
}
```

Each block ends with one LF. The TeX registry freezes these exact operations:

| ID | Exact mutation | Required diagnostic and terminal |
|---|---|---|
| `T01_UNDEFINED_TIGHTLIST` | delete the complete line `\newcommand{\tightlist}{}` | log contains `Undefined control sequence` at `\tightlist`; build gate `BLOCKED` |
| `T02_UNSUPPORTED_UNICODE_MATH` | replace the first literal `Gate fixture` with `Gate fixture ⟶` | log contains `Unicode character ⟶ (U+27F6)` and `not set up for use with LaTeX`; build gate `BLOCKED` |
| `T03_UNDEFINED_REFERENCE` | replace only `\ref{sec:gate}` with `\ref{q1_missing_ref_mutant}` | log contains an undefined-reference warning naming `q1_missing_ref_mutant`; build gate `BLOCKED` |
| `T04_UNDEFINED_CITATION` | replace only `\cite{fixture}` with `\cite{q1_missing_citation_mutant}` | log contains an undefined-citation warning naming `q1_missing_citation_mutant`; build gate `BLOCKED` |

The registry stores the two fixture digests, engine/version, exact edit,
expected regex, exit-code policy, and expected terminal for every TeX mutant.

## Recursive release rule

This protocol commit must be a strict ancestor of the Lane A runner/output,
Lane B verifier/manifest/output, TeX article, and all result-bearing commits.
Protocol and result first appearing in one commit is invalid.

Any failed obligation becomes a versioned child cycle with the predecessor and
negative result preserved. A replacement method must beat the same frozen gate
or explicitly narrow the article claim. No negative, null, donor tie, or
contamination event may be deleted to manufacture a positive portfolio.
