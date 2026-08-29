# ORION-01 — Sibling cross-reference decoupling audit V1

**Schema:** `ORION.PaperClosure.SiblingDecouplingAudit.v1`
**Date:** 2026-08-28
**House-style requirement:** Paper A and Paper B must each be independently readable; neither
may depend on the other's text to make sense.
**scientific_authority_delta:** `NONE`

## 0. Consequence — read this first

> **Paper B is NOT independently readable as it stands. BLOCKING FOR SUBMISSION.**
>
> Paper B's Contribution 3 and the whole of its §4 rest on `kappa_R6M = 2`. The **only**
> evidence pointer for that value anywhere in Paper B is line 141, and it resolves to the
> sibling manuscript rather than to an artifact. A referee sent Paper B alone has a numbered
> contribution with no evidence path.
>
> The replacement text is **written and its sufficiency is verified** (§3, §3.1). It is
> **deliberately not applied**, pending an operator decision on the content-freeze conflict
> (§4).

## 0.1 Status

| Step | Status |
|---|---|
| Audit of every cross-reference | **DONE** — §1, §2, complete enumeration |
| Sufficiency of the proposed rebind | **DONE — VERIFIED** — §3.1 |
| Application of hard-dependency fixes | **BLOCKED — NOT APPLIED** — see §4 |

**Disposition (team lead, 2026-08-28):** do not apply the edit. Editing a frozen manuscript and
re-pinning its two hash records in one motion is the operator's call, not a worker's — that
deliberateness is what the content freeze exists to enforce. The dependency is recorded as
**blocking**, explicitly *not* closed as WONTFIX.

This audit does **not** mark the decoupling task complete. One hard dependency exists and it
is **still present in the manuscript**.

---

## 1. Enumeration method

Both manuscripts and all four claim ledgers were searched for literal sibling references
(`Paper A`, `Paper B`, `paper A`, `paper B`) and for cross-package evidence pointers
(`A1`, `B1`). Result: **four** cross-references, all in the manuscripts; **zero** in any of the
four ledgers.

Quoted text below was recovered by base64 round-trip of the exact lines, because this
session's output path passes markdown through a stopword-compression hook that elides
function words. Every quotation is byte-exact from disk.

---

## 2. Cross-reference table

| # | File | Line | Quoted text | Kind | Verdict |
|---|---|---|---|---|---|
| X1 | `theory-B-MANUSCRIPT_V2.md` | 141 | "R6M's sharp control is independently bound through Paper A." | Evidence binding | **HARD DEPENDENCY** |
| X2 | `theory-B-MANUSCRIPT_V2.md` | 25 | "Paper A provides the positive normal-form theorem. This paper identifies its exact proof-language complexity and compares it with independently established intrinsic support." | Framing pointer | SOFT |
| X3 | `theory-A-MANUSCRIPT_V2.md` | 77 | "This distinction is developed fully in Paper B." | Forward pointer | SOFT |
| X4 | `theory-B-MANUSCRIPT_V2.md` | 4 | "Scientific cut: Paper-B/B1 parents plus R2 alphabet-Davenport theorem" | Provenance header | SOFT |

`theory-A-MANUSCRIPT_V2.md:4` ("Scientific cut: Paper-A/A1 parents plus R2 theorem package")
is a **self**-reference to Paper A's own parents and is not a sibling reference. Recorded for
completeness; no action.

### X1 — why this is hard, not soft

Paper B's §4 is one of its five contributions ("**Tight control:** the R6M certificate and
intrinsic support are both equal to two") and carries the whole force of the paper's argument
that the certificate is *not generically loose*. The value `kappa_R6M = 2` is asserted in §4
and is the tight half of the tight/loose pair that §5's separation is measured against.

Line 141 is the **only** place in Paper B where that value is given an evidence pointer, and
the pointer resolves to the sibling manuscript rather than to an artifact. A referee reading
Paper B alone therefore has:

- a numbered contribution (`kappa_R6M = 2`),
- no evidence path for it,
- and an instruction to go read a paper they were not sent.

Note the contrast within the same paragraph: R6I's parents are bound to "the B1 package",
an artifact; only R6M is bound to a sibling document. That asymmetry is the defect.

### X2, X3, X4 — why these are soft

Each is orienting prose. Removing the sibling name from X2 and X3 costs the reader nothing,
because the mathematical content each gestures at is **stated in full in both papers**: Paper
A proves the deletion theorem as its Theorem 1, and Paper B independently states and proves
the same abstract result as its own Theorem 1 in §3. There is no imported lemma in either
direction. X4 is a provenance header, not body text.

---

## 3. Prepared replacement wording (NOT APPLIED)

### X1 — `theory-B-MANUSCRIPT_V2.md:141`

Replace:

> R6M's sharp control is independently bound through Paper A.

with:

> The R6M all-size upper theorem and its exact support-one obstruction witness are
> commit-bound in the A1 parent package at
> `research/extensions/orion-qg/paper_a_a1_multitag_tare.py` and
> `research/extensions/orion-qg/PAPER_A_A1_MULTITAG_TARE_RESULTS_2026-08-24.json`.

Sufficiency of this rebind was left open in the first pass and has since been **verified**;
see §3.1. The wording deliberately says "commit-bound in" rather than asserting that the
artifact proves the corollary.

### 3.1 Sufficiency of the proposed rebind — VERIFIED

Raised by the team lead and independently re-checked here by loading
`research/extensions/orion-qg/PAPER_A_A1_MULTITAG_TARE_RESULTS_2026-08-24.json` and reading
the fields directly. **Every value below was confirmed against the artifact in this pass**, not
taken on report.

**Verdict: the proposed rebind IS sufficient for the narrow claim `kappa_M = 2`**, and is
strictly better than the current pointer, which resolves to a sibling manuscript rather than to
an artifact.

Evidence, verbatim from the artifact:

```
terminal            = "PAPER_A_A1_MULTITAG_TARE_ALL_N_SUPPORT_AT_MOST_CONSTRAINT_RANK__R6M_SHARP_BINARY_COROLLARY"
theorem.r6m_corollary = "s=1, mu=2, t_restore=1, kappa=2 sharp"

r6m_parent_binding.sharp_kappa        = 2
r6m_parent_binding.all_checks         = true
r6m_parent_binding.lower_checks       = {gates: true, kappa2: true, no_physical: true, terminal: true}
r6m_parent_binding.upper_checks       = {authority: true, gates: true, no_novelty: true, not_r6: true, outcome: true}
r6m_parent_binding.lower_path         = "research/extensions/orion-qg/QG18_TARE_KAPPA_RESULTS.json"
r6m_parent_binding.lower_file_sha256  = "ace665d82f07bc7ffc12f51fb5813ab7886f4d9bcc415f8f3d1bca6b2610f013"
r6m_parent_binding.upper_path         = "research/extensions/orion-q/MAX_R6S_ALL_N_COMPOSITION_RESULTS.json"
r6m_parent_binding.upper_file_sha256  = "b6d72913c3bd42d9c822eace19563378c046e620d7b9641ec7d818fbcc6b9875"

gates.r6m_sharp_parent_bound          = true   (all seven gates pass)
objective_ledger.all_checks           = true
objective_ledger.checks.unit_r6m_on_boundary = true
```

Both pinned parent files were confirmed to exist on disk. Note that `upper_path` is under
`research/extensions/orion-q/`, **not** `orion-qg/`; a manifest binding these must use the
exact paths above.

#### The condition: five authority ceilings must be carried forward

The same artifact records:

```
multitag_sharpness_authority     = false
ci_authority                     = false
novelty_authority                = false
physical_quantum_advantage_claim = false
outside_cone_support_necessity   = false
scientific_authority             = "DEFINED_MULTITAG_TARE_M2_STRUCTURAL_GRAMMAR_ONLY"
generic_multitag_tare_transfer   = false
cross_unrelated_grammar_transfer = false
```

