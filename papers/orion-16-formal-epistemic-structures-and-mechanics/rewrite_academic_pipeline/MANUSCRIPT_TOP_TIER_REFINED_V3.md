# Conservative Certificate Lifting under Scientific Change

## Abstract

Scientific and AI workflows increasingly reuse execution certificates, provenance records, typed effects, authorization receipts and reproducible traces across changes in scientific state. A lower-level certificate can remain valid even when the question, measurement semantics or inferential obligation for which it was used has changed. Recomputing every certificate after every change discards valid assurance; reusing every certificate unchanged can preserve a scientific conclusion whose original support no longer applies.

We formalize **conservative certificate lifting** as a semantic layer between native certificate validity and continued scientific standing. Native certificates keep their own verdicts. A scientific conclusion is carried forward only when the claim-specific lift conditions required by the new scientific state remain satisfied. In a registered five-coordinate finite model, revalidating the complete affected set is sufficient to restore the lifted conclusion, while every proper subset is unsound for at least one admissible state. The donor-independent checker covers all 31 nonempty affected-coordinate patterns and all 211 strict-subset repair choices. Historical loops instantiate the same patterns across five donor families, yielding 155 complete successes and 1,055 strict-subset failures, but those repetitions are implementation coverage rather than independent scientific observations.

A separate product study gives 31 distinct countermodels in which multiple lower-level assurance signals remain valid while a required scientific bridge is absent. An information-equivalent competing product supplied with the same scientific coordinates and lift rule ties exactly. We also prove a commutation theorem for fully separated deterministic mechanics: with disjoint writes, reciprocal read exclusions and scientific noninterference, independent execution orders yield the same current scientific projection, while audit histories may differ by swaps of independent events. A fresh-kernel replay and mutation controls check the theorem's implementation boundary.

The contribution is a bounded formal repair law for preserving valid lower-level assurance without laundering it into unchanged scientific authority after material change. The five coordinates are not claimed universally minimal, and deployed cost savings or external-system superiority remain unestablished.

## 1. Native validity and scientific standing are different relations

A proof object can remain valid under its proof system. A workflow receipt can remain an accurate record of an execution. A provenance statement can remain true about an artifact. An authorization record can remain valid for a past action. None of these facts alone guarantees that the same object still supports a scientific conclusion after the question or interpretation changes.

This creates two symmetric errors.

- **Global reset:** discard or recompute every lower-level certificate after any material change.
- **Blind reuse:** retain every locally valid certificate as if its scientific relevance were unchanged.

Conservative lifting separates the two layers. Native systems continue to own native validity. A scientific lift records the additional relation connecting that native verdict to a current claim.

The paper asks when that bridge can be repaired selectively.

## 2. Registered scientific lift state

The finite model represents five claim-relevant continuity coordinates:

1. exact claim/content identity;
2. measurement semantics;
3. evidence semantics;
4. inferential obligation;
5. scientific epoch.

These coordinates define the present study; they are not proposed as a universal ontology of scientific state.

A transition changes some affected set `A` of coordinates. Unaffected native certificates remain native-valid unless their own premises changed. The scientific question is which elements of `A` must be revalidated before the old lower-level evidence may again support the current claim.

## 3. Complete affected-set repair is sufficient

Assume that native validity survives on unchanged premises and unaffected lift coordinates remain established.

**Theorem 1 (selective sufficiency in the registered model).** Revalidating every coordinate in the affected set `A` restores the lifted scientific conclusion.

The theorem is intentionally claim-specific. It does not say every change invalidates every certificate. It says the bridge is restored once every scientific condition that actually changed has been re-established.

This formalizes the middle ground between full recomputation and unconditional reuse.

## 4. Every strict subset is unsound somewhere

Sufficiency alone would permit an arbitrarily conservative repair rule. The sharper result is a necessity statement inside the registered finite model.

**Theorem 2 (strict-subset unsoundness).** For every nonempty affected set `A` and every proper subset `B⊂A`, there exists an admissible state in which all coordinates in `B` are repaired but one coordinate in `A\B` remains the missing condition that breaks the scientific lift.

There are 31 nonempty affected sets over five coordinates and 211 proper-subset repair choices. The donor-independent finite checker constructs or verifies a countermodel for every strict-subset choice and verifies successful lifting after every complete affected-set repair.

These 31 and 211 counts are counts of distinct scientific configurations in the registered model.

## 5. Repeated donor loops are not independent evidence

The same repair patterns were historically exercised across five donor families. This produces 155 complete repair successes and 1,055 strict-subset failures.

Those larger numbers should not be read as 1,210 independent experiments. They are repeated implementations of the same finite scientific patterns under different donor wrappers. Their role is coverage and portability checking.

