# PROTECTED_PROMPT_FIT_PREFLIGHT_V1 development packet

## Development question and atomic fibers

Can an additive, outcome-blind preflight bind each authorized
ScienceAgentBench protected input row to the frozen public mask manifest,
construct the exact masked and recovered direct-route packet shapes, and bind
every state-independent rendered prompt without retaining any protected body?

The question is split into independently checkable fibers:

1. strict source shape and source-artifact identity;
2. exact task ID, domain, type, canonical byte-count, and SHA-256 binding for
   all five allowed source fields;
3. deterministic masked and recovered packet construction;
4. exact direct-route template rendering for state-independent phases;
5. prompt byte-count and SHA-256 retention with no packet or prompt body;
6. hardcoded GGUF filename, byte count, SHA-256, repository, and revision;
7. mandatory production binding of an independent staging receipt plus a
   separate full rehash and byte count from a held live GGUF descriptor;
8. optional exact-GGUF token-ledger identity, completeness, and fit checks;
9. an explicit dynamic boundary for RR phase 1, whose phase-0 model state is
   unavailable prospectively;
10. descriptor-held input reads and `openat` new-file-only receipt output.

## Saturation assessment and challenge

The relevant local search universe is bounded by the merged mask manifest,
direct-route contract, prompt bundle, generation driver, and their hostile
validators. Those artifacts freeze source-field digests, canonical JSON,
template replacement, seeds, context geometry, and phase caps, but currently
provide neither a production packetizer nor protected task-fit receipts.

This is not a global saturation claim. A false-flat conclusion could arise by
equating prompt byte length with tokenizer length, substituting a public
tokenizer for the GGUF tokenizer, treating a mutable contract and ledger as an
identity authority, accepting a staging receipt without independently
rehashing the live GGUF, treating RR phase 1 as static, trusting an unbound
extracted row source, reopening validated paths, or persisting protected
packet/prompt bodies in the receipt. The implementation therefore fails closed
at each boundary.

Potentially missing representations are Parquet decoding and direct live
GGUF tokenization. This lane deliberately uses only the Python standard
library and accepts an owner-authorized strict JSON extraction plus an
optional externally produced exact-GGUF token ledger. Production additionally
requires the staged GGUF itself and an independent staging receipt. The CLI
rehashes the entire live GGUF from a held descriptor; an optional external
source-receipt hash is provenance only and can never substitute that live
measurement. Asserted prompt-token counts are not independently remeasured.

## Frozen implementation hypothesis

If every authorized row has exactly the seven allowed fields and every
canonical source value matches the corresponding manifest descriptor, then a
preflight can safely retain only source, packet, and rendered-prompt hashes and
byte counts. It can deterministically bind 1,224 state-independent prompt
records for 102 tasks and three attempts, while retaining 306 RR phase-1
records as typed dynamic `CANNOT_CHECK` placeholders.

Without a complete ledger bound to the exact GGUF/runtime and every static
prompt hash, prompt token counts remain null. With such a ledger, static
context fit may be checked from the supplied counts, but production
admissibility, RR phase-1 fit, billed USD, semantic-choice sensitivity, and
scientific authority remain unchanged.

## Hostile tests frozen before implementation

The standard-library unittest gate will cover:

- canonical JSON and exact visible/recovered packet shapes;
- task-ID/domain/source-field mismatch, wrong type, extra field, duplicate
  ID, missing task, manifest drift, prompt-bundle drift, and source-hash drift;
- exact seed/phase matrix and rendered prompt hash retention;
- absence of source values, packet bodies, and prompt bodies from receipts;
- explicit RR phase-1 dynamic status;
- absent, incomplete, duplicate, extra, mismatched-hash, wrong-runtime, and
  non-integer token ledgers;
- static fit/pass and overflow/fail classification from a fully bound ledger;
- strict JSON duplicate-member/non-finite rejection;
- absolute nonsymlink inputs, alias rejection, `O_EXCL` output, and
  write-failure rollback.

## Reopen triggers

Reopen the design rather than weakening checks if:

- the upstream manifest, prompt bundle, direct-route contract, seeds, caps,
  or model/runtime identity drifts;
