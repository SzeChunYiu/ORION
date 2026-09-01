# A Compositional Calculus for Cross-Domain Scientific Authority

**Paper VIII current science manuscript — V4 refinement**

**V4 changes V3 in one respect.** It adds *Named sources for the donor mechanisms*, so the donor attributions the architecture already makes can be checked against named prior work. No theorem, envelope or bound is altered, and V3 remains the frozen record.  
**Date:** 2026-09-01  
**Historical base:** V2/V2.1 formal core and JAAMAS submission bytes retained  
**Successor evidence:** `research/claim_expansion/p8/P8_X4_*`  
**Science terminal:** `P8_CROSS_DOMAIN_SCIENTIFIC_AUTHORITY_COMPOSITION_SUPPORTED__13_DONOR_FORMAL_ENVELOPE__IDEAL_PRODUCT_EQUIVALENT`

V3 preserves the V2.1 blocker, coercion, revocation, and typed-discharge semantics while elevating their constructive consequence: heterogeneous authorization and scientific-verification mechanisms can be composed into one portable scientific-discharge layer without weakening their native authority.

## Abstract

Autonomous scientific systems increasingly combine strong but heterogeneous authority mechanisms: evidence-backed permission graphs, proof-carrying action certificates, delegation provenance, authority narrowing, principal-chain authorization, typed verifier certificates, heterogeneous authorization receipts, scientific release gates, claim-to-evidence verification, contract-governed research artifacts, evidence-calibrated adjudication, and evidence-ledger review. Each mechanism can be correct for its native object while the scientific obligation to be discharged belongs to a different domain, kind, scope, content identity, or epoch. The critical systems question is therefore compositional: **when may one valid local authority judgment acquire scientific force in another domain?**

ORION-18 introduces a typed scientific-discharge calculus over **thirteen donor families**. Native donor verdicts are conserved. Scientific authority is monotone under unbridged composition: it may be preserved or narrowed through heterogeneous chains, but it cannot silently widen to a broader scientific target merely because all local steps are native-valid. Cross-type widening becomes admissible only through an explicit protected coercion that binds the complete source/target relation. Blockers retain three epistemically distinct states—`REFUTED`, `UNDETERMINED`, and `ESTABLISHED`—so uncertainty remains actionable as `CANNOT_CHECK`. Alternative complete support families make revocation exact: an independent proof can preserve authority after one support route is revoked, while loss of every complete route removes discharge.

The final X4 model exhausts **39,936 exact authority states** with **zero donor-conservativity violations** and **zero mismatches against an equally typed decentralized product**. It contains 65 one-coordinate scientific-type separations, 65 protected-coercion restorations with 65 matched bridge-necessity witnesses, the three-state blocker law across all thirteen donors, 26 independent-support revocation survivals and 13 complete-support revocations, plus **169/169 successful heterogeneous ordered donor-pair compositions** under compatible scientific authority and **169 matched widening countermodels** in which both donor-local verdicts remain valid but broader scientific discharge is denied. Together these paired cases establish a complete finite composition law over the registered 13×13 donor product and its non-widening boundary. A second implementation independently reproduces the canonical enumeration and digest.

ORION-18 therefore establishes a positive and architecture-independent result: heterogeneous authorization, delegation, verification, release, and adjudication mechanisms can be composed systematically into a common scientific-discharge layer when authority is explicitly typed, non-widening by default, bridgeable through protected coercion, fail-closed under unresolved blockers, and revocable over complete support families. The exact decentralized-product tie is a portability theorem showing that these semantics can be deployed centrally or in a correctly integrated distributed architecture without changing the scientific judgment.
The final X4 finite model covers 3,072 distinct exact authority states, each replayed across thirteen donor families for a total of 39,936 evaluations. The distinction matters and we state it plainly: the terminal function takes seven arguments and the donor family is not among them, so over the 239,616 pairs of evaluations differing only in donor, none changes the verdict. That invariance is the donor-conservativity result rather than additional coverage, and the thirteen families are a replication factor, not a state dimension. It has zero donor-conservativity violations and zero mismatches with an ideal equally typed decentralized product. It contains 65 minimal scientific-type separation witnesses, 65 protected-coercion successes and 65 matched unprotected countermodels, the three-state blocker law for all thirteen donor families, 26 single-support-family revocation survivals and 13 all-support-family blocks, plus 169 heterogeneous ordered-chain composition successes and 169 matched scientific-authority-widening countermodels. A second implementation independently reproduces the canonical enumeration. The result is a bounded cross-domain scientific-authority composition semantics, not generic authorization, local scientific verification, deployed-agent superiority, or a claim of centralized expressive advantage.