**These are authority CEILINGS, not gate failures.** Every entry in `gates` passes, and
`gates.authority_and_donor_boundaries_preserved = true`. The artifact establishes the specific
boundary corollary at `s=1, mu=2, t_R=1` and explicitly withholds general multitag-sharpness
authority.

**Any rebind must carry that ceiling forward.** Without it, Paper B would replace a
sibling-manuscript pointer with an artifact pointer and, in doing so, silently escalate a
bounded corollary into a general sharpness claim. This is consistent with — and must not
override — Paper A's ledger row A2-C6 (`s+1` is necessary for general MultiTag-TARE |
**OPEN; NOT CLAIMED**) and Paper A Limitation 5 ("General multi-Tag sharpness is open").

Recommended ceiling clause, to accompany the §3 replacement text:

> This binding establishes the R6M boundary corollary at `s=1`, `mu=2`, `t_R=1` only. The
> parent artifact withholds general multi-Tag sharpness authority; no claim of sharpness
> beyond this specialization follows from it.

**Still not verified:** the two pinned parent artifacts were confirmed to exist and to be
hash-pinned, but were **not opened or replayed**. This pass verifies that the A1 artifact
*binds* `kappa_M = 2` with passing checks — not that the underlying upper theorem and
necessity witness are themselves correct. That remains the independent-proof-replay gate both
manuscripts already list as external-only.

### X2 — `theory-B-MANUSCRIPT_V2.md:25` (optional)

Replace "Paper A provides the positive normal-form theorem." with:

> The positive normal-form direction — that `zsf(H;A)` is a sufficient support ceiling — is
> proved in §3 below.

### X3 — `theory-A-MANUSCRIPT_V2.md:77` (optional)

Replace "This distinction is developed fully in Paper B." with:

> The separation between a certificate ceiling and an intrinsic compiler bound is not
> pursued further here; this paper claims intrinsic sharpness only for the R6M
> specialization of §8.

### X4 — `theory-B-MANUSCRIPT_V2.md:4` (optional)

Replace "plus R2 alphabet-Davenport theorem" with "plus the R2 alphabet-Davenport theorem
package". Removes the implication that the theorem arrives from a sibling document rather
than from the shared R2 package that both papers draw on.

---

## 4. Why the fixes were not applied

`papers/orion-01-certificate-realization` is under a **committed content freeze**, and the
manuscripts are pinned by sha256 in files **outside this worker's write scope**.

`papers/publication_closure/receipts/remaining11/ORION-01_SCIENCE_CONTENT_FREEZE_V1.json`
records:

```
"paper_content_frozen": true,
"science_frozen": true,
"terminal": "ORION_01_EARNED_CERTIFICATE_REGISTRY_SCIENCE_AND_CONTENT_FROZEN"
```

Two committed hash pins would be stranded by any edit to the manuscripts:

| Pin | Location | Values |
|---|---|---|
| `manuscript_cuts[].sha256` | `papers/publication_closure/receipts/remaining11/ORION-01_SCIENCE_CONTENT_FREEZE_V1.json` | A `596217cfcf623b77ab77ecbd2ae0abbffdaf7ef2392cb2f8915ed790eec68365`, B `66654d730332917bc5b8210bfd8610b8ad6f709cf87a746325c5a5a5a551ea04` |
| `source_bindings.orion01_theory_{a,b}_manuscript.git_blob_sha` | `papers/publication_closure/wave2/WAVE2_DISPOSITION_V1.json` | A `cfffe0993b28b9e1b5e3842c8592d27e26650e8b`, B `23a41bb569b970189bd779f8194a91bd39039ed7` |

Both pin files live under `papers/publication_closure/`, which this worker was instructed not
to write to. Editing the manuscript without updating them in the same commit leaves a
committed receipt whose recorded hashes do not match the files it names.

