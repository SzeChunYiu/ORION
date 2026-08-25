# ORION publication rewrite development packet

Date: 2026-08-25

Status: historical intake and authority-reconciliation record. Final manuscript
dispositions, narrowed targets, source hashes, and release QA are superseded by
`papers/FIVE_PAPER_ATOMIC_VERIFICATION_V7_2026-08-25.md` and
`papers/FIVE_PAPER_REVIEW_SYNTHESIS_R4_2026-08-25.md`.

## Frozen inputs

- ORION checkout: `/workspace/scratch/d9c618f2e1ef/orion-publication-rewrite`
- Rewrite branch: `codex/orion-publication-rewrite-20260825`
- ORION base commit: `cb3b73f1a971716022b7c5ee25e561b755218a31`
- Academic-paper-skills merge commit: `8a2ff684eb4b777b88592e57637984f08544f56e`
- Academic-paper-skills final implementation head: `680165e0b315093c5d82b6ae7c9dfaf03151c750`
- Imported publication portfolio SHA-256:
  `6d16b4d27a07410644ecf3f836d9fe7c580f912fed0ff461458168fcb45c98a6`
- Imported ownership-map Markdown SHA-256:
  `592ca96ccc2a4eb41361c136fa5a1ea4f6b8b08e109e4c08b01d3884d82ff797`
- Imported ownership-map JSON SHA-256:
  `e582085e2c3aa7b9c6e73731fb9308363b78bb8174f0bf30dd8b8c5e8ac87ad1`

The three imported handoff artifacts are preserved byte-for-byte and remain
untracked until their authority is adjudicated. They are a draft control
overlay, not yet repository authority.

## Scientific closure and non-goals

The global closure constraint is binding:

`FORMAL_COMPONENTS_ONLY_NO_UNIFIED_CALCULUS`

All five manuscripts must remain separate claim namespaces. No manuscript may
state or imply a universal or unified calculus for diagnosis, belief revision,
sufficiency, metareasoning, or scientific authority. A typed, versioned,
non-authorizing interface for scientific-admissibility components is allowed
only when scoped to the concrete compiler or protocol under discussion.

This pass will not:

- revive the struck universal-calculus novelty claim;
- transfer evidence or authority between papers merely because terminology is
  shared;
- promote finite searches, local replays, or machine certificates to general
  theorems without the corresponding proof authority;
- claim hardware, time, depth, qubit, or population-level advantage from
  compiler counts or registered-panel results alone;
- edit or import the concurrent `shadow/theory-abcd-completion-20260824`
  branch until its payload is complete and independently verified.

## Atomic development questions

1. Which repository paths are the authoritative sources for A, B, C, D, and
   the non-quantum paper?
2. Which branch or worktree owns each manuscript, and are there concurrent
   implementations that supersede or conflict with this handoff?
3. Which claims have proof, computation, provenance, and target-journal
   authority, and which are merely candidates or finite observations?
4. What is the narrowest defensible paper identity and target journal for each
   manuscript?
5. Which claim, evidence, figure, source, and concern ledgers must be frozen
   before prose generation?
6. What evidence would move each paper from its current terminal state to
   `simulated_publication_ready_for_target`?

## Reconstructed manuscript intake

### Paper A — shared-tag TARE normal forms

- Authoritative source candidates:
  - `papers/Q-paper-01-tare-expressivity/MANUSCRIPT_V3_REFINED.md`
  - `papers/Q-paper-01-tare-expressivity/MANUSCRIPT_SUBMISSION_DRAFT.md`
  - `papers/Q-paper-01-tare-expressivity/manuscript/main.tex`
  - archived QG1 material only where provenance is explicit
- Current branch/worktree: repository `main` material at the frozen base;
  rewrite lane `codex/orion-publication-rewrite-20260825`.
