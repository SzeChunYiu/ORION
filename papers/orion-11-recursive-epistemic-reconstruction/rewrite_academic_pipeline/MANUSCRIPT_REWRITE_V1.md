# Separating Search Success, Intervention Safety and Cost in Recursive Scientific Repair

## Abstract

Comparative studies of scientific-repair agents can attribute a performance margin to the wrong mechanism when strong baselines are not given the same opportunity to iterate. We report a falsification-driven reconstruction of one such study. The original experiment compared a governed recursive-repair policy with three parent mechanisms on a frozen family of 2,882 credential-free mechanical worlds, including 480 protected hidden-shift worlds and 2,402 controls. The governed policy solved every hidden-shift case with no forbidden high-level mutation, whereas the registered parents solved only 49.375% of hidden shifts. That margin initially appeared to support a mechanism-necessity claim.

A later faithful-comparator study changes one operation in each parent: instead of taking a single top-confidence repair, the parent searches the same public repair menu in order. All three repaired parents recover hidden-shift task success from 49.375% to 100%. One repaired parent also reaches zero forbidden high-level mutation and therefore matches the governed policy on both registered primary gates. The original comparative necessity claim is consequently retracted. Two other repaired parents recover success but retain forbidden-mutation rates of 23.768% and 41.083%, showing that search success and intervention restraint are distinct outcomes.

Conditioned on clearing both success and safety gates, a cost difference remains on this single world family: mean intervention cost is 1.8341 units for the governed policy and 2.6676 for the faithful parent, under the same four-unit budget. We do not attribute that gap to the governed responsibility mechanism. A donor-owned probability-to-cost ordering principle provides an obvious alternative explanation, and the dedicated successor test has not yet supplied publication authority. The contribution is therefore a corrected empirical decomposition: ordered search explains the former success margin, mutation permissions explain part of the safety separation, and an unattributed cost residual remains to be tested prospectively. The study shows how a failed mechanism claim can produce a more informative comparative paper when the falsifier is preserved rather than optimized away.

## 1. Introduction

When an AI-assisted scientific workflow outperforms several baselines, the most tempting explanation is the mechanism unique to the winning system. That explanation is unsafe until competing systems have been given the strongest obvious repair that preserves the intended comparison.

This problem is acute in recursive repair. A policy that can search several candidate interventions will naturally outperform a baseline forced to make a single top-confidence choice, even if the purportedly novel responsibility or dependency machinery is not what produces the success difference. If later work gives the parent the missing search operation and the margin disappears, the scientifically correct response is not to find a new metric on which the original system still wins. It is to retract the mechanism interpretation and ask what, if anything, remains.

We present that reconstruction for one frozen mechanical-world programme. The corrected paper separates three outcomes that had previously been compressed into a single comparative story:

1. **task success** on protected hidden-shift worlds;
2. **intervention safety**, measured by forbidden high-level mutation;
3. **cost**, interpreted only among policies that clear both scientific gates.

This decomposition changes the headline. Ordered search fully explains the old success margin. Safety remains different for two repaired parents but not for the strongest faithful parent. A cost residual survives between the two policies that satisfy both primary gates, but its mechanism is intentionally left unattributed.

## 2. Frozen evaluation contract

The study uses 2,882 credential-free mechanical worlds produced by one fixed generator. Of these, 480 are protected hidden-shift worlds and 2,402 are controls. Every policy operates under a four-unit intervention budget.

The primary criterion is conjunctive:

- solve the protected root task on hidden-shift worlds; and
- perform no forbidden high-level mutation.

This joint criterion is load-bearing. A policy can be inexpensive because it fails, or it can recover task success by modifying a level that the scientific contract declares out of bounds. Neither behavior is equivalent to safe repair.

The registered governed policy explicitly carries protected-sibling, dependency-impact and lower-level exclusion constraints. The original parent mechanisms use related donor strategies but, in their registered forms, make one top-confidence repair choice rather than searching the same candidate menu.

## 3. The original comparative result

In the original protected evaluation, the governed policy achieves hidden-shift success 1.0 with forbidden-mutation rate 0. The three registered parents each achieve hidden-shift success 0.49375; two additionally exhibit substantial forbidden high-level mutation.

Taken at face value, the approximately 0.506 success margin appears large. The problem is that the comparison entangles the proposed governance mechanism with a simpler difference: whether the policy iterates over available repairs after the first attempt fails.

A mechanism-necessity claim requires ruling out that simpler explanation. The faithful-comparator study is designed to do exactly that while holding the world set, budget, public repair menu, seeds and protected matrices fixed.

## 4. Ordered search falsifies the necessity interpretation

The faithful comparator modifies one operation in each parent: the single top-confidence choice becomes an ordered search over the same public repair and diagnostic menu. No new information or budget is added.

All three repaired parents improve from 0.49375 to 1.0 hidden-shift success. The success margin is therefore completely recovered by search alone.

The strongest repaired parent also has forbidden-mutation rate 0 and matches the governed policy on both components of the primary criterion. The paired success comparison contains no disagreements. Under the registered margin, the two policies are indistinguishable on the primary endpoint.

This result retracts the previous comparative necessity reading. The observed success margin measured a difference between iterating and non-iterating policies, not a demonstrated necessity of the governed responsibility mechanism.

The retraction is part of the result. Later analyses do not relabel the original comparison as successful on a different mechanistic interpretation.

## 5. Search success and intervention restraint are different

The falsifier does not make all repaired parents equivalent. Two repaired parents recover 100% task success while continuing to mutate the forbidden high-level layer. Their forbidden-mutation rates are 0.23768 and 0.41083, far above the registered ceiling.