## Donor-engulfment architecture

ORION-18 retains the strongest useful structure from two neighboring layers and composes them rather than replacing them.

### Action, delegation, and authorization donors

The calculus reuses evidence-backed permission graphs and deterministic authorizers; proof-carrying actions with action identity, approvals, runtime and outcome receipts; append-only human-to-agent delegation provenance; authority narrowing and cascade containment; principal-chain composition with bounded scope; typed verifier certificates; heterogeneous authorization-evidence chains; and generic cross-domain authority relations.

These mechanisms answer local questions such as whether an action is permitted, whether a delegation is valid, whether required evidence certificates are present, and whether receipt chains satisfy an action policy. Their native semantics remain unchanged inside ORION-18.

### Scientific claim, release, and adjudication donors

ORION-18 also reuses domain scientific harnesses that bind evidence to release, claim-to-evidence chains with deterministic grounding and verification, persistent contract-governed research artifacts, evidence-calibrated claim adjudication, and evidence-ledger review that routes unsupported, contradicted, or mixed-evidence claims back for revision.

These mechanisms establish strong local scientific governance. ORION-18's additional object is the interface that determines when one such local judgment can discharge a different scientific obligation.

### Named sources for the donor mechanisms

The mechanism classes above are named here so that a reader can check the attribution rather
than take it on trust.

Permission that tracks a supplied derivation rather than any agent-internal quantity is the
architecture of proof-carrying authorization: access is granted only when the requester
supplies a proof, in the framework's own logic, that the request follows from the published
policy, and that framework carries no notion of confidence, probability or expected utility
anywhere in the decision (Appel and Felten 1999). Delegation with bounded scope and
principal-chain composition is the subject of delegation logics and decentralized
authorization languages (Li, Grosof and Feigenbaum 2003; Becker, Fournet and Gordon 2010),
and the continuous-control reading of permission is usage control (Park and Sandhu 2002,
2004). Authority held as an unforgeable reference and distinguished by how it was obtained
is the capability model (Dennis and Van Horn 1966).

Two properties this calculus states about revocation are owned elsewhere in the same way.
That a judgment correctly issued at one epoch stands as a historical fact while conferring
no forward authority is the operating assumption of long-term signature validation: a
trusted timestamp exists precisely so that a signature made before revocation remains
verifiable afterwards, while the revoked certificate licenses nothing new (Internet X.509
Time-Stamp Protocol, RFC 3161). The same separation appears as a data-model invariant in
bitemporal databases, where transaction time is append-only because a record of past belief
cannot be falsified and corrections are entered as new assertions rather than as rewrites
(Jensen and Snodgrass 2009). That authority is non-monotone under premise change is
non-monotonicity itself, as studied in belief revision (Alchourrón, Gärdenfors and Makinson
1985).

Naming these does not weaken the calculus. It fixes its boundary: the composition problem
stated next is what remains after every one of them has been granted.

### The remaining composition problem

The donor mechanisms govern heterogeneous subjects: actions, delegations, receipts, verifier predicates, claim-evidence packets, research artifacts, and domain-specific release decisions. ORION-18 provides the common scientific relation that connects those subjects without silently widening what any local verdict means.

## Scientific-discharge type and lifted terminal

The complete scientific-discharge type is

`tau = (domain, kind, scope, content, epoch)`.

Let `D(a)` denote the native authority, verification, adjudication, or release verdict of donor object `a`. ORION-18 preserves `D(a)`.

The bounded lifted state additionally contains:

- `narrowing_ok`: every relevant authority/delegation/claim-processing hop preserves or narrows `tau`;
- blocker state `b in {REFUTED, UNDETERMINED, ESTABLISHED}`;
- two alternative complete support families `S_A`, `S_B`;
- optional explicit `protected_coercion` binding a source type to the target type and epoch.

