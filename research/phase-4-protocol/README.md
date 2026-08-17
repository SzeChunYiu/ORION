# Phase-4 protocol pre-registration

**Status:** `PREPARATORY_AWAITING_ACTIVATION`

Issue #210 is blocked on #209. Nothing in this directory authorizes a
self-sustaining research programme, activates a GitHub Actions workflow, or
closes a gate.

| Path | Role |
|------|------|
| `CHECKBOX_AUDIT_210.md` | Blocked-on-#209 vs preparatory-runnable classification |
| `workflows/*.yml.template` | Inert cycle/epoch/anti-collapse templates. **Must not** be copied into `.github/workflows/` until authorization. |
| `../development/PHASE4_PREPARATORY_RECEIPTS_PACKET.md` | Development packet for the remaining shapes |

Machine-readable shapes live in `src/orion/programme/` (`activation`,
`governance`, `cycle_protocol`, `epoch_manifest`, `longitudinal`, `receipts`)
alongside the `#276` knowledge-layer package. They import that package; they do
not edit its `__init__` exports.
