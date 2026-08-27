# P5 frozen live-trial packet is not bound to the merged execution path

**Observed:** 2026-08-17 while discriminating whether issue #8's
`papers/paper-05-self-orion/protocol/LIVE_TRIAL_PACKET_V1.json` is a valid
pre-outcome freeze that may now be executed.

**Terminal:** `CANNOT_CHECK` on the packet-to-closure-subject binding, plus a
separate structural defect recorded below. No gate is closed by this note and
no authority is granted by it.

## What was checked, and what held

Four hypotheses about the packet were tested and **refuted**. The packet is in
better condition than the surrounding issue text suggests.

1. **"The packet is Copilot-scoped."** Refuted. The packet freezes
   `orion.providers.llm.openai_responses.OpenAIResponsesLLMProvider` (reasoner)
   and `orion.providers.verification.protected_http.ProtectedHTTPVerificationProvider`
   (verification). The Copilot CLI lane does not appear in the packet at all; it
   was added to `src/orion/providers/live_phase2.py` **after** the freeze, by
   `38bc710` and `a844f5d` (both 2026-08-17), as an additive alternative
   constructor. The packet was merged by `fbf0d37` at 2026-08-16 23:53:12 +0200.

2. **"The packet is stale / has been edited since freeze."** Refuted. The blob
   identity of `LIVE_TRIAL_PACKET_V1.json` is `198347b9e0` at both `fbf0d37`
   (freeze) and current `main` (`86ebc02`). Byte-identical across 171 intervening
   commits.

3. **"Merged GLM-5.2 outcomes make the packet post-outcome."** Refuted — the two
   are different subjects. `evidence/glm-5.2-attribution/report.json` records
   `suite_path = papers/paper-05-self-orion/evidence/hidden-cause-suite/PROTECTED_SUITE_V1.json`,
   24 root-cause attribution cases `P5-HC-001`..`P5-HC-024`. The packet's tasks are
   `P5.LIVE.WIDE.stopping-rule-source-families` and
   `P5.LIVE.DEEP.flat-round-without-lineage`. Post-hoc-ness is defined relative to
   outcomes on the *same* tasks.

4. **"Outcomes already exist for the packet's tasks."** Refuted, with scope stated.
   Searching both task id strings across the full worktree returns only the packet
   itself, the source constants (`live_packet.py:493-494`) and one unit test —
   no result artifact. `git log --all -S` on
   `P5.LIVE.DEEP.flat-round-without-lineage` returns only the three freeze-era
   commits (`937fe21`, `7625476`, `fbf0d37`, all 2026-08-16). The packet's
   `outcome_accessed: false` is therefore corroborated by the tree, not merely
   self-declared.

The deep task's answer region has also **not** drifted: the gold targets the
bounded-saturation guard for a flat round declaring no evidence lineage, which
lives in `src/orion/kernel/saturation.py`. That file's blob is `cc44ca4d2d0f` at
both freeze and HEAD, with zero intervening commits.

## Failure

**The packet's subject binding is absent by construction, and the merged
execution path does not execute the packet.**

### (a) Subject binding is absent, not merely deferred

`corpus_revision` is the literal string `"UNBOUND"` at the packet top level and
in both task bindings. `src/orion/self_orion/live_packet.py` treats this as a
sentinel and its own preflight blocks on it
(`"deep-target corpus revision is UNBOUND; bind it with --corpus-revision"`).
Deferral to execution is therefore intentional and guarded — but it means the
packet by itself binds **no** subject.

Independently, `PHASE_1_CORE_TECHNICALLY_CLOSED` — the terminal #75 declares —
appears **nowhere** in the tree. There is no in-repo receipt naming the exact
final Phase-1-derived closure subject that #8 requires the trial be bound to.
So the question "is the packet frozen against the exact final closure subject?"
cannot be answered from the repository: the packet declares no subject, and no
canonical subject is recorded. This is `CANNOT_CHECK`, and it is the correct
terminal rather than a guess.

### (b) The merged workflow runs a different trial than the frozen packet

`.github/workflows/p5_phase2_live_execution.yml` (added `f2d3f44`, 2026-08-17 —
absent at freeze) is triggered by a push to `main` touching itself or
`papers/paper-05-self-orion/phase2/LIVE_EXECUTION_TRIGGER.txt` (added `f74e494`).
It never reads `LIVE_TRIAL_PACKET_V1.json`.

