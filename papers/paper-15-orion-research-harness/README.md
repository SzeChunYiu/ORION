# P15 — The ORION research harness

**Stable ID:** ORION-P15
**Paper issue:** none yet — this directory was opened ahead of one.
**Status:** `DIRECTORY_OPENED / NO_PROTECTED_RESULT`

A systems paper introducing the two execution harnesses ORION research runs on, and
the guarantees each provides. It carries no scientific superiority claim and grants
no authority.

## Why P15 rather than a new namespace

The P-series already contains non-claim papers: #669 writes P14 (ORION-RSE) as a
"methods/evaluation-contract paper only", and the merged P10 technical note was
evaluation infrastructure. A systems paper is therefore in-series, not an exception.
`Q-paper-NN-*` stays reserved for the ORION-Q programme's own scientific numbering.

If a programme issue later assigns this subject a different number, that decision
wins; this README is not an authority over numbering.

## What it would cover

### 1. The ORION research harness

`packages/orion-research-harness/` — a turnkey local harness for tool-integrated
research sessions, landed through #725 and hardened afterwards. What makes it a
paper rather than a utility is the guarantee surface, which is already under test:

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

`development/orion-q-max-r0/` — a two-lane agreement benchmark with per-lane
receipts (`DUAL_HARNESS_AGREEMENT_BENCHMARK_V0_PROTOCOL.md`, lane A/B receipt
sets, and content-addressed per-problem and per-request receipts). The object of
interest is **agreement between independently executing lanes**, which is a
different guarantee from single-harness determinism.

### 5. What the two share, and where they differ

Both bind results to content-addressed receipts. Whether they share a receipt
semantics or merely resemble each other is an open question, and answering it
honestly is the paper's most likely real contribution.

## What this paper must not claim

- that a harness makes a scientific result valid — it makes a result *attributable*,
  which is a strictly weaker property;
- that resolution-first control makes every research question decidable;
- that a negative result should or can always be converted into a positive result;
- superiority over any other research-execution harness, absent a matched comparison
  that does not currently exist;
- that receipt coverage implies evidence quality.

A cautionary case sits in this repository already: the P1-U R6 campaign produced
fully receipted rows that were then rejected wholesale by a digest-representation
type error. Receipts were complete and the result was still unusable. See
`research/failures/2026-08-digest-representation-boundary-mixup/`.

## Before this becomes a paper

Per #670's rule — research decomposition is fine-grained, publication synthesis is
coarse-grained — a directory is not an identity. This needs a paper issue, a claim
ledger, a donor matrix against existing research-execution and workflow-provenance
systems, and a protocol freeze, none of which exists yet.
