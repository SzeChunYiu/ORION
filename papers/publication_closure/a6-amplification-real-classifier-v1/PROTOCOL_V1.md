# A6 amplification attack, encoded against ORION-16's real transition audit

**Status at time of writing:** `PROTOCOL_FROZEN__NOT_YET_RUN`
**Scientific authority delta:** `NONE`. This checks a property of a classifier. It
proves nothing about the world and nothing about the papers' published claims.

`IMPLEMENTATION_GAP_V1.md` recorded that the previous amplification check ran against a
model I wrote myself, which is the weakest possible target — I could have shaped it to
lose. This protocol removes that objection by running the attack against
`papers/orion-16-formal-epistemic-structures-and-mechanics/top_tier/check_real_transition_audit_independent_v1.py`,
imported by path, never copied.

Subject file sha256: `698f49ca952f59ec015ff50aafec9f78a44c4a17481723dcede4a3b5e4c8c4db`

## The target property

From `A6_COMPOSITION_ROUTE_V1.md`:

> Selective revalidation is not an authority-amplification channel: repair cannot promote
> `CANNOT_CHECK` to `AUTHORIZED` without new protected evidence.

ORION-16's `classify()` decides over eight booleans and returns one of `CANNOT_CHECK`,
`DENIED`, `REOPEN`, `ADMISSIBLE`. `ADMISSIBLE` is the local analogue of `AUTHORIZED`.

## The attack, restated for this state space

`A6_AMPLIFICATION_COUNTEREXAMPLE_V1.md` argues that repair may re-ground a claim in a
domain whose obligations are vacuous, so that requirements are satisfied by *absence*
rather than by discharge. In this eight-coordinate space, exactly three coordinates are
vacuously satisfiable that way:

```
VACUOUS = {evidence_transport_known, evidence_transport_valid, obligations_clear}
```

`evidence_transport_*` is vacuously true when the re-derivation transports no evidence.
`obligations_clear` is vacuously true when `O_h = ∅`.

The other five are not. `execution_support`, `provenance_binding` and `source_current`
name facts about the artifact; `generic_permission` and `commit_authority` name grants.
Neither class can be conjured by choosing a different derivation route.

**Attack definition.** An *amplifying edge* is an ordered pair of states `(s, s')` with
`classify(s) = CANNOT_CHECK`, `classify(s') = ADMISSIBLE`, and `s' \ s` consisting only of
`False -> True` flips inside `VACUOUS`.

## Method

1. Import the real `classify` by file path. Record the subject file's sha256 at run time
   and fail closed if it differs from the value above.
2. Enumerate all 2^8 = 256 states. Report every amplifying edge.
3. Report the complement: promotion edges that require flipping a coordinate outside
   `VACUOUS`. These are the legitimate repairs.
4. Run five controls, each of which must land as stated or the run is void.
5. Check whether the 24 real cases in `p6_real_transition_cases_v1.json` realize any
   amplifying edge.

## Controls, pre-declared

| id | construction | required verdict | what it rules out |
|----|--------------|------------------|-------------------|
| `C-NULL` | no flip applied | stays `CANNOT_CHECK` | promotion reported where none occurred |
| `C-DENY` | attack applied with `generic_permission=False` | `DENIED` | the attack being unconditional |
| `C-REOPEN` | attack applied but `obligations_clear=False` | `REOPEN` | vacuity being unnecessary |
| `C-OUTER` | attack applied with `source_current=False` | `CANNOT_CHECK` | the attack reaching the outer unknown layer |
| `C-LEGIT` | same delta, evidence genuinely supplied | `ADMISSIBLE` | the checker detecting the attack rather than the delta |

`C-LEGIT` is the control that decides how this result must be *read*. It applies the same
coordinate change with a different cause. If it also reaches `ADMISSIBLE` — and it will,
because the classifier sees only the coordinates — then the finding is not "the classifier
is wrong". It is that **the state space has no coordinate recording why a flag became
true**, so an attack and a legitimate repair are indistinguishable to it.

## Prediction, recorded before running

Written now so it cannot be adjusted afterwards:

1. Amplifying edges exist. The attack lands.
2. `C-OUTER` holds: no amplifying edge starts from a state where `execution_support`,
   `provenance_binding` or `source_current` is false. The outer `CANNOT_CHECK` layer is
   already amplification-resistant; only the inner one is exposed.
3. `C-LEGIT` reaches `ADMISSIBLE`, making the finding one about vocabulary, not about a
   classification error.
4. No pair among the 24 real cases realizes an amplifying edge, because the case set was
   built to exercise families, not adjacency.

If (1) fails the counterexample dies against the real classifier and the composed claim
survives, which is the better outcome for the papers.

## What this cannot show

- It cannot show ORION-16 claims non-amplification. It does not; that is the gap.
- It cannot show any real transition was so promoted. Step 5 asks, and absence there is
  absence of a witness, not proof of safety.
- The mapping of "re-grounding" onto those three coordinates is an interpretation of the
  papers' definitions, argued in the counterexample document. It is not proved, and it is
  the load-bearing assumption of the whole result.
