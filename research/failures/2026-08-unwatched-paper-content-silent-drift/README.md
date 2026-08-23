# Twenty-one papers whose contents nothing was watching

**Observed:** 2026-08-21, checking whether the framework and the harness notice a
change to a paper's contents, after six paper tranches added files under
`papers/`.

## Failure

`papers/SYNC_CONTRACT.md` names two obligations, and they are easy to read as
one:

1. **Framework/paper terminology sync.** `papers/FRAMEWORK_SNAPSHOT.json` is
   machine-checked against `orion.registry` by
   `tests/unit/publication/test_framework_snapshot.py`. The contract is honest
   about its reach: matching it "proves only terminology/mechanic
   synchronization, not scientific validity or empirical support". It compares
   five registry constants — framework version, sync epoch, state coordinates,
   core operator ids, mechanics substrate ids. It reads no paper content at all.

2. **Paper content binding.** A committed digest per file, so that changing a
   paper's bytes without regenerating its manifest fails a check.

The second is the one that notices a content change, and it is declared by
**three of the twenty-four directories** under `papers/`.

Measured by `orion.programme.content_binding_coverage` on this tree:

```
3/24 papers bound; 161 files bound, 1351 unbound; 0 drifted
```

| directory | files | binding |
| --- | ---: | --- |
| `paper-06-formal-epistemic-structures-and-mechanics` | 38 | `SHA256SUMS` + `CONTENT_MANIFEST_V1.json` |
| `paper-07-epistemic-navigation-open-worlds` | 39 | `SHA256SUMS` + `CONTENT_MANIFEST_V1.json` |
| `paper-08-epistemic-authority-autonomous-science` | 38 | `SHA256SUMS` + `CONTENT_MANIFEST_V1.json` |
| `paper-01-recursive-epistemic-reconstruction` | 150 | none |
| `paper-02-open-world-scientific-discovery` | 268 | none |
| `paper-03-global-knowledge-portrait` | 143 | none |
| `paper-04-verified-scientific-discovery` | 86 | none |
| `paper-05-self-orion` | 89 | none |
| `paper-09` … `paper-15`, `paper-xx-*`, Q and QG series | 587 | none |

The binding that does exist is good. `check_content_binding_v1.bound_paths`
enumerates by `rglob` rather than from a fixed list, so a file *added* to P6, P7
or P8 changes the derived manifest and the check goes red — it notices additions,
not only edits. Confirmed by mutation: appending one comment line to a bound file
reds five tests across all three papers, because that file is shared material all
three manifests bind.

**The defect is not that the other twenty-one papers are wrong. It is that they
are silent.** Ask "how many files drifted?" and an unbound paper answers `0`,
exactly as a bound and clean one does. The reports agree; the epistemic states
are opposite.

This is the failure the programme has now hit six times, applied to the manifests
themselves. It is `VACUOUS_GUARD_ZERO_DENOMINATOR`
(`research/failures/2026-08-vacuous-guard-zero-denominator/`) one level up: the
numerator is carried and the denominator is dropped, so "nothing changed" and
"nothing was watched" print the same character.

It also has the P1 shape. `research/failures/2026-08-unreachable-operator-inert-ablation/`
ended with: *a check that enumerates what must be present cannot notice what
should have been.* A registry of which papers are watched is exactly that
enumeration, one level up again — which is why the survey below discovers
bindings by convention and lists every directory under `papers/`, so a paper
that never adopts binding cannot drop off the report.

## Failure class

`UNWATCHED_CONTENT_SILENT_DRIFT`

A content-integrity check reports zero drift over the artifacts it covers. Where
coverage is partial and the covered set is not reported alongside the count, an
uncovered artifact is indistinguishable from an unchanged one.

## Correct response

1. Report the denominator. `content_binding_coverage.drift_exercise` builds a
   `GuardExercise` whose opportunities are *files under binding*, not files under
   `papers/`, so an unbound paper produces zero opportunities and
   `assess_guard` returns `CANNOT_CHECK` — which blocks a promotion exactly as
   `FAIL` does.
2. Make the taxonomy total. `PaperBindingState` names `UNBOUND` as a state, so
   the twenty-one silent directories appear in the report instead of being
   absent from it.
3. **Do not pool.** Assessing the pooled exercise alone reports `PASS` on this
   tree — 161 bound files, 0 drifted — and that pass would be P6's clean digests
   standing in for P1's unwatched bytes. The survey's verdict is the worst
   per-paper verdict; the pooled number is reported beside it, labelled as not
   being the answer.
4. Discover by convention, not by registry, so adopting a binding needs no edit
   here and never adopting one cannot hide.
5. Verify independently of the generator. `check_content_binding_v1` derives the
   manifest it then compares against; the survey only reads what is committed and
   hashes what is on disk, so the two disagree if either is wrong.
6. Keep a ratchet, not a target. `test_binding_coverage_does_not_regress` asserts
   at least three papers stay bound and that they are the three named ones.
   Un-binding a paper is a silent loss of the only check that notices its bytes.

Binding the remaining twenty-one papers is not done here. It is real work per
paper — each needs a manifest whose `bound_files` and roles someone has actually
reviewed — and generating twenty-one manifests mechanically would produce
exactly the unreviewed enumeration this record warns about. The measurement and
the ratchet are here; the bindings are the papers' lanes to add.

## General lesson candidate

**An integrity check must report what it covered, not only what it found.** A
count of violations is uninterpretable without the size of the watched set, and
the two most common ways to get a zero — held under pressure, and never looked —
are the two a bare count cannot separate.

The corollary for coverage specifically: **partial coverage reported as a global
number is worse than no check**, because it converts an open question into an
apparent clean bill. Whenever a checker takes a set of subjects, ask what is
*not* in that set and whether the report says so.