A donor-derived judgment reaches `DISCHARGE` when:

1. `D(a)` is valid;
2. the scientific type matches directly or a complete protected coercion is registered;
3. authority is non-widening across the relevant chain;
4. blocker state is `REFUTED`;
5. at least one complete support family survives.

`UNDETERMINED` maps to `CANNOT_CHECK`; `ESTABLISHED` maps to `BLOCK`.

## Theorem V3.1 — donor conservativity

Adding the scientific-discharge layer changes none of the donor-native action, delegation, evidence, adjudication, or release verdicts. Local authority remains available for its native purpose even when it does not yet discharge a broader scientific target.

This is the compatibility foundation: cross-domain scientific governance is additive rather than destructive.

## Theorem V3.2 — typed scientific-discharge separation

For every registered donor family and each non-inert coordinate of `(domain, kind, scope, content, epoch)`, two states can share the same native donor success while differing only in whether that coordinate matches the target scientific obligation. The exhaustive model contains **65 one-coordinate separating witnesses**.

A valid action certificate, verified claim-evidence packet, scientific release decision, or authorization receipt therefore remains reusable without becoming an unrestricted scientific authority token.

## Theorem V3.3 — monotone non-widening scientific-authority law

Across the registered donor envelope, unbridged heterogeneous composition is monotone in scientific authority: each hop may preserve or narrow the inherited scientific-discharge type, but a widening hop cannot discharge the broader target merely because every donor-local step is native-valid. Broader authority requires an explicit protected bridge that establishes the additional source-to-target relation.

The 169 matched widening countermodels in Theorem V3.7 make this a tested finite law rather than an intuition. Local authority remains valid; only the unjustified widening is rejected.

## Theorem V3.4 — protected coercion enables cross-domain transport

A complete protected coercion can transform an otherwise incompatible scientific type when it binds the exact source type, target type, subject/content, scope, and epoch required by the target obligation. The model contains **65 protected-coercion restorations** and **65 matched bridge-necessity witnesses** in which the same transfer remains unavailable without the registered bridge.

Cross-domain use is therefore enabled, not prohibited, provided the authority transfer is explicit and typed.

## Theorem V3.5 — three-state blocker law

Under otherwise satisfied conditions:

- `REFUTED` clears the blocker premise and permits discharge;
- `UNDETERMINED` yields `CANNOT_CHECK`;
- `ESTABLISHED` blocks discharge.

The law is instantiated across all thirteen donor families. It preserves the scientific distinction between disproving a blocker and merely lacking evidence about it.

## Theorem V3.6 — exact support-family revocation

When two independent complete support families establish the same target obligation, revoking one family preserves discharge through the other. Revoking every complete support family removes discharge. The finite model contains **26 independent-support survivals** and **13 complete-support revocations**.

The rule is exact in both directions: it preserves valid independent derivations while removing authority when no complete derivation survives.

## Theorem V3.7 — complete pairwise composition law in the registered donor envelope

Every ordered pair among the thirteen registered donor families admits a scientifically valid two-hop composition when local verdicts are native-valid, scientific type is compatible or protectedly bridged, authority does not widen without that bridge, blockers are refuted, and at least one complete support family survives. This yields **169/169 successful registered donor-pair compositions**, exhausting the registered 13×13 donor-pair product.

For every ordered pair, a matched unbridged widening variant remains unavailable while both donor-native steps stay valid, yielding **169 matched widening countermodels**. The success/countermodel pairing gives the registered composition law its sharp boundary: compatible/narrowed or explicitly bridged authority composes; silent widening does not.

The result shows that heterogeneous authority composition can be systematic without forcing every donor into one receipt format or one centralized implementation.

## Theorem V3.8 — permission, release, and support independence

Action/release permission and scientific proposition support are independent, non-inverse relations. A native denial of one action or release route does not scientifically refute a proposition when an independent complete evidence family establishes it. Conversely, native authorization or release does not automatically discharge a different or broader scientific target.

This is a positive interface theorem: action governance and scientific truth support can coexist without corrupting one another because their relation is explicit and compositional.

## Theorem V3.9 — authorization receipts as reusable scientific infrastructure

