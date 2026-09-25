# ORION-16 recursive editorial refinement R2

**Target:** AIJ Research Note; JAR specialist fallback  
**Input master:** `MANUSCRIPT_REWRITE_FINAL.md`  
**Scientific authority delta:** `NONE`  
**Adoption terminal:** `R2_EDITORIAL_REFINEMENT_COMPLETE__ARTICLE_TYPE_AND_PACKAGE_REBUILD_REQUIRED`

## 1. Editorial diagnosis

The final master now contains two theorem families and one auxiliary commutation result:

1. claim-specific certificate lifting after semantic change;
2. dependency-graph quality laws after structural change;
3. order-independence of fully separated mechanics on the current scientific projection.

The combination is coherent only if the paper is framed around one question: **how prior scientific assurance should be conservatively revalidated after change**. Without that hinge, reviewers may see two formal papers joined by a broad “epistemic mechanics” label.

The main remaining risks are:

- breadth for a Research Note;
- universal-ontology language around the five lift coordinates;
- treating exhaustive finite checking as proof authority;
- treating a true semantic dependency graph as something an ordinary extractor automatically supplies;
- letting the commutation theorem interrupt the primary repair argument.

R2 therefore makes the lifting and graph laws the main body and moves commutation to a compact later section or appendix unless the target editor requests a fuller formal article.

## 2. Title decision

Use:

> **Conservative Revalidation under Scientific Change: Certificate Lifting and Dependency-Graph Quality**

The title unifies the two main theorem families and avoids the vaguer phrase `formal epistemic structures and mechanics`.

## 3. Refined abstract for adoption

Scientific and AI workflows increasingly reuse execution certificates, provenance records, typed effects, authorization receipts, and reproducible traces after the scientific question or system structure changes. Two different errors can follow. A lower-level certificate can remain natively valid while no longer supporting the current scientific claim; and an incomplete or conservative dependency graph can change the safety and amount of revalidation even when the closure rule is correct.

We develop a bounded theory of conservative scientific revalidation. In a registered five-coordinate lifting model, native certificates retain their own verdicts while scientific standing is restored only after every affected claim-specific lift coordinate is revalidated. Complete affected-set repair is sufficient, and every proper subset is unsound for at least one admissible state. The donor-independent checker covers all 31 nonempty affected-coordinate patterns and all 211 strict-subset failures; repeated donor-family realizations are implementation coverage rather than independent evidence.

For structural change, let `G*` be the true finite DAG of semantic dependencies. Over-approximating `G*` is always sound and costs exactly the additional reachable nodes. Under-approximating `G*` is unsound exactly for nodes whose every true path from the change set uses a missing edge. With nonnegative obligation weights, no sound revalidation set can beat the true affected closure. Exhaustive verification over all registered DAGs on three to five nodes finds no violations and includes planted non-degenerate controls. A separate theorem shows that fully separated deterministic mechanics can commute on the current scientific projection while retaining histories that differ by swaps of independent events.

The contribution is a portable set of repair laws, not a universal scientific-state ontology, a guarantee that a real dependency extractor recovers `G*`, or evidence of deployed cost savings. Analytic proofs carry the general authority; finite enumeration and independent implementations test transcription and boundary cases.

## 4. First-page argument

Use this progression:

1. native certificate validity and scientific standing are different judgments;
2. semantic change reopens a claim-specific bridge rather than every native certificate;
3. structural change reopens a dependency closure whose quality depends on the graph;
4. both problems are conservative revalidation under incomplete scientific state;
5. state the lifting repair theorem family;
6. state the graph-quality theorem family;
7. state the real-system nonclaim.

The five-coordinate model should be introduced as a registered finite adapter, not as the paper's ontology proposal.

## 5. Main-text allocation

### 5.1 Main Results

Keep in main text:

- native-validity versus scientific-lift distinction;
- complete affected-set sufficiency and strict-subset countermodels;
- non-laundering product result;
- four graph-quality theorems;
- real extractor versus true semantic graph boundary.

