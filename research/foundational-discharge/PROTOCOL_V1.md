# Scientific Discharge Calculus — theorem and prospective research protocol V1

**Date:** 2026-08-20  
**Status:** `THEORY_PROTOCOL_FROZEN_FOR_NEW_FALSIFIER_SUITE`  
**Authority:** this protocol proposes a new programme theorem target; it does not retroactively upgrade any paper terminal or claim universal validity.

## 1. Research question

Can one generic formal relation explain when a locally valid result in an autonomous scientific workflow is **sufficient and entitled** to change the standing of a different scientific object?

The intended target is a typed **scientific discharge calculus** that subsumes, without paper-specific exceptions, reformulation authority (P1), task closure (P2), scientific identity (P3), promotion authority (P4), certificate lifting (P6), closure transport (P7), and cross-domain authority composition (P8).

The theory must distinguish three questions that existing systems often conflate:

1. Is the local artifact valid for its native object?
2. Does it contain enough information for a target decision?
3. Is it scientifically authorized to discharge the target obligation?

## 2. Donor ownership / prior-art ceiling

The calculus does **not** claim as novel:

- generic proof validity or proof-theoretic accounts of inference;
- statistical sufficiency / Blackwell comparison of experiments;
- causal generalizability or transportability;
- capability-security no-authority-amplification or delegated-scope attenuation;
- generic authorization evidence chains, action certificates, or proof-carrying execution;
- provenance, scientific claim verification, abstention, workflow closure, or benchmark auditing as standalone mechanisms.

The proposed residual is the common **target-bound scientific discharge relation** above these donor mechanisms.

## 3. Formal objects

A scientific object is

`x = (id, domain, kind, scope, content, epoch)`.

A scientific obligation is

`o = (target=x, predicate, required_authority_type, status)`

with `status in {OPEN, DISCHARGED, BLOCKED, UNDETERMINED}`.

A local artifact/judgment is

`a = (subject, native_type, native_verdict, evidence, provenance, epoch, authority_signature)`.

`NativeValid(a)` is defined by the donor-native validator and must be conserved by the scientific layer.

A discharge bridge/rule is

`r: (a_1, ..., a_n, premises) -> o`

and is admissible only when it is registered for the target type/scope/content/epoch and every hard premise is satisfied. A bridge may represent a valid scientific inference, transport rule, revalidation, identity rule, closure rule, promotion rule, coercion, or other target-specific scientific relation.

Let `R` be the registered sound bridge set. Define `DischargeClosure(A,R)` as the least fixed point of obligations directly discharged by native-authorized artifacts plus applications of admissible bridge rules.

## 4. Authority-neutral transformations

An authority-neutral transformation `F` may compute, summarize, aggregate, reorder, serialize, map representation, repeat a local check, or compose native-valid artifacts, but it introduces:

- no new authorized evidence;
- no new bridge/inference rule;
- no protected revalidation;
- no stronger authority signature;
- no unrecorded target-type change.

`F` may make implicit information explicit or compute consequences already licensed by `R`. It is not prohibited from deriving conclusions; those conclusions must already lie in the authorized closure of the inputs and registered rules.

## 5. Frozen theorem targets

### T1 — native conservativity

Adding the scientific-discharge layer never changes a donor-native validity verdict for the object the donor actually certifies.

### T2 — no unlicensed scientific-authority amplification

For any authority-neutral transformation `F`,

`DischargeClosure(F(A), R) subseteq DischargeClosure(A, R)`

up to representation-equivalent restatement of the same scientific objects.

If `F` is information-preserving for the registered discharge decisions, equality should hold.

Interpretation: computation may expose an already licensed implication, but cannot silently create authority over a different target obligation.

### T3 — bridge necessity for target widening

If a target obligation `o` is outside `DischargeClosure(A,R)`, no finite sequence of authority-neutral transformations can discharge `o`. Discharge requires at least one of:

- new authorized evidence;
- an admissible bridge/inference rule whose premises are satisfied;
- protected revalidation supplying a previously missing premise.

### T4 — representation independence / recoverability

If two implementations expose information-equivalent scientific objects and the same sound bridge rules, they agree extensionally on every discharge judgment in the registered model.

This theorem is the programme-level generalization suggested by repeated ideal-product ties in P1/P2/P4/P6/P7/P8.

### T5 — sufficient-interface compression

For a registered task family, if a reduced interface `S(A)` yields exactly the same discharge closure as the richer representation `A` for all states in that family, then `S` is decision-sufficient on that family. Richer representations may still carry audit/provenance value that is orthogonal to decision sufficiency.

The protected P1 objective-basis tie and cross-domain abstract-signature tie are candidate bounded instances. Mathematical minimality requires strict-subset/interface falsifiers and is not assumed.

### T6 — unresolved obligation preservation

An `UNDETERMINED` target premise is not equivalent to false and may not be silently removed by unrelated local success. Unless a registered bridge discharges it, the unresolved scientific obligation remains visible as an inability-to-close/check state.

