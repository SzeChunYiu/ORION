# Codex / LUNARC Execution Packet R8

Date: 2026-08-26  
Repository: `SzeChunYiu/ORION`  
Working branch: `codex/five-paper-top-tier-r8-20260826`  
Frozen scientific base: `99049ff6dfbdd78590bbdae0d24b9037aae83e3c`  
Coordination thread: `codex://threads/01a03963-d804-7320-b10a-2b828119df93`

This packet delegates computation and review work. It grants no theorem, novelty, production, or journal authority. Every job must preserve negative, timeout, malformed-output, and `CANNOT_CHECK_RESOURCE_BOUND` outcomes.

## Global custody rules

1. Work only on `codex/five-paper-top-tier-r8-20260826` or a child branch created from the exact R8 packet commit recorded in `R8_PACKET_COMMIT.json`.
2. Do not modify PR #1365, `codex/orion-postmerge-clipping-repair-20260826`, the protected Task-3 branch, or Task-3 files.
3. Record `git rev-parse HEAD`, `git status --porcelain=v1`, compiler/interpreter versions, module list, CPU model, memory, SLURM job id, command line, exit status, wall time, maximum RSS, stdout/stderr SHA-256, and every result-file SHA-256.
4. A solver `UNSAT` is not accepted without either a checkable proof/certificate or a structurally independent complete replay.
5. A survivor is not accepted until independently replayed from primitive group/logic semantics.
6. Never reuse an earlier result file as an input to the implementation under test. Frozen witnesses and problem definitions may be read; prior verdicts may only be compared after the new result is sealed.
7. Commit source, scripts, logs, manifests, and machine-readable receipts. Do not commit large transient search state.

---

## JOB-NQ-R8-1 — clean-room replay of the exact early `C_5^3` constants

### Objective

Independently reproduce the declared finite claims:

- `s_{<=6}(C_5^3)=24`, `s_{<=7}(C_5^3)=19`, and the registered spectrum through length 12;
- `D_2(C_5^3)=20`;
- the complete normalized length-19 no-two-disjoint witness count `98,622` under the declared normalization;
- `D_3(C_5^3)=25`;
- the length-25 structured extension census of `230,983` candidates and zero survivors with no three disjoint zero sums.

### Frozen semantic inputs

Read only the mathematical definitions, explicit lower witnesses, and normalization statement from:

- `development/orion-rg-davenport/X1F_D3_C5CUBED_PROTOCOL_V1.md`;
- `research/orion-rg/X1F0_D2_C5CUBED_EXACT_RESULTS.json`;
- `research/orion-rg/X1F_D3_C5CUBED_EXACT_RESULTS.json`;
- `papers/five-paper-top-tier-r8/NQ/NQ_INDEPENDENT_REPLAY_PROTOCOL_R8.md`.

Do not copy the algorithms in `x1f0_*` or `x1f_*` into the clean-room engine.

### Required independent architecture

Use two implementations:

- **Engine CR-A:** canonical orderly generation plus exact multi-bin subset-sum/factorization DP;
- **Engine CR-B:** independently written SAT/CP-SAT or meet-in-the-middle formulation with a different state representation and different symmetry implementation.

At least one engine must emit a complete canonical manifest for the 98,622 length-19 representatives or a digest-addressed equivalent from which every representative can be replayed.

### LUNARC resource request

Submit CPU-only jobs with no assumed partition name:

```bash
#SBATCH --job-name=orion-nq-r8-cleanroom
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=128G
#SBATCH --time=24:00:00
#SBATCH --output=logs/%x-%j.out
#SBATCH --error=logs/%x-%j.err
```

If the job cannot complete within this allocation, stop at `CANNOT_CHECK_RESOURCE_BOUND`; do not silently increase the scientific search grammar. A successor resource request must state which frozen completeness obligation needs the extra resource.

### Commands

From a clean checkout:

```bash
git fetch origin codex/five-paper-top-tier-r8-20260826
git checkout --detach "$(python papers/five-paper-top-tier-r8/harness/read_packet_commit.py)"
python -m venv .venv-r8-nq
. .venv-r8-nq/bin/activate
python -m pip install --upgrade pip
python -m pip install -r papers/five-paper-top-tier-r8/NQ/cleanroom-requirements.txt
mkdir -p papers/five-paper-top-tier-r8/NQ/cleanroom/{src,results,logs,manifests}
python papers/five-paper-top-tier-r8/NQ/cleanroom/run_cleanroom.py --engine both --threads 32 --output papers/five-paper-top-tier-r8/NQ/cleanroom/results
python papers/five-paper-top-tier-r8/NQ/cleanroom/verify_receipt.py papers/five-paper-top-tier-r8/NQ/cleanroom/results/NQ_D2_D3_CLEANROOM_RECEIPT.json
```

The Codex/LUNARC worker owns implementing the `cleanroom/` directory under this exact contract before execution.

### Required terminal

`NQ_D2_D3_INDEPENDENT_REPLAY_PASS` only when both engines agree on every frozen count and witness verdict. Otherwise use one of:

- `NQ_D2_D3_INDEPENDENT_REPLAY_DISAGREEMENT`;
- `NQ_D2_D3_PRIOR_RESULT_REFUTED`;
- `CANNOT_CHECK_RESOURCE_BOUND`;
- `CANNOT_CHECK_ENVIRONMENT`.

### Authority boundary

A PASS upgrades reproducibility of the finite claims. It does not establish novelty, peer review, or `D_4(C_5^3)`.

---

## JOB-NQ-R8-2 — lift-aware exact solver for the 27-diagonal

### Objective

Decide the complete full-obstruction problem for the first surviving rank-two repeated-stratum orbit on `s+c_4=27`:

`H=e_1^4 e_2^4` plus 23 distinct singleton points in `C_5^3`.

Then, without changing the grammar, process the five registered `4,2,2` orbits. The output must be either a fully replayed source sequence satisfying every obstruction condition or a complete certified exclusion.

### Exact source-level contract

For every candidate `S=HX`, enforce simultaneously:

1. `|S|=31` and `sigma(S)=0`;
2. the 23 singleton points are pairwise distinct and are different from the repeated points;
3. `span(S)=C_5^3`;
4. no nonempty source submultiset of length at most five sums to zero;
5. saturation defect certificates exist for every singleton and double point under the R6 theorem;
6. every quotient atom is lift-realizable by its exact source members;
7. cross-atom and atom/`H` short zero sums are excluded at source level, not only after compression; and
8. the maximum number of pairwise disjoint nonempty source zero sums is at most four.

The weighted compressed relaxation alone is explicitly forbidden because the registered countermodel passes it without a proved source lift.

### Solver design

Use a counterexample-guided exact architecture:

- a canonical SAT/CP-SAT master over the 123 possible singleton points after fixing the repeated plane;
- lazy source-short-sum cuts generated from primitive addition mod 5;
- exact existential saturation-certificate constraints;
- an exact five-bin disjoint-zero-sum adversary; every detected five-factorization adds a sound no-good or structural cut;
- orbit canonicalization under the full stabilizer of the repeated multiset, with a separate verifier proving one representative per orbit.

A second implementation must replay all terminal survivors or independently certify the final canonical UNSAT manifest. Merely running the same clauses through two SAT solvers is not structural independence.

### LUNARC resource request

Initial allocation:

```bash
#SBATCH --job-name=orion-nq-r8-lift27
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=64
#SBATCH --mem=256G
#SBATCH --time=48:00:00
#SBATCH --output=logs/%x-%j.out
#SBATCH --error=logs/%x-%j.err
```

If the master is partitioned, every partition must have an immutable range id and a manifest; the union of ranges must be machine-checked for exact coverage and disjointness.

### Required terminal

- `NQ27_LIFT_AWARE_UNSAT_CERTIFIED`;
- `NQ27_LIFT_AWARE_SURVIVOR_REPLAYED`;
- `NQ27_PARTIAL_STRATUM_COMPRESSED_TO_NEW_INVARIANT`;
- `CANNOT_CHECK_RESOURCE_BOUND`;
- `CANNOT_CHECK_COMPLETENESS`.

No `D_4` conclusion follows unless all remaining length-31 strata are closed under an ordinary proof or a complete independently replayed classification.

---

## JOB-AB-R8-1 — hostile theorem and nearest-work audit

