# ORION-17 — prospective density prediction: result

**Paper:** ORION-17 — Epistemic Navigation in Open Worlds
**Successor id:** `ORION17.DENSITY_PROSPECTIVE.v1`
**Predictions stamped:** commit `1db5eaa46`, `2026-08-28T19:22:36Z`
**Status:** `PROSPECTIVE_PREDICTION_CONFIRMED__5_OF_5_INCLUDING_THE_DISAMBIGUATOR`
**Scientific terminal:** `READY_TO_SUBMIT_TOP_TIER` (evidence)
**Filing terminal:** `BLOCKED__NO_STANDALONE_MANUSCRIPT` (see final section)
**Scientific authority delta:** `NONE`

---

## 1. Ordering, which is the whole point

| step | artifact | time (UTC) |
|---|---|---|
| import graphs only, no policy evaluated | `HELD_OUT_DENSITY.json` | 19:20:17 |
| **predictions committed to history** | commit `1db5eaa46` | **19:22:36** |
| policy outcomes produced | `HELD_OUT_RESULT.json` | 19:23:30 |

The density pass calls only `build_import_graph`; it never evaluates a policy. The
outcomes did not exist when the predictions were committed, and the threshold
`1.5` fixed in `STAMPED_PREDICTIONS.md` was never moved.

## 2. Outcome

Rule: predict `donor-coarse` unsound iff `import_edges / modules >= 1.5`.

| package | organization | modules | edges/module | predicted | **observed** | donor false retentions | exact |
|---|---|---|---|---|---|---|---|
| requests | psf | 19 | 0.84 | sound | **sound** | 0 | 0 |
| networkx | networkx | 583 | 2.14 | unsound | **unsound** | 91,507 | 0 |
| django | django | 906 | 3.68 | unsound | **unsound** | 63,398 | 0 |
| tornado | tornadoweb | 74 | 5.57 | unsound | **unsound** | 12,773 | 0 |
| sympy | sympy | 1,566 | 8.70 | unsound | **unsound** | 344,352 | 0 |

**5 of 5 correct**, on five packages from five organizations, none of them numpy,
scipy or flask.

`exact-containment` falsely retains nothing on any of the five, consistent with
the pairwise and arbitrary-length composition theorems.

## 3. The confound is resolved

The frozen campaign's only sound domain, flask, was both small (24 modules) and
sparse (0.79), so size and density were confounded and the §4 attribution in
`ORION17.CLOSURE_CHAIN_COMPOSITION.v1` could equally have been a size effect.

`tornado` was registered in advance as the case that separates them: 74 modules —
small, three times flask, far below numpy — but 5.57 edges/module, denser than
numpy or scipy.

- density rule predicted **unsound**;
- a size-based explanation predicted **sound**;
- observed: **unsound**, 12,773 false closure retentions.

**Density carries the effect, not size.** The attribution that was explanatory
when written is now a confirmed prediction on held-out systems.

## 4. What this is worth, and its limits

This converts ORION-17's one post-hoc observation into a prospectively validated
mechanism claim. It does **not** convert the arbitrary-length composition
theorem's status: `CLAIM_LEDGER_V4.md` row `ORION-17.V4.5` already owned that
result, the earlier packet's contrary framing stays retracted, and nothing here
reinstates it.

Scope, stated exactly:

- The claim is about **Python import graphs** under this campaign's construction.
  Whether `1.5` transfers to other ecosystems is untested; the threshold is
  calibrated on three domains and validated on five.
- `requests` repeats flask's small-and-sparse confound and so adds little beyond
  `tornado`; the disambiguation rests on `tornado` alone.
- The mechanism claim is about **where `donor-coarse` fails**, not about the
  magnitude of failure, which varies over two orders of magnitude across the five.
- The naturalistic multi-hop study of blueprint §4.12 is still **not run**. This
  lane does not substitute for it and does not claim to.

## 5. Convergent boundary, found independently

ORION-16's real-system discriminator, run separately, found that on
nf-core/rnaseq — a shallow pipeline graph — the cheap `direct-neighbours` policy
strands nothing and exact closure buys nothing over it. That is the same boundary
in a different formalism and a different ecosystem: **cheap approximations are
adequate on sparse or shallow dependency structure and unsound on rich structure.**
Neither result was used to tune the other.

## 6. Authority

`scientific_authority_delta = NONE`. The frozen three-domain campaign, its
policies, counts and every `CANNOT_CHECK` are untouched; the five held-out
packages are additive. No manuscript, ledger or `submission/` byte is modified,
and no `CANNOT_CHECK` is converted.

## 7. Independent verification

`independent_checker/check_density_prediction.py` re-derives each verdict from the
recorded density and campaign files, imports no ORION-17 module, and re-runs no
campaign. Four checks and four negative controls, all firing, including that an
inverted rule scores strictly worse and that a size-based rule mispredicts at
least one case. `CANNOT_CHECK` exits 3 and is never reported as a pass.

## 9. Packaging status — no venue-format manuscript exists

The scientific package described above is complete and independently verified.
**The submission package is not**, and the terminal above should be read as a
statement about the evidence, not about readiness to file.

The only manuscript artifact is `manuscript/main.pdf`, which renders as
*"Working framework draft"* over historical base documents. It is an internal
versioned working document: it carries no venue template, no author block, no
abstract/introduction/related-work structure in submission form, and no
anonymisation. `JOURNAL_READINESS_V2.md` records the same gap from the other
side — its *"convert Markdown manuscript to venue template and perform
copyedit/reference-format pass"* item is unchecked.

Accordingly the operative terminal for filing is:

**`BLOCKED__NO_STANDALONE_MANUSCRIPT`**

The distinction from a paper that merely needs re-typesetting is evidential:
this `main.tex` leads with `sections/01-replacement-abstract`, contains no
`\begin{abstract}` environment, and has no introduction or related-work section.
A complete manuscript in the wrong template needs mechanical work; this needs
authorial work.

This is a manuscript-preparation blocker, not a scientific one. Nothing in the
evidence is missing or undetermined because of it, and no experiment is required
to clear it. What is required is writing: converting the working framework into a
venue manuscript under the `nature-*` skills protocol, then a copyedit and
reference-format pass.