- the authorized extraction cannot preserve exact JSON values represented by
  the manifest;
- exact GGUF tokenizer evidence cannot bind each prompt hash uniquely;
- an independent staging receipt and the separately rehashed live GGUF do not
  agree on the hardcoded filename, bytes, SHA-256, repository, and revision;
- any protected source, packet, prompt, generated state, evaluator, rubric,
  gold, candidate, or outcome body would enter the receipt;
- a sound prospective upper bound for dynamic RR phase 1 is proposed.

## Authority boundary

This additive lane grants no task execution, model execution, official
evaluation, outcome opening, CI, manuscript, PDF, publication, or merge
authority. It preserves:

```text
production_admissibility = CANNOT_CHECK
semantic_choice_sensitivity = NOT_ESTABLISHED
billed_cost_usd = null
billed_cost_status = CANNOT_CHECK
scientific_authority_delta = NONE
```

Verification commands and final evidence are appended only after the TDD
cycle and bounded implementation are complete.

## Implemented packet

The directory contains exactly seven files:

1. `PROTECTED_PROMPT_FIT_CONTRACT_V1.json`
2. `protected_prompt_fit_preflight_v1.py`
3. `validate_protected_prompt_fit_preflight_v1.py`
4. `SYNTHETIC_VALIDATION_RECEIPT_V1.json`
5. `DEVELOPMENT_PACKET.md`
6. `HANDOFF_V1.md`
7. `SHA256SUMS`

The module is Python-standard-library-only. It duplicates only the small
canonical JSON and template-replacement mechanics needed to reproduce the
merged direct-route renderer; the exact prompt bundle, direct-route contract,
and merged driver bytes are all SHA-bound. No existing Runner, adapter,
analysis, prompt, manuscript, registry, or other lane file is modified.

## Source, packet, and body-retention rules

The production input is not raw Parquet because this standard-library lane has
no Parquet decoder. It is one owner-authorized strict JSON extraction from the
exact verified Parquet identity. The file must itself be canonical JSON plus
one LF and has exactly four top-level fields. Every row has exactly:

```text
instance_id, domain, task_inst, output_fname,
domain_knowledge, dataset_folder_tree, dataset_preview
```

For all five source-value fields, the implementation verifies the manifest's
declared state, type, canonical byte count, and SHA-256. It also recomputes the
whole manifest-record binding from task ID, domain, and the five descriptors.
Only after all checks pass does it construct:

- a masked packet with visible fields plus deterministic typed markers for the
  three recovered fields; and
- a recovered packet with the exact seven authorized values.

Those packet objects exist only in process memory. The receipt retains each
packet's canonical byte count and SHA-256, never its body. Prompt text also
exists only in process memory and is reduced to UTF-8 byte count and SHA-256.
Every input and static upstream file is opened once by component-wise
`openat` traversal with held directory/file descriptors and no-follow flags.
All reads and hashes use those descriptors. Path and inode identity are
reverified before and after output. The output uses the already-held parent
descriptor with `openat(O_EXCL|O_NOFOLLOW, 0600)`; a parent or input swap fails
closed and removes the unchanged newly created receipt. The final output-name
identity and digest are reverified; a replacement at that name fails closed
without deleting the replacement. Existing destinations and lexical,
case-fold, symlink, hardlink, or device/inode aliases fail before any caller
input body is read.

## Prompt matrix and tokenizer boundary

For each task and attempts 1/2/3, the state-independent matrix is:

```text
RR_PHASE0, OS_PHASE1, NR_PHASE0, NR_PHASE1
```

At 102 tasks this produces 1,224 exact rendered-prompt bindings. RR phase 1 is
not rendered prospectively because its prompt requires the generated sealed RR
phase-0 state. The receipt instead retains 306 dynamic records with:

```text
CANNOT_CHECK_DYNAMIC_RR_PHASE0_STATE_REQUIRED
```

The exact inference tokenizer is the hardcoded GGUF identity: repository,
revision, filename, 18,556,689,568 bytes, and SHA-256
`fadc3e5f8d42bf7e894a785b05082e47daee4df26680389817e2093056f088ad`.
Contract or ledger mutation cannot redefine those constants. Production
requires both an independently produced staging receipt and a fresh full
SHA-256/byte-count measurement of `--live-gguf` from its held descriptor; the
two must agree exactly. This development validation did not open that model.