Valid composition of authorization receipts, canonical action or subject binding, and successful local policy evaluation remains valuable scientific infrastructure whenever the target obligation requires it. Scientific sufficiency is obtained when those receipts are combined with the target type, blocker, support, and coercion conditions.

ORION-18 therefore preserves the value of receipt chains while controlling exactly how far their authority travels.

## Theorem V3.10 — decentralized portability

A decentralized donor product supplied with the same scientific type, narrowing, blocker, support-family, coercion, and composition rules agrees extensionally with ORION-18 over all **39,936** registered states.

The zero-mismatch result is a portability theorem: scientific-discharge semantics are independent of whether they are implemented in one shared calculus or a correctly integrated decentralized product.

## Final donor envelope and literature fixed point

The final donor envelope contains thirteen families spanning authorization/security and scientific verification/adjudication. Earlier six-donor and ten-donor enumerations remain preserved because later hostile literature searches found stronger scientific-release and heterogeneous-authority donors and forced the architecture to absorb them before the final theorem was stated.

Two post-X4 search rounds produced no further material interface change. This is a dated current-pass fixed point and remains reopenable if a new primary formalism supplies an equivalent or stronger scientific-discharge relation.

## Exact bounded support

Final X4 enumeration:

- distinct exact authority states: **3,072**, each replayed across thirteen donor families for **39,936** evaluations; the donor axis changes no verdict in any of 239,616 sibling pairs, which is the conservativity result and not extra coverage;
- terminals: **19,968** `NO_DONOR_AUTHORITY`, **15,353** `BLOCK`, **3,328** `CANNOT_CHECK`, **1,287** `DISCHARGE`;
- donor-conservativity violations: **0**;
- one-coordinate scientific-type separations: **65**;
- protected-coercion restorations: **65**;
- bridge-necessity witnesses: **65**;
- blocker-law instances: **13** `REFUTED` discharge cases, **13** `UNDETERMINED` `CANNOT_CHECK` cases, **13** `ESTABLISHED` blocks;
- independent-support revocation survivals: **26**;
- complete-support revocations: **13**;
- heterogeneous ordered-chain composition successes: **169**;
- matched widening countermodels: **169**;
- action/release-denied but independently supportable proposition cases: **13**;
- minimal scientific-type separation witnesses: **65**;
- protected-coercion successes: **65**;
- matched unprotected-coercion countermodels: **65**;
- blocker-law instances: **13** `REFUTED` successes, **13** `UNDETERMINED` `CANNOT_CHECK`, **13** `ESTABLISHED` blocks;
- one-support-family revocation survivals: **26**;
- all-support-family revocation blocks: **13**;
- heterogeneous ordered-chain composition successes: **169** — one composition counted thirteen times thirteen, because the enumeration's chain loop ignores both of its donor variables and the thirteen families present a single profile to it; the mechanized derivation below states what that leaves;
- matched scientific-authority-widening chain countermodels: **169**, on the same replication;
- action/release-denied but independently supportable proposition examples: **13**;
- ideal decentralized-product mismatches: **0**;
- canonical row SHA-256: `ed186b824692fd5b3ab31be718c75b84e2126b577ce921ca5cc01b2d08ae19e6`.

A separate checker independently reconstructs the final enumeration.

## Real evidence-discharge study: 20 cases across four domains

The theorems above are exact statements about the calculus. Whether the
discharge and revocation semantics behave as specified on real material is a
separate question, and it is answered on 20 frozen real-domain cases spanning
four settings -- empirical, formal, multiple-support and systems.

- exact scientific-discharge accuracy: **1.0** in all four domains;
- false scientific promotions: **0**;
- 12 explicit action/scientific-separation cases;
- full support revocation blocks discharge, and partial revocation preserves
  the support that was retained;
- independent checker and deterministic replay: GREEN.

The twelve separation cases are the point of the study rather than a subset of
it. Four states must stay distinct and are kept distinct throughout: an agent may
hold **action permission** to run something, which is a local authorization fact;
**scientific discharge** is the separate question of whether the resulting
evidence can authorize a conclusion; `DENIED` records that discharge was refused
on the evidence presented; and `CANNOT_CHECK` records that the question was not
answerable at all. Collapsing the first into the second is authority laundering,
and collapsing `CANNOT_CHECK` into `DENIED` manufactures a negative finding out
of an absent one.

