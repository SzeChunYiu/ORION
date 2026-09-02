# ORION-01 — Primary-source novelty audit V1

> **V4 status header — added 2026-09-02 (additive; the audit body below is unchanged).**
>
> This audit targeted the **V2-era theory manuscripts** (`theory-A-MANUSCRIPT_V2.md`,
> `theory-B-MANUSCRIPT_V2.md`). The canonical ORION-01 surfaces are now
> `MANUSCRIPT_V4.md` and `CLAIM_LEDGER_V4.md`. Status of this audit's actionable
> recommendations in V4, verified against those files on 2026-09-02:
>
> | Audit recommendation | Status in V4 | Verified basis |
> |---|---|---|
> | Demote A2, B1, B5 from numbered contribution lists (no surviving delta) | Closed in V4 | V4 §1 has no numbered contribution list and states the binary rank identity, Davenport-type theory, proof-system relativity, and direct-product arithmetic are "scaffolds rather than standalone novelty"; §10 calls the product a definitional amplification; ledger O1-V4-C14 marks them FORBIDDEN/DONOR-OWNED. |
> | A1 phrasing ("universal support ceiling for every deletion-dominant grammar") read stronger than the ledger | Closed in V4 | Theorem 2 is stated conditionally on Assumptions 1-4 for declared instance contracts; ledger O1-V4-C2 carries the boundary; the abstract phrases the result as a whole-instance contract and descent. |
> | B4's weight limited by proof review B-F4 (one-rule exactness) | Closed 2026-09-02 | The V4 abstract now names the one-rule scope and the true-by-construction status of the budget's exactness (see `INDEPENDENT_PROOF_REVIEW_V1.md` header, B-F4 row). |
> | Naming collision on "certificate complexity" (audit §3) | Closed in V4 | V4 §5 uses "rank-only certifiable support budget" with an explicit collision-avoidance sentence. |
> | §5 items 1-4 (TARE donor-PDF retrieval; bibliographic verification against CrossRef/arXiv; subset-Davenport naming search; parent-artifact execution) | Open by design — external gates | Not closable from repository files. V4 §13 retains "the author-side checks are not independent proof certification, novelty authority, peer review, or external replication." A submission-day literature refresh remains a filing prerequisite (see `SUBMISSION_CHECKLIST_QIC.md`). |
>
> This header records no novelty authority and does not change
> `novelty_authority_established: false`.

> **Subject-version note (2026-09-02).** This audit's subject is
> `theory-A/B-MANUSCRIPT_V2.md`, **not** the canonical `MANUSCRIPT_V4.md`
> (designated 2026-09-01). Its per-contribution classifications (NO SURVIVING
> DELTA / THIN / SURVIVING) describe the V2 billing, and V4 has since absorbed
> the conclusion into its own text: V4 Section 1 states that the binary rank
> identity, Davenport-type theory, generic proof-system relativity and
> direct-product arithmetic are scaffolds rather than standalone novelty, and
> the V4 claim surface is built on the surviving items only. Do not cite this
> audit's V2 line numbers or contribution list as the live billing; the
> venue-fit consequence is tracked in SzeChunYiu/ORION-paper#78.


**Schema:** `ORION.PaperClosure.PrimarySourceNoveltyAudit.v1`
**Date:** 2026-08-28
**Subjects:** `theory-A-MANUSCRIPT_V2.md`, `theory-B-MANUSCRIPT_V2.md`
**scientific_authority_delta:** `NONE`

## 0. Method and its limits

Working assumption, per the closure brief: **the nearest donor exists**. Davenport constants
and zero-sum sequences over abelian groups, sparse optimal solutions in integer optimization,
proof-system-relative complexity, and certificate/decision-tree complexity are all mature
literatures. Each claimed contribution below is assumed derivative until a residual is
isolated.

**Verification status is reported per reference and is deliberately conservative.** No
external database was queried in this pass. A reference is:

- `CITED-IN-MS` — appears in a manuscript's Selected references with the identifier shown;
  the identifier is recorded, **not** independently confirmed against the publisher.
- `UNVERIFIED` — named here from reviewer knowledge; bibliographic details are **not**
  confirmed and must be checked before any of this text reaches a submission.

This audit is **not** a novelty certificate. The freeze receipt records
`novelty_authority_established: false`; nothing here changes that. It also cannot establish a
submission-date novelty claim, which Paper B's Limitation 7 already assigns to an external
gate.

---

## 1. Donor map