### T7 — revocation soundness

If every complete support family for a discharged target is revoked or invalidated, discharge is removed. If an independent complete support family remains valid, discharge may persist through that family.

## 6. Required paper embeddings

A generic implementation must encode each paper using only declarations of object/obligation/bridge types, not custom decision code.

- **P1:** diagnostic/performance artifact -> reformulation obligation; objective-basis selection/admission.
- **P2:** route state/processing -> material-route and task-closure obligations; evaluation transport validity.
- **P3:** mapping/alignment -> claim-relative identity obligation.
- **P4:** verification/provenance/custody -> scientific-promotion obligation; benchmark score -> competence-claim identifiability obligation.
- **P6:** donor certificate -> preservation/revalidation of scientific standing.
- **P7:** donor navigation transform -> transported task-global closure.
- **P8:** heterogeneous donor authority -> target scientific-discharge obligation.

Retrospective recovery of existing paper decisions is a compatibility test only; it cannot by itself establish a new empirical result because those outcomes are already known.

## 7. Prospective falsifier suite

A new hidden suite must be frozen before execution and contain cross-paper cases designed specifically to break the generic calculus.

Required families:

1. **Legitimate novel inference:** source artifacts do not individually support the target, but a registered scientific inference rule does. The calculus must permit the new conclusion, preventing a trivial “authority can never grow” rule.
2. **Illicit aggregation:** many individually valid weak/local artifacts are aggregated without a target bridge. The calculus must refuse silent authority amplification.
3. **Representation compression:** a reduced interface and a rich audit object are decision-equivalent on one family but diverge on a hostile family carrying a hidden load-bearing coordinate.
4. **Transport shift:** internally valid evidence is moved to a target domain/epoch/population with and without a valid transport bridge.
5. **Identity collision:** semantic compatibility is held constant while scientific identity authority differs.
6. **Closure leakage:** every available route locally stops while one material unavailable/invalid route remains unresolved.
7. **Promotion laundering:** provenance/verification/generic authorization pass while exact target promotion scope is missing.
8. **Revalidation necessity:** a scientific object changes and only the complete affected bridge restores standing.
9. **Cross-domain widening:** native-valid authority chains preserve/narrow or widen scientific type with/without protected coercion.
10. **Evaluator non-identifiability:** two policies with different intended competence obtain the same score because of a construction shortcut; the calculus must deny the stronger competence discharge.

## 8. Primary falsifiers

The programme theorem target is refuted or must be narrowed if any of the following occurs:

- a valid target discharge appears after an authority-neutral transformation even though it was outside the authorized closure of the inputs and no new evidence/bridge/revalidation entered;
- a paper requires an ad hoc exception that cannot be expressed as a typed object, obligation, or bridge rule;
- an information-equivalent implementation with the same rules produces different discharge judgments;
- the generic calculus blocks a legitimate registered scientific inference because it mistakes all authority growth for laundering;
- donor prior art already proves an equivalent target-bound scientific-discharge calculus at the same scientific-workflow scope;
- prospective cross-domain cases show that the proposed type/bridge structure does not predict when scientific standing should change.

## 9. Novel predictions required before a foundational claim

The programme must predict at least one previously untested result before outcome access, preferably several:

- a benchmark construction that will saturate/non-identify a claimed competence;
- a strong donor combination that will tie ORION because it already carries a decision-sufficient interface;
- a seemingly strong local-success product that will fail exactly because one target-bound discharge bridge is absent;
- a strict-subset repair family establishing a new necessary-and-sufficient bridge law;
- a cross-domain transport case where local validity survives but target scientific authority correctly does not.

## 10. Scientific-success criterion

A foundational claim is earned only if:

1. one generic calculus recovers all registered P1/P2/P3/P4/P6/P7/P8 decisions without paper-specific algorithmic branches;
2. T1–T7 survive independent formal/checker reconstruction;
3. the prospective falsifier suite is frozen before execution and passes without leakage;
4. at least one genuinely novel prediction is prospectively confirmed;
5. hostile literature review finds no prior system proving the same target-bound scientific-discharge result at equivalent scope;
6. external real-science campaigns in multiple disciplines show transfer beyond invented/mechanical contracts.

Until then the correct status is:

`SCIENTIFIC_DISCHARGE_CALCULUS__FOUNDATIONAL_THEOREM_TARGET__NOT_YET_UNIVERSAL`

## 11. Intended synthesis

If the criterion is eventually met, the core result should be stated as a theory of scientific inference governance rather than as a collection of agent features:

> **A locally valid result changes another scientific object's standing only through a sound target-bound discharge relation. Computation may expose licensed consequences, but cannot replace missing evidence, missing bridge premises, missing revalidation, or missing authority.**

This is deliberately compatible with strong proof theory, statistical sufficiency, causal transportability, capability security, proof-carrying actions, provenance, and scientific verification. Those theories become donor layers; the research question is how their locally valid judgments acquire scientifically legitimate force over different obligations in an autonomous research process.