- Current status: rewrite from scratch. The current main draft changed the
  framing to “Constraint-Rank Normal Forms for Shared-Tag TARE Quantum
  Compilation” and must be reconciled with the handoff portfolio before it is
  treated as the paper identity.
- Target: `Quantum` only after proof blockers close; fallbacks `Quantum Science
  and Technology` or `ACM Transactions on Quantum Computing`. `PRX Quantum` is
  not justified without a broader theorem.
- Admissible core: scoped A01–A06 claims and active
  `kappa_R6M = 2` result, subject to ledger verification.
- Blocked/forbidden surface: A07 all-n three-family classification without its
  proof chain; objective-independent support-two claims; generic sparsity or
  priority claims; physical time, runtime, depth, or qubit advantage.
- Intake terminal: `current_claims_not_established` until the proof and
  authority ledgers are frozen.

### Paper B — intrinsic support numbers

- Authoritative source candidates:
  - `papers/QG-paper-03-intrinsic-support-numbers/MANUSCRIPT_V1.md`
  - `papers/QG-paper-03-intrinsic-support-numbers/CLAIM_LEDGER.md`
- Current branch/worktree: repository `main` material at the frozen base;
  rewrite lane `codex/orion-publication-rewrite-20260825`.
- Current status: rewrite from scratch. `kappa_R6I = 1` and the support-ladder
  constructions are active; the inherent 5-vs-1 or 2-vs-1 proof-system lower
  bound is not established.
- Target: a TQC/specialist venue now; `Quantum` only after a formal lower bound;
  `PRX Quantum` only after a parameterized result.
- Intake terminal: `scientifically_sound_but_target_mismatch` for the current
  high-tier framing, with the lower-bound claim blocked.

### Paper C — fixed-six SixLCU theorem

- Authoritative source candidates: no standalone manuscript currently exists;
  extract only the SixLCU material with explicit provenance from archived QG1.
- Current branch/worktree: repository `main` archive at the frozen base;
  rewrite lane `codex/orion-publication-rewrite-20260825`.
- Current status: construct a new standalone manuscript. C01 is the active
  fixed-six all-instance theorem. C02–C04 are finite observations. Retracted
  QG32, QG34, QG35, and QG39 are excluded; QG41 is a control only.
- Target: `Quantum` after an m-term theorem or a real PREPARE/SELECT result;
  otherwise QIP/TQC.
- Intake terminal: `blocked_on_author_evidence` for the broader target framing.

### Paper D — certified static forecasting

- Authoritative source candidates:
  - `papers/QG-paper-02-certified-static-forecasting/manuscript/main.tex`
  - `papers/QG-paper-02-certified-static-forecasting/MANUSCRIPT_V3.md`
- Current branch/worktree: repository `main` material at the frozen base;
  rewrite lane `codex/orion-publication-rewrite-20260825`.
- Current status: hold/archive as a technical report. The 9545/9546 result is a
  deterministic registered-panel outcome, not population accuracy; the exact
  10 < 11 comparison is a falsifier. Any “authority calculus” language must be
  compiler-scoped and must not imply a universal calculus.
- Target: no journal submission until an authority-survival theorem, a second
  independent compiler, or a real framework integration exists.
- Intake terminal: `blocked_on_author_evidence`.

### Non-quantum paper — zero-sum problem in C5^3

- Authoritative source candidates: the X1F/X1F4 protocols, certificates,
  results, and associated donor-search records. No standalone manuscript is
  currently authoritative.
- Current branch/worktree: repository `main` material at the frozen base;
  rewrite lane `codex/orion-publication-rewrite-20260825`.
- Current status: candidate machine-checked `D_3(C_5^3) = 25` result, not yet
  proof or novelty authority. The 1405-class census is supporting evidence.
  Spectrum conflicts at T = 9, 11, and 12 require diagnosis. A human proof and
  independent certificate remain required.
- Target: `Journal of Number Theory` or `Electronic Journal of Combinatorics`
  after proof; `Integers` fallback. `Journal of Combinatorial Theory, Series A`
  requires a structural theorem.
