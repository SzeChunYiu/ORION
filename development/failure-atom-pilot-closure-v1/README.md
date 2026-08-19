# Failure-atom pilot closure V1 — development packet

Date: 2026-08-19

Issues: #516 / #517 / #518, feeding #507 and #508.  
Stack dependency: #513 (`BoundedEpistemicAtomStudy.v1` and `FailureKnowledge.v1`).  
Authority boundary: this packet freezes research hypotheses and falsifiers only. It does not itself close an issue, establish novelty, or authorize scientific mutation.

## 1. Atomic development questions

### F1 — observability/recognition

Can one domain-general failure-signal atom classify material silent failure from the registered public trajectory alone, or do observationally indistinguishable valid/invalid worlds force decomposition into specialized signal families plus fail-closed routing/materiality?

### F2 — failure to scoped negative knowledge

Given a detected failure and an independently assessed responsibility state, does ORION need a new extraction primitive, or can the registered result be represented by ATMS/TMS/nogood structure plus the responsibility/evidence semantics already owned elsewhere?

### F3 — staleness/reopening

Does scoped negative knowledge need a standalone semantic staleness calculus, or is unchanged-context matching only a conservative fast path while semantic cross-regime applicability is already determined by P7-style complete transport witnesses and fail-closed reopening?

The three questions are deliberately separate. F1 owns observability, F2 owns the scope of a negative conclusion, and F3 owns later applicability of an already warranted negative conclusion.

## 2. Bounded saturation assessment

### Round A — inherited prior work

The preceding #500/#507/#508 research already established the following donor boundaries:

- anomaly/OOD/runtime monitors and domain verifiers are prior structure for failure signals;
- Doyle TMS and de Kleer ATMS own reason/dependency maintenance, assumption environments, contradictions/nogoods, context switching and backtracking;
- CEGIS and related counterexample-guided methods own iterative constraint learning from falsifying examples inside registered search/formal spaces;
- P6 responsibility owns plural/identified/unresolved failure-responsibility state without self-authorizing revision;
- P7 owns representation/chart change, evidence/obligation transport and fail-closed reopening when transport is incomplete or target-ambiguous;
- selective replay/continual learning owns compatibility-sensitive reuse and negative-transfer concerns.

### Round B — adversarial refresh

Primary-source refresh before freezing this packet:

- Fei et al., *How Do Agents Fail on AutoResearch: End-to-End Diagnostic Evaluation on 100 Real-World Frontier Research Tasks*, arXiv:2608.14905 — process-level failure taxonomy over complete autonomous-research trajectories.
- Zhan et al., *Why Your Deep Research Agent Fails? On Hallucination Evaluation in Full Research Trajectory*, arXiv:2601.22984 — process-aware evaluation exposes implicit/intermediate failures hidden by final-outcome scoring.
- Xu et al., *ResearchClawBench: A Benchmark for End-to-End Autonomous Scientific Research*, arXiv:2606.07591 — failures concentrate in protocol/evidence/scientific-core mismatches under expert rubrics.
- Deng et al., *Towards Verifiable and Self-Correcting AI Physicists for Quantum Many-Body Simulations*, arXiv:2604.00149 — reliability is improved by separate programming and scientific/domain verifiers rather than a single semantic failure oracle.
- Doyle, *A truth maintenance system*, Artificial Intelligence 12(3), 1979 — beliefs are maintained with recorded reasons and dependency-directed revision/backtracking.
- de Kleer, *An assumption-based TMS*, Artificial Intelligence 28(2), 1986 — assumption environments support inconsistent alternatives and context switching.
- Jha & Seshia, *Are There Good Mistakes? A Theoretical Analysis of CEGIS*, arXiv:1407.5397 — counterexample choice and bounded histories change synthesis behavior but the counterexample-to-constraint loop is established prior structure.
- Meng et al., *Rethinking Transfer in Continual Learning: A Replay-Based Realisation*, arXiv:2607.15587 — replay benefit depends on compatibility of prior tasks; indiscriminate transfer is not warranted.
- ORION P7 `FORMAL_CORE_V2.md` — complete transport witnesses preserve support semantics, while incomplete target-ambiguous transport must reopen or return `CANNOT_CHECK`.

No source above is treated as proof of an ORION terminal. The point of the refresh is to make the strongest parents explicit before constructing discriminators.

## 3. Challenge to the saturation basis

The search could look falsely flat for different reasons in each atom.

### F1 challenge

A universal-monitor search can miss domain-native verification because papers describe the verifier by its scientific object (proof checker, conservation law, simulator invariant, custody/provenance audit) rather than by the phrase `failure detector`. Conversely, a process-monitor paper can report aggregate reward while hiding false alarms on surprising-but-valid controls. Therefore saturation must include both generic process monitors and native semantic verifiers.

### F2 challenge

`Failure memory`, `negative knowledge`, `nogood`, `conflict set`, `counterexample constraint`, `diagnosis`, and `belief maintenance` live in different vocabularies. A search restricted to agent-memory language would falsely manufacture novelty. The comparison must be structural: what assumptions and evidence make a conclusion inconsistent, and under which environments does that conclusion persist?

### F3 challenge

`Staleness` can mean timestamp expiry, cache invalidation, task similarity, dependency revocation, or semantic transport. Only the last is load-bearing here. A version/hash comparison may be safe but over-reopen; a semantic carry-forward needs a witness about preserved referents, measurements, satisfaction relations and defeaters.

## 4. Why important domains might still be missing

Reopen the search if any of the following appears:

