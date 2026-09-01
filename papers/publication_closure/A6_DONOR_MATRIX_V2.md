# A6 Phase 1 — donor matrix V2

**Status:** `REQUIRED_FIELDS_COVERED__DONOR_SUBTRACTION_ONLY`
**Date:** 2026-09-01
**Scientific authority delta:** `NONE`.  This matrix can only narrow novelty.

This supersedes the *field coverage* of the first-pass donor discussion in
`A6_DONOR_SUBTRACTION_V1.md`; it does not erase its result-by-result analysis or
the later adversarial downgrades.  The point of V2 is to make every donor field
required by Tier-A issue #49 explicit, including the two fields that were only
implicit before: proof-carrying action/authorization and assurance cases.

| Required donor field | Primary donor objects checked | What the donor already supplies | A6 consequence |
|---|---|---|---|
| authorization / delegation logics | Abadi, Burrows, Lampson & Plotkin, *A Calculus for Access Control in Distributed Systems*, TOPLAS 15 (1993), 706–734; Appel & Felten, *Proof-Carrying Authentication*, CCS 1999, DOI 10.1145/319709.319718 | principals, delegation/on-behalf-of reasoning, logical authorization, client-supplied authorization proofs | Generic permission/delegation and “proof justifies request” are donor. A6 can only own constraints introduced by combining repair/change with these authority semantics. |
| provenance algebras | Green, Karvounarakis & Tannen, *Provenance Semirings*, PODS 2007, DOI 10.1145/1265530.1265535; W3C PROV-O Recommendation, 30 Apr 2013 | algebraic lineage/why-provenance; interoperable entities/activities/agents and derivation relations | Lineage, support propagation and provenance binding are donor. A6 must not call a provenance graph or support algebra new merely because it is used for scientific certificates. |
| TMS / ATMS / belief revision | Doyle, *A truth maintenance system*, Artificial Intelligence 12 (1979), DOI 10.1016/0004-3702(79)90008-0; de Kleer, *An assumption-based TMS*, Artificial Intelligence 28 (1986), DOI 10.1016/0004-3702(86)90080-9; Alchourrón, Gärdenfors & Makinson, *On the Logic of Theory Change*, JSL 50 (1985) | dependency-based belief maintenance, assumption environments, retraction/contraction/revision | ORION-16 root/descendant reopening and ORION-18 retraction/non-monotonicity are donor or specialisation. The possible contribution must live at the authority consequences of a repair, not repair/retraction itself. |
| proof-carrying action / authorization | Necula, *Proof-Carrying Code*, POPL 1997, DOI 10.1145/263699.263712; Bauer, Schneider & Felten, *A Proof-Carrying Authorization System*, Princeton TR-638-01 (2001); Bauer, Schneider & Felten, *A General and Flexible Access-Control System for the Web*, USENIX Security 2002 | untrusted producer/client supplies a proof; consumer checks a simpler proof against a policy; distributed policy components can be assembled into an authorization proof | “A certificate/proof accompanies an action” is donor. A6’s composed question is narrower: whether **repair-generated replacement certificates can amplify authority without a fresh authority-bearing premise**. |
| typed effects / capabilities | Morrisett, Walker, Crary & Glew, *From System F to Typed Assembly Language*, POPL 1998, DOI 10.1145/268946.268954; Crary, Walker & Morrisett, *Typed Memory Management in a Calculus of Capabilities*, POPL 1999 | types/capabilities constrain which low-level operations/resources are available; safety follows from checked typing/capability premises | Typed scopes, effect separation and capability restrictions are donor mechanisms. Domain/epoch confinement may be expressed with these mechanisms but is not novel merely because it is typed. |
| assurance cases | Kelly & Weaver, *The Goal Structuring Notation — A Safety Argument Notation*; SEI, *Toward a Theory of Assurance Case* (2012) | structured claims, arguments, assumptions/context and supporting evidence; explicit argument/evidence dependency | Claim→evidence argument structure and evidence custody are donor. A6 must distinguish a machine-checkable certificate/authority semantics from an assurance-case presentation, and must not treat a well-structured case as proof that its premises are true. |

## Result-level disposition after donor subtraction

The controlling tally is the adversarially revised one from
`A6_REMAINING_CANDIDATES_ADVERSARIAL_V1.md`, not the earlier provisional tally:

| disposition | count | interpretation |
|---|---:|---|
| `DONOR` | 6 | the result is already a standard donor fact/pattern at the relevant level |
| `SPECIALIZATION` | 5 | a donor fact instantiated to this certificate/authority setting |
| `SURVIVING_NEW_CONSEQUENCE` | 1 | ORION-18 Proposition 14 clause 2 remains the only paper-local provisional survivor after the current donor attacks |

The composed repair→authority object in `A6_MERGED_THEOREM_OBJECT_V1.md` is **not**
added to that twelve-result tally.  It is a new cross-paper object and must be
judged separately: the independent formalization can establish internal
consistency/countermodels, but novelty remains subject to primary-source review.

## Atomic donor-substitution rule

For every theorem or proposition in a merged paper:

1. replace paper-specific nouns with the standard objects in the first column;
2. insert the strongest donor theorem that applies;
3. classify the residue as `DONOR`, `SPECIALIZATION`, or
   `SURVIVING_NEW_CONSEQUENCE`;
4. if the residue disappears, do not recover novelty by renaming the donor
   object or by appealing to mechanization;
5. if the residue survives only in the composition of two donor mechanisms,
   state exactly the cross-mechanism invariant/counterexample and test that
   composition directly.

## Boundary

This is a donor matrix, not an exhaustive priority certificate.  A later source
that states the composed repair/non-amplification result directly would narrow
or eliminate the surviving claim; the matrix must be updated rather than the
claim defended by terminology.