The CLI never substitutes the separately published tokenizer. Without
`--token-ledger`, every static prompt token count is null and typed
`CANNOT_CHECK`. An optional owner-supplied ledger must bind the hardcoded
GGUF/runtime object, all source identities including the live staging receipt
and measurement, and every static prompt hash exactly once. The preflight then
checks only completeness and
`prompt_tokens + phase_output_cap <= 32768`; it explicitly records that the
counts were not independently remeasured here. RR phase 1 remains dynamic even
when every static prompt fits.

## TDD witness

The initial complete 19-test hostile validator was written before
implementation. A twentieth malformed-ID regression was added during the
post-green hardening audit and also followed red/green order.

1. Bootstrap RED: `Ran 19 tests` and `FAILED (failures=19)` because the
   implementation, contract, and receipt were absent.
2. Core implementation: 18 behavior/contract tests passed; the final test
   remained red because the synthetic receipt was intentionally absent.
3. Pre-receipt RED: `Ran 19 tests` and `FAILED (failures=1)` with exact cause
   `synthetic validation receipt is missing`.
4. Reviewer-hardening RED: the added twentieth test exposed an uncaught
   `TypeError` for an unhashable task ID while the prior behavior tests stayed
   green.
5. GREEN: all 20 tests passed using two invented nonbenchmark rows.
6. Independent NO-GO repair RED: four new blocker tests failed because
   tokenizer fields were mutable, no live staging validator existed, and no
   descriptor-held input/output interface existed. The full run reported
   `Ran 24 tests` with those failures plus the intentionally stale receipt.
7. Post-write swap RED: the added twenty-fifth test proved that an input swap
   after output creation raised but initially left the receipt behind.
8. Output-name swap RED: the added twenty-sixth test proved that replacing the
   created receipt at its output name required identity-aware failure and
   rollback behavior that never deletes the replacement.
9. GREEN: all 26 tests passed after final output identity verification and
   identity-aware rollback were added.

Hostile coverage includes field/type/hash drift, source task-set/order drift,
duplicate JSON members, non-finite JSON, every principal token-ledger mismatch,
static overflow retention, dynamic RR status, body absence, output aliases,
exclusive creation, write-failure rollback, and malformed/unhashable task IDs.
The repair coverage additionally mutates filename/bytes/SHA/revision while a
ledger agrees, rejects receipt-only live identity, retains descriptor bytes
across an input rename, races an output-parent rename inside `openat`, and
forces an input swap immediately after output write to prove receipt rollback.
It also replaces the output name after write to prove detection without
deleting the replacement.

## Focused verification

From the repository root, run:

```text
rtk env PYTHONPYCACHEPREFIX=/tmp/orion-p1-protected-prompt-fit-v1-pycache python3 -m py_compile development/p1-scienceagentbench-protected-prompt-fit-preflight-v1-2026-08-24/protected_prompt_fit_preflight_v1.py development/p1-scienceagentbench-protected-prompt-fit-preflight-v1-2026-08-24/validate_protected_prompt_fit_preflight_v1.py
rtk rm -rf /tmp/orion-p1-protected-prompt-fit-v1-pycache
rtk env PYTHONDONTWRITEBYTECODE=1 python3 development/p1-scienceagentbench-protected-prompt-fit-preflight-v1-2026-08-24/validate_protected_prompt_fit_preflight_v1.py
rtk env PYTHONDONTWRITEBYTECODE=1 python3 development/p1-scienceagentbench-preflight-2026-08-24/validate_preflight_v1.py
rtk env PYTHONDONTWRITEBYTECODE=1 python3 development/p1-scienceagentbench-direct-route-freeze-v1-2026-08-24/validate_direct_route_freeze_v1.py
rtk shasum -a 256 -c development/p1-scienceagentbench-protected-prompt-fit-preflight-v1-2026-08-24/SHA256SUMS
rtk git diff --check origin/main...HEAD
```

No protected preflight, exact tokenizer, provider, model, evaluator, LUNARC,
CI, pytest, manuscript, or PDF command belongs to this verification packet.