This asymmetry reveals a more defensible scientific object. Ordered search is sufficient to recover *task success* for all three parent families. It is not sufficient to recover *restraint* for two of them. A scalar success metric cannot distinguish a policy that solves the task through an admissible lower-level repair from one that solves it by changing a scientifically protected level.

The strongest repaired parent demonstrates the necessary caution: one donor family achieves both success and restraint once search is admitted. We therefore do not claim that governed responsibility is uniquely necessary for safe repair. The current evidence only shows that the permission structure differs across the tested mechanisms and that some parents buy success through changes the registered contract forbids.

## 6. Cost is meaningful only after the gates

Cost comparisons are conditioned on satisfying both the success and safety requirements. A failed or unsafe policy cannot be declared preferable merely because it spends less.

Among the two policies that clear both gates, the governed policy spends 1.8341 mean intervention units and the faithful search-admitted parent spends 2.6676. The paired cost ratio is approximately 0.6876 under the common four-unit ceiling.

Several failed parents are cheaper than the governed policy. One registered parent spends 1.7585 mean units while failing both the success and safety gates; its search-repaired form spends 1.9514 while still failing safety. These controls show why the cost residual cannot be reported in isolation.

The surviving empirical statement is therefore precise: on this one frozen world family, among the policies that achieve full hidden-shift success and zero forbidden high-level mutation, the governed policy uses less intervention budget than the faithful matching parent.

## 7. The residual cost mechanism is intentionally unresolved

The cost gap should not be attributed to the typed responsibility filtration merely because that machinery is present in the lower-cost policy. A simpler donor explanation exists: ordering candidate interventions by a probability-to-cost rule can reduce expected search cost independently of the responsibility hierarchy.

A theoretical result in the programme already shows that a level filtration cannot make ordering cheaper than unconstrained probability-to-cost ordering when the latter is admissible; it ties in an aligned case and can cost more otherwise. This makes the donor explanation strong enough that the paper must leave mechanism attribution open.

A successor experiment has been designed to compare the observed policy directly with a simple probability-to-cost baseline and an exact dynamic-programming optimum on a new frozen world family. Until that successor produces admissible results, the present manuscript treats the 1.8341 versus 2.6676 difference as a measured residual, not evidence for a specific causal mechanism.

## 8. What the study establishes

The reconstructed evidence supports four bounded conclusions.

First, the original success margin is not evidence of mechanism necessity; ordered search fully recovers it. Second, task success and intervention safety are separable: some repaired parents solve every protected task while violating the mutation constraint. Third, a faithful parent can match the governed policy on both primary gates, ruling out broad superiority. Fourth, a cost residual remains among the gate-matched policies on this one world family, but its mechanism has not been identified.

The study also preserves the internal ablation evidence that removing protected-sibling, dependency-impact, lower-level exclusion or ordering components degrades the governed policy in the registered direction. Those are within-system necessity statements. They do not restore the retracted cross-policy necessity claim.

## 9. Why falsification improves the paper

The faithful comparator changes the scientific interpretation more than an additional positive benchmark would have. It isolates a baseline-design defect and turns an apparently monolithic performance advantage into three distinct questions: does the policy search enough, is the chosen intervention scientifically admissible, and how much does an admissible success cost?

This is a useful pattern for agent evaluation. Stronger baselines should receive obvious algorithmic repairs before a system-specific mechanism receives credit. If the repaired comparator absorbs the effect, the claim should shrink. If a residual remains, it should be tested against the strongest plausible explanation rather than automatically attributed to the focal mechanism.

The current paper is therefore a corrected mechanism/failure analysis rather than a leaderboard paper.

## 10. Relation to repair, planning and agent evaluation

Iterative repair, value-of-information planning, dependency-directed reasoning and counterfactual repair are established areas. The paper does not claim ordered search or probability-to-cost ordering as new. Those mechanisms are precisely the donors used to subtract the original interpretation.

The residual contribution is empirical and methodological: a controlled faithful-comparator falsification, a decomposition of success/safety/cost under a protected intervention contract, and an explicit example in which a large original margin disappears once the comparator receives the missing iteration capability.

## 11. Limitations

The evaluation uses one generated mechanical-world family. Its 2,882 cases are numerous but not a population of naturalistic scientific tasks. The faithful repair is one particular improvement to each parent; other repairs could change the safety comparison further. The replication world set remains unread because its anchor gate was instrumented incorrectly; it is neither a replication success nor a replication failure.

Most importantly, the remaining cost gap has no established mechanism and should not be generalized beyond this world family. The study does not show broad agent superiority, general safety, or improved scientific productivity.

## 12. Reproducibility and availability

The publication package should expose the frozen world definitions, registered and repaired parent policies, primary success/safety criterion, cost accounting, paired comparison records and claim-retraction ledger. The original and repaired comparisons should remain separately reconstructable so that the falsification chronology cannot be overwritten by the revised narrative.

## 13. Conclusion

A strong comparator can change the scientific meaning of an apparent agent advantage. In this study, giving each parent the same ordered search opportunity eliminates the former protected-task success margin, and one faithful parent matches the governed policy on both success and intervention safety. Two other parents recover success while continuing to violate the mutation contract, revealing that task completion and scientific restraint are distinct. A lower intervention cost remains for the governed policy among gate-matched arms, but the mechanism behind that residual is still open. The corrected result is therefore not necessity or superiority; it is a falsification-driven decomposition of what recursive scientific repair actually measured.