| Donor area | Nearest donor | Status | What it already gives |
|---|---|---|---|
| Zero-sum sequences | Davenport constant `D(G)`; **small Davenport constant `d(G) = D(G)-1`** = max length of a zero-sum-free sequence over `G` | `UNVERIFIED` (standard; see Geroldinger–Halter-Koch, *Non-Unique Factorizations*, 2006 — `UNVERIFIED`) | Exactly the invariant `zsf`, for the full alphabet. Paper A §2 concedes `zsf(H;H\{0}) = D(H)-1`. |
| Subset / generalized Davenport | M. Freeze and W. A. Schmid, *Remarks on a generalization of the Davenport constant*, Discrete Math. 310, 3373–3389 (2010), arXiv:0905.4248 | `CITED-IN-MS` (Paper B only) | Generalized/restricted Davenport constants over selected sequence families. This is the nearest donor for the **subset-alphabet** variant. |
| Weighted / universal zero-sum | G. Wang, *The universal zero-sum invariant and weighted zero-sum for infinite abelian groups*, Commun. Algebra 53 (2025), DOI `10.1080/00927872.2024.2418017` | `CITED-IN-MS` | Flexible invariant frameworks over selected sequence families and weights. |
| `D(F_2^d)` | Olson's theorem for elementary abelian `p`-groups, giving `D(F_2^d) = d+1`, hence `d(F_2^d) = d` | `UNVERIFIED` | Paper A §4 in full, as a special case. |
| Sparse optimal solutions | I. Aliev, J. A. De Loera, F. Eisenbrand, T. Oertel, R. Weismantel, *The Support of Integer Optimal Solutions*, SIAM J. Optim. 28, 2152–2157 (2018), DOI `10.1137/17M1162792` | `CITED-IN-MS` (both papers) | Objective-independent support bounds for integer optimal solutions, and matching lower constructions. |
| Integer-cone support | Eisenbrand–Shmonin, Carathéodory bounds for integer cones | `UNVERIFIED` | Related sparse-support bounds. |
| Proof-system-relative complexity | Cook–Reckhow, *The relative efficiency of propositional proof systems*, JSL (1979) | `UNVERIFIED` | The entire "what a restricted proof system can certify, versus the object's true difficulty" framing. Donor-owned outright. |
| Certificate complexity `C(f)` | Nisan (1991); Buhrman–de Wolf survey, *Complexity measures and decision tree complexity* (2002) | `UNVERIFIED` | The established meaning of "certificate complexity", in the `s(f)`/`bs(f)`/`deg(f)` web. See §3. |
| Pauli symplectic algebra | Standard stabilizer formalism (Dehaene–De Moor; Aaronson–Gottesman) | `UNVERIFIED` | The `F_2` symplectic-product signature machinery of Paper A §5. |
| Donor primitive | N. Schillo, A. Sturm, R. Quay, *TARE: Block Encoding Linear Combinations of Pauli Strings Without Ancilla State Preparation*, arXiv:2601.05740v4 (2026) | `CITED-IN-MS`, `UNVERIFIED` | The upstream construction. Paper A §1 explicitly assigns it no novelty. Post-dates this reviewer's knowledge; **cannot be confirmed here at all** — flagged for the external donor-PDF audit already listed as an external-only gate. |

---

## 2. Per-contribution residual

### Paper A

| # | Claimed contribution | Closest donor | Residual delta |
|---|---|---|---|
| A1 | Alphabet-Davenport deletion theorem: `zsf(H;A)` is a support ceiling for deletion-dominant grammars | Small Davenport constant, restricted to a subset alphabet | **THIN — instantiation only.** The mathematical core ("a word longer than `d`-restricted-to-`A` has a zero-sum subsequence") *is* the definition of the invariant. Nothing is proved about `zsf` that the donor does not already give. What survives is the identification of a compiler deletion argument as an instance, plus Assumptions 1–3 as the transfer conditions. Ledger row A2-C9 already concedes this ("DONOR-OWNED / Residual is compiler instantiation and accounting") and the concession is **correct**. Contribution 1 as phrased in §1.1 — "a universal support ceiling for every deletion-dominant grammar" — reads stronger than the ledger allows. |
| A2 | Binary rank corollary: `zsf(F_2^d;A) <= d`, equality with a basis | Olson: `d(F_2^d) = d`; plus elementary linear dependence | **NO SURVIVING DELTA.** Both directions are textbook. "Every word longer than `d` over `F_2^d` is dependent" is first-course linear algebra; "a basis is zero-sum-free" is immediate. This is a worked special case, correctly labelled a corollary, and should not be listed as a contribution. |
| A3 | Exact arbitrary-block Restore sensitivity `b-1` and the cone `mu >= (b-1)t_R` | None found | **SURVIVING.** `F_b` is the authors' own functional; its exact one-argument sensitivity and the resulting objective cone are not statements the donor literature can contain. Mathematically elementary (a finite case check — see proof review C5) but genuinely theirs. |
| A4 | `kappa_R6M = 2` | None found | **SURVIVING, contingent.** Specific to the frozen one-Tag/three-block R6M grammar. Depends entirely on the A1 parent upper theorem and necessity witness; see §5. |
| A5 | Boundary semantics (alphabet ceiling / realized rank / intrinsic support / cone / physical resources) | Cook–Reckhow | **THIN.** The proof-language-versus-object distinction is donor-owned. The residual is the specific five-way taxonomy instantiated on compiler support, which is expository rather than mathematical. |