The packet is not an orphan artifact — it is read and protected elsewhere, which
is why the gap is easy to miss. `load_packet_document` (`live_packet.py:811`)
reads it and raises on a fingerprint mismatch, so a hand-edited packet fails
rather than being trusted. `write_packet_document` (`live_packet.py:780`) refuses
to overwrite the frozen path with a corpus-bound packet, on the stated ground that
"an artifact any later command can rewrite in place is not frozen". Unit tests
(`tests/unit/self_orion/test_live_packet.py:193-243`) pin the on-disk JSON to the
in-source `packet_document()`. Verified independently here: recomputing
`sha256` over the document body reproduces the declared
`packet_fingerprint 53f99a2c7e6cfdd74cf5b10a62ba273bc911999b5719cf700eda64044f917e48`
exactly.

So the packet is well-guarded **as a published artifact**. The defect is that the
codebase carries **two divergent frozen task registries** — the packet's, in
`live_packet.py`, and a second one in `phase2_preflight.py` — and the merged
execution workflow consults the second, which is not the published protocol.

The workflow calls
`orion.self_orion.phase2_preflight.build_frozen_live_trial_packet(preflight)`,
which **rebuilds** a packet from runtime values. The divergences are not cosmetic:

| Binding | Frozen packet | What the workflow would execute |
|---|---|---|
| WIDE task | `P5.LIVE.WIDE.stopping-rule-source-families` (stopping rules / saturation) | `phase2:wide:microglia-complement-cross-disease` (microglial complement signalling) |
| DEEP task | `P5.LIVE.DEEP.flat-round-without-lineage` (ORION source corpus) | `phase2:deep:mos2-screening-exciton` (monolayer MoS2 screening) |
| Initial domains | `domain:orion-source`, `domain:evidence-synthesis` | `neuroimmunology`, `2d-materials`, … |
| DEEP ground truth | `ground_truth_bound: true`, `protected_gold_digest: 0c237e14…` | `FrozenShadowTaskSpec` has **no gold field**; the digest is not carried |
| `packet_id` | `P5.shadow-live-research.v1` | `preflight.protocol_id` = `phase2-shadow-closure-v1` |
| Epoch | `P5.shadow-live-research.epoch-1` | env, or for the Copilot lane `github-actions-<run_id>-attempt-<n>` (generated per run) |
| Budget units | `24.0` (and baseline matched at `24.0`) | workflow default `32` |
| Reasoner model var | `ORION_P5_REASONER_MODEL` | `ORION_PHASE2_REASONER_MODEL` (default `gpt-5.6`) |
| Baseline id | `simple_llm_retrieval_baseline.v1` | `simple-llm-retrieval-baseline-v1` |

The tasks are not a near-miss variant of the frozen tasks. They are a different
pair of research problems in different fields.

### (c) The gate that should catch this is a shape check, not an identity check

`assess_phase2_preflight` reaches `READY_TO_EXECUTE_SHADOW_TRIAL` when
`subject_revision_hash`, `provider_manifest_hash` and `evaluator_artifact_hash`
are each *well-formed lowercase hex of length 64 and not all-zeros*, the epoch and
baseline id are *non-empty*, and `resource_budget_units > 0`. None of the five is
compared against any frozen value. Any syntactically valid digest passes.

The consequence is specific and checkable: `provider_manifest_hash` is
`sha256` over `LivePhase2ProviderManifest.payload`, which includes the reasoner
`model` string and the verifier `endpoint`. Substituting the reasoner — Copilot,
GLM-5.2, or any other — therefore *necessarily* produces a different manifest
hash than the frozen `b08642b8…`. That substitution would be **admitted silently**,
because the gate only asks whether the hash is well-formed. The binding exists in
the artifact and is not consulted by the gate.

The module already knows this failure mode. `phase2_preflight.py:152-160` carries a
comment explaining that the authority-attack check was previously a count and was
hardened to an identity check against `AUTHORITY_ATTACK_IDS`, ending: "The registry
existing and the gate consulting it are different things, which is the whole
lesson." The same lesson was not applied to the three binding hashes ten lines
below, nor to the budget.

## What is correctly built

Recording this so the repair does not damage it. The packet's own declared
execution path — `python -m orion.self_orion.live_packet --live`, the command the
packet names — is sound. `_run_live` calls `preflight(packet)` **before**
constructing any provider or spending anything, and refuses on missing
credentials, on `corpus_revision == UNBOUND`, and on an environment epoch that
differs from the frozen epoch. Refusal emits immutable `CANNOT_CHECK` episodes and
returns `EXIT_CANNOT_CHECK`. `execution_manifest` independently refuses to bind a
run to an `UNBOUND` corpus. `attest_repository_subject` binds the subject from a
clean HEAD and fails on a dirty or untracked worktree.

