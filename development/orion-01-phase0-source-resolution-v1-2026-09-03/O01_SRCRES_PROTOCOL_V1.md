# O01-SRCRES Phase-0 source-resolution protocol V1 (registered before outcome)

**Study id:** `O01-P0-SRCRES-V1`
**Lane:** `development/orion-01-phase0-source-resolution-v1-2026-09-03/`
**Paper:** ORION-01 (certificate realization)
**Executed phase:** Phase 0 (`resolve_source`) of the frozen successor protocol
`orion-01-production-completeness-v1-2026-08-29` (`PROTOCOL.json` `ordered_phases[0]`).
**Registration date:** 2026-09-03. Registered BEFORE any resolution attempt. No
resolution, advertisement fetch, or prefix query of `Quantomatic/pyzx` was performed
under this identity before this file was committed.

## Aim

Discharge exactly one ordered phase of the frozen successor protocol: resolve the
frozen commit prefix `dade7d46` against the upstream `Quantomatic/pyzx` repository
and emit the registered Phase-0 artifacts, or land on a registered adverse/cannot
terminal. This is the mandatory next rung: Phase 1 (`prove_source_boundary`)
requires `SOURCE_RESOLVED` and the frozen protocol forbids semantic testing before
resolution (`semantic_testing_before_resolution_permitted: false`).

## Frozen definitions (imported machinery only — nothing re-declared here)

Every scientific constant is READ at runtime from the frozen files; this protocol
and the driver copy none of them:

| Frozen artifact | What is imported |
|---|---|
| `development/orion-01-production-completeness-v1-2026-08-29/PROTOCOL.json` | repository, commit prefix, `required_match_count`, `required_object_type`, full-object-name length, floating-ref ban, phase-0 terminal names |
| `.../CORPUS_MANIFEST.json` | `resolution_algorithm` (7 ordered steps), `resolution_failure_terminals` map, `source_resolution_receipt_required_fields`, `byte_corpus.required_record_fields` + `path_order` + `symlink_policy` + `submodule_policy`, `environment_freeze.required_fields` |
| `.../EXPECTED_TERMINALS.json` | phase-0 terminal classes and the single legal transition `PROTOCOL_FROZEN__NO_OUTCOME -> {SOURCE_RESOLVED, SOURCE_PREFIX_UNRESOLVED, SOURCE_PREFIX_AMBIGUOUS, SOURCE_OBJECT_NOT_COMMIT, CANNOT_RESOLVE_SOURCE}` |
| `.../registry_protocol_checker_v1.py` | imported and executed as gate G0 (canonical versioned checker; the frozen protocol freeze must validate before any resolution step) |

The frozen predecessor directory is never written to. The canonical checker's
`FUTURE_ONLY` scope proves the freeze stays pristine (gate G0 re-runs it).

## Registered questions

- **Q1.** Does the frozen prefix resolve to exactly `required_match_count` commit
  object name(s) in the object database reachable from all advertised
  `refs/heads/*` and `refs/tags/*` of the declared remote?
- **Q2.** Is the unique match a `commit` object with exactly 40 lowercase hex
  characters (`git cat-file -t`)?
- **Q3.** Does an independent resolution channel (GitHub REST commit endpoint,
  via `gh api`) return the same full object name?
- **Q4.** Does the pinned tree declare `.gitmodules` submodules (frozen
  `submodule_policy` is fail-closed until separately pinned)?
- **Q5.** Is the source file manifest complete — exactly one row per `git ls-tree -r`
  entry of the pinned tree, in the frozen `path_order` (raw UTF-8 byte order)?

## Registered resolution procedure (the frozen algorithm, operationalized)

1. Fresh **bare** clone (`git clone --bare --no-local`, `GIT_NO_REPLACE_OBJECTS=1`,
   no alternates, no grafts, no shallow) of the declared remote into an uncommitted
   scratch directory; assert non-shallow.
2. Record the remote-ref advertisement (`git ls-remote`, byte hash + per-kind
  counts); assert every advertised head/tag is present in the clone.
3. `git rev-list --all` in the bare clone; retain object names beginning exactly
   with the frozen prefix; require the frozen match count.
4. Require 40 lowercase hex and `git cat-file -t` == `commit`; record tree,
   parents, and the commit-object byte hash.
5. Record annotated/signed tags peeling to the commit (a tag is never substituted
   for the commit).
6. Build `SOURCE_FILE_MANIFEST.jsonl` from `git ls-tree -r` of the pinned tree
   (blob bytes read for hashing only — no checkout, no import, no semantic scan);
   `.gitmodules` check per the frozen fail-closed policy.
7. Write `ENVIRONMENT_RECEIPT.json`, then `SOURCE_RESOLUTION_RECEIPT.json`
   (hashing the manifest), before any semantic testing of the source.

## Hard gates (executed, not logged)

