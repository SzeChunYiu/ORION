# Sync obligation matrix — DISC-IMPACT-01

54 registered reopen edges produce 54 successor obligations. The mapping is 1:1 and asserted in `disc_impact_01.py`.

An obligation is *registered*, not *discharged*. Obligations whose target is a theorem are authority-gated: this job has authority for repository synchronization only and cannot update a claim.

| obligation | reopen edge | kind | successor artifact | identity | required action | authority |
|---|---|---|---|---|---|---|
| `SYNC-000` | `EVIDENCE:EXEC-CM-01` → `EXPERIMENT:EXEC-CM-01` | DEPENDS_ON | `research/orion-foundations-v3/exec/EXEC-CM-01/EXECUTION_PROTOCOL.json` | MATCH | re-run the experiment protocol and re-register its receipt | sync-only |
| `SYNC-001` | `EVIDENCE:EXEC-CM-01` → `THEORY:T8` | VALIDATES | `research/orion-foundations-v3/THEOREM_DERIVATIONS_T0_T23_V1.md#section:T8` | MATCH | re-derive the theorem section against the reopened evidence | authority-gated |
| `SYNC-002` | `EVIDENCE:EXEC-CM-01` → `THEORY:T10` | VALIDATES | `research/orion-foundations-v3/THEOREM_DERIVATIONS_T0_T23_V1.md#section:T10` | MATCH | re-derive the theorem section against the reopened evidence | authority-gated |
| `SYNC-003` | `EVIDENCE:EXEC-CM-01` → `THEORY:T13` | VALIDATES | `research/orion-foundations-v3/THEOREM_DERIVATIONS_T0_T23_V1.md#section:T13` | MATCH | re-derive the theorem section against the reopened evidence | authority-gated |
| `SYNC-004` | `EVIDENCE:EXEC-NOV-01` → `EXPERIMENT:EXEC-NOV-01` | DEPENDS_ON | `research/orion-foundations-v3/exec/EXEC-NOV-01/EXECUTION_PROTOCOL.json` | MATCH | re-run the experiment protocol and re-register its receipt | sync-only |
| `SYNC-005` | `EVIDENCE:EXEC-P1-01` → `EXPERIMENT:EXEC-P1-01` | DEPENDS_ON | `research/orion-foundations-v3/exec/EXEC-P1-01/EXECUTION_PROTOCOL.json` | MATCH | re-run the experiment protocol and re-register its receipt | sync-only |
| `SYNC-006` | `EVIDENCE:EXEC-P1-01` → `THEORY:T14` | VALIDATES | `research/orion-foundations-v3/THEOREM_DERIVATIONS_T0_T23_V1.md#section:T14` | MATCH | re-derive the theorem section against the reopened evidence | authority-gated |
| `SYNC-007` | `EVIDENCE:EXEC-P1-01` → `THEORY:T21` | VALIDATES | `research/orion-foundations-v3/THEOREM_DERIVATIONS_T0_T23_V1.md#section:T21` | MATCH | re-derive the theorem section against the reopened evidence | authority-gated |
| `SYNC-008` | `EVIDENCE:EXEC-P10-01` → `EXPERIMENT:EXEC-P10-01` | DEPENDS_ON | `research/orion-foundations-v3/exec/EXEC-P10-01/EXECUTION_PROTOCOL.json` | MATCH | re-run the experiment protocol and re-register its receipt | sync-only |
| `SYNC-009` | `EVIDENCE:EXEC-P10-01` → `THEORY:T15` | VALIDATES | `research/orion-foundations-v3/THEOREM_DERIVATIONS_T0_T23_V1.md#section:T15` | MATCH | re-derive the theorem section against the reopened evidence | authority-gated |
| `SYNC-010` | `EVIDENCE:EXEC-P10-01` → `THEORY:T22` | VALIDATES | `research/orion-foundations-v3/THEOREM_DERIVATIONS_T0_T23_V1.md#section:T22` | MATCH | re-derive the theorem section against the reopened evidence | authority-gated |
| `SYNC-011` | `EVIDENCE:EXEC-P10-02` → `EXPERIMENT:EXEC-P10-02` | DEPENDS_ON | `research/orion-foundations-v3/exec/EXEC-P10-02/EXECUTION_PROTOCOL.json` | MATCH | re-run the experiment protocol and re-register its receipt | sync-only |
| `SYNC-012` | `EVIDENCE:EXEC-P10-02` → `THEORY:T22` | VALIDATES | `research/orion-foundations-v3/THEOREM_DERIVATIONS_T0_T23_V1.md#section:T22` | MATCH | re-derive the theorem section against the reopened evidence | authority-gated |
| `SYNC-013` | `EVIDENCE:EXEC-P11-01` → `EXPERIMENT:EXEC-P11-01` | DEPENDS_ON | `research/orion-foundations-v3/exec/EXEC-P11-01/EXECUTION_PROTOCOL.json` | MATCH | re-run the experiment protocol and re-register its receipt | sync-only |
| `SYNC-014` | `EVIDENCE:EXEC-P11-01` → `THEORY:T16` | VALIDATES | `research/orion-foundations-v3/THEOREM_DERIVATIONS_T0_T23_V1.md#section:T16` | MATCH | re-derive the theorem section against the reopened evidence | authority-gated |
| `SYNC-015` | `EVIDENCE:EXEC-P11-01` → `THEORY:T18` | VALIDATES | `research/orion-foundations-v3/THEOREM_DERIVATIONS_T0_T23_V1.md#section:T18` | MATCH | re-derive the theorem section against the reopened evidence | authority-gated |
| `SYNC-016` | `EVIDENCE:EXEC-P12-01` → `EXPERIMENT:EXEC-P12-01` | DEPENDS_ON | `research/orion-foundations-v3/exec/EXEC-P12-01/EXECUTION_PROTOCOL.json` | MATCH | re-run the experiment protocol and re-register its receipt | sync-only |
| `SYNC-017` | `EVIDENCE:EXEC-P12-01` → `THEORY:T17` | VALIDATES | `research/orion-foundations-v3/THEOREM_DERIVATIONS_T0_T23_V1.md#section:T17` | MATCH | re-derive the theorem section against the reopened evidence | authority-gated |
| `SYNC-018` | `EVIDENCE:EXEC-P13-01` → `EXPERIMENT:EXEC-P13-01` | DEPENDS_ON | `research/orion-foundations-v3/exec/EXEC-P13-01/EXECUTION_PROTOCOL.json` | MATCH | re-run the experiment protocol and re-register its receipt | sync-only |
| `SYNC-019` | `EVIDENCE:EXEC-P13-01` → `THEORY:T18` | VALIDATES | `research/orion-foundations-v3/THEOREM_DERIVATIONS_T0_T23_V1.md#section:T18` | MATCH | re-derive the theorem section against the reopened evidence | authority-gated |
| `SYNC-020` | `EVIDENCE:EXEC-P13-01` → `THEORY:T11` | VALIDATES | `research/orion-foundations-v3/THEOREM_DERIVATIONS_T0_T23_V1.md#section:T11` | MATCH | re-derive the theorem section against the reopened evidence | authority-gated |
| `SYNC-021` | `EVIDENCE:EXEC-P14-01` → `EXPERIMENT:EXEC-P14-01` | DEPENDS_ON | `research/orion-foundations-v3/exec/EXEC-P14-01/EXECUTION_PROTOCOL.json` | MATCH | re-run the experiment protocol and re-register its receipt | sync-only |
| `SYNC-022` | `EVIDENCE:EXEC-P14-01` → `THEORY:T19` | VALIDATES | `research/orion-foundations-v3/THEOREM_DERIVATIONS_T0_T23_V1.md#section:T19` | MATCH | re-derive the theorem section against the reopened evidence | authority-gated |
| `SYNC-023` | `EVIDENCE:EXEC-P14-01` → `THEORY:T21` | VALIDATES | `research/orion-foundations-v3/THEOREM_DERIVATIONS_T0_T23_V1.md#section:T21` | MATCH | re-derive the theorem section against the reopened evidence | authority-gated |
| `SYNC-024` | `EVIDENCE:EXEC-P15-01` → `EXPERIMENT:EXEC-P15-01` | DEPENDS_ON | `research/orion-foundations-v3/exec/EXEC-P15-01/EXECUTION_PROTOCOL.json` | MATCH | re-run the experiment protocol and re-register its receipt | sync-only |
| `SYNC-025` | `EVIDENCE:EXEC-P15-01` → `THEORY:T20` | VALIDATES | `research/orion-foundations-v3/THEOREM_DERIVATIONS_T0_T23_V1.md#section:T20` | MATCH | re-derive the theorem section against the reopened evidence | authority-gated |
| `SYNC-026` | `EVIDENCE:EXEC-P2-01` → `EXPERIMENT:EXEC-P2-01` | DEPENDS_ON | `research/orion-foundations-v3/exec/EXEC-P2-01/EXECUTION_PROTOCOL.json` | MATCH | re-run the experiment protocol and re-register its receipt | sync-only |
| `SYNC-027` | `EVIDENCE:EXEC-P2-01` → `THEORY:T12` | VALIDATES | `research/orion-foundations-v3/THEOREM_DERIVATIONS_T0_T23_V1.md#section:T12` | MATCH | re-derive the theorem section against the reopened evidence | authority-gated |
| `SYNC-028` | `EVIDENCE:EXEC-P3-01` → `EXPERIMENT:EXEC-P3-01` | DEPENDS_ON | `research/orion-foundations-v3/exec/EXEC-P3-01/EXECUTION_PROTOCOL.json` | MATCH | re-run the experiment protocol and re-register its receipt | sync-only |
| `SYNC-029` | `EVIDENCE:EXEC-P3-01` → `THEORY:T9` | VALIDATES | `research/orion-foundations-v3/THEOREM_DERIVATIONS_T0_T23_V1.md#section:T9` | MATCH | re-derive the theorem section against the reopened evidence | authority-gated |
| `SYNC-030` | `EVIDENCE:EXEC-P4-01` → `EXPERIMENT:EXEC-P4-01` | DEPENDS_ON | `research/orion-foundations-v3/exec/EXEC-P4-01/EXECUTION_PROTOCOL.json` | MATCH | re-run the experiment protocol and re-register its receipt | sync-only |
| `SYNC-031` | `EVIDENCE:EXEC-P4-01` → `THEORY:T2` | VALIDATES | `research/orion-foundations-v3/THEOREM_DERIVATIONS_T0_T23_V1.md#section:T2` | MATCH | re-derive the theorem section against the reopened evidence | authority-gated |
| `SYNC-032` | `EVIDENCE:EXEC-P4-01` → `THEORY:T3` | VALIDATES | `research/orion-foundations-v3/THEOREM_DERIVATIONS_T0_T23_V1.md#section:T3` | MATCH | re-derive the theorem section against the reopened evidence | authority-gated |
| `SYNC-033` | `EVIDENCE:EXEC-P5-01` → `EXPERIMENT:EXEC-P5-01` | DEPENDS_ON | `research/orion-foundations-v3/exec/EXEC-P5-01/EXECUTION_PROTOCOL.json` | MATCH | re-run the experiment protocol and re-register its receipt | sync-only |
| `SYNC-034` | `EVIDENCE:EXEC-P5-01` → `THEORY:T19` | VALIDATES | `research/orion-foundations-v3/THEOREM_DERIVATIONS_T0_T23_V1.md#section:T19` | MATCH | re-derive the theorem section against the reopened evidence | authority-gated |
| `SYNC-035` | `EVIDENCE:EXEC-P5-01` → `THEORY:T21` | VALIDATES | `research/orion-foundations-v3/THEOREM_DERIVATIONS_T0_T23_V1.md#section:T21` | MATCH | re-derive the theorem section against the reopened evidence | authority-gated |
| `SYNC-036` | `EVIDENCE:EXEC-P6-01` → `EXPERIMENT:EXEC-P6-01` | DEPENDS_ON | `research/orion-foundations-v3/exec/EXEC-P6-01/EXECUTION_PROTOCOL.json` | MATCH | re-run the experiment protocol and re-register its receipt | sync-only |
| `SYNC-037` | `EVIDENCE:EXEC-P6-01` → `THEORY:T10` | VALIDATES | `research/orion-foundations-v3/THEOREM_DERIVATIONS_T0_T23_V1.md#section:T10` | MATCH | re-derive the theorem section against the reopened evidence | authority-gated |
| `SYNC-038` | `EVIDENCE:EXEC-P6-01` → `THEORY:T11` | VALIDATES | `research/orion-foundations-v3/THEOREM_DERIVATIONS_T0_T23_V1.md#section:T11` | MATCH | re-derive the theorem section against the reopened evidence | authority-gated |
| `SYNC-039` | `EVIDENCE:EXEC-P7-01` → `EXPERIMENT:EXEC-P7-01` | DEPENDS_ON | `research/orion-foundations-v3/exec/EXEC-P7-01/EXECUTION_PROTOCOL.json` | MATCH | re-run the experiment protocol and re-register its receipt | sync-only |
| `SYNC-040` | `EVIDENCE:EXEC-P7-01` → `THEORY:T13` | VALIDATES | `research/orion-foundations-v3/THEOREM_DERIVATIONS_T0_T23_V1.md#section:T13` | MATCH | re-derive the theorem section against the reopened evidence | authority-gated |
| `SYNC-041` | `EVIDENCE:EXEC-P8-01` → `EXPERIMENT:EXEC-P8-01` | DEPENDS_ON | `research/orion-foundations-v3/exec/EXEC-P8-01/EXECUTION_PROTOCOL.json` | MATCH | re-run the experiment protocol and re-register its receipt | sync-only |
| `SYNC-042` | `EVIDENCE:EXEC-P8-01` → `THEORY:T4` | VALIDATES | `research/orion-foundations-v3/THEOREM_DERIVATIONS_T0_T23_V1.md#section:T4` | MATCH | re-derive the theorem section against the reopened evidence | authority-gated |
| `SYNC-043` | `EVIDENCE:EXEC-P8-01` → `THEORY:T10` | VALIDATES | `research/orion-foundations-v3/THEOREM_DERIVATIONS_T0_T23_V1.md#section:T10` | MATCH | re-derive the theorem section against the reopened evidence | authority-gated |
| `SYNC-044` | `EVIDENCE:EXEC-P8-01` → `THEORY:T11` | VALIDATES | `research/orion-foundations-v3/THEOREM_DERIVATIONS_T0_T23_V1.md#section:T11` | MATCH | re-derive the theorem section against the reopened evidence | authority-gated |
| `SYNC-045` | `EVIDENCE:EXEC-P9-01` → `EXPERIMENT:EXEC-P9-01` | DEPENDS_ON | `research/orion-foundations-v3/exec/EXEC-P9-01/EXECUTION_PROTOCOL.json` | MATCH | re-run the experiment protocol and re-register its receipt | sync-only |
| `SYNC-046` | `EVIDENCE:EXEC-P9-01` → `THEORY:T14` | VALIDATES | `research/orion-foundations-v3/THEOREM_DERIVATIONS_T0_T23_V1.md#section:T14` | MATCH | re-derive the theorem section against the reopened evidence | authority-gated |
| `SYNC-047` | `EVIDENCE:EXEC-PA-01` → `EXPERIMENT:EXEC-PA-01` | DEPENDS_ON | `research/orion-foundations-v3/exec/EXEC-PA-01/EXECUTION_PROTOCOL.json` | MATCH | re-run the experiment protocol and re-register its receipt | sync-only |
| `SYNC-048` | `EVIDENCE:EXEC-PA-01` → `THEORY:T8` | VALIDATES | `research/orion-foundations-v3/THEOREM_DERIVATIONS_T0_T23_V1.md#section:T8` | MATCH | re-derive the theorem section against the reopened evidence | authority-gated |
| `SYNC-049` | `EVIDENCE:EXEC-PA-01` → `THEORY:T10` | VALIDATES | `research/orion-foundations-v3/THEOREM_DERIVATIONS_T0_T23_V1.md#section:T10` | MATCH | re-derive the theorem section against the reopened evidence | authority-gated |
| `SYNC-050` | `EVIDENCE:EXEC-PA-01` → `THEORY:T11` | VALIDATES | `research/orion-foundations-v3/THEOREM_DERIVATIONS_T0_T23_V1.md#section:T11` | MATCH | re-derive the theorem section against the reopened evidence | authority-gated |
| `SYNC-051` | `EVIDENCE:EXEC-PA-01` → `THEORY:T20` | VALIDATES | `research/orion-foundations-v3/THEOREM_DERIVATIONS_T0_T23_V1.md#section:T20` | MATCH | re-derive the theorem section against the reopened evidence | authority-gated |
| `SYNC-052` | `EVIDENCE:EXEC-XP-01` → `EXPERIMENT:EXEC-XP-01` | DEPENDS_ON | `research/orion-foundations-v3/exec/EXEC-XP-01/EXECUTION_PROTOCOL.json` | MATCH | re-run the experiment protocol and re-register its receipt | sync-only |
| `SYNC-053` | `EVIDENCE:EXEC-XP-01` → `THEORY:T23` | VALIDATES | `research/orion-foundations-v3/THEOREM_DERIVATIONS_T0_T23_V1.md#section:T23` | MATCH | re-derive the theorem section against the reopened evidence | authority-gated |

## By edge kind

- `DEPENDS_ON`: 20 obligations (0 authority-gated)
- `VALIDATES`: 34 obligations (34 authority-gated)
