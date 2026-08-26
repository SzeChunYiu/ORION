# ORION-15 hidden-cause fresh-transfer campaign runbook V1

Frozen 2026-08-17 against `origin/main`. This runbook does **not** launch
providers, does **not** mint empirical credit, and does **not** recommend host
promotion.

The executable gate is:

```bash
PYTHONPATH=src python -m orion.study.p5.fresh_transfer_campaign
```

Exit `2` means the campaign is unbound. The process prints only credential
*names* when they are missing. Values are never copied into the report.

## Why this campaign is frozen

Issue #159 may not run a result-bearing hidden-cause fresh-transfer campaign
until **all** of the following are true on `origin/main`:

1. `#8` packet is bound — the in-source Phase-2 registry must execute the
   published live-trial identities, not a second pair of research problems.
2. Phase-2 preflight is fail-closed — `#277` / PR `#289`. The P0 probe
   (`subject="a"*64`, `provider="b"*64`, `evaluator="c"*64`) must **not**
   reach `READY_TO_EXECUTE_SHADOW_TRIAL`.
3. Required credentials exist in the host environment without being printed.

As of `origin/main` after PR `#289`, condition (2) holds: the P0 probe no
longer reaches READY. Conditions (1) and (3) still fail. The only admissible
campaign status remains `CANNOT_CHECK` / `REFUSED_UNBOUND`. `#277` stays OPEN
because the merged workflow still does not execute the frozen `#8` packet.

| Binding | Frozen `#8` packet | In-source execution registry |
|---|---|---|
| WIDE | `ORION-15.LIVE.WIDE.stopping-rule-source-families` | `phase2:wide:microglia-complement-cross-disease` |
| DEEP | `ORION-15.LIVE.DEEP.flat-round-without-lineage` | `phase2:deep:mos2-screening-exciton` |
| Epoch | `ORION-15.shadow-live-research.epoch-1` | per-run `github-actions-<run_id>-attempt-<n>` |
| Budget | `24.0` | `32` |

These are two pairs of research problems in different fields. Silently adopting
either registry would settle an authority question by fiat. The preflight names
**both** sides and refuses.

## Immutable diagnosis seed — preserve, do not "fix"

The merged GLM-5.2 attribution archive is **not** fresh-transfer evidence. It is
the diagnosis seed later campaigns must start from:

- path: `papers/orion-15-self-orion/evidence/glm-5.2-attribution/`
- model: `glm-5.2`
- `21/24 = 0.875` correct, macro-F1 `0.8726`
- transport/execution errors: `0`
- immutable misclassifications:
  1. `ORION-15-HC-002`: `RETRIEVAL_MISS -> REPRESENTATION_GAP`
  2. `ORION-15-HC-012`: `ENVIRONMENT_DEPENDENCY_TOOL_FAILURE -> IMPLEMENTATION_BUG`
  3. `ORION-15-HC-018`: `REPRESENTATION_GAP -> METHOD_BASIS_GAP`

A 24/24 rewrite, deletion of those three rows, or substitution of the unbound
`#212` 24/24 comment is a `CANNOT_CHECK` blocker, not an improvement.

## Credential names (never log values)

From `papers/orion-15-self-orion/protocol/LIVE_TRIAL_PACKET_V1.json`:

```text
OPENAI_API_KEY
ORION_PROTECTED_VERIFIER_URL
ORION_PROTECTED_VERIFIER_TOKEN
ORION_PROTECTED_VERIFIER_ARTIFACT_HASH
ORION_PHASE2_EVALUATION_EPOCH_ID
```

Presence is a boolean. A missing name is `credentials_absent:<NAME>`. A present
name is never followed by its value in stdout, reports, or exceptions.

## Host procedure once `#8` is bound

Do not skip the preflight. Do not launch from a worker that can merge.

1. Confirm `origin/main` still contains fail-closed Phase-2 preflight (`#289`;
   P0 probe must not reach READY). `#277` is not closed until the frozen `#8`
   packet is the one the execution path would run.
2. Confirm the in-source registry task ids equal the published `#8` packet.
   Governance, not this runbook, chooses which registry is canonical; this
   gate only refuses divergence.
3. Confirm credential *names* are present in host custody.
4. Recompute the 21/24 archive from `results.jsonl` and refuse if the three
   errors moved.
5. Freeze subject / provider-manifest / evaluator / epoch / split hashes
   **before** outcome access. Record them in the host evidence bundle.
6. Run the `#8` wide + deep live trial and the matched simple baseline under
   the frozen resource contract.
7. Run at least one `#76` observed-failure development cycle through
   `STATIC -> DIAGNOSE -> DISCRIMINATE -> CANDIDATE -> REPLAY -> FRESH -> PROTECTED`.
8. Execute matched baselines. Unavailable external implementations stay
   `CANNOT_CHECK`; do not substitute weaker proxies as official arms.
9. Retain every harmful/null/rejected candidate on the append-only negative
   history chain.
10. Host-only promotion recommendation is derived from protected evidence.
    Candidate code must not self-certify or merge.

If any step lacks a receipt, the campaign remains `CANNOT_CHECK`. Architecture
completion, unit-test green, or a READY preflight is not fresh-transfer
benefit.

## Authority boundary

`FreshTransferCampaignReport.recommends_host_promotion` is structurally
`False`. `empirical_authority` is structurally `CANNOT_CHECK` until a later
host evidence archive is independently admitted. This entrypoint never calls a
provider.

## Reproduction

```bash
PYTHONPATH=src pytest -q tests/test_p5_fresh_transfer_campaign_preflight.py
PYTHONPATH=src python -m orion.study.p5.fresh_transfer_campaign \
  --write-audit papers/orion-15-self-orion/evidence/ISSUE_159_CHECKBOX_AUDIT_V1.json
```

The checkbox audit ticks only items independently verified on the inspected
tree. Result-bearing `#8`/`#76`/metrics/figure boxes remain unticked.