### Objective

Audit every theorem and proof in `AB/MANUSCRIPT_R8_CONSOLIDATED.md`, with special attention to:

- interaction-block additivity and hidden global feasibility;
- the kernel-weighted quotient bound;
- the complete-move realization gate;
- the XOR strong-reduction proof when duplicate fragments arise;
- search-volume leading constants.

Construct the smallest counterexample to every omitted premise. Produce `AB_HOSTILE_REVIEW_R8.md` and a machine-readable theorem disposition ledger.

### Required terminal

`AB_THEOREM_HOSTILE_REVIEW_PASS`, `AB_THEOREM_REPAIRED`, or `AB_THEOREM_REFUTED`.

---

## JOB-AB-R8-2 — external exact-optimizer realization

### Objective

Identify one open, auditable parity/XOR, modular-repair, or exact-synthesis optimizer whose complete legal move inventory can be frozen. Implement:

1. the weak certificate language;
2. the stronger production language;
3. realized weak terminal witnesses;
4. exact production irreducibility/reducibility checks; and
5. measured state-volume or runtime consequences under a declared enumeration architecture.

The toy XOR grammar remains a calibration unless this job establishes a faithful external realization.

### Required terminal

`AB_EXTERNAL_PRODUCTION_CASE_PASS`, `AB_EXTERNAL_CASE_ABSORBED_BY_PRIOR_WORK`, `AB_EXTERNAL_CASE_NO_INCREMENTAL_VALUE`, or `CANNOT_CHECK`.

---

## JOB-C-R8-1 — independent FiberGuard replay

### Objective

Reimplement all three exhaustive panels without importing `fiberguard_r8.py`. Match all instance counts, fibre counts, maximum diameters, endpoint witnesses, and refinement outcomes. Verify each endpoint with a third small checker.

### Resource request

One CPU node, 16 cores, 32 GB, 2 hours.

### Required terminal

`C_FIBERGUARD_INDEPENDENT_REPLAY_PASS`, `C_FIBERGUARD_DISAGREEMENT`, or `CANNOT_CHECK`.

---

## JOB-C-R8-2 — primary-source and scaling audit

### Objective

Compare the exact contribution with radii of information, invariant-representation tradeoffs, Weisfeiler–Leman/GNN expressivity, learned branch-and-bound, SAT representation learning, and benchmark collision testing. Then extend at least one domain by one exact size step or a symmetry-certified sample large enough to test whether the selected refinement continues to close or merely memorizes the finite panel.

### Required terminal

`C_PRIMARY_SOURCE_POSITIONING_PASS_AND_SCALING_SURVIVES`, `C_NOVELTY_NARROWED`, `C_REFINEMENT_FAILS_TO_SCALE`, or `CANNOT_CHECK`.

---

## JOB-D-R8-1 — current provenance/Datalog overlap audit

### Objective

Read the complete primary papers, not only abstracts, including Thapa–Staab on recursive and stratified Datalog, provenance semirings/annotations, and current agent provenance/policy systems. Produce a theorem-by-theorem comparison table. Generic support hypergraphs, hitting sets, deletion robustness, and hardness remain donor-owned.

### Required terminal

`D_PRIMARY_SOURCE_OVERLAP_AUDIT_PASS`, `D_RESIDUAL_NOVELTY_NARROWED`, or `D_DONOR_ABSORBS_HEADLINE`.

---

## JOB-D-R8-2 — real policy case and expert validation packet

### Objective

Select a public rule system with a real distinction between two authority classes, such as prospective versus post-outcome evidence, data-use permission, jurisdiction, or action authorization. Freeze the source documents and domain interpretation before running the typed evaluator. Compare:

- coordinatewise evaluation;
- naive license merge;
- the R8 safe-merge checker;
- the operational decision under each semantics.

The final terminal requires a named domain expert to confirm that the positive-rule encoding and cap semantics match the source policy. Without that review, the terminal remains `INTERNAL_CASE_ONLY`.

### Required terminal

`D_REAL_POLICY_CASE_EXPERT_VALIDATED`, `D_REAL_POLICY_CASE_INTERNAL_ONLY`, `D_MODEL_MISMATCH`, or `CANNOT_CHECK`.