- a formal monitoring framework proves uniformly sound material-failure recognition across heterogeneous scientific semantics using only the public information allowed by the F1 protocol;
- a truth-maintenance/diagnosis formalism cannot encode an F2 scoped exclusion that the candidate ORION extractor can encode at the same information/resource bound;
- a theory of theory change, schema evolution, refinement, bisimulation, conservative extension or proof transport supplies a strictly stronger negative-knowledge transport criterion than P7 and changes an F3 protected disposition;
- a primary source establishes that a current ORION parent claim was misattributed or materially weaker than assumed;
- a hostile benchmark exposes an outcome that the frozen terminal cannot classify without adding a genuinely new observable coordinate.

## 5. Frozen implementation hypotheses and falsifiers

These are candidate outcomes to be tested by the bounded packet; they are not issue results until the packet is independently reviewable and repository CI is green.

### H-F1 — monolithic F1 does not survive

Candidate terminal: `MULTIPLE_FAILURE_SIGNAL_ATOMS_REQUIRED`.

Reasoning to test: if two worlds are identical on every registered public trajectory feature yet differ in protected material-validity semantics, no deterministic public-only detector can classify both correctly. The only sound responses are to obtain an additional specialized verifier/evidence source or return `UNRESOLVED/CANNOT_CHECK`. Native invariant, process-integrity, evaluator/custody and data-integrity signals therefore remain distinct evidence families; a generic layer may route/aggregate warnings but cannot manufacture their semantic observations.

Falsify H-F1 if a registered general detector separates every matched indistinguishability pair without access to protected labels or extra domain evidence and without over-alarming valid controls.

### H-F2 — no standalone extraction primitive at this resolution

Candidate terminal: `TMS_NOGOOD_PLUS_RESPONSIBILITY_SUFFICIENT`.

Reasoning to test: once domain evidence has warranted a contradiction/exclusion and responsibility has identified the relevant scientific assumptions, the current `FailureKnowledge.v1` content can be represented as assumption-environment-scoped nogoods plus retained non-conflicting nodes, with responsibility/evidence lineage and authority kept external. `FailureKnowledge.v1` may remain useful as an ORION interchange/storage contract; that does not make the underlying extraction logic a new atom.

Falsify H-F2 if a protected case requires a scientifically warranted scope/preservation result that cannot be represented by ATMS/nogood structure plus the registered responsibility/evidence relation at the same bound.

### H-F3 — P7 transport owns semantic staleness

Candidate terminal: `P7_TRANSPORT_SUFFICIENT`.

Reasoning to test: exact unchanged context is an identity-transport fast path. A changed representation/measurement/objective/interface/evaluator may preserve or invalidate an old negative conclusion only through its load-bearing support semantics. P7 already requires complete support/evidence/obligation transport for carry-forward and requires reopening or `CANNOT_CHECK` under incomplete target-ambiguous transport. The negative lesson is just another conclusion whose support must be transported; no extra staleness primitive is hypothesized.

Falsify H-F3 if negative knowledge needs a preservation condition that is neither reducible to P7 support/evidence/obligation/defeater transport nor owned by an existing dependency/revocation mechanism.

## 6. Frozen bounded case families

The closure packet must include at least:

### F1 positive/paired cases

1. same successful-looking numerical trace; protected physical invariant valid in one world and violated in the other;
2. same high evaluator score; custody/protocol intact in one world and tampered in the other;
3. same plausible proof text; native proof checker accepts one derivation and rejects the other;
4. same local-step plausibility; cross-step semantic composition valid in one world and inconsistent in the other.

No-failure controls must include surprising-but-valid, rare-but-valid, benign tolerance error and checker warning with no threatened contract.

### F2 scope cases

1. measurement failure must not refute theory;
2. invalid execution must not refute scientific mechanism;
3. theorem counterexample kills an unrestricted statement while preserving a restricted theorem;
4. non-identifying/underpowered null emits no exclusion;
5. evaluator defect excludes the evaluator conclusion, not the candidate;
6. correlated repeated failures do not become independent exclusion evidence by repetition alone.

### F3 applicability cases

1. identity context: old scoped negative applies;
2. semantic-preserving rename/refactor: negative may transport, so name/hash mismatch alone is not sufficient evidence to discard it;
3. repaired measurement/evaluator: old rejection must reopen;
4. changed objective: evidence may transport while the old failure conclusion does not;
5. domain expansion: old local negative remains local unless a verified transport extends it;
6. incomplete mapping: `UNRESOLVED`/reopen, never silent carry-forward.

## 7. Non-compensatory gates

- no protected gold label may enter candidate-visible F1 observations;
- a warning is not responsibility diagnosis;
- responsibility is not scientific refutation authority;
- no F2 exclusion may be globally promoted by count, confidence or wording;
- no F3 semantic transport may be inferred from a version/name/hash similarity alone;
- missing load-bearing evidence is `UNRESOLVED/CANNOT_CHECK`, not guessed transfer;
- a negative/subsumption result does not delete the useful V1 data contracts unless the contract itself is harmful.

## 8. Implementation scope

Implement only an additive research/finite-check packet that:

- freezes the paired worlds, parent mappings and expected candidate terminals;
- mechanically verifies the F1 observational-indistinguishability construction;
- mechanically checks that F2/F3 mapping rows are total over the frozen fields/cases and never grant authority;
- emits a reproducible report for review;
- does not add a runtime universal detector, automatic negative-knowledge extractor, or new semantic transport engine.

No manuscript claim, protected experiment result, global Jump claim or #507 terminal is authorized by this implementation.