| Gate | Assertion | On failure |
|---|---|---|
| G0 | canonical checker `run_checks()` passes, terminal `PROTOCOL_FREEZE_VALIDATED__NO_SOURCE_OUTCOME`; frozen dir sha256 set matches the registration pin | exit 3, no protocol terminal |
| G1 | advertisement acquired (ls-remote exit 0, >=1 head or tag ref) | `CANNOT_RESOLVE_SOURCE` |
| G2 | fresh full bare clone: non-shallow, all advertised heads+tags present | `CANNOT_RESOLVE_SOURCE` |
| G3 | prefix match count == `required_match_count` | 0 -> `SOURCE_PREFIX_UNRESOLVED`; >1 -> `SOURCE_PREFIX_AMBIGUOUS` |
| G4 | unique object is `commit`, 40 lowercase hex | `SOURCE_OBJECT_NOT_COMMIT` |
| G5 | channel-2 (REST) returns the identical full object name | unavailable -> `CANNOT_RESOLVE_SOURCE`; disagreement -> exit 3 |
| G6 | no semantic testing: no checkout, no pyzx import, blob reads for hashing only; receipt written before any semantic step | exit 3 |
| G7 | `.gitmodules` absent, or fail-closed per frozen policy | `CANNOT_RESOLVE_SOURCE` (submodule_pinning_required) |
| G8 | anti-instrument import gate: driver imports are stdlib + the frozen checker module only (ast-parsed); no `pyzx`, no ORION production code, no network libraries in-process | exit 3 |
| G9 | manifest completeness: one row per ls-tree entry, frozen field set, frozen path order | exit 3 |

## Artifacts

Registration commit (this file + driver, NO outcomes):
`O01_SRCRES_PROTOCOL_V1.md`, `README.md`, `requirements-lock.txt`,
`research/extensions/orion01/o01_srcres_phase0.py`.

Outcome commit: `RUN_O01_SRCRES_PHASE0.log`,
`SOURCE_RESOLUTION_RECEIPT.json` (always), `SOURCE_FILE_MANIFEST.jsonl` +
`ENVIRONMENT_RECEIPT.json` (only on the `SOURCE_RESOLVED` path, per
`EXPECTED_TERMINALS.json` required artifacts),
`research/extensions/orion01/O01_SRCRES_PHASE0_RESULTS.json` (canonical result),
`SHA256SUMS`.

## Terminals (frozen at registration)

The five Phase-0 terminals of the frozen protocol, with exactly the frozen
failure mapping (`CORPUS_MANIFEST.json.resolution_failure_terminals`):

| Condition | Terminal |
|---|---|
| unique commit match, channels agree, no submodule blocker | `SOURCE_RESOLVED` |
| zero matches | `SOURCE_PREFIX_UNRESOLVED` |
| more than one match | `SOURCE_PREFIX_AMBIGUOUS` |
| unique match is not a commit | `SOURCE_OBJECT_NOT_COMMIT` |
| advertisement/clone/network unavailable, advertised refs incomplete, or submodule fail-closed | `CANNOT_RESOLVE_SOURCE` |

Study-level consistency terminals (exit 3, NO protocol terminal claimed):
`SOURCE_RESOLUTION_MACHINERY_INVALID` (G0/G8/G9), `SOURCE_RESOLUTION_CHANNEL_DISAGREEMENT` (G5).

## Authority ceiling

- This phase grants NO registry authority, NO move-completeness upgrade, and NO
  paper-claim delta. The old terminal `CANNOT_CHECK_MOVE_COMPLETENESS` is not
  reinterpreted, extended, or upgraded (frozen `prohibited_shortcuts`).
- Phase 0 success only unlocks Phase 1 (`prove_source_boundary`) under the frozen
  ordering; it does not execute or imply any part of it.
- `novelty_authority: false`; `physical_quantum_advantage_claim: false`;
  `paper_authority_delta: NONE`.
- Uniqueness is claimed only over the object database reachable from advertised
  heads+tags at the recorded advertisement hash and timestamp (recorded in the receipt).

## Adverse-terminal revival levers (one-stage attribution, pre-registered)

- `SOURCE_PREFIX_UNRESOLVED` — attributable to the frozen prefix never naming a
  commit reachable from current refs (e.g. garbage-collected, force-pushed away, or
  mistyped at freeze). Lever: the frozen decision boundary terminates the protocol;
  revival requires a NEW successor protocol identity with an operator-corrected
  prefix, never an extension of this one.
- `SOURCE_PREFIX_AMBIGUOUS` — same stage; lever: lengthen the prefix in a new
  frozen identity (uniqueness is prefix-length dependent by git's object model).
- `CANNOT_RESOLVE_SOURCE` (submodule) — lever: a pinning-amendment lane that
  commit-pins and hashes every declared submodule, then re-runs Phase 0 fresh.
