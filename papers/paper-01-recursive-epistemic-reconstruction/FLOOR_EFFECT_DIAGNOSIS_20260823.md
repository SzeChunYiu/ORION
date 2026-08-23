# P1 campaign floor effect — diagnosed: three instrument defects; H1 untested and unrescuable from existing data

Diagnosis run 2026-08-23 over `results/raw/test_scored.jsonl` (2,880 records = 12 × 48 × 5;
repeats vacuous — 1 of 576 (system,case) pairs shows any across-seed variation, so
effective n = 12 × 48).

## Defect 1 — the floor is a perception ceiling, by construction

`root_success` (`src/orion/study/p1/metrics.py:534`) is binary and requires the shared
lexical cue detector (`extract_cues`, fixed `_MARKERS` substring table,
`baselines.py:218`) to have seen a **material** cue. Run over the 48 TEST cases, a
material cue fires on **exactly one** (p1-c111, marker "crashes" → EXECUTION); 23 have
weak cues only; 24 none. So `1/48` is a hard ceiling for the entire mechanical arm —
`Δ = 0` and `p = 1` are forced arithmetic, not findings. The suite bans gold vocabulary
from public fields, so a lexical marker table cannot recover formulation responsibility
*by design* — and `baselines.py`'s own docstring says so ("all eleven systems abstain on
47 of 48 cases… the graded arm is the live provider"). Known at freeze time.

## Defect 2 — the campaign's only success is a proxy false positive

p1-c111's gold responsibility is INTERFACE (demand signalling); the detector matched an
EXECUTION cue; the succeeding record simultaneously carries `failure_mode=MISSED_REFRAME`,
`responsibility_correct=False`, reopen recall 0. `root_solved` should require
responsibility-consistent clearing. The single non-floor cell in 2,880 records is wrong.

## Defect 3 — the graded arm discards its answers

`ProviderBackedSystem.run()` (`provider.py` ~181) sends the prompt, receives ~1,205
tokens/case of completion, then constructs a **hardcoded-empty** `SystemTrace`
(`reframed=False`, no responsibility, no coordinates, no reopen). The model's answer is
never parsed and the raw text is archived nowhere. 240/240 live records are empty
regardless of provider health. Also: `INTEGRITY_NOTE.md` is stale — it describes the
superseded auth-failure file (md5 `8ebcb759…`), while the file in tree (`c881cded`, md5
`2e6041bd…`) is a later all-OK glm-5.2 re-run.

## The decisive negative: the ablation contrast does not exist in the data

`orion_full` is **record-for-record identical** (0/240 records differ) to
`orion_without_explicit_M`, `orion_without_explicit_W`, and
`full_reset_instead_of_dependency_reopen`. What graded sub-signal exists *inverts* the
hypothesis (the self-audit ablation beats full at 0.062 vs 0.000 on responsibility/axis,
by acting on weak cues full abstains on). Rescoring existing data cannot rescue H1.

## Disposition

1. The 2,880 records are **retired to instrument-validation / negative-control status**.
   They can support no claim about H1 in either direction.
2. Failure anatomy: 83% system-class impossibility by design (not broken cases — the cases
   are human/LLM-solvable), 8.5% answers-discarded (the whole live arm), 7.8% wrong/weak
   coordinate, 0.7% partial progress zeroed. The cases survive; the instruments do not.
3. **Do not** extend `_MARKERS` to make cases legible — that is outcome-tuning.

## The path that makes H1 testable

The project already designed the fix and never ran it: successor
**`P1.epistemic-mutation-necessity.v2.2.4`** (DESIGN_FROZEN, execution bindings UNBOUND) —
480 hidden shifts + 2,400 controls, seed `202608172211`, each world exposing a **public
intervention menu with a host-side counterfactual response matrix** and a 3-intervention
budget. Success becomes a property of intervention *policy*, not lexical perception:
mechanical arms can genuinely differ, credential-free, and the design is pre-powered
(H1 needs n = 385; frozen 480) with pre-registered margins (≥ 10 pp, paired bootstrap).

**Decision: materialize v2.2.4 as the P1 execution path.** Secondary, cheaper complement
(optional, after): fix `provider.py` to elicit + parse + archive structured traces and run
the live arm as a *policy pair* (ORION-policy vs strongest-baseline-policy — H1 is a
contrast), graded against the existing per-case `root_success_rubric` fields, noting
n = 48 bounds it to large effects (~±14 pp).
