# ORION-16 ETS prospective protocol V1

**Programme:** #977  
**Paper:** ORION-ORION-16  
**Protocol state:** `FROZEN_BEFORE_EXECUTION`  
**Purpose:** test the top-tier Epistemic Transition Systems claim above the finished V2.1 theory without altering historical ORION-16 results.

## Scientific question

Given the same visible transition facts, does an explicit epistemic-transition contract distinguish scientific admissibility from computational/generic-policy validity in cases where a strong donor product still lacks responsibility-scoped evidence/obligation transport semantics?

This protocol tests a bounded finite interface. It does not establish universal superiority over all possible integrated donor systems.

## Transition factorization

Each case exposes four logically distinct coordinates:

1. `computational_support` — dependency/support correctness after the transition;
2. `evidence_transport` — content/scope/epoch preservation or protected revalidation;
3. `scientific_obligation` — responsibility-scoped obligations are discharged, preserved or reopened correctly;
4. `scientific_authority` — generic permission is separated from authority to commit the scientific state.

Additional facts record provenance, footprint audit, change reachability and independent support.

## Comparator

The donor-complete comparator receives **exactly the same case record** as ETS and may use:

- dependency/support validity;
- provenance binding;
- generic permission;
- generic obligation completion;
- declared footprint audit;
- preservation certificate and independent-support facts.

It deliberately does not reinterpret responsibility-scoped scientific evidence/obligation fields as generic policy fields. If adding those semantics makes the donor extensionally identical to ETS, the correct result is equivalence, not ORION-16 superiority.

## Frozen families

Exactly 18 cases are frozen in `ets_cases_v1.jsonl`, six in each family:

- `formal-software`;
- `agent-memory-tool-state`;
- `scientific-evidence-state`.

Every family contains:

- clean admissible transition;
- computationally valid but evidence-inadmissible transition;
- independent-support preservation case;
- stale epoch/context case;
- hidden/declaration-footprint failure;
- authority/obligation laundering case.

The gold scientific disposition is frozen separately in `ets_gold_v1.json` before the checker exists.

## Dispositions

- `ADMISSIBLE` — transition may retain/commit the scientific state;
- `REOPEN` — affected scientific state must be reopened/revalidated;
- `DENIED` — explicit authority violation;
- `CANNOT_CHECK` — missing/failed transport or footprint evidence prevents a safe conclusion.

## Primary endpoints

1. unsafe false-admissible rate;
2. unnecessary reopen rate on independent-support preservation cases;
3. exact disposition accuracy;
4. obligation/authority laundering false-admissible count;
5. per-family accuracy.

A ORION-16 positive requires lower unsafe false-admissible rate than the donor comparator **without** increasing unnecessary reopen on the frozen independent-support controls.

## Independent executable theorem obligations

The checker added after this freeze must exhaustively verify these finite propositions:

### T6.1 finite factorization/non-implication

For all Boolean assignments of the four coordinates, `ETS_ADMISSIBLE` implies every required coordinate. For each strict subset of required coordinates there exists an assignment where that subset is true while `ETS_ADMISSIBLE` is false. Therefore computational/generic validity alone does not entail epistemic admissibility in the finite interface.

### T6.2 finite composition under transport

For two individually admissible transitions with matching intermediate content/scope/epoch and no newly opened obligations, composition is admissible. The checker must also exhibit counterexamples where individual local validity does not compose because the intermediate epoch/scope/obligation transport condition fails.

### T6.3 donor-observable erasure witness

The checker must identify at least one pair of frozen cases that are identical on the declared donor decision coordinates but require different gold scientific dispositions because responsibility-scoped evidence/obligation/authority semantics differ.

## Hostile requirements

The post-freeze checker must fail if:

- it reads any non-frozen answer source;
- case IDs/family names affect classification;
- ETS gets a field the donor does not receive;
- donor classification uses hard-coded case IDs;
- the positive depends on always reopening;
- any family is missing a required case type;
- the theorem counterexamples are absent.

## Authority boundary

This protocol/corpus can close bounded executable ETS obligations only. It does not by itself satisfy ORION-16's requirement for broad external real-system evidence or immediate pre-submission literature refresh.
