# P14 External Rounds R1 (frontier agents) + R3 (negative-history ablation) — Execution Plan V1 (FROZEN)

Status: `FROZEN`. Machine-readable twin: `P14_EXTERNAL_R1R3_EXECUTION_PLAN_V1.json`
(the JSON is authoritative; this file mirrors it). Frozen **before** any full-lane
execution: the only pre-freeze agent calls were one single-packet wiring probe per
system (`PKT-FC-0001`, recorded in the harvest summaries as `already_harvested`).
Driver: `r1/run_p14_external_r1_v1.py` (stdlib only, fail-closed, resumable).
After the freeze commit, none of the plan, driver, or suite may change; any
revision requires a new plan version and a new receipt.

Binds `P14_EXTERNAL_PILOT_PROTOCOL_V1.md` §6 (R1, R3), §4 (metrics reused
verbatim), §7 (hostile checks), §9 (receipt). Nothing in this round weakens
`check_external_contract_v1.py`.

## 1. Systems

| System | Kind | Invocation | Credential provenance |
|---|---|---|---|
| `CODEX_GPT56` | external frontier agent (non-ORION) | `codex exec --skip-git-repo-check <prompt>`; stdin `/dev/null`; cwd `/tmp/p14r1_exec` (empty scratch, no instruction files) | operator-local codex CLI login; no token material in any artifact |
| `CLAUDE_GLM53` | external frontier agent (non-ORION) | `claude -p <prompt> --output-format json`; same cwd | operator-local claude CLI, `CLAUDE_CONFIG_DIR=/Users/billy/.claude-cn`, `ANTHROPIC_BASE_URL=https://api.z.ai/api/anthropic`, `ANTHROPIC_MODEL=glm-5.3` |

Ambient-config honesty: the codex global instructions on this host contain
operator/LUNARC ops text (no science or programme content) and are not modified;
the claude-cn config dir has no `CLAUDE.md` and the scratch cwd carries no project
memory. Both states are recorded in each harvest summary. Blocked systems
(no local settings file at freeze time, not runnable within existing
credentials): `DEEPSEEK_STACK`, `GLM_52_OPENROUTER_STACK`.

## 2. Prompt contract

Byte-identical across systems and arms; full text embedded in the plan JSON
(header sha256 recorded there). Structure: neutral instruction header (role,
read-only evidence scope, disposition glosses, authority-status glosses, required
JSON content fields, "respond with the JSON object only") + the frozen record
block (packet fields as canonical JSON + every visible evidence record verbatim
with `artifact_id`, `role`, `sha256`) + footer. The header necessarily enumerates
the decision-schema enums; it carries no packet-specific content, so the
fail-closed leakage scan applies to the record block. The harness overwrites
`schema_version`, `packet_id`, `system_id`, `resource_usage`; the agent supplies
content fields only.

## 3. R1 — frontier-agent round

All 67 packets, both systems, one call per packet, sequential within a system
(the two systems run as independent processes). Decisions must validate against
`P14_EXTERNAL_DECISION_SCHEMA_V1.json` (fail closed). Retry policy: ≤3 attempts
per packet, 600 s subprocess timeout per attempt. Missing-run policy: no
schema-valid decision after 3 attempts ⇒ failure log row, run status `DEGRADED`,
no imputation; counts and packet ids reported. Outputs: `r1/out_r1/`
(`decisions/`, `raw/` per-packet prompt + per-attempt output archive,
`harvest_*_summary.json`).

## 4. R3 — longitudinal negative-history ablation

Subset: the 3 round-pairs = 6 `REGIME_CHANGE_REOPEN` packets
(`PKT-FC-0022/0023`, `PKT-EM-0023/0024`, `PKT-RI-0019/0020`; gold all `REOPEN`).

Withhold set (one record per round-2 packet — the record that carries the
**retained earlier-round history**): `PKT-FC-0023`→`EV-FC-00096` ("Round 1's
certificate remains valid for its scope"), `PKT-EM-0024`→`EV-EM-00182` ("the
claim's record must be amended with both rounds"), `PKT-RI-0020`→`EV-RI-00251`
("the round-1 'unarchivable' record is amended ... earlier scope retained").
Rule: the single non-protocol, non-current-round record whose content amends or
retains the round-1 record/certificate/scope. Round-1 packets are unablatable:
their round-1 result is the subject of the packet, not retained history.

Arms: present = R1 rows restricted to the subset (identical input, same session
window); withheld = fresh calls on the 3 round-2 packets with the withhold set
removed (round-1 rows from R1). Scoring: reopen accuracy and negative loss under
the frozen metric definitions (`run_p14_external_pilot_v1.system_metrics`
verbatim), on the 6-packet subset and on the 3 round-2 packets alone. Outputs:
`r1/out_r3/`.

## 5. Scoring and authority

Metrics are computed by importing `system_metrics` from the pilot runner
verbatim; no metric definition lives in the round driver. The co-primary
promotion condition is recorded as `CANNOT_CHECK`: R2 independent blinded human
adjudication is not available in this execution lane (missing authority:
independent non-author adjudicators), so model-only rounds cannot confirm it.
No promotion claim is made; the paper state does not change. Per-row
`authority_status` values emitted by a system (including
`EXTERNALLY_AUTHORIZED`) are recorded unedited but carry no adjudication
authority for any manuscript claim.

## 6. Verify phase (hostile checks, fail-closed)

Suite digests vs the frozen plan; decision-schema conformance of every row;
driver-field enforcement; measured `resource_usage` presence; evidence-budget
enforcement; prompt re-render byte-compare against the archived prompt;
leakage re-scan of every record block (adjudication tokens, programme name,
gold-only keys); programme-name scan of full prompts and raw outputs
(warning level). Exit 0 = integrity holds; `DEGRADED` (if any) is reported,
never silently dropped.
