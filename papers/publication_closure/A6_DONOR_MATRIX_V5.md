# A6 Phase 1 — donor matrix V5 (ORION-16)

**Status:** `FIVE_ORION16_FIELDS_CLOSED__DONOR_SUBTRACTION_ONLY`
**Date:** 2026-09-02
**Scientific authority delta:** `NONE`. Like V2–V4, this matrix can only narrow
novelty. Nothing here promotes a claim.

V2–V4 worked ORION-18's field list. ORION-16's
`JOURNAL_READINESS.md` §2 asks for seven families, and auditing them against the
A6 corpus — reading match context, with a control term, and enumerating each
alternative separately rather than trusting a combined pattern — leaves five
gaps of two kinds.

## Audit result before this document

| ORION-16 §2 family | A6 coverage | verdict |
|---|---|---|
| dynamic epistemic logic / action-model | 0 files | **absent** |
| AGM / iterated revision / entrenchment / ranking | `AGM` in 6 files with real verdicts; `iterated revision`, `entrenchment`, `ranking function`, `Spohn`, `Darwiche`, `Pearl` each **0** | **partial** |
| truth-maintenance / dependency-directed / rollback | 6 files, dispositioned | covered |
| incomplete / inconsistent / hyperintensional revision | 0 files | **absent** |
| process / separation / temporal / effect / authorization logic | `separation logic` 3, `effect system` 3; `temporal logic`, `process calculus`, `process algebra` each **0** | **partial** |
| cognitive-architecture / language-agent formalism | 0 files | **absent** |
| provenance / audit / incremental-repair | 5 files, dispositioned | covered |

Control: 111 matches for `donor` across the same 17 documents, so the scan
demonstrably reads them. Per-alternative enumeration is deliberate — a combined
pattern reported the AGM row as covered when only the plainest of its six
alternatives was, and the same shortcut produced a wrong absence claim in V4.

## Fields dispositioned in V5