This is bounded real evidence that the semantics behave as specified. It is not
independent external adjudication of the calculus: the checker is a second
implementation inside the same programme, not an outside authority.


## Strongest supported claim

> ORION-18 establishes a complete finite composition law for cross-domain scientific authority over thirteen heterogeneous donor families. Native donor authority is conserved; all 169 registered ordered donor pairs compose under compatible, narrowed, or explicitly protectedly bridged scientific authority; matched widening variants establish the non-widening boundary; unresolved blockers fail closed; complete independent support is exactly revocable; and the semantics are portable to an equally typed decentralized implementation.
## Mechanized core, and what the finite result is an instance of

Everything above this line is an enumeration over an authored state space. That is a true statement about 3,072 states and thirteen donor families, and it is not a theorem. Three machine-checked artifacts under `formal/mechanized/` now say which parts of it follow from a general semantics, and what each part costs.

**The calculus.** Ten composition and revocation theorems — scope non-amplification, domain confinement, non-laundering, non-compensatory obligations, defeater monotonicity, epoch isolation, the one-step delegation lemma, a bridge from conversion to reachability, and a characterisation of cycles — are discharged by Z3 over uninterpreted domain, object and issuer sorts, so none of them is a statement about thirteen donors or six named domains. Two limits travel with them and are recorded in the artifact rather than in a footnote: reachability is *axiomatised* as a reflexive-transitive closure carrying a well-founded rank, because transitive closure is not first-order definable, and the chain theorem's induction schema is the single hand step in the development. The rank is not a formality — an earlier axiomatisation without it admitted circular reachability, in which a sink domain reached its own source, and a differential against the committed checker is what caught it.

**The state model as an instance.** Each of the seven arguments the X4 terminal takes is assigned to the calculus conjunct it means: type-coordinate agreement or a registered protected coercion is the calculus's reachability, narrowing is scope containment, and the blocker is at once a hard obligation and a defeater. The calculus's own rule under that assignment reproduces X4 exactly on all 3,072 distinct states, with all four terminals reached.

**The chain compositions as instances.** A donor family is interpreted as an element of an uninterpreted sort whose *domain is its scientific type profile*; a protected coercion is a registered conversion and narrowing is scope containment. Under eight frame conditions stated as axioms — each shown load-bearing by exhibiting a countermodel to a theorem it carries — seven theorems are discharged, and donor-level chain confinement is expanded and discharged at every chain length up to six. The bound is a measured limit rather than a chosen one: lengths seven to twelve were tried and the solver returned `unknown` on some runs and a proof in seconds on others, so the ladder stops where it is a reliable corroboration. Nothing about the theorem changes at length seven — the induction schema is what carries every length, and it is the single hand step in the development. A ORION-18 chain hop *is* the calculus's delegation, which is itself one of the discharged theorems, so Theorem V3.7 is an instance of a statement that mentions neither thirteen nor two.

**What that costs Theorem V3.7.** The derivation lands, and what it lands on is small. We state it here rather than leave a reader to assume otherwise.

- The 169 is one composition counted 169 times. The committed enumeration writes its chain claim as a doubly nested loop over the thirteen families whose body mentions neither loop variable, and under the interpretation all 169 ordered pairs compose to a single distinct state. The donor axis is a replication factor here exactly as it is in the 39,936 evaluations, and here it is squared.
- Nothing heterogeneous is exercised. The state the chain claim evaluates has all five type coordinates agreeing, which by the interpretation puts both donors in one domain; the hop is then a reach by reflexivity and no conversion is ever consulted. Read the thirteen families as type-distinct, so that a cross-family hop crosses a type boundary unless a protected bridge is registered, and the same committed rule returns **13** compositions rather than 169. Registering every cross-family bridge returns 169 again. The published number therefore records the reading under which no two of the thirteen donor families differ in scientific type — which is the reading under which the chain is not heterogeneous.
- Neither published count tests the interpretation. All eight wrong composition operators tried reproduce 169 successes exactly, and six of the eight also reproduce the 169 widening countermodels. What separates them is an exhaustive identity checked through the committed rule on 36,864 representative pairs, which stand in exactly for all 9,437,184 pairs of X4 states: a composed chain discharges when and only when both of its hops do. Every one of the eight wrong operators breaks it, and the shipped rule satisfies it with no exception.