The defect is that the merged workflow bypasses this path entirely.

## Failure class

`FROZEN_ARTIFACT_NOT_CONSULTED_BY_EXECUTION`

A protocol artifact is frozen, merged, content-fingerprinted, tamper-checked on
read and pinned by tests — and the execution path that claims to run it consults a
*different* in-source registry instead, reconstructing its own bindings from
runtime state. Every individual guard passes. The artifact is genuinely protected;
it simply is not the thing the executor reads. Local integrity checks cannot
detect this, because nothing is corrupt: two coherent definitions exist and the
wrong one is wired to the trigger.

Distinct from stale-evidence replay (the artifact here is byte-intact and
genuinely pre-outcome) and from subject substitution after the fact (no outcomes
exist on either task set). The diagnostic that finds it is not "is the freeze
valid?" but "which definition does the code that spends money actually load?".

## Correct response

1. Do **not** execute the current workflow and count it as an #8 trial. It would
   produce a real, paid outcome on `phase2:wide:microglia-complement-cross-disease`
   and `phase2:deep:mos2-screening-exciton` under budget 32, with no protected gold
   carried, and none of it would satisfy #8's frozen-packet requirements.
2. Do **not** re-freeze the packet as a first move. It is byte-intact and
   pre-outcome; re-freezing would discard a good artifact and invite exactly the
   post-hoc-freeze suspicion this repository guards against.
3. Bind execution to the frozen packet: have the Phase-2 path load
   `LIVE_TRIAL_PACKET_V1.json`, recompute and compare `packet_fingerprint`, and
   **identity-check** `provider_manifest_hash`, `evaluator_artifact_hash`,
   `evaluation_epoch_id`, `baseline_id`, the task id set and `resource_limits`
   against it — failing closed on any mismatch. Alternatively trigger the packet's
   own `--live` command, which already enforces most of this.
4. Carry `protected_gold_digest` and `ground_truth_bound` through
   `FrozenShadowTaskSpec`, or the DEEP criteria `D2.gold-tokens` and
   `D3.gold-anchor-cited` cannot be evaluated at all.
5. Bind the corpus before the run (`--corpus-revision`) to the exact final
   Phase-1-derived closure subject, once that subject has a recorded identity.
   It does not currently have one.
6. Treat provider substitution as requiring a new pre-outcome packet with a
   recomputed `provider_manifest_hash`, never as an env-level swap. Such a freeze
   would still be legitimately pre-outcome today, because no outcomes exist on
   these tasks.

## Nearest work absorbed

Twelve `codex/issue-102-*` / `codex/issue-159-*` branches work this problem. Read
read-only via `git show`; none checked out or modified.

**Merged (8):** `copilot-live-provider`, `copilot-model-probe`,
`copilot-model-refresh`, `p5-v2-protocol`, `p5-v2-evidence`, `p5-v2-analysis`,
`phase2-live-execution`, `phase2-live-preflight`. These produced the Copilot lane
and the live-execution workflow analysed above.

**Unmerged (4):** `github-models-fallback` (8 ahead), `open-weight-phase2` (6),
`hidden-cause-suite` (9), `issue-159-p5-live-trial` (4). Per #208, unmerged branch
work is not evidence.

**The substitution question was already answered in practice, and answered wrongly.**
`github-models-fallback` and `open-weight-phase2` each add a new reasoner/verifier
adapter and edit `.github/workflows/p5_phase2_live_execution.yml`, and each touches
**zero** files under any `protocol/` directory. Neither re-freezes
`LIVE_TRIAL_PACKET_V1.json` or produces a new packet. Together with the merged
Copilot lane, that is **three** successive provider substitutions into a packet
frozen for none of them, with no new pre-outcome freeze in any case.

This is not a precedent to follow. It is the predicted consequence of the defect
above: because the workflow never loads the packet and the gate only shape-checks
`provider_manifest_hash`, each new lane can add a constructor yielding a different
manifest hash and be admitted silently. The pattern is evidence *for* the finding.