### 5.2 Compress or move

Move detailed donor-loop counts, exhaustive-DAG enumeration totals, solver encodings, kernel proof traces, and most commutation machinery to Methods/appendix. Main text needs only enough detail to show that the controls are non-degenerate and that proof authority is analytic.

### 5.3 Commutation placement

For an AIJ Research Note, place the commutation theorem after the graph laws as an additional consequence of separating current scientific projection from audit history. If page pressure is high, move the full proof and mutation controls to an appendix while retaining one paragraph in the main text.

## 6. Display plan

### Figure 1 — two-layer certificate use

Show:

`native certificate -> native validity`  
`claim-specific lift conditions -> current scientific standing`.

After change, native validity remains green while affected lift coordinates reopen. This figure should prevent readers from interpreting the method as invalidating lower-level provenance or proof systems.

### Figure 2 — graph quality ladder

Three panels:

- `G' superset G*`: sound closure plus exact extra reachable nodes;
- `G*`: minimal sound affected closure;
- `G'' subset G*`: wrongly retained missing-path nodes.

Include nonnegative weights as an annotation showing that weights cannot select a proper sound subset of the true closure.

### Table 1 — theorem authority and assumptions

Rows:

- lifting sufficiency;
- lifting necessity within registered model;
- product non-laundering;
- graph monotonicity;
- over-approximation cost;
- under-approximation failure;
- weighted minimality;
- commutation.

Columns: assumptions, conclusion, authority, executable check, excluded interpretation.

## 7. Terminology discipline

Use **native validity** and **scientific standing** consistently. Use **lift coordinate** only for the registered bridge model. Use **true semantic dependency graph `G*`** rather than `the dependency graph` where authority matters.

Reserve **sound** for inclusion of every affected scientific obligation under the declared semantics. Use **conservative** for over-approximation that may add work but does not omit affected nodes.

Do not call repeated donor-family loops replications. They are implementation realizations of the same 31/211 scientific configurations.

## 8. Desk-rejection stress test

### “This is two papers.”

Repair: one title, one opening problem, and one figure establish conservative revalidation as the common object. Keep the graph law as the structural counterpart to semantic lifting.

### “The five coordinates are arbitrary.”

Repair: present them as a finite registered model used to prove necessity and sufficiency within that model; explicitly allow different adapters in other domains.

### “A real dependency graph is never known.”

Repair: make that limitation a main result boundary. The theorem states what over- and under-approximation imply; it does not certify an extractor.

### “The exhaustive search is doing the proof.”

Repair: state analytic theorems first, give proof ideas in main text, and describe enumeration as an implementation/boundary audit.

### “Weights should reduce revalidation cost.”

Repair: explain that under non-compensatory soundness every sound set contains the true affected closure; weights matter only outside this exact set-selection problem or when obligations can be traded.

## 9. AIJ/JAR package checks

Before adoption:

1. resolve exact article type and target before restructuring length;
2. reconcile every formal statement with its proof and notation source;
3. verify all 31/211 and graph-enumeration counts against generated artifacts;
4. keep proof authority distinct from exhaustive checks in captions and abstract;
5. refresh literature on truth maintenance, incremental computation, dependency-directed revalidation, proof-carrying actions, provenance, and dynamic scientific workflows;
6. rebuild a named arXiv surface and the exact AIJ/JAR target source from one scientific payload;
7. inspect diagrams, theorem numbering, cross-references, bibliography, links and final PDF pages;
8. rerun claim-to-proof, claim-to-PDF, availability, licence, archive, metadata, visual and byte-manifest audits;
9. keep the current green release package authoritative until the R2 adoption is fully bound.

## 10. Final claim ceiling

R2 licenses only:

> In the registered lifting model, complete affected-coordinate repair is sufficient and every strict subset is unsound somewhere; for a true finite dependency DAG, over-approximation is safely conservative with exact extra work, under-approximation fails exactly on missing-path nodes, and the true affected closure is minimum-cost among sound sets under nonnegative weights.
