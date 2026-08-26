# Formal Epistemic Structures and Mechanics — V3 science update

**Paper VI current science manuscript overlay**  
**Date:** 2026-08-19  
**Base manuscript:** `FINAL_V2_1.md` (unchanged historical V2.1 body)  
**Successor evidence:** `research/claim_expansion/p6/`  
**Science terminal:** `P6_GENERAL_SCIENTIFIC_CERTIFICATE_SEMANTICS_SUPPORTED__BOUNDED_FORMAL_EMBEDDINGS__IDEAL_PRODUCT_EQUIVALENT`

This V3 source is the current scientific manuscript specification. It preserves every V2.1 theorem, countermodel and donor boundary and adds the prospectively frozen ORION-16-X theorem family below. PDF/typesetting bytes are deliberately deferred; the historical V2.1 PDF must not be presented as containing V3.

## Replacement abstract for V3

Scientific agents change more than propositional belief. Mature theory already supplies truth/dependency maintenance, incremental computation, typed effects, continuing authorization, provenance, workflow reproducibility, and increasingly explicit execution-attestation certificates. We therefore do not claim those mechanisms or certificates as new. ORION-16 asks a narrower formal question: when such mature dynamic systems operate on scientifically certified state, can donor-native computational or operational validity remain unchanged while scientific admissibility changes because a load-bearing evidence, source-authority, claim-scope, or verification-epoch obligation has changed?

The V2.1 paper developed a history-aware epistemic-mechanic contract, safe root-inclusive reopening, the soundness-versus-minimality distinction, preservation versus protected revalidation, footprint-faithful composition, obligation persistence, authority non-escalation, and a typed-erasure separation. ORION-16-X generalizes the separation as a conditional scientific-certificate theorem schema over three bounded donor semantic embeddings: dependency maintenance, effectful computation, and continuing authorization plus execution provenance. A forgetful map preserves each donor's native validity, yet whenever it erases a non-inert scientific certificate coordinate it need not reflect scientific admissibility. When all scientific obligations are discharged, the enrichment reduces exactly to donor-native validity; after change, any changed scientific coordinate must be preserved or explicitly revalidated for certificate continuity. An ideal donor product carrying the same scientific coordinates and predicate is extensionally equivalent.

An exhaustive finite model evaluates 1,536 states. It finds zero donor-preservation violations, 96 typed-erasure separation witnesses spanning all four scientific coordinates, 96 conservative-reduction cases with zero violations, zero ideal-product mismatches, 96 certificate-revocation countermodels, and 24 donor-valid no-alarm cases. A second implementation independently reproduces all counts. The contribution is thus a bounded scientific-admissibility enrichment and conservative-extension/separation theorem family, not generic certification, provenance, authorization, or deployed-agent superiority.

## V3 related-work / donor update

The V2.1 donor stance remains in force. The successor search adds stronger pressure rather than reclaiming territory. Current proof-of-execution work already treats governed agent actions as certificate-bearing objects whose authorization, effect, history and replay evidence can be attested at runtime. Formal scientific-workflow work likewise binds provenance and reproducibility conditions into workflow signatures. These results remove any plausible ORION-16 claim that attaching certificates, provenance or execution history to computations is itself novel.

Accordingly, ORION-16-X grants an ideal donor product all ordinary dependency/effect/authorization/provenance machinery and, in the strongest comparison, every scientific coordinate used by ORION-16-X. The latter product ties extensionally. The residual is the explicit scientific-admissibility distinction and the theorem identifying exactly when a donor-visible forgetful view ceases to reflect it.

## 17. Post-saturation successor: scientific-certificate semantics as a conservative enrichment

### 17.1 Bounded donor embeddings

ORION-16-X freezes three semantic embeddings. They are deliberately small abstractions of mature donor families rather than claims to reproduce every theorem or implementation detail of those fields.

1. **Dependency maintenance.** Donor validity requires computational validity and supported dependency state.
2. **Effectful computation.** Donor validity requires computational validity and a valid declared effect.
3. **Continuing authorization plus execution provenance.** Donor validity requires current action authorization and valid execution provenance.

The scientific enrichment adds four independent certificate coordinates: current evidence version, authorized scientific source, supported claim scope, and current verification epoch. For embedding `D`, scientific admissibility is donor validity plus discharge of every scientific certificate obligation.

### 17.2 Forgetful map and preservation

Let `U_D` erase the four scientific certificate coordinates while preserving the complete donor-visible state. By construction, `U_D` preserves the truth value of the donor-native validity predicate. This is a compatibility requirement: ORION-16-X does not rewrite a donor's native semantics merely to manufacture a distinction.

### 17.3 Conditional typed-erasure separation

