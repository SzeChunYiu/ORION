# P15 — Scientific Execution Integrity: the ORION research harness

**Stable ID:** ORION-P15
**Paper issue:** none yet — this directory was opened ahead of one.
**Status:** `PROSPECTIVE_ACQUISITION_PROTOCOL_FROZEN / NO_SCIENTIFIC_RESULT`

`P15_ACTIVE_CLAIM_AUTHORITY_V2.json` is the machine-readable active lifecycle
record and `CLAIM_EVIDENCE_LEDGER.md` is its human-readable claim boundary. It
binds the prospectively frozen `P15A_RESEARCH_HARNESS_ACQUISITION_PROTOCOL_V1.md`
and its fail-closed preflight. P15 still has no H1 or protected experiment, so
this state is neither a failed result nor an unchecked scientific claim and
cannot be promoted as a positive empirical finding.
**Status:** `METHODS_SCOPE_ONLY / NO_SCIENTIFIC_RESULT`

`P15_ACTIVE_CLAIM_AUTHORITY_V1.json` is the machine-readable active lifecycle
record and `CLAIM_EVIDENCE_LEDGER.md` is its human-readable claim boundary. P15
has no H1 or protected experiment, so this state is neither a failed result nor
an unchecked scientific claim and cannot be promoted as a positive empirical
finding.
**Stable ID:** ORION-P15  
**Paper issue:** #979  
**Promotion programme:** #977 / `TOP_TIER_PROMOTION_V1.md`  
**Status:** `PAPER_ISSUE_OPEN / NO_PROTECTED_SEI_RESULT`

P15 is the systems paper for the two execution harnesses ORION research runs on and
the guarantees each provides. Its higher scientific object is **Scientific Execution
Integrity (SEI)**: separating what execution receipts can establish about
attribution/replay/agreement from what they cannot establish about scientific
validity or claim authority.

It carries no scientific superiority claim yet and grants no authority.

## Why P15 rather than a new namespace

The P-series already contains non-claim papers: #669 writes P14 (ORION-RSE) as a
methods/evaluation-contract paper, and the merged P10 technical note was evaluation
infrastructure. A systems paper is therefore in-series, not an exception.
`Q-paper-NN-*` stays reserved for the ORION-Q programme's own scientific numbering.

## Scientific separation ladder

The publication target is not generic provenance. P15 must formalize and test the
non-implications

`ATTRIBUTABLE_EXECUTION`
`!= REPLAYABLE_EXECUTION`
`!= AGREEMENT_BETWEEN_EXECUTIONS`
`!= SCIENTIFICALLY_VALID_RESULT`
`!= AUTHORIZED_SCIENTIFIC_CLAIM`.

Some implications may hold under additional premises; those premises must be stated
explicitly rather than smuggled into receipt semantics.

The top two rungs are externally supplied frozen disposition types, donor-owned by
the P6/P8 authorization layer (typing) and the P14 admission layer (decision), with
P13-class responsibility-scoped sufficiency likewise entering only as a frozen
disposition type. Every scientific disposition in P15's receipts is an imported
frozen judgment from its source paper or a deterministic contract — never an
output of the provenance layer, which records dispositions and does not decide
them.

## What it covers

### 1. The ORION research harness

`packages/orion-research-harness/` — a turnkey local harness for tool-integrated
research sessions, landed through #725 and hardened afterwards. Its guarantee surface
is already under adversarial test:

| Concern | Test / gate |
|---|---|
| host/capability failures never enter scientific evidence | `test_governance_hardening.py` |
| bounded file, process and directory output | `test_local_limits.py` |
| strict, non-coercing receipt schemas | `test_hardening.py` |
| race-safe receipt publication | `test_campaign_strictness.py` |
| recovery from invalid content | `test_invalid_content_recovery.py` |
| execution coverage accounting | `test_execution_coverage.py` |
| paper mechanics execute positive + fail-closed semantics | `ORION_HARNESS_P1_P15_OPERATIONAL` |
| verified answer does not self-authorize task stop | `ORION_HARNESS_RESEARCH_DIRECTOR_CONSENSUS_EXTRACTION_V3_OPERATIONAL` |
| unresolved outcomes carry typed resolution obligations | V4 covariance gate |
| verified negative results retain negative polarity and assimilation disposition | V4 covariance gate |

The original load-bearing claim is a separation: **a host or capability failure is
reported without being recorded as a scientific result.** V4 adds two more
separations that are equally important for a research harness:

1. **unresolved is not negative** — `CANNOT_CHECK` means the current contract cannot
   decide the target judgment and normally creates an active
   `ResearchResolutionObligation.v1` with admissible next actions;
2. **negative is not unresolved** — a verified obstruction, donor subsumption,
   falsification, non-identifiability result or bounded impossibility remains a
   `ResearchNegativeResult.v1` and is assimilated into the next research move.