**#8's governing text does not permit substitution within an existing freeze.**
The ORION development protocol requires, before final trial outcome access:
"Freeze task packet, provider identities, resource limits evaluator before
observing outcomes." Trial requirements separately list "Real LLM provider identity
frozen", "Real retrieval-source identities frozen" and "Protected evaluator/verifier
identity epoch frozen outside candidate custody." Provider identity is named as a
frozen quantity. Changing it changes the freeze, so it requires a **new** freeze that
is itself pre-outcome. #8 contains no substitution-within-freeze clause.

Mechanically this is already enforced at the artifact level and only there:
`provider_manifest_hash` is `sha256` over a payload including the reasoner `model`
and the verifier `endpoint`, so any substitution necessarily yields a hash other
than the frozen `b08642b8…`. The binding exists; the gate does not consult it.

**A correction to #159's reported result.** #159 comment 2 reports the GLM-5.2
hidden-cause campaign as "Step 5/6 — COMPLETE" at 24/24 (100.0%), macro F1 1.000,
all 24 cases at HIGH confidence, via `cmkey.cn`. The merged artifact on `main`
reports **21/24** (0.875), macro F1 **0.875**, confidence MEDIUM 9 / HIGH 15, via
`http://127.0.0.1:8765`, with `P5-HC-002`, `P5-HC-012` and `P5-HC-018` incorrect.
Recounting the raw `results.jsonl` independently reproduces 21/24 and the
MEDIUM/HIGH split, so the merged artifact is self-consistent.

Two merged states exist for this campaign. `1061d72` recorded 0/24, all LOW
confidence, endpoint `https://api2.cmkey.cn/v1`. `688fe74`, titled "honest evidence
re-run", recorded 21/24, endpoint `http://127.0.0.1:8765`, and is what `main`
carries. The comment's figure matches neither.

Which run the comment describes is **not determinable from the repository**. It may
describe the cmkey run whose merged record is 0/24, an unrecorded third run, or a
mis-transcription; nothing in the tree distinguishes these. The numbers and
endpoints above are stated as facts and the mapping is left open, for the same
reason the subject binding is left at `CANNOT_CHECK`.

#212 already quarantined the 24/24 report as `UNBOUND_EXECUTION_REPORT`, so it
already carries no empirical authority. What is added here is only that the honest
re-run has since landed and supplies a verified value, 21/24, to set against it.
The comment remains uncorrected on the issue scoped to closing #8's dependencies,
so a reader of #159 still takes away a perfect score.

**On the keyless route.** `AUTORESEARCHBENCH_WIDE_KEYLESS_PROBE_V1.json` records
`candidate: "ORION keyless arXiv public-provider probe"` with `total_tokens: 0` and
`claim_scope: "external_probe_not_full_multi_provider_orion"`. Keyless here means a
public arXiv retrieval route consuming no LLM tokens — there is no LLM identity to
freeze, so it cannot satisfy #8's "Real LLM provider identity frozen". The artifact
scopes its own claim correctly. Its `provider_status_counts` also record 52/400
`RATE_LIMITED`, a harness-level confound that any hit-rate near zero should be
attributed against before being read as a capability null.

## Discriminator / reopen condition

This note is superseded when **all** of the following hold on merged `main`:

- an in-repo receipt names the exact final Phase-1-derived closure subject by
  commit oid and subject revision hash;
- the execution path loads the frozen packet and fails closed on any binding
  mismatch, demonstrated by a hostile test that flips one binding and observes
  refusal;
- `resource_budget_units` at execution equals the frozen `24.0`, or the packet is
  re-frozen pre-outcome at the intended budget;
- the DEEP protected gold digest is carried into execution and checked.

Until then the empirical status of #8 is `NOT_EXECUTED`, not `FAILED` — the trial
has never run, on either task set.

## General lesson candidate

A freeze is only as strong as the check that consults it, and "consulted
somewhere" is not "consulted by the executor". This packet is fingerprinted,
tamper-checked, overwrite-guarded and test-pinned — and none of that reaches the
workflow that would spend the money, because the workflow reads a second
definition. Auditing a frozen artifact by verifying the artifact will always
return green here. The question that finds the defect is which definition the
spending path loads.

Where two definitions of the same frozen thing exist in one codebase, that
duplication is itself the defect: one must be derived from the other or deleted.
A hostile test should flip one binding in the published artifact and assert the
executor refuses — a test that cannot fail if the executor never reads the
artifact, which is exactly what makes its absence diagnostic.

Corollary for verdicts: "the packet exists and is pre-outcome" and "executing now
would satisfy the issue" are independent claims. Establishing the first says
nothing about the second.