**Theorem V3.1 — scientific non-reflection under non-inert erasure.**  
Suppose at least one scientific certificate coordinate is non-inert: there exist two states identical on donor-visible coordinates and on all other scientific coordinates for which changing that coordinate changes scientific admissibility. Then `U_D` does not reflect scientific admissibility. In particular, there exist `s,t` with `U_D(s)=U_D(t)` and equal donor-native validity but different scientific-admissibility judgments.

The theorem is explicitly conditional. It does not assert that every TMS, effect, authorization, provenance, workflow, or proof-carrying system necessarily erases scientifically relevant information. A donor already carrying the same scientific coordinate and rule belongs on the information-equivalent side of the result.

### 17.4 Conservative special case

**Theorem V3.2 — conservative reduction.**  
If every scientific certificate obligation is discharged, scientific admissibility reduces exactly to donor-native validity under the embedding.

This theorem makes the enrichment conservative where the additional scientific coordinates are inert or already satisfied, instead of changing ordinary computation for its own sake.

### 17.5 Ideal-product equivalence

**Theorem V3.3 — no inherent expressivity advantage.**  
An ideal donor product enriched with the exact ORION-16-X scientific coordinates and the same admissibility predicate is extensionally equivalent to ORION-16-X.

The negative result is part of the headline boundary. ORION-16's contribution does not arise from centralization or from an information advantage over an equally typed product.

### 17.6 Certificate continuity after change

**Theorem V3.4 — preservation/revalidation requirement.**  
A donor-valid transition preserves an existing scientific certificate only when every scientific certificate coordinate changed by the transition is either preserved under the exact change or explicitly revalidated. If a non-inert scientific coordinate becomes false while donor-native validity remains true, the old scientific certificate cannot remain admissible solely because computation, support, effect execution, or tool authorization succeeded.

This generalizes the V2.1 distinction between recomputation/support continuity and scientific revalidation.

### 17.7 Exhaustive finite model and independent audit

The frozen checker enumerates all Boolean states of the donor-visible and four scientific coordinates for each embedding: 512 states per embedding and 1,536 evaluations total.

- donor-preservation violations: **0**;
- typed-erasure separation witnesses: **96**, spanning all four scientific coordinates;
- conservative-reduction cases: **96**, violations **0**;
- ideal-product equivalence violations: **0** across all 1,536 states;
- certificate-revocation countermodels: **96**;
- donor-valid no-alarm cases: **24**;
- canonical primary enumeration SHA-256: `9a181cc61f1a1b56daa8f313d63acc3928f758b4150d242fe03c14e347ec511c`.

A second theorem audit, implemented independently of the primary finite checker, reproduces the 1,536 evaluations, 96 separation witnesses, 96 conservative cases, 96 revocation countermodels, 24 no-alarm cases, and zero ideal-product mismatches.

### 17.8 Interpretation

The result widens ORION-16 from one typed-erasure construction to a bounded theorem family: **computational/operational preservation does not imply scientific-certificate preservation when a non-inert scientific obligation has been erased**. Equally importantly, the theorem states when that distinction disappears: discharge all scientific obligations or provide an information-equivalent donor product, and ORION-16-X reduces or ties exactly.

The result does not establish deployed-agent utility, universal scientific semantics, or that these four scientific coordinates are uniquely necessary in every domain. It also does not claim to mechanize every theorem of the donor formalisms represented by the three embeddings.

## Replacement conclusion for V3

ORION-16's broader message is now sharper. Scientific computation can reuse mature truth-maintenance, incremental, effect, authorization, provenance, workflow and execution-attestation machinery without pretending to reinvent it. What must remain explicit is the semantic boundary between **a transition that remains valid in the donor's own operational theory** and **a transition whose scientific certificate is still entitled to stand**.

V2.1 established this distinction through the mechanic contract, reopening/minimality results, preservation/revalidation boundary, faithful composition and a typed-erasure counterexample. ORION-16-X supplies the more general conditional theorem: if a donor-visible forgetful map erases a non-inert scientific certificate coordinate, donor validity may be preserved without scientific admissibility being reflected. The enrichment is conservative when those obligations are discharged, and an ideal product carrying exactly the same information ties extensionally.

That combination—separation, conservative reduction, certificate-continuity conditions, and the explicit ideal-product equivalence boundary—is the current ORION-16 scientific claim. Generic certificates, provenance, effects, authorization and dependency maintenance remain donor-owned; real-system efficacy remains a separate empirical question.

**Current science terminal:** `P6_GENERAL_SCIENTIFIC_CERTIFICATE_SEMANTICS_SUPPORTED__BOUNDED_FORMAL_EMBEDDINGS__IDEAL_PRODUCT_EQUIVALENT`.
