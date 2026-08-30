# ORION18.AUTHORITY_CUT_IDENTIFIABILITY.v1

## Question

Can repository-internal evidence, by itself, certify that the scientific adjudication which produced it was institutionally independent of the programme being adjudicated?

## Definitions

Let a possible world `w` carry:

- an internal observable transcript `O(w)` containing every repository-visible receipt, signature, replay, mechanized proof, test result and internal reviewer output available to the programme;
- an independence predicate `I(w) in {0,1}`, where `I(w)=1` means the decisive adjudicator/custodian lies outside the programme's relevant control-principal closure.

An **internal independence certifier** is any function `f` whose input is only `O(w)` and whose intended output is `I(w)`.

A **control cut** is the boundary of the programme's control-principal closure. An evidence path crosses the cut only when some load-bearing observation or decision is produced under a governance principal whose relevant control is not reducible to the programme's principals.

## Theorem 1 — mixed-fibre non-identifiability

There exists a correct certifier `f(O(w)) = I(w)` on a world class `W` **iff** `I` is constant on every fibre of `O`.

Equivalently, if there are worlds `w_ind, w_coord` such that

`O(w_ind) = O(w_coord)` but `I(w_ind) != I(w_coord)`,

then no rule using only the internal transcript can correctly certify independence on both worlds.

### Proof

If `I` is constant on each observable fibre, define `f(o)` to be that common value. Conversely, if one fibre contains both labels, any single value `f(o)` is wrong on at least one member of that fibre. QED.

This is an identifiability result, not a probabilistic assumption and not a claim about the honesty of any particular participant.

## Theorem 2 — the internal-control-cut obstruction

Suppose every load-bearing producer, checker, signer, replay service and adjudicator that determines the transcript lies inside one programme control-principal closure, and the transcript contains no independently authenticated fact about governance outside that closure. Then institutional independence is not identifiable from the transcript alone whenever the admissible world class permits both:

1. an independent world in which the visible artifacts are produced as recorded; and
2. a coordinated world in which the same bytes and decisions are produced under common control.

### Proof

Construct the two worlds to agree on every mechanism that writes `O`: source bytes, keys, outputs, timings allowed by the transcript, decisions, proofs and receipts. Change only the governance relation that says whether the decisive principal is outside the programme closure. By hypothesis that relation is not independently observed in `O`, so the transcripts are equal while `I` differs. Theorem 1 applies. QED.

## Corollary 2.1 — more internal replicas do not close the cut

Adding implementation-independent checkers, internal agents, additional programme-controlled keys, or deterministic replays can strengthen correctness and tamper evidence, but cannot by multiplicity alone identify institutional independence if every new evidence path remains inside the same control cut.

## Corollary 2.2 — an exogenous edge is necessary, not sufficient

To make institutional independence identifiable, the evidence interface must contain at least one load-bearing fact whose provenance crosses the control cut—for example independently governed custody, adjudication or challenge authority with an authenticated identity and conflict rule. Crossing the cut is **necessary** for the broad independence claim under this model; it is not sufficient for scientific correctness, expertise, absence of conflict, or validity of the adjudication.

## Relation to the current ORION-18 evidence

The current paper already earns substantial bounded authority: the composition operator has an exact reduced-state audit; wrong operators are discriminated; and a separate 20-case real-domain study reports zero false scientific promotions with a second implementation. None of those results is weakened here.

This theorem explains a different ceiling. Programme-internal mechanization and replay can establish properties of the calculus and of the recorded study, but cannot self-certify the governance fact required by a broad autonomous-science authority claim when that fact is outside the internal observable sigma-algebra.

## Sharp claim boundary

Earned deductive claim:

> Institutional independence is not identifiable from a transcript whose observable fibres conflate independent and commonly controlled governance worlds; therefore a broad independence claim requires a load-bearing exogenous governance observation.

Not earned:

- that any current ORION-18 actor is coordinated or conflicted;
- that an external institution will agree with ORION-18;
- that external review is automatically correct;
- population-level autonomous-science authority.

`scientific_authority_delta: NONE`

This theorem converts an external-authority blocker into an exact information boundary. It does not manufacture the missing external evidence.