- Intake terminal: `blocked_on_author_evidence`.

## New-main reconciliation items

The frozen ORION base contains work that postdates the imported ownership map
and therefore cannot silently enter a manuscript:

- Paper A's submission draft now uses constraint-rank framing and a generalized
  theorem presentation. Its proof, source, and novelty authority must be
  audited against the A ledger.
- New non-quantum M1–M3 results are not among the ownership map's 48 objects:
  - M1 gives `5k + 10 <= D_k(C_5^3) <= 5k + 11` for `k >= 4`, with a
    conditional tail if `D_4 = 30`.
  - M2 gives a saturation-defect lemma and excludes support at most 9 for the
    stated length-31 object, but is a post-outcome local dual replay.
  - M3 excludes support 10, hence yields support at least 11 if such an object
    exists, but is also a post-outcome local dual replay.
  These are donor mathematics or supporting lemmas, not automatically ORION
  novelty, and they do not decide `D_4`.

## Concurrent implementation disposition

Open ORION pull request #1181, branch
`shadow/theory-abcd-completion-20260824`, claims to complete manuscripts A–D.
Its visible change consists of two base64 payload fragments. At intake, their
lengths were 13,819 and 13,818 characters; the 27,637-character concatenation
has length congruent to 1 modulo 4 and fails base64/gzip/tar decoding with
premature end-of-file. A partial archive listing names A–D files, but the
content cannot be reconstructed or verified.

The concatenated payload was recovered only to the last complete tar member.
Ten protocol/report files were readable; result ledgers were absent, Paper A's
verifier could not be bound to its claimed results, and Paper B's verifier was
itself corrupted. The recoverable documents were inspected for conflicts, but
the payload is not admissible as an implementation source and is not imported.

Current `main` independently contains a complete R2 five-paper authority wave
at commit `3f363fb4b02320a88872a2e2872479847c2b1329`. Its deterministic verifier
reproduces the committed result object exactly. That R2 wave supersedes the
broken transport as the implementation source. This codex lane will provide a
clean replacement PR; only after that replacement is available should PR #1181
be closed as superseded.

## R2 authority reconciliation

The following current-main sources are now the direct V3 parents:

- `papers/theory-A-multitag-constraint-rank/MANUSCRIPT_V2.md`
- `papers/theory-B-certificate-complexity/MANUSCRIPT_V2.md`
- `papers/theory-C-low-order-information/MANUSCRIPT_V2.md`
- `papers/theory-D-falsification-authority/MANUSCRIPT_V2.md`
- `papers/nonquantum-c5cubed-davenport/MANUSCRIPT_V2.md`
- the matching five `CLAIM_LEDGER_R2.md` files;
- `papers/FIVE_THEORY_HARDENING_R2_RESULTS.json` and
  `papers/verify_five_theory_hardening_r2.py`.

The R2 wave closes the intake uncertainties as follows: Paper A has the
alphabet-restricted generalized theorem and the sharp frozen R6M corollary;
Paper B preserves the unrestricted-proof-system lower bound as open; Paper C
has the all-`m >= 5` decision theorem plus sharp value-estimation lower bounds;
Paper D has finite positive rule-graph fixed-point and retraction theorems but
must be reframed as a bounded component rather than an authority calculus; and
the non-quantum paper has a human-proof corridor, structural obstruction phase,
and clearly separated bounded computation while leaving `D_4(C_5^3)` open.

## Bounded saturation assessment

- Knowledge: the handoff portfolio, the 48-object ownership map, current-main
  manuscript sources, the recoverable portion of PR #1181, the R2 theorem wave,
  and the merged academic-paper pipeline have been read. The corrupted PR is
  inadmissible and superseded by the independently verified current-main wave;
  A and M1–M3 are reconciled in the five sealed V3 controls.