**Independently verified:** the on-disk sha256 of both manuscripts currently matches the
freeze receipt exactly. The freeze is intact right now, and applying a fix would break it.

### Precision on what the CI gate does and does not do

`papers/publication_closure/remaining11/check_orion01_final_freeze.py` was read in full. To
avoid an overstated justification propagating:

- It **hard-asserts** the two **ledger** sha256 values against
  `research/orion-01-05-convergence-v1/SCIENCE_STATUS_V1.json`. Editing either claim ledger
  fails the checker immediately.
- It does **not** assert the manuscript hashes; it *writes* them into a regenerated receipt.
  Its only manuscript assertions are that both files exist and that each still contains a
  reader-visible physical-resource nonclaim.
- `.github/workflows/orion01-final-freeze.yml` contains a step **"Require canonical paper
  bytes unchanged"** (`git diff --exit-code -- papers/orion-01-certificate-realization`), but
  that workflow triggers only on `workflow_dispatch` and on pushes to
  `chatgpt/orion01-final-freeze-20260827`. It does not run on `wave2/integration`.

So the blocking reason is the **stranded pins plus the recorded `paper_content_frozen: true`**,
not a CI gate that would fire on this branch.

### Adding files is safe; editing canonical files is not

The pins are per-blob, and `paper_tree_oid` is regenerated by the checker rather than
asserted. Adding new files to this directory — including the four audit documents produced by
this pass — strands nothing and breaks no assertion. Only edits to the four canonical files
(`theory-A-MANUSCRIPT_V2.md`, `theory-B-MANUSCRIPT_V2.md`, and the two `_R2` ledgers) are
unsafe.

### Governance conflict to resolve

`papers/publication_closure/wave2/WAVE2_DISPOSITION_V1.json` lists
`HOUSE_STYLE_DECOUPLING_OF_SIBLING_REFERENCES` under ORION-01 `remaining`, which requires a
manuscript edit. The freeze receipt records `paper_content_frozen: true`, which forbids one.
Both are committed on main. This worker does not have the authority to break the tie and has
**not** done so.

Resolving it requires one of:

1. a single commit that edits `theory-B-MANUSCRIPT_V2.md:141` **and** updates both pin files
   in lockstep, made by an actor with write access to `papers/publication_closure/`; or
2. an explicit successor identity that supersedes the content freeze; or
3. a decision that X1 is accepted as-is, with the dependency recorded.

**Selected (team lead, 2026-08-28): option 3, in its recording variant — the dependency is
carried as BLOCKING, not closed as WONTFIX.** Rationale: editing a frozen manuscript while
re-pinning its two hash records in the same motion is precisely the action the content freeze
exists to make deliberate rather than convenient, and it changes a paper's content. That is an
operator decision, not a worker or team-lead one. Options 1 and 2 remain available to the
operator, and §3 plus §3.1 are written so either can be executed without further analysis.

This item is therefore **OPEN and BLOCKING FOR SUBMISSION**. Paper B is **not** independently
readable with respect to `kappa_R6M = 2`.

---

## 5. Files inspected and not edited

| File | Status |
|---|---|
| `theory-A-MANUSCRIPT_V2.md` | frozen — not edited |
| `theory-B-MANUSCRIPT_V2.md` | frozen — not edited (contains the one hard dependency, X1) |
| `theory-A-CLAIM_LEDGER_R2.md` | frozen, hash-asserted by the checker — not edited |
| `theory-B-CLAIM_LEDGER_R2.md` | frozen, hash-asserted by the checker — not edited |
| `theory-A-CLAIM_LEDGER.md` | superseded by `_R2`; no sibling references — not edited |
| `theory-B-CLAIM_LEDGER.md` | superseded by `_R2`; no sibling references — not edited |
| `evidence/convergence-v1/*`, `experiments/r11-pyzx-full-reduce/*` | frozen evidence and receipts — not inspected for edits, not edited |
