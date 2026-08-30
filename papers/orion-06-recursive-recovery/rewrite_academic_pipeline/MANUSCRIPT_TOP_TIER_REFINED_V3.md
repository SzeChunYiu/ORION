# Recovering from Negative Results in AI-Assisted Scientific Search

## Abstract

AI-assisted research systems can propose hypotheses, run analyses and revise plans rapidly, but iterative automation creates a governance problem after an adverse result. If the failed question, comparator and success criterion can all change after the outcome, repeated search can mutate failure into apparent success. If every negative instead terminates the programme, useful information about missing mechanisms and next evidence is lost.

We model scientific iteration as a sequence of **claim episodes**. Each episode freezes its question, admissible evidence, strongest registered donor, evaluation rule and terminal conditions before interpretation. Negative, absorbed, mixed, saturated and unresolved terminals remain immutable. A successor is a new episode and is licensed only when the parent identifies a specific unresolved scientific obligation. This yields a post-terminal transition contract for AI-assisted scientific reasoning rather than an algorithm for maximizing positive results.

A complete single-programme case study in exact quantum compilation illustrates the contract. The sequence moves from donor saturation to an explanatory conjecture, two exact counterexamples, finite support-two closure, a prospectively committed prediction on a previously unread public Hamiltonian, and finally an all-size normal-form theorem. Later success never relabels the failed parents. Seven additional adverse episodes provide a negative control on the recovery narrative: two yield bounded successor improvements, one is absorbed by stronger prior work, and four remain negative.

The evidence does not establish that the protocol improves research productivity, false-discovery rates or reliability relative to ordinary iteration. There is only one deep programme and no matched counterfactual workflow. The contribution is a reasoning/governance object: adverse scientific outcomes can be retained as typed state that constrains which successor questions are scientifically licensed. A broader causal claim requires a prospective cross-domain comparison.

## 1. Why scientific iteration needs immutable terminals

A generic research loop—propose, test, evaluate, revise—does not specify what is allowed to change after failure. This omission is especially consequential for AI systems because hypothesis generation and evaluation can be repeated cheaply.

Suppose a system observes a negative result and then changes the question, comparator and threshold simultaneously. The new experiment may be perfectly valid under its new definition, but it cannot retroactively turn the original result positive. Conversely, a hard stop after every negative discards information that may identify the next scientifically meaningful discriminator.

We therefore represent a research programme as a graph of claim episodes rather than as one continuously edited hypothesis. A parent terminal is historical scientific state. A successor may learn from that state but cannot rewrite it.

### Contributions

1. A typed post-terminal contract for negative, absorbed, mixed, saturated, lower-bound, positive and unresolved outcomes.
2. A successor-licensing rule requiring a specific open scientific obligation exposed by the parent.
3. A strongest-donor rule preventing a weak comparator from becoming novelty merely through repeated search.
4. An auditable deep case study in which two exact refutations remain refutations after a later theorem.
5. A negative control showing that recovery is allowed to stop: most of the additional adverse episodes do not become positive successors.

## 2. Claim-episode contract

Before an episode becomes outcome-bearing, the system records the scientific question, evidence boundary, available tools, strongest relevant donor, resource definition, success/refutation criteria, controls and stopping rule.

The terminal is then immutable. A later discovery can create a new episode with a new question, but it cannot modify the old gate.

This chronology separates **scientific revision** from **result revisionism**. Scientific revision changes what is asked next. Result revisionism changes what the previous experiment is said to have tested.

## 3. Donor subtraction before recovery

A candidate successor receives incremental scientific credit only after the strongest relevant known mechanism is given the same information and resource opportunity. If that donor explains or matches the apparent gain, the correct terminal is `absorbed`, not “successful after a weaker baseline.”

This rule matters because AI systems can generate many plausible variants. Without strongest-donor subtraction, the search process can discover improvements that are real operationally but scientifically non-residual.

Donor absorption is not failure of the research process. It is a scientifically useful conclusion that redirects the next question away from already-owned territory.

## 4. Typed adverse terminals and successor licensing

Different adverse outcomes authorize different next moves.

- **Negative:** the registered claim failed; a successor may target the failure mechanism.
- **Absorbed:** a stronger donor explains the result; a successor requires a different residual.
- **Mixed:** the effect is regime-dependent; a successor may characterize the regime.
- **Saturated:** the registered family has no remaining residual under the current comparison; a successor should change the scientific question, not continue local tuning.
- **Unresolved:** required evidence or authority is missing; the next action is evidence acquisition, not positive/negative relabelling.

A successor counts as productive recovery only when the parent is preserved, the parent identifies a specific open obligation, the successor receives a new frozen identity and the successor yields a materially different scientific object such as a counterexample, regime boundary, prospective prediction or theorem.

## 5. Deep exact case study

Exact quantum compilation supplies an unusually transparent environment because proposed mechanisms can be checked against exact optima and later theorem statements can be separated cleanly from finite evidence. The compilation theorem is not the novelty claim of this paper; it is the endpoint through which the recovery discipline can be audited.

The programme trace is:

> donor saturation → explanatory conjecture → exact counterexample → repaired conjecture → second exact counterexample → finite support-two closure → prospective prediction → all-size theorem.

### 5.1 Donor saturation changes the question

Increasingly expressive candidate families collapse onto existing donor envelopes on the registered open instances. The correct terminal is saturation of the residual optimization claim. The next question becomes explanatory: why does unrestricted optimization repeatedly collapse onto low-support constructions?

### 5.2 Local regularity does not license global closure

A first explanatory successor finds no violation in 688,041,472 local configurations. That local inequality is real within the tested object. A global closure conjecture built from it is nevertheless refuted by an exact construction with cost 8 where the donor family needs 9.

The local result remains supported; the global conjecture becomes negative. The counterexample identifies a missing shared-coupling mechanism and licenses a successor representing it.

### 5.3 Repair exposes a converse coupling mechanism

The repaired family closes the first witness and is then refuted by a second exact construction, reaching cost 5 where the repaired donor needs 6. The second witness spends more local support to reduce a different global cost.

The two failures are retained independently. Their scientific value lies in exposing complementary coupling currencies, not in being stepping stones that later disappear from the narrative.

### 5.4 Finite closure stays finite

A complete support-two family subsequently matches the unrestricted optimum throughout the registered finite domain. This closes that domain but does not become an all-size theorem. The surviving obligation is explicit: can support greater than two ever be necessary outside the verified domain?

### 5.5 Prospective prediction precedes exact opening

A structural predictor is frozen for a previously unread public chemistry subject and its regime prediction is committed before the unrestricted referee is opened. The prediction agrees with the exact outcome on all 15 registered matchings.

This is forward-use evidence on one subject, not proof or a reliability estimate.

### 5.6 The final successor is mathematical

An exchange argument finally proves that support above two is unnecessary for every admitted size under the frozen grammar. A matching exact lower witness makes the normal form sharp. The theorem answers the specific obligation left by finite closure without altering the status of either earlier conjecture.

## 6. Recovery is allowed to remain negative

A governance protocol that always ends in a positive result would be difficult to distinguish from outcome-driven search. We therefore retain seven additional adverse episodes at the mechanism level.

Two produce bounded successor improvements, one is absorbed by a stronger donor, and four remain negative after relevant follow-up. The denominator is small and heterogeneous, so these counts are not a recovery-rate estimate. Their role is simpler: the protocol contains genuine stop states and does not mechanically convert every failure into a positive descendant.

## 7. What the evidence establishes

The case study establishes operational properties of the reasoning contract:

- adverse terminals can remain immutable across later success;
- a counterexample can license a successor by identifying a missing mechanism;
- strongest-donor subtraction can terminate apparent novelty;
- finite closure can be held below theorem authority;
- prospective prediction can remain distinct from proof;
- unresolved and negative states can persist without being treated as pipeline errors.

It does **not** establish that this contract causes better science. The programme has no matched human-only, naive-iteration or donor-stopping counterfactual and only one deep domain.

## 8. Relation to AI reasoning and scientific-agent governance

Preregistration, provenance, experiment tracking, falsification, negative-result publication, strong-baseline methodology, truth maintenance, reflection and self-correction address adjacent pieces of the problem. They are donors, not claimed inventions.

The residual object is the **transition semantics after a terminal**: which evidence state is frozen, which previous claims remain live, and what kind of new question a failure is allowed to license. This makes the paper an AI reasoning/governance contribution rather than a quantum-compilation performance paper.

For AIJ, the key intellectual claim is that negative scientific evidence can be represented as persistent typed state constraining future action, instead of being reduced to a scalar reward or deleted as an unsuccessful branch.

## 9. Limitations and decisive next test

The evidence comes from one programme with unusually exact referees. Multiple episodes inside that programme are not independent domains. No causal statement about productivity, novelty quality or false-promotion reduction is authorized.

The decisive extension is a prospectively frozen multi-programme comparison in which matched scientific tasks are assigned to claim-episode recovery, ordinary flexible iteration and donor-stopping controls. Predeclared endpoints should include claim mutation, unsupported novelty, productive recovery, evidence cost, terminal calibration and valid-positive retention.

A null result must remain possible. If ordinary provenance plus strong donors reproduce the same behavior, the additional transition machinery should lose its incremental claim.

## 10. Reproducibility and release

The public archive should bind episode definitions, frozen gates, adverse terminals, counterexamples, donor comparisons, prospective commitments, exact replays and the final theorem trace. Reviewer-facing prose should describe scientific episodes rather than repository branches or CI job names.

The bounded paper requires no new science for its current claim. The remaining named-arXiv build is a release-surface obligation and should not be presented as scientific evidence.

## 11. Conclusion

Negative results are useful to an AI-assisted research system only if they cannot be rewritten away. The claim-episode contract preserves each terminal and permits a successor only when that terminal exposes a new scientific obligation. In one exact research programme this yields an auditable path from saturation through two refutations and a prospective prediction to an all-size theorem, while most additional adverse episodes remain adverse. The contribution is a formalized recovery discipline for scientific reasoning, not evidence that recursive AI research is generally more productive or reliable.