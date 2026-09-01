# ORION-17 `BLOCKED__NO_STANDALONE_MANUSCRIPT` — the route, and why it is an operator decision

**Written:** 2026-09-01. **Authority delta:** `NONE`. This document decides nothing;
it records a verified mechanism and hands the decision to the operator.

## What is left after the density packet lands

`PUBLICATION_DISPOSITION_MATRIX_V1.md` row 17 names three conditions for ORION-17 to
leave `NO_BOX_EARNED_ON_MAIN`: *"land packet path-by-path, adjudicate governance,
write standalone manuscript."*

The density packet landed on `main` in PR #1821, at
`papers/publication_closure/orion17-density-prospective-v1/`, which discharges the
first two. It carries `GOVERNANCE_ADJUDICATION_V1.md`, which adjudicates the #1649
one-shot conflict — finding the result admissible rather than a forbidden rescue,
because #1649's stop fired on a different object, the arbitrary-chain theorem owned by
V4.5 — and yields `TOP_TIER_SUCCESSOR_NOT_SUPPORTED__BOUNDED_RETAINED`.

The packet sits outside `papers/orion-17-*/` rather than inside it, for the binding
reason `RELOCATION_V1.md` records. That placement does not weaken the discharge: the
matrix asks for the packet to be *on main*, which it now is.

The third condition stays open. `RESULT.md` carries the filing terminal
`BLOCKED__NO_STANDALONE_MANUSCRIPT` and is unusually clear about what kind of blocker
it is: the only manuscript artifact is a working framework draft, `main.tex` leads
with `sections/01-replacement-abstract` and contains no `\begin{abstract}`
environment, no introduction and no related-work section. *"Nothing in the evidence is
missing or undetermined, and no experiment is required to clear it."* What remains is
writing — converting the working framework into a venue manuscript under the
`nature-*` skills protocol, plus a copyedit and reference-format pass.

So this is not a science gap. It is a manuscript-preparation gap sitting behind a
binding wall.

## Why it cannot simply be written

Every one of the 24 files under `papers/orion-17-epistemic-navigation-open-worlds/manuscript/`
is bound in `CONTENT_MANIFEST_V2.json` — `main.tex`, all eight `sections/*.tex`,
`bibliography.bib`, and the PDFs included. `_subject_identity` resolves each of the
123 bound files through `git show 2b4cde64…:{path}`, so ORION-17's tree is
**byte-frozen, not merely addition-frozen**: editing a bound file breaks the pin
exactly the way adding an unbound one does.

Repinning is not available inside a single pull request. This repository
squash-merges, so a `subject_commit` written on a branch names a commit that is
destroyed at merge, and
`tests/unit/programme/test_content_binding_pin_is_reachable.py` exists to catch that
class. New manuscript bytes exist at no commit on `main`, so there is no reachable
commit to pin them to.

## The mechanism that does work, verified against history

The pin history of ORION-17's V2 manifest shows the repository has already solved
this, twice, with a two-pull-request sequence:

| commit on `main` | pull request | pin it carried |
|---|---|---|
| `2b4cde640` | #1987 — rebuild ORION-06/17/18 PDFs, re-pin 17/18 | `43c9eacba75a` (branch commit, destroyed at merge) |
| `add541c6d` | #1989 — pin content-binding subjects to a main-reachable commit | `2b4cde64084b` (now on `main`) |

PR A changes the bound bytes and rebinds the digests; its pin is necessarily stale.
PR B then pins to PR A's squash commit, which by then exists on `main`.

The intermediate state need not be red. `test_current_tree_is_classified_target_by_target`
asserts an exact per-candidate tally, and P8's expected tally is already
`{"BOUND": 7, "PARTIAL": 1, "CANNOT_CHECK": 1, "DEFERRED": 1}` on green `main`. The
schema models a declared-partial target as legal, and line 60 requires every non-BOUND
target to carry a non-empty `blocker` string, so the partial state must be stated
rather than merely tolerated. PR A can therefore land green by declaring P7 partial
with its blocker; PR B restores the tally to `BOUND` when the pin becomes reachable.

## Why an implementer should not take this route unilaterally

The tally in `expected_counts` is a ratchet. Its whole function is to name which
papers are permitted to sit at `PARTIAL`, so that a paper drifting into that state is
noticed. Loosening it for ORION-17 means authoring the exemption, consuming it, and
depending on one's own follow-through to revert it — with nothing outside that
follow-through enforcing PR B. If PR B never lands, `main` carries a permanently
partial ORION-17 and the only check that would have objected was removed by the same
hand that made it necessary.

This compounds an existing designation. Refreshing ORION-17's manuscript surface is
already recorded as an operator decision rather than an implementer's call, because
it flips a reproducibility target from `BOUND` to `PARTIAL`.

## What is being asked

An operator decision on whether to open the two-pull-request window for ORION-17's
manuscript, on the understanding that:

- the science is complete and independently checked — the packet's checker returns
  `PASS`, `5/5`, with all four negative controls firing;
- the work required is authorial, under `papers/PAPER_WRITING_SKILLS_PROTOCOL_V1.md`;
- PR A must state the partial target with a blocker string rather than quietly widen
  the ratchet, and PR B must land before any other work touches ORION-17's binding.

Writing the manuscript outside `papers/orion-17-*/manuscript/` was considered and
rejected. `manuscript-clipping-audit.yml` asserts exactly 21
`papers/orion-??-*/manuscript/main.tex` entry points, so a manuscript placed anywhere
else is never rebuilt and never geometry-audited. An unaudited manuscript offered as
the discharge of a manuscript blocker is worse than the open blocker.

## Until then

ORION-17 stays `NO_BOX_EARNED_ON_MAIN`, with two of the matrix's three conditions
discharged and the third named precisely. The matrix's existing instruction still
holds and is worth repeating: **do not harden this into `NO_RESCUE`** — the evidence
exists, and what is missing is a manuscript, not a result.