| Required donor field | Primary donor objects checked | What the donor already supplies | A6 consequence |
|---|---|---|---|
| dynamic epistemic logic / action models | Plaza, *Logics of Public Communication* (1989); Baltag, Moss & Solecki, *The Logic of Public Announcements, Common Knowledge, and Private Suspicions*, TARK (1998); van Ditmarsch, van der Hoek & Kooi, *Dynamic Epistemic Logic*, Springer (2007) | epistemic change as an **operation with its own syntax** — an action model that transforms a model rather than a proposition asserted about one; product update; and the machinery for who learns what, including private and partially-observed announcements | Modelling an epistemic *mechanic* as a first-class object that acts on a state — rather than as a proposition about the state — is **donor**, and it is the closest thing in the literature to what "epistemic mechanics" names. ORION-16 may not claim the move itself. Product update also already handles the multi-agent observation asymmetry, so any ORION-16 result about who sees a revision must be checked against it. |
| iterated revision / entrenchment / ranking | Gärdenfors & Makinson, *Revisions of Knowledge Systems Using Epistemic Entrenchment* (1988); Spohn, *Ordinal Conditional Functions* (1988); Darwiche & Pearl, *On the Logic of Iterated Belief Revision*, Artificial Intelligence, DOI 10.1016/S0004-3702(96)00038-0 (1997); Lehmann (1995) on revision over belief states; Booth & Chandler on the DP postulates | entrenchment as the structure that decides what survives a revision; ranking functions as a graded, iterable strength; and — the load-bearing part — **Darwiche & Pearl's move from knowledge bases to epistemic states**, where the state carries everything needed for coherent reasoning *including the revision strategy itself*, precisely so that revision can be iterated coherently | This is the **nearest parent to ORION-16 as a whole**, and it was not in the A6 corpus at all. "The object being revised must carry its own revision machinery, not just its beliefs" is Darwiche & Pearl (1997), following Lehmann (1995). ORION-16's residual-obligation preservation and its recursion/fixed-point claims sit directly on the iterated-revision postulates and must be stated as satisfying, violating, or refining them — not as new territory. The DP postulates are also contested, so *disagreeing* with them is a recognised position rather than a novelty. |
| incomplete / inconsistent / hyperintensional revision | the paraconsistent revision literature; the hyperintensional turn in belief revision; Fermé & Hansson, *AGM 25 Years* (2011), as the survey that maps both | revision that tolerates inconsistency instead of exploding, and revision sensitive to how a belief is *presented* rather than only to what it entails | Handling a corpus that is incomplete or locally inconsistent without collapsing is **donor**, and so is the observation that logically equivalent contents can revise differently. ORION-16 must not present either as new. **Row completed 2026-09-02** by `A6_HYPERINTENSIONAL_ROW_CLOSURE_V1.md`, which resolved the primaries against published records and found that Berto 2019 composes both properties in one paper — the combined claim is a specialization of Berto 2019, not a union of two literatures. |
| temporal logic / process calculi (completing the process-logic row) | Pnueli, *The Temporal Logic of Programs*, FOCS (1977); Milner, *A Calculus of Communicating Systems* (1980) and the π-calculus | properties of a system **over time** rather than at a point — safety, liveness, until — and compositional descriptions of interacting processes with an equivalence theory | Reasoning about what must hold across a sequence of epistemic operations is **donor**. Separation logic and typed effects were already dispositioned; the temporal and process halves of the same §2 item were not. Any ORION-16 claim of the form "this property is preserved along every trajectory" is a temporal-logic claim and should be written as one. |
| cognitive architectures / language-agent formalisms | Laird, Newell & Rosenbloom, *SOAR: An Architecture for General Intelligence*, Artificial Intelligence (1987); Anderson, ACT-R; Rao & Georgeff, *BDI Agents: From Theory to Practice* (1995); Sumers, Yao, Narasimhan & Griffiths, *Cognitive Architectures for Language Agents* (CoALA), arXiv:2309.02427 (2023), TMLR 2024 | a decomposition of an agent into memory types, a decision cycle, and action spaces — with BDI supplying belief/desire/intention as *typed* mental state, and CoALA supplying the same decomposition for LLM-based agents | Decomposing an epistemic agent into typed memory and a decision cycle is **donor**, and CoALA has already applied that decomposition to the language-agent case ORION-16 addresses. One honest asymmetry is worth keeping: CoALA is explicitly a **taxonomy, not an implementation or a formal semantics**, so it does not own a *formal* mechanics — which is where ORION-16's residual, if any, must be located. That is a narrow opening and should be claimed narrowly. |

## Effect on ORION-16's claim

Two of these are more than box-filling.

**Iterated revision is the nearest parent and was entirely absent.** The
epistemic-states move is not adjacent to ORION-16, it is the same move. Every
ORION-16 theorem about preserving structure across successive revisions must be
positioned against the DP postulates explicitly.

**Dynamic epistemic logic already owns "an epistemic change is an object".**
Action models act on states; that is the mechanic framing. What remains is
whatever ORION-16's mechanics do that a product update does not.

Neither is fatal, and both are the kind of parent that makes a paper easier to
place once named. But the residual after V5 is smaller than the readiness plan
assumed when it listed these as boxes to tick.

## What remains open in ORION-16 §2

Hostile exact-composition search, two consecutive no-material-change rounds, a
current `#287` novelty certificate — and the `PARTIAL_DISPOSITION` flagged above
for the hyperintensional row, whose primary sources are `CANNOT_CHECK` here, was
completed same-day by `A6_HYPERINTENSIONAL_ROW_CLOSURE_V1.md`.

## Citation provenance

Darwiche & Pearl (with DOI, and the Lehmann/Booth–Chandler reception) and CoALA
were located and checked against published records for this document. The
remaining entries are cited by title, venue and year only; volume, issue and DOI
were deliberately omitted rather than asserted from recollection. The
hyperintensional row was explicitly marked `CANNOT_CHECK` rather than dressed in
citations that were not verified; its primaries are now verified in
`A6_HYPERINTENSIONAL_ROW_CLOSURE_V1.md`.

## Boundary

A donor matrix, not a priority certificate. Every entry can only subtract from
what ORION-16 may claim. If a source not listed here states its composed result
directly, this matrix must be amended rather than the claim defended by
terminology.