The main manuscript therefore reports the 31 distinct affected sets and 211 distinct incomplete repairs as the scientific denominator and moves the repeated donor-loop totals to implementation context.

This distinction avoids pseudo-replication in a formal systems paper.

## 6. Product assurance cannot fill an absent scientific bridge

A natural objection is that the lift layer becomes unnecessary if enough lower-level assurance products are combined. We test that proposition directly.

Thirty-one distinct product countermodels keep the registered lower-level assurance coordinates valid while withholding one required scientific lift relation. The native product remains valid under its own semantics, yet the current scientific conclusion is unsupported.

The result does not imply that provenance, authorization or reproducibility are weak. It shows that they certify different propositions. Additional valid native certificates cannot discharge a missing scientific obligation unless an explicit bridge connects those native judgments to the changed claim.

## 7. Information-equivalent products tie

An ideal competing product is then enriched with exactly the same scientific lift coordinates and decision predicate. It agrees on every registered finite state.

This exact tie is the expected control if the contribution is semantic rather than architectural. The paper does not claim that one centralized implementation has unique expressive power. Any system carrying equivalent scientific state and applying the same lift relation should make the same decision.

The contribution is therefore a portable interface between native assurance and scientific standing.

## 8. Commutation of separated scientific mechanics

Dynamic scientific systems also apply multiple mechanics whose execution order can vary. Requiring byte-identical full states after swapping independent actions is inappropriate because an audit history should preserve chronology.

We distinguish the **current scientific projection** from the ordered history.

**Theorem 3 (scientific-projection commutation).** For deterministic admissible mechanics with disjoint writes, reciprocal read exclusions and scientific noninterference, executing the two mechanics in either order yields the same current scientific projection. Their histories may differ only by swaps of adjacent independent events.

A serialized kernel derivation replays the proof from primitive rules, and a separate solver check verifies the translated assumptions. Mutation controls remove each reciprocal read exclusion in turn; each removal admits a countermodel.

The mutation behavior is important because it demonstrates that the theorem depends on genuine separation conditions rather than a vacuous encoding.

## 9. Why the lift is conservative

The lifting rule is conservative in two senses.

First, it never broadens a native certificate. The proof system, provenance mechanism or authorization layer retains sole authority for its own verdict.

Second, it does not carry scientific standing across a material change until every affected bridge condition is re-established. Unknown or missing evidence remains unresolved.

The rule is selective because unaffected lower-level assurance is preserved. It is fail-closed because a missing affected condition cannot be compensated for by unrelated valid certificates.

No empirical cost-saving claim is needed for this formal contribution. Whether selective repair is faster or reduces scientific error in deployed systems is a separate future study.

## 10. Relation to assurance, provenance and dependency systems

Proof-carrying computation, certified execution, workflow provenance, authorization, effect systems, truth maintenance, dependency-directed recomputation and selective invalidation are established donor mechanisms. They own important native validity and update problems.

The residual question arises only when a locally valid object is reused to support a changed scientific commitment. Conservative certificate lifting adds a claim-specific bridge above donor verdicts and specifies how that bridge is reopened and repaired.

For AIJ, the contribution is a formal state-transition semantics for reasoning systems that must preserve valid evidence through changing scientific responsibilities without overextending its authority.

## 11. Limitations

The five-coordinate model is finite and explicit. The study does not prove that the coordinates are universally necessary, sufficient, independent or minimal. Real scientific systems may require additional semantics or may reasonably reopen more state than the model predicts.

The independent implementation and fresh-kernel replay are same-programme checks, not external custodianship. No wall-clock saving, deployment error reduction or agent-performance improvement is established.

The commutation theorem applies only to deterministic mechanics satisfying its separation assumptions. Shared reads/writes, stochastic actions and partially observed state require new proof obligations.

## 12. Reproducibility and release

The publication archive should expose the formal definitions, all 31 affected-set cases, all 211 strict-subset countermodels, product non-laundering cases, information-equivalent control, kernel derivation, solver translation and mutation controls. Repeated donor-loop rows should be labelled implementation coverage rather than independent evidence.

The trusted computing base of mechanized checks should be stated explicitly. Reviewer-facing prose should use scientific semantics instead of repository module names or CI chronology.

## 13. Conclusion

Scientific change should not force a choice between discarding every prior certificate and carrying every certificate forward unchanged. Conservative certificate lifting preserves native validity while reopening the claim-specific scientific bridge affected by change. In the registered finite model, complete affected-set repair is sufficient and every strict subset is unsound somewhere; accumulating unrelated native assurance cannot fill the missing bridge; and an information-equivalent product ties exactly. Under explicit noninterference assumptions, independent mechanics also commute at the level that matters scientifically even when audit histories preserve order. The result is a bounded formal repair law for dynamic scientific reasoning, not a universal ontology or deployed-performance claim.