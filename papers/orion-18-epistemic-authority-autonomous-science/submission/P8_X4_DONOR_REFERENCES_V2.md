# ORION-18-X4 donor reference ledger V2 — the classical layer

Date: 2026-09-02

`P8_X4_DONOR_REFERENCES.md` (2026-08-19) records the donor identities used by the
V3 science update and states plainly that it "is not a claim of exhaustive
literature coverage". It is not: **every entry in it is a 2026 arXiv preprint or
a 2026 IETF draft.** The shipped `submission/JAAMAS_MANUSCRIPT.tex`
bibliography inherits that shape — thirteen entries, eleven of them dated 2026,
the oldest being Park & Sandhu (2002).

The A6 donor-subtraction programme has since identified the classical work that
owns most of the primitives ORION-18 composes. Those results post-date the
ledger above and never flowed back into it. This V2 supplies them in the same
format, so the next bibliography regeneration has them.

**This is an attribution ledger, not a novelty argument.** Every entry below can
only narrow what ORION-18 may claim. `scientific_authority_delta: NONE`.

## Why this matters to the submission

A reviewer opening the current bibliography sees a paper positioned almost
entirely against work from its own year. The classical parents are named in
ORION-18's *working* manuscript — `manuscript/FINAL_V5.md`, "Named sources for
the donor mechanisms" — but not in what would be submitted. That asymmetry reads
as incrementality concealed rather than incrementality disclosed, which is the
opposite of what the working manuscript actually does.

## Authorization, delegation and trust management

- **Abadi, Burrows, Lampson & Plotkin**, *A Calculus for Access Control in
  Distributed Systems*, ACM TOPLAS 15 (1993), 706–734. Principals, delegation
  and "speaks-for" reasoning. Source: `A6_DONOR_MATRIX_V2`.
- **Appel & Felten**, *Proof-Carrying Authentication*, CCS 1999,
  DOI 10.1145/319709.319718. Access granted only when the requester supplies a
  proof, in the framework's own logic, that the request follows published
  policy — with no notion of confidence or expected utility anywhere in the
  decision. Source: `A6_DONOR_MATRIX_V2`.
- **Blaze, Feigenbaum & Lacy**, *Decentralized Trust Management*, IEEE S&P
  (1996) — PolicyMaker. Compliance checking without a central authority.
  Source: `A6_DONOR_MATRIX_V4`.
- **Blaze, Feigenbaum, Ioannidis & Keromytis**, *The KeyNote Trust-Management
  System, Version 2*, RFC 2704 (1999), DOI 10.17487/rfc2704.
  Source: `A6_DONOR_MATRIX_V4`.
- **Ellison, Frantz, Lampson, Rivest, Thomas & Ylonen**, *SPKI Certificate
  Theory*, RFC 2693 (1999), DOI 10.17487/rfc2693; **Rivest & Lampson**, *SDSI —
  A Simple Distributed Security Infrastructure* (1996). The **deliberate
  separation of naming from authorization**, kept apart because conflating them
  was recognised as a design fault in the PolicyMaker lineage. ORION-18 must not
  claim that separation. Source: `A6_DONOR_MATRIX_V4`.
- **Clarke, Elien, Ellison, Fredette, Morcos & Rivest**, *Certificate Chain
  Discovery in SPKI/SDSI*, Journal of Computer Security 9(4) (2001).
  Delegation chains discovered rather than pre-registered.
  Source: `A6_DONOR_MATRIX_V4`.
- **Li, Mitchell & Winsborough**, the RT role-based trust-management framework.
  Multiple roots of trust, already dispositioned `SPECIALIZATION` in
  `A6_DONOR_SUBTRACTION_COMPLETION_V1`.

## Obligation, permission and non-monotonicity

- **Alchourrón, Gärdenfors & Makinson**, *On the Logic of Theory Change*,
  Journal of Symbolic Logic (1985). Rationality postulates for revising a corpus
  on new information. Source: `A6_DONOR_MATRIX_V2`, and already named in
  `manuscript/FINAL_V5.md`.
