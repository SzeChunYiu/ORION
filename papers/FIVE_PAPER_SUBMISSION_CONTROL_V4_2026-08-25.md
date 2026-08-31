# Five-paper submission control V4

Date: 2026-08-25
ORION base: `cb3b73f1a971716022b7c5ee25e561b755218a31`
Branch: `codex/orion-publication-rewrite-20260825`
Writing implementation: `academic-paper-skills@8a2ff684eb4b777b88592e57637984f08544f56e`

## Binding scientific closure

`FORMAL_COMPONENTS_ONLY_NO_UNIFIED_CALCULUS`

The five manuscripts remain independent scientific namespaces. No evidence,
proof, novelty, or publication authority transfers merely because terminology
is calibrated across papers. The retired all-in-one novelty claim must not be
restored in a title, abstract, body, cover letter, or submission form.

## Reconstructed source and target map

| Paper | Submission-facing source | Verified parent | Primary target | Current state |
|---|---|---|---|---|
| A | `theory-A-multitag-constraint-rank/MANUSCRIPT_V3_PIPELINE.md` | `MANUSCRIPT_V2.md` + R2 ledger | Quantum | source/PDF package complete; author and archive fields open |
| B | `theory-B-certificate-complexity/MANUSCRIPT_V3_PIPELINE.md` | `MANUSCRIPT_V2.md` + R2 ledger | ACM Transactions on Quantum Computing | source/PDF package complete; author and portal-format fields open |
| C | `theory-C-low-order-information/MANUSCRIPT_V3_PIPELINE.md` | `MANUSCRIPT_V2.md` + R2 ledger | Quantum; QIP fallback | source/PDF package complete; author and archive fields open |
| D | `theory-D-falsification-authority/MANUSCRIPT_V3_PIPELINE.md` | `MANUSCRIPT_V2.md` + R2 ledger | Journal of Automated Reasoning | source/PDF/artifact package complete; author declarations open |
| Non-quantum | `nonquantum-c5cubed-davenport/MANUSCRIPT_V3_PIPELINE.md` | `MANUSCRIPT_V2.md` + R2 ledger | Electronic Journal of Combinatorics | initial PDF package complete; author and archive fields open |

All paths are relative to `papers/`. Each source remains governed by its
colocated `PIPELINE_CONTROL_V3.md` claim/evidence ledger.

## Venue resolution and analogue calibration

### Papers A and C — Quantum

Quantum accepts an arXiv identifier rather than a direct manuscript upload; the
work must be posted or cross-listed in `quant-ph`. It imposes no house format or
length limit at initial submission, but asks that the main result, assumptions,
and contribution be visible in the first pages. Both manuscripts now expose
their theorem scope, negative boundaries, and contribution lists before the
technical development. The generated PDFs are review copies; authors must add
metadata, approve the text, post to arXiv, and supply the arXiv identifier.

Official requirements: <https://quantum-journal.org/instructions/authors/>

### Paper B — ACM Transactions on Quantum Computing

The paper is calibrated as a specialist quantum-compilation theory article:
formal object, exact separation theorem, production controls, and an explicitly
restricted enumeration consequence. The package uses a portable one-column
review layout because the final portal/template configuration must be confirmed
at upload. The claims do not assert an unrestricted algorithmic lower bound.

Journal page: <https://dl.acm.org/journal/tqc>

### Paper D — Journal of Automated Reasoning

JAR covers the theory, implementation, and application of logical reasoning by
computer. Paper D is therefore framed as a finite positive-rule semantics with
a deterministic executable artifact, not as a general theory of scientific
judgment. The abstract is within the 150–250-word requirement; six keywords,
data/code availability, and a declarations checklist are included. The JSON
Schema validates structure, while the evaluator enforces identifier uniqueness
and cross-field referential integrity. Nine unit tests exercise both layers.

Official requirements: <https://link.springer.com/journal/10817/submission-guidelines>
Scope: <https://link.springer.com/journal/10817/aims-and-scope>

### Non-quantum paper — Electronic Journal of Combinatorics

E-JC requests an initial PDF with a self-contained abstract and no page limit;
source is requested only after acceptance. The abstract states background and
principal results without citations. The manuscript repeatedly distinguishes
the theorem-grade support-through-ten result from the unreviewed support-through-
22 computation. Its submission checklist records the journal's requirement
that authors remain responsible for every proof, detail, attribution, and
AI-assisted sentence.

Official requirements and AI policy:
<https://www.combinatorics.org/ojs/index.php/eljc/about/submissions>
<https://www.combinatorics.org/ojs/index.php/eljc/about/index>

## Cross-paper terminology ledger

| Term | Locked meaning | Prohibited inference |
|---|---|---|
| intrinsic support | smallest compiler-wide exact support ceiling plus a matching compiler obstruction | a certificate ceiling is intrinsic without a separate witness |
| certificate complexity | exact ceiling of a named proof/deletion language on its stated production scope | a lower bound for every proof system or algorithm |
| decision certificate | statistic deciding the declared yes/no query | value or optimizer recovery |
| evidence license | declared label propagated by capped positive rules | truth, probability, or broad scientific acceptability |
| bounded computation | exact result for the recorded finite search boundary | theorem authority beyond that boundary or without independent replay |
| support | manuscript-specific structural support | physical gate count, runtime, depth, qubits, or quantum advantage |

## Surface and submission disposition

The academic-paper pipeline passes intake, claim/evidence control, section-level
revision, journal calibration, citation correction, executable-artifact QA,
portable PDF construction, and manuscript surface scanning. The packages are
not represented as accepted or independently peer reviewed.

Actual upload is blocked only by author-controlled facts and scholarly acts:

1. author order, affiliations, corresponding email, and ORCIDs;
2. author approval, contribution statement, funding, conflicts, and ethics/
   declarations where applicable;
3. permanent archive/DOI identifiers for code and verification artifacts;
4. human line-by-line proof review and final novelty assessment;
5. arXiv identifiers for Quantum submissions and current portal/template
   confirmation for ACM/Springer; and
6. confirmation that no manuscript is simultaneously under consideration.

Until those are supplied, the exact terminal state is
`TECHNICALLY_PACKAGED_AUTHOR_SIGNOFF_REQUIRED`, not “accepted,” “peer reviewed,”
or guaranteed top-tier publication.