### Paper B

| # | Claimed contribution | Closest donor | Residual delta |
|---|---|---|---|
| B1 | Exact abstract certificate theorem: terminal complexity of the deletion language is `zsf(H;A)` | Definition of zero-sum-free; same donor as A1 | **NO SURVIVING DELTA.** Under nonzero total, "terminal" and "zero-sum-free" are the same predicate (see proof review B-F2), so Theorem 1 restates the definition. The manuscript itself says so — §3: "This theorem is generic zero-sum mathematics." That sentence is accurate and should govern how Contribution 1 is billed. |
| B2 | Realization criterion: a compiler inherits the lower bound only if it realizes a maximum zero-sum-free word | Standard lower-bound methodology (an extremal witness transfers only if realizable) | **THIN.** Methodologically routine. The residual is its explicit statement as an obligation for compiler support claims. |
| B3 | Tight control: `beta_rank-only(R6M) = kappa_R6M = 2` | None found | **SURVIVING, contingent.** |
| B4 | Strict separation: `beta_rank-only(R6I) = 5`, `kappa_R6I = 1` | None found | **SURVIVING — this is the real contribution of the pair.** A *matched* tight/loose pair on the same certificate schema, where one production family aligns and another separates by 5-to-1, is the one thing here that no donor supplies. Its weight is limited by proof review B-F4: exactness is relative to a one-rule proof system. |
| B5 | Product/search amplification: `5t` vs `t`, ratio `Theta(n^(4t))` | Direct-sum behaviour of zero-sum invariants (donor); the product's own definition | **NO SURVIVING DELTA as mathematics.** The result follows from defining the product with additive support budget and no cross-component move. Ledger row B2-C8 already forbids reading it as a second mechanism. It is a legitimate corollary, not a contribution. |

---

## 3. Naming collision — report, not a novelty loss

Paper B uses **"certificate complexity"** for `beta_P(F,C)`, the least uniform support budget a
proof system can certify. In complexity theory, `C(f)` — certificate complexity of a Boolean
function — is a standard and entirely different object. A referee from that community will
read the title and abstract against the established meaning.

This costs no novelty. It will cost comprehension. Recommend either a disambiguating sentence
at first use or a distinct term (e.g. *certifiable support budget*). `UNVERIFIED` on the exact
bibliographic details of the donor line (Nisan 1991; Buhrman–de Wolf 2002).

---

## 4. Bottom line

**The surviving mathematical residue of the two-paper pair is narrower than the ten listed
contributions suggest.** Of ten:

- **No surviving delta (3):** A2, B1, B5 — restatement, textbook special case, and a
  definitional corollary respectively. Each is honestly described *inside* the manuscript
  body, but each is nonetheless billed as a numbered contribution in §1.1.
- **Thin / instantiation only (3):** A1, A5, B2.
- **Surviving (4):** A3, A4, B3, B4 — with B4 the substantive one.

The recommended framing follows from that split: **the pair's contribution is the matched
tight/loose compiler pair (B3/B4) plus the exact `F_b` sensitivity and cone (A3), instantiated
on a donor-owned invariant.** Contributions A2, B1 and B5 should be demoted from the numbered
lists to the body text where their honest descriptions already sit. Paper A's §9 and Paper B's
§7 already give correct donor credit; the defect is only in the contribution lists.

## 5. What this audit could not verify

1. **arXiv:2601.05740v4 (TARE).** Post-dates this reviewer's knowledge and was not retrieved.
   The donor primitive underlying Paper A §5 is therefore entirely unchecked here. Settled by
   the full donor-PDF audit already listed as an external-only gate in both manuscripts.
2. **Every reference's bibliographic accuracy.** Identifiers are recorded as printed. Settled
   by a citation check against CrossRef/arXiv.
3. **Whether the subset-alphabet Davenport variant is already named in the literature under
   another convention.** Paper A §2 anticipates this ("we use the explicit `zsf` notation to
   avoid conflating it with several established weighted, universal, or subset Davenport
   conventions") but does not resolve it. If a published subset-Davenport invariant coincides
   with `zsf`, A1's residual narrows further, to instantiation alone. Settled by a targeted
   search of the Freeze–Schmid and Wang citation neighbourhoods.
4. **The A1/B1 parent results themselves.** See `JOURNAL_PACKAGE_STATUS_V1.md` §4; A4, B3 and
   B4 are contingent on parents this pass did not execute.
