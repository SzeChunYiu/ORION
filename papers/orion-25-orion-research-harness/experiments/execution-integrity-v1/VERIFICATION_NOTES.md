# Verification notes — ORION-25 execution-integrity audit (2026-08-28)

**scientific_authority_delta:** `NONE`. These are audit observations against
committed artifacts. They change no terminal and promote nothing.

---

## V1. Frozen protocol digest does not verify at its current path

`P15_ATTESTATION_COMPOSITION_RESULT_RECEIPT_V2.md:13` declares
`protocol SHA-256: 6a7649be7e7f3a290d668de9ca31d798bfb11621d9db3e92558e8f52108e9bd7`.

The file at `top_tier/P15_ATTESTATION_COMPOSITION_PROTOCOL_V2.md` currently hashes
to `fe04e31e9883549c64ce0e6bd578d201a8e9a2d726b87fdfed9bcf90dbaa5505`.

**Resolved.** The declared digest is verifiable at commit `7f7f91931`, path
`papers/paper-15-orion-research-harness/top_tier/P15_ATTESTATION_COMPOSITION_PROTOCOL_V2.md`
(hashed and confirmed byte-exact). Commit `3a1a83178` — "ORION-01…25 namespace
unification, 2734 renames" (PR #1474) — renamed the file at `R091` similarity,
rewriting roughly 9% of its bytes.

**Status:** not a freeze violation of scientific content; a **provenance-locator
defect**. A verifier following the receipt to the current path gets a mismatch and
has no in-receipt pointer to the pre-rename locator. The three data fixtures are
unaffected and still match the receipt byte-for-byte
(`a9a29f9e…`, `142d14d0…`, `87812194…`, all confirmed).

**Not repaired here.** Per issue #1608, no frozen paper byte is modified to run
successor science. The correct locator is pinned in `SOURCE_MANIFEST.json`
(`protocol_of_record.frozen_form_locator`).

---

## V2. Namespace pass desynchronized cryptographic constants from the code

The same rename rewrote the **domain-separation constants in the protocol prose**
but not in the implementations.

| | GENESIS preimage | key seed prefix |
|---|---|---|
| `run_attestation_composition_v2.py:28,72` | `P15-ATTESTATION-COMPOSITION-V2-GENESIS` | `P15-ATTESTATION-COMPOSITION-V2-KEY-` |
| `check_attestation_composition_independent_v2.py:83,92` | `P15-…-GENESIS` | `P15-…-KEY-` |
| `P15_ATTESTATION_COMPOSITION_PROTOCOL_V2.md:18,20` | `ORION-25-…-GENESIS` | `ORION-25-…-KEY-` |

**Consequence.** A third party implementing from the current protocol text derives a
different genesis digest and a different key at every role, and cannot reproduce the
study. The runner and the independent checker still agree with **each other**, so
the bound V2 result is internally consistent and is **not** invalidated — the
two-implementation agreement terminal stands. What drifted is the specification of
record, not the evidence.

**Handling.** `SOURCE_MANIFEST.json` records `CODE_NOT_PROSE` as the authority and
pins both values. `PROTOCOL.json` requires the successor runner to read constants
from the manifest, so this defect class is not inherited.

**Queued, not dropped:** the prose/code divergence is a concrete defect for the
ORION-25 owner to reconcile in the frozen artifact lane. It is recorded here rather
than silently patched.

---

## V3. Cross-site replay availability (tracker box 4)

Checked 2026-08-28 by direct `ssh` with `BatchMode=yes`:

| site | hostname | platform | python | cryptography | result |
|---|---|---|---|---|---|
| `billy-old` | `billy-laptop-old` | Linux x86_64 | 3.14.4 | 46.0.5 | reachable, exit 0 |
| `lunarc` | `cosmos2.int.lunarc` | Linux x86_64 | 3.11.5 | 41.0.5 | reachable, exit 0 |

Box 4 is therefore **AVAILABLE**, not blocked. The three-site protocol is specified
in `PROTOCOL.json` (`cross_site_replay`).

Residual, declared and not eliminated: all three sites share a human operator and a
GitHub identity. That is a real common-mode path; `ARM-K3-D3-COMMONMODE` exists to
measure it rather than to assume it away.

---

## V4. Bound fault corpus is declared facts, not executed faults

`sei_fault_cases_v1.jsonl` (18 records) encodes each case as a boolean fact vector —
`spawn_ok`, `host_ok`, `timeout`, `exit_zero`, `reaped`, `finalized_after_reap`,
`cleanup_complete`, `retry_accounting_valid`, and so on. No process is spawned,
killed, starved or timed out anywhere in the corpus.

This is not a criticism of the bound study, which claims exactly what it measured:
`INTERNAL_UNIT_TEST_EVIDENCE` over registered internal panels, with
`population_inference: false`. It is the precise reason tracker box 3 is **ABSENT**
rather than partially satisfied, and it is what
`PROTOCOL.json.host_process_fault_injection` is designed to supply.

---

## V5. Trust-domain count in the bound study

`run_attestation_composition_v2.py:71-73` derives all three role keys from one
committed constant. Three distinct key values, one custody boundary:
`d = 1`, `T = 1`, at `k = 3`. The protocol declares this scope openly ("fixed
test-only seeds… not a key-management or hardware-attestation claim"), so this is a
**disclosed scope boundary, not a caught defect**. Full reasoning, including why
A-SPLICE must not be read as a dose-response over domains, is in
`../../TRUST_DOMAIN_REFRAME_V1.md` section 4.
