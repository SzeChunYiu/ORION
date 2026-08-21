# A content binding whose watched set is written by the thing it watches

**Observed:** 2026-08-21, checking whether P10's content binding is complete,
after four of its five superiority terminals (#663) came back `CANNOT_CHECK` with
`evidence: []` while the paper's publication closure reports
`publication manifest: PASS (547 files)` and `P9/P10 bounded local closure: PASS`.

## Failure

P10 is one of the few papers in this repository with real content binding, and
it is the most elaborate: three digest files, two digest algorithms, two CI
workflows, and a `LOCAL_CLOSURE_AUTHORITY.json` that names its own scope. The
binding works. `VERIFY_LOCAL_CLOSURE.sh` walks
`papers/orion-learning-machine/PUBLICATION_MANIFEST_SHA256.txt`, hashes all 547
named paths, and every one matches. Append a single newline to one of them and
it stops dead:

```
AssertionError: publication manifest drift: results/PHASE0_SOLVER_ECOLOGY.txt
```

That is a real guard with a real denominator, and this record does not deny it.

What it never asks is whether 547 is the right 547. Membership is decided inside
the lane the manifest protects, by `generate_publication_manifest.included_files()`:

```python
roots = [ROOT / "framework", ROOT / "results",
         PAPERS / "paper-xx-executable-research-core",
         PAPERS / "paper-xx-content-bound-math-evaluation"]
suffixes = {".arff", ".bib", ".json", ".lean", ".md", ".py", ".sh", ".txt"}
```

and both shipped verifiers then iterate **the manifest**, never the tree. So the
guard's denominator is an output of the subject: adding a file to the publication
does not add an opportunity for the guard to fire.

Run the real `VERIFY_LOCAL_CLOSURE.sh`, unmodified, on a byte-for-byte copy of
the whole publication universe (16 MB, 571 files; nothing under `papers/` was
touched):

| mutation, all inside the manifest's own declared roots | verifier line | closure |
| --- | --- | --- |
| none | `publication manifest: PASS (547 files)` | `PASS` |
| `experiments/phase1_mechanic_composition/run_v2.py` replaced with a stub | `PASS (547 files)` | `PASS` |
| new file added under `framework/orion_learning_machine/` | `PASS (547 files)` | `PASS` |
| `benchmark/corpus/mathlib4_e72c1e277f31/lean-toolchain` repointed to `v4.99.0-rc9` | `PASS (547 files)` | `PASS` |
| `P10_PUBLICATION_OVERLAY_V2.json` emptied and its `.txt` twin blanked | `PASS (547 files)` | `PASS` |
| **control:** one newline appended to `results/PHASE0_SOLVER_ECOLOGY.txt` | **drift** | **red** |

The control is what makes the other four rows a finding rather than a
speculation. The check is sharp on the set it names, and blind to the set.

Measured by `python -m orion.study.p10.membership_audit` against this checkout:

```
scope 571   enrolled 551   unenrolled 20   stale-only 12
drift verdict PASS   membership verdict FAIL
```

Twenty files sit inside the roots the generator itself walks and are named by no
digest any gate opens:

| unenrolled | why it matters |
| --- | --- |
| all 13 files under `experiments/` | the drivers that produced the committed results |
| `VERIFY_LOCAL_CLOSURE_V2.sh` | the verifier **both CI workflows actually run** |
| `PUBLICATION_MANIFEST_P10_V2.txt` | the overlay's human-readable twin |
| `README.md` | |
| `benchmark/corpus/mathlib4_e72c1e277f31/lean-toolchain` | the Lean version pin behind P10's eight native acceptance receipts |
| `benchmark/native/lean_readlink_self.c` | the native verification shim |
| two `.gitattributes` inside the vendored corpora | how those corpora materialize on checkout |

`PUBLICATION_MANIFEST_SHA256.txt` and `P10_PUBLICATION_OVERLAY_V2.json` are *not*
in that list: a manifest cannot record its own digest, and the audit exempts an
enforced binding's own path for that reason and only that reason.

### The producers are outside the binding and the transcripts are inside

`results/` is one of the generator's four roots. `experiments/` is not. So the
manifest pins every committed number the two predecessor papers cite and none of
the code that produced them:

| committed result | bound | producer bound | producer re-run and compared |
| --- | --- | --- | --- |
| `PHASE0_SOLVER_ECOLOGY.txt` | yes | **no** | **no** |
| `PHASE1_MECHANIC_COMPOSITION.txt` | yes | **no** | **no** |
| `PHASE1_MECHANIC_COMPOSITION_V2.txt` | yes | **no** — `run_v2.py` is in no manifest at all | **no** |
| `PHASE2A_RESULTS.json` | yes | **no** | yes, `test_phase2a_re_derives_byte_identically` |
| `FRAMEWORK_TESTS.txt` | yes | yes (`framework/tests`) | yes, in both workflows |

`REPRODUCE_LOCAL_CLOSURE.sh` does run phase 0, phase 1 V2 and phase 2A — and
then prints their output. It never diffs any of it against `results/`. It is also
run by nothing: no workflow and no test invokes it, and `pyproject.toml`'s
`candidates` extra declares `numpy` and `scikit-learn` but not `sympy`, which
both the phase-0 and the phase-1 runner import at the top of the file. The repository's own declared
dependency closure cannot execute two of the three experiments its reproduction
script names.

### A receipt that has already drifted, and nothing noticed

Twelve of the twenty unenrolled files *look* covered. `SCRIPT_MANIFEST_SHA256.txt`
names 36 paths including every experiment driver, is itself bound by the
publication manifest, and sits next to it in the same directory. `REPRODUCE.md`
is honest about what it is — "a historical receipt for the 36 files as delivered
at commit `bbe178d`; it is not the current publication manifest" — and nothing in
the repository hashes a single path it names.

That claim does not have to be taken on trust. Hash them:

```
SCRIPT_MANIFEST_SHA256.txt: 36 named, 26 match, 10 drifted, 0 missing
```

Ten recorded digests disagree with the bytes on disk — including
`VERIFY_LOCAL_CLOSURE.sh` itself, `runtime.py`, `math_eval.py`, `types.py` and
three framework tests — while every gate in the repository is green. A digest
file whose contents can be wrong by ten without anything going red is not a
check, and counting its entries as coverage is exactly how a reviewer grepping
for `run_phase2a.py` concludes the experiments are bound.

### The overlay supersedes five paths that had not changed

`VERIFY_LOCAL_CLOSURE_V2.sh` — the script both workflows run, and one of the
unenrolled twenty — skips five legacy sha256 rows as "intentionally superseded"
and re-checks those paths by Git blob identity instead. Recomputing both
digests (in Python; `git` is never invoked):

| overlay paths | substitutions | additive | substitutions whose *legacy sha256* still matches disk |
| ---: | ---: | ---: | ---: |
| 9 | 5 | 4 | **5 of 5** |

All five superseded files still match the digest the legacy manifest records. The
substitution pins the same bytes twice under two algorithms; the overlay's real
contribution is the four additive paths. A second binding over content the first
one already binds does not widen coverage, and while it was being added, `run_v2.py`
and the toolchain pin stayed outside both.

### What the 547 is made of

| | count | share |
| --- | ---: | ---: |
| vendored Mathlib `.lean` source | 461 | 84.3% |
| vendored ASlib scenario | 7 | 1.3% |
| authored by ORION | **79** | 14.4% |
| — of which, in the lane itself | 33 | |
| — of which, in `paper-xx-content-bound-math-evaluation` (retired P10) | 32 | |
| — of which, in `paper-xx-executable-research-core` (retired P9) | 12 | |
| entries outside the lane directory | 514 | 94.0% |

`PASS (547 files)` is mostly a Mathlib checkout. And of the 547, **zero** are at
P10's registered active identity: `papers/paper-10-structured-problem-solving/`
holds exactly one file, `successor/P10_U_MANUSCRIPT.tex`, and none of the three
digest files names it. Everything under binding belongs to a shared lane or to
two directories `VACATED_PAPER_NUMBERS` records as vacated paper numbers — and
whose grade the superiority ledger enters as `PredecessorArtifact`, which
discharges nothing.

### Why the existing instrument does not report this

`orion.programme.content_binding_coverage` is the right family and the wrong
question, twice over.

```
inspect_paper(repo, papers/orion-learning-machine)
  -> UNBOUND, files_bound=0, CANNOT_CHECK
```

It discovers bindings by looking for a `SHA256SUMS` file, which this lane does
not use, so it calls a directory carrying 547 live digests *unbound*. It blocks,
which is safe, but it blocks for a reason that is false, and it cannot see the
binding it would need to audit. Second, and independently:

```
PaperBinding(files_on_disk=500, files_bound=1, drifted_paths=())
  -> unbound_files 499, verdict PASS
```

`unbound_files` is computed and reported and never reaches the verdict.
`assess_paper` builds its exercise from `files_bound`, so partial coverage
assesses exactly like total coverage. The number was there; nothing acted on it.

## Failure class

`SELF_SCOPED_MANIFEST_UNCLOSED_MEMBERSHIP`

A content-integrity check verifies **inclusion** — the files it names still hash
correctly — and never **membership** — that everything inside its own declared
scope is named. Where the naming is done by the artifact under protection, the
guard's denominator is an output of the subject: it is real, non-zero, exercised
and clean, and adding a file to the tree does not add an opportunity.

This extends the family rather than repeating it. Each prior record is one
variable that could not vary:

- `2026-08-unreachable-operator-inert-ablation/` — the **independent** variable.
- `2026-08-vacuous-guard-zero-denominator/` — the **dependent** variable.
- `2026-08-unapplied-treatment-vacuous-null/` — the **cause** was never applied.
- `2026-08-label-recoverable-from-construction-cue/` — the **label** came from the
  construction.
- `2026-08-invertible-commitment-vacuous-custody/` — the **commitment** opened.
- `2026-08-unfalsifiable-check-zero-refutation-capacity/` — the **predicate** was a
  tautology.
- `2026-08-supplied-premise-unbuilt-decision/` — the **decision** was a parameter.
- `2026-08-unconditional-terminal-self-issued-authority/` — the **verdict** had no
  predicate.
- `2026-08-unwatched-paper-content-silent-drift/` — the **denominator** was dropped:
  21 of 24 papers watched nothing and reported the same `0` as a clean one.
- here — **the population was drawn by the subject.** The denominator is not
  missing and not zero. It is 551, it is exercised 551 times, every one holds, and
  it was chosen by a function inside the artifact. This is the P8 `claim_ceiling`
  move — "a limit only the claimant can set" — applied to a *sample* instead of a
  *bound*, and it is invisible to every instrument the programme has, because they
  all take the watched set as given.

Four properties let it survive review, and each is a virtue of the binding.

1. **The check is genuinely sharp.** One byte in a named file reds it. Every
   reviewer who tests the guard tests it on a file the manifest names, because
   that is the file list they have.
2. **The count reads as a scope.** `PASS (547 files)` is a large, specific,
   reproducible number. Nothing in it says whether the tree has 547 files or 571.
3. **A stale receipt is indistinguishable from a binding.** `SCRIPT_MANIFEST_SHA256.txt`
   is committed, is itself digest-bound, and lists the experiments. Only hashing
   its entries reveals that ten are already wrong.
4. **Adding a binding feels like adding coverage.** The V2 overlay is a second
   algorithm, a second manifest and a second workflow, and five of its nine paths
   restate bytes the first manifest already pinned.

## Correct response

1. Make membership a guard with its own denominator.
   `orion.programme.manifest_membership` builds two `GuardExercise` objects from
   one audit: `drift_exercise` has the enrolled set as its denominator, which is
   what the shipped verifier measures, and `membership_exercise` has the
   **declared scope**, which is what nothing measures.
2. Do not pool. `audit_outcome` is `worst_outcome` of the two. Assessing drift
   alone reports `PASS` on this tree — 551 enrolled, 0 drifted — and that pass
   would be intact bytes standing in for a watched set, the same compensatory
   move `content_binding_coverage` refuses one level down.
3. Discover the scope by walking, never from a list. `scope_paths` rglobs the
   declared roots. A scope enumerated from a fixed list is the same defect one
   level up: it can only report files somebody remembered to write down, which is
   what the manifest already does.
4. Do not narrow the denominator to agree with the artifact. The scope
   deliberately ignores the generator's suffix filter — which suffixes to bind
   *is* the membership decision under audit — and drops only build output, on the
   identity grounds `content_binding_coverage` uses: a `.pyc` filename carries the
   interpreter that made it.
5. Require a digest file to say who reads it. `DigestBinding.dereferenced_by` is
   mandatory and may be empty, and an empty value has a consequence: the binding
   enrolls nothing, and its entries appear as `stale_only` — paths that look
   covered and are not. The claim is then *measured* rather than asserted:
   `unenforced_drift` reports the ten digests that are already wrong.
6. Exempt only a manifest's own path. It cannot record its own digest. A second
   file repeating the same digests can be bound and is not, so
   `PUBLICATION_MANIFEST_P10_V2.txt` is reported as unenrolled.
7. Point the instrument at the shipped artifact.
   `orion.study.p10.publication_binding` loads the real
   `generate_publication_manifest.py` and calls `included_files()` — never
   `main()`, which would rewrite the manifest it audits — and the audit asserts
   the committed manifest equals what the generator derives. A test pins that the
   two files the generator reaches for outside its roots are exactly two, so a new
   root cannot silently shrink the scope.
8. Recompute Git blob identity rather than shelling out. `DigestAlgorithm.GIT_BLOB_SHA1`
   hashes Git's own `blob <len>\0` envelope, pinned in a test against Git's ids for
   the empty file and `hello\n`. An audit that needs a working tree cannot run on
   an exported publication package, which is the artifact that actually leaves the
   repository.
9. Report what the count is made of. `manifest_entry_origin` splits the 547 into
   461 vendored Lean files, 7 ASlib files and 79 authored ones, and names the 514
   that are not in the lane directory.

Not done here, and deliberately:

- **The bindings themselves are not widened.** Enrolling the twenty files means
  regenerating `PUBLICATION_MANIFEST_SHA256.txt`, which is bound by its own
  contents, asserted by `tests/unit/candidates/test_p9_p10_learning_machine.py`,
  and checked by two CI workflows. That is the lane's own change to make, and
  mechanically adding twenty rows would produce the unreviewed enumeration the
  programme keeps warning about. The measurement and the ratchet are here.
- **`papers/` is not touched.** The lane is content-bound; an audit that edited
  its subject to measure it would be reporting on a different artifact. The
  mutation evidence above was produced on a byte copy, and a test asserts the
  audit leaves the manifest unchanged.

## General lesson candidate

**An integrity check must report the set it watched *and* who chose it.** The
previous form of this lesson — a count of violations is uninterpretable without
the size of the watched set — assumed the watched set was a fact about the world.
Where the artifact writes its own manifest, it is a fact about the artifact, and
a clean result over it is a statement the artifact composed.

The sharper form: **ask what would have to happen for this guard's denominator to
grow.** If the answer is "someone edits the thing being guarded", the guard
measures diligence, not integrity. Every digest manifest in this repository
should be asked to produce a file that is inside its own declared scope and
outside its own row list; if one exists, the manifest is a list of files somebody
remembered, and the count it publishes is a fact about their memory.

And one corollary about layered bindings, which is how this one grew: **a second
binding over content the first already covers is not coverage.** Five of nine
overlay paths restate the legacy manifest exactly. Two more workflows, one more
algorithm, one more manifest — and the thirteen experiment drivers stayed exactly
as unwatched as they were before.

## Residuals and reopen coordinates

- The twenty files are not enrolled here (see *Correct response*). The audit
  blocks on them, which is the honest state.
- The three `paper-xx-` and `orion-learning-machine` directories are reported
  `UNBOUND` by `content_binding_coverage` because they carry no `SHA256SUMS`.
  That is a false negative on a directory with 547 live digests. Teaching that
  survey to recognise this lane's convention is real work in its lane and is not
  done here; the two instruments now disagree about the same tree, which is
  itself the reportable state.
- `SCRIPT_MANIFEST_SHA256.txt`'s ten drifted digests are **not** a defect in the
  lane: `REPRODUCE.md` says plainly that it is an archival receipt. What is
  denied is that its entries are coverage. If it is ever wired into a gate, that
  gate reds on ten files immediately, and `dereferenced_by` in
  `orion.study.p10.publication_binding` must change in the same commit.
- Phase 0 and Phase 1 committed results have no re-derivation check anywhere, and
  `sympy` is absent from `pyproject.toml`'s `candidates` extra, so the declared
  environment cannot run either producer. Whether those results still reproduce is
  a separate, open question this record does not answer.
- P10's ledger row carries `evidence: []`; T1–T4 are `CANNOT_CHECK` and T5
  (`SCOPE_DISCIPLINE`) passes on a grade supplied by a `PredecessorArtifact`.
  That is documented, deliberate behaviour in `PaperSuperiorityRecord.strongest_grade`
  and is not challenged here. It is recorded because it means the only P10-U gate
  currently passing is licensed by the same retired directory that holds 32 of the
  79 authored files under binding.
- Reopen if `generate_publication_manifest.included_files()` gains or loses a
  root, if `SCOPE_ROOTS` is edited, or if either verifier stops walking the
  manifest and starts walking the tree — the last is the repair, and
  `test_the_shipped_binding_is_clean_and_its_membership_is_open` reds when it
  lands.
