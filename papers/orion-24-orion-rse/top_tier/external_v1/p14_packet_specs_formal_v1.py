"""P14 external packet specifications - domain 1/3: FORMAL_COMBINATORICS_AND_ALGEBRA.

Deterministic data only (no clock, no network, no randomness at import).
All content is anonymized per the external governance protocol: no system
names, no terminal labels, no venue or artifact provenance that identifies
the originating programme. Numbers are carried over from preserved internal
records with identifiers renamed to generic codes.

Spec fields:
  family  - required scientific-state family (8 total across the suite)
  gold    - protected adjudication record value (never agent-visible)
  q       - the question put to the external system
  ev      - list of (role, content) evidence items; roles are
            PRIMARY/DONOR/CONTROL/PROTOCOL/RESULT/BACKGROUND
  dp      - preregistered decision points
  scope   - claim_language.max_scope
  forbid  - claim_language.forbidden_promotions
"""

DOMAIN = "FORMAL_COMBINATORICS_AND_ALGEBRA"

SPECS = [
    # ---------------- STRONG_PROMOTABLE (5) ----------------
    dict(
        family="STRONG_PROMOTABLE", gold="PROMOTE",
        q="A quasivariety-style fragment Q is claimed to satisfy a dichotomy: either every failure of the "
          "fragment's preservation property P has a two-element witness, or P is preserved under all "
          "direct products. Determine the strongest defensible action on this claim from the visible evidence.",
        ev=[
            ("PROTOCOL", "Statement frozen 14 days before any proof attempt; witness-size bound and product-preservation "
                         "conclusion both preregistered, with the two-element case declared the only admissible short certificate."),
            ("PRIMARY", "Proof manuscript (9 pp.): lemma chain (L1 embedding reduction, L2 canonical-diagram collapse, "
                        "L3 two-element normal form). Each lemma carries an explicit certificate obligation."),
            ("RESULT", "Independent mechanical certificate checker run C-2211: all 3 lemma obligations discharged, "
                       "412 proof steps, 0 gaps, checker hash 6f9c..., exit 0, run on an unmodified public checker build."),
            ("DONOR", "Classical quasivariety preservation theorem (donor D-K): gives the products direction for "
                      "universal classes only; does not give the two-element witness bound."),
            ("CONTROL", "Negative control: the analogous statement for the restricted fragment Q' is known false; "
                        "the manuscript's L2 step is shown to fail for Q' exactly where the witness grows."),
        ],
        dp=["certificate independently checked", "delta against donor D-K stated and material", "control case distinguished"],
        scope="the fragment Q as defined in the frozen statement",
        forbid=["extension to arbitrary universal fragments", "any claim about decidability not proven in the manuscript"],
    ),
    dict(
        family="STRONG_PROMOTABLE", gold="PROMOTE",
        q="An exact value 2n-3 (n>=7) is claimed for a combinatorial width parameter W, improving the known "
          "general bound 2n-1. Determine the strongest defensible action.",
        ev=[
            ("PROTOCOL", "Value, bound family, and n>=7 restriction frozen before construction; the 2n-2 case declared "
                         "in advance as the falsifier of any careless induction."),
            ("PRIMARY", "Matching construction: explicit family attaining 2n-3 with a verifiable witness listing for "
                        "n=7..12 (41, 82, 155, 293, 551, 1036 witnesses)."),
            ("RESULT", "Machine verification of all six witness listings against the parameter definition: 6/6 pass, "
                       "exhaustive for n=7 (state space 2^18 enumerated), certificate 88 KB."),
            ("DONOR", "Donor D-A: general upper bound 2n-1 by a greedy argument; no exact value known there."),
            ("CONTROL", "Independent re-derivation of the upper bound by a second method (LP relaxation of the "
                        "covering formulation) agrees at 2n-3 for n=7..12."),
        ],
        dp=["witness listings machine-verified", "exactness argument covers all n>=7", "donor delta is the exact value itself"],
        scope="the width parameter W on the family defined in the frozen statement",
        forbid=["transfer to the weighted variant W_w", "any asymptotic strengthening beyond 2n-3"],
    ),
    dict(
        family="STRONG_PROMOTABLE", gold="PROMOTE",
        q="A preservation theorem is claimed: a definable class closed under substructures and ultraproducts is "
          "claimed to admit a finite equational axiomatisation iff its complement is closed under subalgebras. "
          "Determine the strongest defensible action.",
        ev=[
            ("PROTOCOL", "Both directions preregistered; the 'only if' direction declared the risky half."),
            ("PRIMARY", "Proof (6 pp.): forward direction by a compactness transfer; reverse by an explicit "
                        "finite table construction with a rank function bounded by 2^k."),
            ("RESULT", "Certificate checker run C-2277: 2 obligations, 0 gaps; the rank-bound lemma machine-verified "
                       "for k<=4 and proven generally in the text."),
            ("DONOR", "Donor D-M: proves the forward direction for varieties; the finite-table reverse direction and "
                      "the complement closure formulation are absent there."),
            ("CONTROL", "Counterexample search over 2,341 small structures of size<=6: 0 violations found, consistent "
                        "with the theorem."),
        ],
        dp=["both directions certified", "donor delta covers the reverse direction", "search control consistent"],
        scope="elementary classes in the frozen signature",
        forbid=["application to second-order definable classes"],
    ),
    dict(
        family="STRONG_PROMOTABLE", gold="PROMOTE",
        q="A duality is claimed between two failure coordinates of a decision fragment: failure-by-nondefinability "
          "and failure-by-nonpreservation are claimed to be inter-reducible in linear time. Determine the strongest "
          "defensible action.",
        ev=[
            ("PROTOCOL", "The two failure coordinates and the linear-time budget frozen before construction."),
            ("PRIMARY", "Two explicit reductions R1, R2 with composed identity checked on normal forms; the "
                        "composition is shown to be the identity up to renaming."),
            ("RESULT", "Round-trip property machine-checked on 10,000 generated normal forms: 10,000/10,000 fixed, "
                       "max reduction depth 3, checker exit 0."),
            ("DONOR", "Donor D-T: states the two coordinates as separately measurable but gives no reduction either way."),
            ("CONTROL", "A third coordinate (failure-by-noncompactness) is shown NOT to reduce to the other two; "
                        "the claimed duality correctly excludes it."),
        ],
        dp=["round-trip identity certified", "excluded third coordinate verified as genuinely excluded", "donor delta stated"],
        scope="the decision fragment of the frozen statement",
        forbid=["claims about the third coordinate", "extension to fragments with function symbols of arity>2"],
    ),
    dict(
        family="STRONG_PROMOTABLE", gold="PROMOTE",
        q="Membership in a class C defined by a mixed quantifier fragment is claimed NL-complete (previously only "
          "the P upper bound was known). Determine the strongest defensible action.",
        ev=[
            ("PROTOCOL", "Both the NL upper bound and a hardness reduction were preregistered as necessary; either "
                         "alone declared insufficient at freeze time."),
            ("PRIMARY", "Upper bound: deterministic logarithmic-space certifier with one-way certificate tape. "
                        "Hardness: log-space reduction from directed reachability with 3-gadget local replacement."),
            ("RESULT", "Certifier implemented and run over 5,000 generated instances: all accepted instances verified "
                       "by an independent brute-force decider (n<=18), 0 disagreements; gadget replacement checked "
                       "edge-locally."),
            ("DONOR", "Donor D-R: P membership via a different dynamic program; no completeness claim."),
            ("CONTROL", "The unrestricted fragment (mixed + transitive closure) is shown to retain its known hardness; "
                        "the NL result does not leak upward."),
        ],
        dp=["upper and lower bounds both certified", "brute-force cross-check clean", "donor delta is the completeness"],
        scope="the mixed fragment without transitive closure",
        forbid=["any claim for the closure-enriched fragment"],
    ),

    # ---------------- APPARENT_POSITIVE_SUBSUMED (5) ----------------
    dict(
        family="APPARENT_POSITIVE_SUBSUMED", gold="SUBSUMED",
        q="A 'novel modular compactness transfer' is claimed: satisfiability of a finite module-theoretic signature "
          "set transfers to a filtered colimit. Determine the strongest defensible action.",
        ev=[
            ("PROTOCOL", "Transfer statement frozen; novelty of the mechanism declared the claim to be evaluated."),
            ("PRIMARY", "Proof (3 pp.): ultraproduct construction plus a Los-style transfer step for the finite signature set."),
            ("RESULT", "Internal review notes the proof is correct."),
            ("DONOR", "Donor D-B (classical, predating the programme by decades): compactness plus the Los lemma give "
                      "exactly this transfer for arbitrary signature sets; the finite restriction is a special case."),
            ("BACKGROUND", "A citable textbook statement (donor D-B, ch. 4) contains the claim verbatim for the more "
                           "general case."),
        ],
        dp=["mechanism-level comparison against donor D-B", "any residual delta isolated", "decision recorded"],
        scope="the finite-signature special case only",
        forbid=["presenting the transfer as new", "claiming the general case as a contribution"],
    ),
    dict(
        family="APPARENT_POSITIVE_SUBSUMED", gold="SUBSUMED",
        q="A claimed-new lattice characterisation of a closure system is proposed: closed sets are exactly the "
          "sets closed under a specified meet-chain condition. Determine the strongest defensible action.",
        ev=[
            ("PROTOCOL", "Characterisation statement frozen."),
            ("PRIMARY", "Proof (4 pp.) of both inclusions via Moore-closure composition."),
            ("RESULT", "Both inclusions verified on 3 example lattices (M3, N5, and a 32-element lattice)."),
            ("DONOR", "Donor D-C: HSP-style theorem already characterises the same closed sets as the subalgebra-closure "
                      "of a generating family; the meet-chain condition is a re-expression."),
        ],
        dp=["isomorphism of the two characterisations checked", "residual delta isolated", "decision recorded"],
        scope="finite lattices",
        forbid=["claiming first characterisation of the closed sets"],
    ),
    dict(
        family="APPARENT_POSITIVE_SUBSUMED", gold="SUBSUMED",
        q="A new invariant I(G) for a class of rewriting systems is proposed with a claimed novel monotonicity "
          "property under rule addition. Determine the strongest defensible action.",
        ev=[
            ("PROTOCOL", "Invariant definition and monotonicity statement frozen."),
            ("PRIMARY", "Definition of I(G) plus a monotonicity proof by induction on rule additions."),
            ("RESULT", "Monotonicity checked computationally on 240 random systems of size<=9: 240/240 monotone."),
            ("DONOR", "Donor D-G: the degree invariant of a related basis (the 'height polynomial') is pointwise equal "
                      "to I(G) on all 240 systems and its monotonicity is classical."),
            ("CONTROL", "The two invariants were compared only after both were defined; comparison code is independent."),
        ],
        dp=["pointwise equality with the donor invariant established", "novelty deficit recorded", "decision recorded"],
        scope="terminating rewriting systems",
        forbid=["claiming the invariant as new", "claiming the monotonicity as new"],
    ),
    dict(
        family="APPARENT_POSITIVE_SUBSUMED", gold="SUBSUMED",
        q="A 'new' closure operator is proposed for separating two definable classes, built by composing two known "
          "operators. Determine the strongest defensible action.",
        ev=[
            ("PROTOCOL", "Operator definition frozen."),
            ("PRIMARY", "The operator is defined as the composition of two classical closure operators with an "
                        "idempotence proof."),
            ("RESULT", "Idempotence verified on 512 sampled sets."),
            ("DONOR", "Donor D-H: composition closure of Moore families is classical; the exact composed operator "
                      "appears as an exercise with solution."),
        ],
        dp=["composed-operator identity against donor established", "residual delta isolated", "decision recorded"],
        scope="finite ground sets",
        forbid=["claiming the operator as a new primitive"],
    ),
    dict(
        family="APPARENT_POSITIVE_SUBSUMED", gold="SUBSUMED",
        q="A quantitative interpolation bound c*n is claimed as new for a modal fragment, with experiments "
          "suggesting c=3. Determine the strongest defensible action.",
        ev=[
            ("PROTOCOL", "The interpolation constant and fragment frozen."),
            ("PRIMARY", "Construction showing 3n labels always suffice, with a 2n lower-bound example."),
            ("RESULT", "Sufficiency machine-checked on generated formulas up to depth 6."),
            ("DONOR", "Donor D-J: a quantitative Craig-style interpolation theorem for the same fragment already "
                      "yields 3n exactly; the lower-bound example also appears there."),
        ],
        dp=["constant matched against donor bound", "residual delta isolated", "decision recorded"],
        scope="the frozen modal fragment",
        forbid=["claiming first quantitative bound for the fragment"],
    ),

    # ---------------- INTERACTION_ONLY (2) ----------------
    dict(
        family="INTERACTION_ONLY", gold="INTERACTION_ONLY",
        q="Shorter certificates are claimed for a decision fragment when a normal-form transformation T1 and an "
          "ordering heuristic O2 are both applied. Determine the strongest defensible action.",
        ev=[
            ("PROTOCOL", "Four-arm design frozen: {none, T1, O2, T1+O2}; interaction declared the estimand, "
                         "not the marginal."),
            ("RESULT", "Mean certificate length over 1,000 held-out instances: none 412.3, T1-only 409.1 (-0.8%, "
                       "bootstrap CI [-2.1, +0.6], includes 0), O2-only 411.0 (-0.3%, CI [-1.8, +1.2], includes 0), "
                       "T1+O2 355.6 (-13.7%, CI [-15.9, -11.4], excludes 0)."),
            ("CONTROL", "Shuffle-null with equal arm sizes: interaction effect 0.0 +- 0.9% (z=15.2 for the observed)."),
            ("BACKGROUND", "Neither component's mechanism alone predicts the compression; the gain arises from "
                           "O2 exploiting a block structure that only T1 exposes."),
        ],
        dp=["both marginals quantified", "interaction separated from marginals", "shuffle control run"],
        scope="the four-arm suite as frozen",
        forbid=["crediting either component alone", "claiming a main effect"],
    ),
    dict(
        family="INTERACTION_ONLY", gold="INTERACTION_ONLY",
        q="A proof-search depth reduction is claimed for a combination of a restart strategy R3 and a lemma-ordering "
          "L4. Determine the strongest defensible action.",
        ev=[
            ("PROTOCOL", "Two-by-two factorial frozen; depth reduction declared the estimand."),
            ("RESULT", "Median search depth on 400 problems: none 88, R3-only 87 (p=0.71), L4-only 88 (p=0.83), "
                       "R3+L4 61 (p<1e-6, paired)."),
            ("CONTROL", "On a problem class without lemma structure, the combination shows no gain (median 92 vs 92, "
                        "p=0.44), locating the interaction in the lemma structure."),
        ],
        dp=["factorial completed", "interaction located in a mechanism", "null class identified"],
        scope="problems with lemma structure",
        forbid=["recommending R3 or L4 as standalone improvements"],
    ),

    # ---------------- NULL_LIVE_PARENT (2) ----------------
    dict(
        family="NULL_LIVE_PARENT", gold="NULL_LIVE",
        q="A known representation theorem (parent result, reproduced here with a new proof) is claimed to admit an "
          "algorithmic strengthening: deciding membership in the represented class asymptotically faster. Determine "
          "the strongest defensible action.",
        ev=[
            ("PROTOCOL", "Parent theorem reproduction and the strengthening declared separately at freeze; the "
                         "strengthening requires a super-constant speedup on the standard witness family."),
            ("RESULT", "New proof of the parent theorem verified (all 4 obligations). Strengthening: measured speedup "
                       "on the witness family is 1.04x-1.11x across n=2^8..2^16, best-fit exponent difference 0.013 "
                       "(CI [-0.031, +0.057], includes 0)."),
            ("CONTROL", "Any-constant-factor null declared the falsifier at freeze; observed factors sit inside the "
                        "constant regime."),
            ("BACKGROUND", "The parent theorem itself is not in question; only the claimed strengthening is."),
        ],
        dp=["parent and strengthening scored separately", "speedup exponent tested against the constant regime", "null recorded as the strengthening's outcome only"],
        scope="the strengthening only",
        forbid=["recording a null against the parent theorem", "claiming the speedup"],
    ),
    dict(
        family="NULL_LIVE_PARENT", gold="NULL_LIVE",
        q="A live counting formula (parent) is claimed to extend to a two-parameter refinement with a predicted "
          "interaction term. Determine the strongest defensible action.",
        ev=[
            ("PROTOCOL", "Parent formula re-validated and the refinement's interaction term preregistered with a "
                         "minimum detectable effect of 5%."),
            ("RESULT", "Parent formula re-validated on 10,000 fresh samples (0 violations). Refinement: fitted "
                       "interaction coefficient 0.0004 (CI [-0.0021, +0.0029], includes 0); the predicted 7-9% "
                       "interaction is excluded."),
            ("CONTROL", "Power check: the design detects the preregistered 5% effect with probability 0.94; the null "
                        "is informative, not underpowered."),
        ],
        dp=["parent separated from refinement", "power stated", "null recorded for the refinement only"],
        scope="the two-parameter refinement",
        forbid=["recording a null against the parent formula"],
    ),

    # ---------------- NEGATIVE_RETAINED (3) ----------------
    dict(
        family="NEGATIVE_RETAINED", gold="NEGATIVE",
        q="Conjecture: every P-definable class closed under substructures admits a finite axiomatisation. "
          "Determine the strongest defensible action.",
        ev=[
            ("PROTOCOL", "Conjecture frozen; a single explicit counterexample declared sufficient to close it negative."),
            ("PRIMARY", "Construction of an infinite antichain A_1 < A_2 < ... of P-definable, substructure-closed "
                        "structures whose union is not finitely axiomatisable; the first three members written out."),
            ("RESULT", "The antichain property machine-verified for the first 6 members (certificate 14 KB, checker exit 0); "
                       "the general construction is proven in the text."),
            ("BACKGROUND", "The conjecture had been used as an assumption in two downstream notes; both are marked "
                           "affected and their conclusions withdrawn in the same record."),
        ],
        dp=["counterexample certified", "downstream usage traced and withdrawn", "negative retained as evidence"],
        scope="the frozen conjecture",
        forbid=["reviving the conjecture", "blaming the verification rather than the conjecture"],
    ),
    dict(
        family="NEGATIVE_RETAINED", gold="NEGATIVE",
        q="A claimed fixed-parameter tractability for a matching parameter k is asserted with a sketch. Determine "
          "the strongest defensible action.",
        ev=[
            ("PROTOCOL", "FPT claim frozen with an explicit algorithm-or-reduction obligation."),
            ("PRIMARY", "The sketch's branching step is shown to require exploring Omega(n^k) configurations: a "
                        "family of instances where every branch differs."),
            ("RESULT", "Reduction from k-Clique: 5-gadget local replacement, verified edge-locally on generated "
                       "instances (1,000/1,000 correct); under the standard assumption this closes the claim negative."),
            ("CONTROL", "The reduction composed with a known solver preserves solution correspondence exactly."),
        ],
        dp=["hardness reduction certified", "conditional nature of the assumption stated", "negative retained"],
        scope="the frozen parameterisation",
        forbid=["publishing the FPT sketch", "re-running the same construction as new evidence"],
    ),
    dict(
        family="NEGATIVE_RETAINED", gold="NEGATIVE",
        q="Decidability is claimed for a mixed first-order fragment with a transitive predicate. Determine the "
          "strongest defensible action.",
        ev=[
            ("PROTOCOL", "Decidability claim frozen; undecidability declared the closing route."),
            ("PRIMARY", "Reduction from the tiling problem: configurations encoded as elements, tiling constraints "
                        "as a two-formula scheme in the fragment."),
            ("RESULT", "The two formulas verified to enforce horizontal and vertical tiling on 512 random 6x6 grids "
                       "(512/512 forced-correct); the reduction is proven in the text."),
            ("BACKGROUND", "A prior decidability sketch relied on a finite-model property that the transitive "
                           "predicate destroys; the destruction is exhibited explicitly."),
        ],
        dp=["undecidability reduction certified", "prior sketch's failed assumption identified", "negative retained"],
        scope="the frozen fragment with transitivity",
        forbid=["claiming decidability", "weakening the fragment silently to recover decidability"],
    ),

    # ---------------- LEAKY_OR_CORRUPT_BENCHMARK (2) ----------------
    dict(
        family="LEAKY_OR_CORRUPT_BENCHMARK", gold="NEGATIVE",
        q="A benchmark suite of 300 'hard' algebras is offered as evidence that a new decision method dominates. "
          "Determine the strongest defensible action.",
        ev=[
            ("PROTOCOL", "Benchmark construction code and labels frozen before any method comparison."),
            ("RESULT", "Reported: new method 96.7% vs strongest public baseline 61.3%."),
            ("CONTROL", "Post-hoc audit artifact: a degenerate invariant (parity of the generator count) classifies "
                        "294/300 instances exactly; a trivial parity-only classifier scores 98.0%."),
            ("BACKGROUND", "The suite's generator drew instances from two disjoint families with parity-aligned "
                           "labels, so label information is recoverable without any algebra."),
        ],
        dp=["audit of label recoverability from degenerate features", "dominance re-stated or withdrawn", "decision recorded"],
        scope="the frozen benchmark suite only",
        forbid=["using the 96.7%-vs-61.3% comparison as evidence of method superiority"],
    ),
    dict(
        family="LEAKY_OR_CORRUPT_BENCHMARK", gold="NEGATIVE",
        q="A certificate checker is offered as the verification oracle for a family of structural claims; 100% of "
          "claims are reported verified. Determine the strongest defensible action.",
        ev=[
            ("PROTOCOL", "Checker version frozen; claims submitted for verification."),
            ("RESULT", "Checker output: 4,317/4,317 claims accepted."),
            ("CONTROL", "Adversarial probe: an empty-conjunction witness (vacuously true obligation set) and a "
                        "circularly-defined obligation are both ACCEPTED by the same checker version (probe "
                        "transcript attached)."),
            ("BACKGROUND", "The checker's acceptance path does not require the witness to mention the goal formula."),
        ],
        dp=["vacuity and circularity probes run", "checker acceptance semantics repaired or oracle replaced", "decision recorded"],
        scope="the checker version identified in the freeze",
        forbid=["counting any acceptance by the unrepaired checker as verification"],
    ),

    # ---------------- NON_IDENTIFIABLE (2) ----------------
    dict(
        family="NON_IDENTIFIABLE", gold="NON_IDENTIFIABLE",
        q="A claimed conservation law for a rewriting calculus is offered with a proof that relies on a "
          "set-theoretic principle independent of the working foundations. Determine the strongest defensible action.",
        ev=[
            ("PROTOCOL", "Working foundations frozen; any dependence outside them declared a non-identifiability."),
            ("PRIMARY", "The proof's key lemma is shown equivalent (in both directions) to a weak choice principle "
                        "known to be independent of the frozen foundations; both the derivation and its converse "
                        "are given."),
            ("RESULT", "With the principle added, the law holds; with its negation, a countermodel exists. Both "
                       "constructions written out and checked."),
            ("CONTROL", "A restricted version of the law provable without the principle is isolated and holds "
                        "unconditionally."),
        ],
        dp=["equivalence-with-independent-principle certified", "restricted unconditional version isolated", "decision recorded"],
        scope="the unrestricted law under the frozen foundations",
        forbid=["claiming the law unconditionally"],
    ),
    dict(
        family="NON_IDENTIFIABLE", gold="CANNOT_CHECK",
        q="A structure theorem is submitted whose proof appeals to an external lemma attributed to an out-of-scope "
          "manuscript; no statement, proof, or certificate for that lemma is present. Determine the strongest "
          "defensible action.",
        ev=[
            ("PROTOCOL", "Freeze requires every external appeal to carry a checkable statement plus proof or certificate."),
            ("PRIMARY", "The submitted proof cites 'Lemma W (external manuscript)' at its central step; the citation "
                        "gives no statement text."),
            ("RESULT", "No artifact in the supplied evidence states Lemma W's content; a proof search over the "
                       "visible corpus returns no candidate statement."),
            ("CONTROL", "Two candidate readings of the missing lemma are exhibited; one makes the theorem true, the "
                        "other false - so the visible evidence cannot discriminate."),
        ],
        dp=["external appeal statement recovered or reconstructed", "discriminating artifact obtained", "decision recorded"],
        scope="the theorem as submitted",
        forbid=["treating the unverified appeal as discharged", "scoring the theorem on its plausibility"],
    ),

    # ---------------- REGIME_CHANGE_REOPEN (2, longitudinal pair) ----------------
    dict(
        family="REGIME_CHANGE_REOPEN", gold="REOPEN", round_no=1,
        q="A search-depth conjecture is evaluated: exhaustive checking to depth 100 over 10^5 generated instances "
          "reports no counterexample. Determine the strongest defensible action at this round.",
        ev=[
            ("PROTOCOL", "Longitudinal design frozen: the same claim is to be re-evaluated under a preregistered "
                         "budget escalation; a round-2 regime change is scheduled."),
            ("RESULT", "Round 1 (budget: depth 100, 10^5 instances): 0 counterexamples; depth-100 exhaustion "
                       "certificate 22 MB."),
            ("CONTROL", "Instrumentation check: the generator's coverage of deep witnesses is confirmed at shallow "
                        "depths by seeding 50 known counterexamples of depth<=40 (50/50 found)."),
            ("BACKGROUND", "The conjecture's failure modes, if any, are predicted to live at depth >= 300 by the "
                           "round-1 analysis itself."),
        ],
        dp=["round-1 exhaustion certified", "scheduled regime change acknowledged", "no terminal action taken on round-1 evidence alone"],
        scope="depth<=100",
        forbid=["closing the conjecture on the depth-100 round"],
    ),
    dict(
        family="REGIME_CHANGE_REOPEN", gold="REOPEN", round_no=2,
        q="Round 2 of the depth conjecture: the preregistered budget escalation to depth 400 is executed. Determine "
          "the strongest defensible action.",
        ev=[
            ("PROTOCOL", "Round-2 budget (depth 400, 10^7 instances) frozen in the same document as round 1, before "
                         "either round ran."),
            ("RESULT", "Round 2: counterexample found at depth 317 (instance I-317-44, witness 2.1 KB, independently "
                       "re-verified by the frozen checker; exit 0)."),
            ("RESULT", "Round 1's certificate remains valid for its scope: the exhaustion is real but its scope was "
                       "depth<=100."),
            ("CONTROL", "The depth-317 instance re-run under the round-1 budget confirms it is outside that budget's "
                        "search space (not reachable in 10^5 draws, seed scan attached)."),
        ],
        dp=["round-2 counterexample certified against round-1 protocol", "scope consistency verified", "prior round's record amended, not deleted"],
        scope="depth<=400",
        forbid=["deleting the round-1 record", "treating round 2 as a new claim"],
    ),
]

assert len(SPECS) == 23, len(SPECS)
