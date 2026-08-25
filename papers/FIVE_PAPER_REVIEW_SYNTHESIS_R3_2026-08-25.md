# Five-paper independent review synthesis R3

> Historical synthesis. Superseded by
> `FIVE_PAPER_REVIEW_SYNTHESIS_R4_2026-08-25.md`; R3 predates the final
> formal-validity and clean-room package passes.

Date: 2026-08-25

## Review protocol

Three passes were kept logically separate before editor synthesis:

1. a hostile proof-and-quantifier pass checked every theorem against its sealed
   claim and evidence boundary;
2. a target-fit pass checked the title, abstract, first-page contribution,
   limitations, availability language, and likely editorial objection; and
3. a reproducibility/surface pass checked executable claims, artifact leakage,
   cross-paper overlap, mathematical typography, and the scientific-closure
   constraint.

This is a simulated review inside the development process, not external peer
review.

## Reviewer findings and dispositions

| Paper | Highest-severity concern | Revision and disposition |
|---|---|---|
| A | Iterative deletion originally omitted an explicit persistence/closure premise, so the simultaneous normal form was under-specified. | Theorem 1 now requires deletion closure plus persistence of nonzero-total, soundness, and dominance assumptions after every edit. The cone is stated as sufficient only. Resolved. |
| B | The five-versus-one separation could be misread as an unrestricted proof lower bound, and the product enumerator as an algorithmic lower bound. | Abstract, theorem discussion, and limitations now bind the result to the rank-only language and a fixed direct-support enumerator. The product is identified as amplification of one mechanism. Resolved. |
| C | Decision sufficiency, value estimation, optimizer recovery, and computational hardness were at risk of collapsing into one claim. | The manuscript now separates the four queries, states both multiplicative conventions, and repeatedly labels the result as information nonidentifiability rather than hardness. Common-padding minimality remains explicitly open. Resolved. |
| D | The prior framing overreached beyond the proved finite positive rule system and lacked a reusable implementation. | The title and prose now describe a finite typed evidence-license component only. A schema, deterministic evaluator, unit tests, exhaustive small-system cross-check, and three case encodings were added. No system-wide authority theory is claimed. Resolved. |
| N | The support-through-22 computation was too close to theorem language, and the paper could be mistaken for a resolution of `D_4(C_5^3)`. | The V3 abstract and main text state the exact open alternatives. The support-ten result remains theorem-grade; the support-22 frontier is bounded evidence pending external replay and is excluded from all proofs. Resolved. |

## Editor synthesis

All five papers have coherent, nonoverlapping identities and target-calibrated
abstracts. Their central claims are visible on the first page, limitations sit
next to the risky inference, and no manuscript contains development history or
publication-decision metadata. Paper D now has the implementation needed to
support its formal-methods target. The non-quantum paper is positioned as a
corridor/obstruction article rather than an exact-constant article.

The editor simulation returns
`simulated_publication_ready_for_target` for A, B, C, D, and N, subject to the
author-only submission boundary recorded in the R3 handoff.

## Family-wide surface decision

- No error-level finding remained under the merged pipeline's strict manuscript
  surface scanner.
- Pandoc parsed every V3 manuscript with single-backslash TeX math enabled.
- Submission files contain no workflow cuts, hardened-draft labels, repository
  paths, PR history, or publication-decision records.
- Paper D contains no use of the retired system-wide framing.
- Cross-paper transfer is limited to explicit citation/context, never evidence
  authority.