- Search universe: bounded to the ORION repository's manuscript, protocol,
  result, certificate, and archive paths plus explicit donor records. External
  novelty search belongs to a later per-paper source-ledger pass.
- Formulation: the five paper identities and their cross-paper overlap boundary
  are sealed in the R3 handoff.

### Challenge to the saturation basis

Repository recency is not scientific authority. A newer draft or result file
can still carry unproved generalization, post-outcome scope, or donor-only
mathematics. Conversely, an archived source can remain the only provenance for
an admissible theorem. File timestamps and PR titles will not substitute for a
claim/evidence audit.

### How the search could be falsely flat

- Scientific claims may be hidden in generated PDFs, archives, or payloads
  rather than the named Markdown/TeX sources.
- Identical terminology may mask different quantifiers or proof systems across
  A–D.
- A negative search for prior art may reflect an overly ORION-specific
  vocabulary.
- Machine certificates may validate instances without establishing the human
  theorem or novelty boundary used in prose.
- A concurrent branch may contain the actual latest proof even when its current
  transport representation is unreadable.

## Frozen implementation hypothesis

Before rewriting prose, create and approve one sealed control bundle per paper:

1. identity and target card;
2. claim ledger with quantifiers, scope, status, and forbidden paraphrases;
3. evidence ledger linking each claim to proofs, data, certificates, and
   provenance;
4. source ledger separating prior work, donor work, and ORION contributions;
5. figure/table ledger;
6. editor/reviewer concern ledger;
7. target-specific surface and length constraints.

Only after all five bundles and the family-wide terminology/overlap ledger are
frozen should the pipeline draft, review, synthesize, revise, and run manuscript
surface QA. Cross-paper processing is limited to terminology consistency,
contradiction detection, contribution-overlap control, and justified
cross-citation; evidence and claim authority never transfer across namespaces.

## Reopen triggers

Reopen intake and do not draft if any of the following occurs:

- PR #1181 becomes decodable, changes head, merges, closes, or is superseded;
- ORION main changes a manuscript source, protocol, proof, result, or
  certificate used by any paper;
- the ownership map is adopted, rejected, or amended;
- Paper A's generalized constraint-rank theorem lacks a complete proof chain;
- a non-quantum M1–M3 item is assigned novelty or manuscript ownership;
- a reviewer identifies a cross-paper claim leak or a universal-calculus
  implication;
- an exact claim lacks source/evidence authority or changes quantifiers during
  prose revision.

## Verification plan after intake closes

For each paper, run the academic-paper pipeline independently through source
normalization, claim/evidence locking, target calibration, drafting, blind
review, editor synthesis, revision, and surface QA. Preserve every blocker and
terminal state. The only success state is
`simulated_publication_ready_for_target`; scientific soundness without target
fit is reported as such rather than upgraded.

The final family pass checks only terminology, contradiction, overlap, and
cross-citation. It must also scan every title, abstract, body, caption,
supplement, cover letter, highlight, and metadata surface for forbidden
unified/universal-calculus language.

## Completion record

- Five submission-facing V3 manuscripts and five sealed pipeline controls are
  present under the verified paper directories.
- `papers/verify_five_theory_hardening_r2.py` returns `all_checks=true`.
- Paper D's reusable evaluator passes six unit tests, including exhaustive
  least-fixed-point comparison on 80 random bounded systems; all three case
  encodings evaluate with the intended nonpromotion behavior.
- `papers/verify_five_publication_pipeline_r3.py` returns `all_checks=true`.
- All five manuscripts parse with Pandoc's single-backslash TeX-math reader.
- The merged academic-paper pipeline's strict surface scanner reports zero
  error-level findings on the five V3 manuscript surfaces.
- The family editor simulation records
  `simulated_publication_ready_for_target` separately for A, B, C, D, and N,
  subject to the author-only metadata, disclosure, archive, and external-review
  boundary in the R3 handoff.