This means the harness should try to resolve uncertainty without pretending that
all scientific questions are decidable, and it should learn from negative results
without relabeling them until they look positive.

### 2. Resolution-first research control

A bare `CANNOT_CHECK` is not an acceptable final harness interface when an admissible
next action exists. The resolution object records the unresolved class, evidence or
capability still required, prior attempts, blockers, and the next permitted actions.
Typical actions include capability repair, evidence acquisition/verification,
independent route expansion, orientation/reframe, responsibility diagnosis,
representation repair, OCME, typed authority checking, or protocol-authorized
resource/protected-evidence widening.

The resolution-first rule is explicitly **not** a promise that every question will
become solvable. Protected evidence can remain unavailable; extension ambiguity or
formal non-identifiability can be real; a frozen resource protocol can block further
work; and the harness cannot mint external authority. Those cases remain typed open
obligations rather than being rounded up to task completion.

### 3. Negative-result assimilation

A verified negative result is a successful research outcome when it eliminates or
sharpens a live hypothesis. The harness must preserve its evidence and assign an
assimilation disposition such as:

- register an obstruction;
- close a hypothesis branch;
- reopen a dependency;
- reframe or widen search;
- register donor subsumption;
- revise a paper claim;
- revise a framework mechanic;
- record a bounded negative terminal.

These dispositions are non-authorizing control metadata. A negative result cannot
self-grant novelty, publication, promotion, merge, or global-stop authority.

### 4. The ORION-Q dual harness

The load-bearing boundary is that **a host or capability failure is reported without
being recorded as a scientific result**. The publication protocol must independently
freeze and test that boundary rather than treating implementation tests as paper
authority.

### 2. The ORION-Q dual harness

`development/orion-q-max-r0/` — a two-lane agreement benchmark with per-lane receipts
(`DUAL_HARNESS_AGREEMENT_BENCHMARK_V0_PROTOCOL.md`, lane A/B receipt sets, and
content-addressed per-problem and per-request receipts).

### 5. What the two share, and where they differ
The object of interest is **agreement between independently executing lanes**, which
is a different property from single-harness determinism and remains weaker than
independently validated correctness.

### 3. Shared and distinct semantics

Both harnesses bind results to content-addressed receipts. P15 must determine which
receipt/integrity semantics genuinely compose across them and which are only similar
implementations.

The top-tier protocol additionally compares/interoperates with generic structured
provenance, W3C PROV/RO-Crate-style workflow provenance, content-addressed execution,
deterministic replay and signed/attested execution systems where feasible. P15's
residual must be the **scientific evidence-admission boundary**, not ownership of
provenance interchange.

## What this paper must not claim

- that a harness makes a scientific result valid — it makes a result *attributable*,
  which is a strictly weaker property;
- that resolution-first control makes every research question decidable;
- that a negative result should or can always be converted into a positive result;
- superiority over any other research-execution harness, absent a matched comparison
  that does not currently exist;
- that receipt coverage implies evidence quality.
- that a harness makes a scientific result valid — attribution is strictly weaker;
- that replayability or dual-lane agreement establishes correctness;
- superiority over another research-execution system absent a matched protected
  comparison;
- that receipt or execution coverage implies evidence quality;
- generic novelty for provenance, workflow reproducibility or proof-of-execution.

A cautionary case already exists in the repository: the P1-U R6 campaign produced
fully receipted rows that were rejected wholesale by a digest-representation type
error. Receipts were complete and the result was scientifically unusable. See
`research/failures/2026-08-digest-representation-boundary-mixup/`.

## Before top-tier submission

Issue #979 now owns the paper identity and scientific question. Remaining scientific
work is explicit rather than administrative:

- [ ] claim/evidence ledger;
- [ ] donor/interoperability matrix;
- [ ] independent publication-specific hostile fault-injection protocol freeze;
- [ ] H15.1–H15.5 executable/formal closure;
- [ ] matched comparator benchmark;
- [ ] independent result adjudication;
- [ ] submission manuscript and reproducibility package;
- [ ] separate content-addressed `P15_TOP_TIER_SUBMISSION_READY` closure receipt.

Per #670's rule — research decomposition is fine-grained, publication synthesis is
coarse-grained — a directory is not an identity. The claim ledger now exists and
records no empirical authority. Promotion still needs a paper issue, a donor
matrix against existing research-execution and workflow-provenance systems, a
protected hostile corpus, a matched comparator or explicitly noncomparative
estimand, and evaluator separation. The protocol now exists; the other inputs
do not. `P15A_ACQUISITION_PREFLIGHT_V1.json` records that boundary without
turning locally authored labels into protected or independent evidence.
matrix against existing research-execution and workflow-provenance systems, and
a prospectively frozen protocol; none of those exists yet.
The planning protocol itself can never emit the final readiness terminal.