- **Makinson & van der Torre**, *Input/Output Logics*, Journal of Philosophical
  Logic, DOI 10.1023/A:1004748624537; *Constraints for Input/Output Logics*,
  DOI 10.1023/A:1017599526096; ***Permission from an Input/Output Perspective***,
  DOI 10.1023/A:1024806529939. Norms as a transformation from inputs to obligated
  outputs rather than truth-valued propositions — the closest formalism to "the
  transformation emits obligations", and the permission paper is the sharper of
  the three for ORION-18. Source: `A6_DONOR_MATRIX_V4`.

## Information flow and channel control

- **Goguen & Meseguer**, *Security Policies and Security Models*, IEEE S&P
  (1982). Non-interference: one domain not influencing another.
- **Rushby**, *Noninterference, Transitivity, and Channel-Control Security
  Policies*, SRI CSL-92-02 (1992). **Intransitive** non-interference — controlled
  downgrading through a named channel. This is the closest parent to ORION-18's
  cross-domain authority laundering, closer than any authorization logic, and
  the single most important addition in this ledger.
- **Sabelfeld & Myers**, *Language-Based Information-Flow Security*, IEEE JSAC
  (2003). Static enforcement by typing. Source for all three:
  `A6_DONOR_MATRIX_V3`.

## Epoch, custody and historical record

- **Internet X.509 Time-Stamp Protocol**, RFC 3161. A trusted timestamp exists
  precisely so a signature made before revocation remains verifiable afterwards,
  while a revoked certificate licenses nothing new. Already named in
  `manuscript/FINAL_V5.md`.
- **Jensen & Snodgrass**, bitemporal data models (2009). Transaction time as an
  append-only record: past belief cannot be falsified, and corrections enter as
  new assertions rather than rewrites. Already named in `manuscript/FINAL_V5.md`.
- **Dennis & Van Horn**, *Programming Semantics for Multiprogrammed
  Computations* (1966). Capabilities as unforgeable authority-bearing references.
- **Green, Karvounarakis & Tannen**, *Provenance Semirings*, PODS 2007,
  DOI 10.1145/1265530.1265535; **W3C PROV-O** Recommendation (2013).
  Source: `A6_DONOR_MATRIX_V2`.

## Effects, capabilities and assurance argument

- **Bernstein** (1966), conditions for safe reordering; **Lucassen & Gifford**,
  *Polymorphic Effect Systems*, POPL 1988. An effect annotation is worthless
  without a soundness theorem tying it to real accesses.
  Source: `A6_DONOR_SUBTRACTION_COMPLETION_V1`.
- **Morrisett, Walker, Crary & Glew**, *From System F to Typed Assembly
  Language*, POPL 1998, DOI 10.1145/268946.268954; **Crary, Walker & Morrisett**,
  *Typed Memory Management in a Calculus of Capabilities*, POPL 1999.
  Source: `A6_DONOR_MATRIX_V2`.
- **Kelly & Weaver**, *The Goal Structuring Notation*; **SEI**, *Toward a Theory
  of Assurance Cases* (2012). Claim→evidence argument structure. A well-structured
  case is not a proof that its premises are true. Source: `A6_DONOR_MATRIX_V2`.

## Abstention and shielding

- **Chow**, *On Optimum Recognition Error and Reject Tradeoff*, IEEE Trans.
  Information Theory (1970); **El-Yaniv & Wiener**, *On the Foundations of
  Noise-Free Selective Classification*, JMLR 11 (2010). `CANNOT_CHECK` **is** the
  reject option; only its non-compensatoriness may survive.
- **Bloem, Könighofer, Könighofer & Wang**, *Shield Synthesis: Runtime
  Enforcement for Reactive Systems*, TACAS 2015,
  DOI 10.1007/978-3-662-46681-0_51; **Alshiekh et al.**, *Safe Reinforcement
  Learning via Shielding*, AAAI 2018. Source for both: `A6_DONOR_MATRIX_V3`.

## Citation provenance

Every entry was located and checked against published records during the A6
donor-subtraction work, and each names the matrix that dispositioned it. Where a
volume, issue or DOI is absent it was **deliberately omitted rather than
asserted from recollection**, and must be completed from the record before the
entry enters `submission/bibliography.bib`.

## Ownership statement

All mechanisms above remain donor-owned, as in V1. Adding them narrows ORION-18's
claim and does not alter it: the paper claims only the bounded cross-domain
composition relation governing when heterogeneous local authority objects may
discharge a target scientific obligation.