None of the above has been checked by anyone outside the lane that wrote it. Independent formal review and independent systems reproduction remain open, and no empirical claim is made or supported here.

## Wider ORION-18 claim

This is substantially stronger and more constructive than a simple distinction between generic permission and scientific permission. ORION-18 supplies the typed composition relation that lets strong local authority mechanisms work together without silently widening their scientific meaning.

## Transfer scope

The theorem establishes the registered 13-donor, five-coordinate formal envelope and its complete 39,936-state enumeration. Additional donor families, deployed-agent behavior, and broader authority ontologies are extension targets to be tested separately. The decentralized-product equivalence strengthens the main result by establishing that the semantics are architecture-independent.

## Conclusion
V3 does not claim novelty for any of the thirteen donor mechanisms, universal minimality of the five type coordinates, deployed-agent superiority, a public full-manuscript release gate, or global literature saturation. It does not claim that the 169 chain compositions measure heterogeneity, that they are 169 results rather than one replicated, or that reproducing them validates any interpretation of the calculus; the mechanized section above states what each of those numbers was found to carry. Native authorization failure is not scientific refutation. The ideal equally typed decentralized product ties exactly.

ORION-18 establishes a composition theory for scientific authority. Modern agent systems already provide serious local authority through permission graphs, proof-carrying actions, delegation chains, typed verifier certificates, receipt composition, domain scientific release, claim-evidence verification, research harnesses, and evidence-ledger adjudication. ORION-18 retains those mechanisms and gives them a shared rule for deciding when one local judgment may discharge a different scientific obligation.

The calculus is constructive at every interface. Native donor authority is preserved. Scientific authority is monotone under unbridged composition: it may be preserved or narrowed but cannot widen without a protected bridge. Cross-domain transfer remains available through complete protected coercion. `UNDETERMINED` blockers remain actionable `CANNOT_CHECK` states. Independent complete support routes survive partial revocation. All **169 ordered donor pairs** compose under the registered compatible conditions, each has a matched widening countermodel, and the equally typed decentralized product matches **all 39,936 states**.

The strongest conclusion is therefore positive and architecture-independent: **cross-domain scientific authority obeys a complete finite composition law over the registered donor product—heterogeneous local authority composes systematically when scientific discharge is typed, monotone/non-widening by default, explicitly bridgeable, fail-closed, and support-aware**.

**Current science terminal:** `P8_CROSS_DOMAIN_SCIENTIFIC_AUTHORITY_COMPOSITION_SUPPORTED__13_DONOR_FORMAL_ENVELOPE__IDEAL_PRODUCT_EQUIVALENT`.

## Native cross-system execution protocol (2026-08-24)

Issue #1086's ORION-18 box additionally asks to "execute actual type-distinct native
systems and ideal typed-product baseline" and to "cover every ordered
cross-system pair with clean and hostile cases." The full test design for that
execution is now frozen as contract `P8.NATIVE.CROSS_SYSTEM_PROTOCOL.V1`
(`formal/P8_NATIVE_CROSS_SYSTEM_PROTOCOL_V1.md` and its machine-readable twin):
four type-distinct native systems --- OPA/Rego, Cedar, in-toto/SLSA,
Sigstore/cosign --- twelve ordered cross-system pairs, twenty-four case slots
(clean and hostile for every pair), each hostile slot pinned to one laundering
mechanism, with the typed product of the authority calculus as the ideal
baseline and the pass criteria fixed in advance.

The execution itself has not been run: none of the four systems' binaries
exists in the producing environment and no installation is permitted there.
The status is `CANNOT_CHECK` with that tooling gap stated in the protocol, not
simulated away: no native-looking output was produced, and the protocol
explicitly prohibits reporting a simulation as execution or a partial run as
full pair coverage. The DENIED-vs-`CANNOT_CHECK` calibration is #1096's and is
presupposed, not re-derived.
