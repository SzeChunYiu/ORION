# Candidate answer — ABSORB.REPRESENTATION_MAP.v0

**Target dimensions:** MATHEMATICS, TRANSITION_MODEL, FAILURE.
**Incumbent evidence:** RAKL `publication/papers/paper-02-structural-mechanics/sections/02_contract.tex` and `sections/04_typed_refusal.tex` @ `bd4ce50f`.

## Proposed step-specific contract

**Mathematics — correspondence is a directional witness, never a similarity score.** Over scoped structural objects \(S=(V,E,\chi,\gamma,q,\varepsilon)\) (typed roles, typed relations, invariants, boundary record, quantity of interest, evidence identities), a representation correspondence is a **directional structural witness**

```text
w_{A->B} = (mu_V, I+, I-, B, E_w, U_w)
```

— role mapping, preserved invariants, **explicitly non-preserved properties**, required target boundary conditions, mapping evidence, uncertainty — licensed only for the registered QoI. The relation is directional (a valid A→B need not license B→A), context-scoped (boundary changes can invalidate it), and non-transitive (A→B and B→C do not license A→C unless the composed obligations are separately satisfied).

**Transition model — non-compensatory, three-valued, typed refusal.** The witness is interpreted as a finite typed transport obligation set with per-obligation status `SATISFIED | VIOLATED | UNKNOWN` (failure to establish a precondition is never evidence it is false). Decision:

```text
LICENSED        iff every load-bearing obligation SATISFIED
REJECTED        iff at least one demonstrably VIOLATED
CANNOT_CHECK    otherwise
REJECTED -> {MERELY_UNLICENSED, CERTIFIABLY_IMPOSSIBLE}
```

No count of preserved relations buys back a violated boundary or forbidden loss. The strong refusal `CERTIFIABLY_IMPOSSIBLE` requires (i) a closed-world completeness declaration on the target, (ii) a *completed* bounded exhaustion over the witness presentation space, and (iii) a witness-independent obstruction (QoI mismatch, missing declared invariant, unmatchable relation type). Budget exhaustion, an open-world target, or any witness-local defect yields `MERELY_UNLICENSED` — the cost asymmetry is inherited honestly.

**Failure.** Signature: *false impossibility certificate* — relabelling a refusal caused by a repairable witness-local defect as proof that no witness can work (the faithful sID import was refuted on exactly this, 4/8 arms). Falsifiers (frozen with the incumbent mechanism): one false certificate where a licensing witness demonstrably exists kills it; never firing the strong verdict on genuinely impossible closed-world cases makes it vacuous; never differing from the naive relabelling makes the distinction empty.

## Known-answer test candidates

The incumbent's eight-arm design transfers directly: repairable role-map/boundary arms must yield `MERELY_UNLICENSED`; structural QoI/invariant/relation arms must yield `CERTIFIABLY_IMPOSSIBLE` with a certificate naming the failed criterion; open-world and budget-exhaustion arms must never produce the strong verdict.

## Not licensed

Natural-domain recovery of witnesses from prose, and any claim that witness verdicts correlate with downstream research utility, remain open empirical coordinates (the incumbent explicitly refuted two of its own instruments there).
