# P1-U R6: role-free identifiers — prospective freeze

**Written 2026-08-21, before any anonymised identifier existed and before any
arm was re-run under one.** Nothing below was chosen after seeing an outcome.

## 1. Why this freeze exists at all

This change can turn a negative into a positive, which is exactly the situation
that needs a protocol fixed in advance.

`research/claim_expansion/p1/claude_t3/` repaired the three guards `P1-U-T3`
named and re-ran them. Fourteen checks hold; `no_candidate_metadata_leakage`
fails on **96 of 96** episode-arms, and the terminal is
`P1_R6_NATIVE_PRIMARY_NOT_SUPPORTED`. The cause is that episode identifiers are
`R5-<QUERY>-A`, `-C`, `-U` and those strings reach the candidate-visible
payload, so the pair role — and with it, for the 22 controls, the gold label —
crosses the provider boundary on every episode of both arms.

Removing the leak is expected to make the leakage guard pass. **If the primary
result also survives, the terminal moves up.** So the rule is fixed here, before
the first anonymised run:

> The re-run is scored by the **repaired guards exactly as they stand**, with no
> threshold, arm, comparator, corpus or scoring function altered. If the primary
> fails under role-free identifiers, that is the result and it is reported as a
> real negative. If it passes, the claim is bounded by §5 and by nothing weaker.

## 2. What is anonymised, and what is not

The defect is that a **candidate-visible string carries the pair role**. The
repair is therefore at the boundary, not in the scoring.

Every identifier that crosses into a candidate-visible payload is replaced by an
opaque handle derived as

```
handle(episode_id) = "ep-" + sha256(SALT + "\x00" + episode_id).hexdigest()[:12]
SALT = "p1-r6-role-free-2026-08-21"
```

The salt is frozen here so the mapping cannot be re-drawn after an outcome. The
mapping is retained host-side, so every scored row remains traceable to its
episode; anonymisation is a boundary property, not a loss of provenance.

**Surfaces covered.** All of them, enumerated rather than sampled — the audit in
`claude_t3` found three token categories (`pair_id`, `episode_id_and_pair_role`,
`query_id`), and a repair that covers two of three is not a repair:

| surface | before | after |
|---|---|---|
| root `problem_id` | `p1-r6-dr1-root:{episode_id}` | `p1-r6-dr1-root:{handle}` |
| root `query_id` | `p1-r6-dr1-root-query:{episode_id}` | `p1-r6-dr1-root-query:{handle}` |
| probe `problem_id` | `p1-r6-probe:{episode_id}:{probe}` | `p1-r6-probe:{handle}:{probe}` |
| probe `query_text` | `p1-r6-native-probe:{episode_id}:{probe}` | `p1-r6-native-probe:{handle}:{probe}` |
| evidence `item_id` | `evidence:p1-r6:{episode_id}:{probe}` | `evidence:p1-r6:{handle}:{probe}` |
| evidence `source_uri` | `p1-r6://{episode_id}/{probe}` | `p1-r6://{handle}/{probe}` |
| claim id | `p1-r6:{episode_id}:runtime-diagnosis` | `p1-r6:{handle}:runtime-diagnosis` |
| support evidence id | `runtime-diagnosis:{episode_id}` | `runtime-diagnosis:{handle}` |

**Not anonymised, deliberately:** the dossier text, the domain, the question,
the success criteria, the scoring functions, the gold labels, the comparator,
the corpus, and every threshold. If the dossier itself leaked the role, that
would be a different defect and this repair would not touch it — which is why
§4's precondition checks the *whole* payload rather than only the fields above.

**Not edited:** `native_orion_core_v1.py`, `repaired_root_v1.py`,
`evaluate_native.py`, and every committed receipt including the DR1 receipt. The
anonymisation is a new wrapper layer. The existing artifacts stand as the record
of what the identified run produced.

## 3. Arms

Unchanged from DR1, byte-identical, imported not reimplemented:
`ORION_NATIVE_ARD_DR1`, `ORION_NATIVE_BASE_DR1`, and the frozen `B3`.

## 4. Preconditions, checked before any arm is scored

Both are properties of the payloads, not of an outcome, and the run aborts on
either rather than reporting numbers over a world that is not the one specified.

1. **The leak is actually gone.** Re-run the repaired leakage audit over the
   anonymised payloads. It must report `0` hits in every category across all 96
   episode-arms. A partial reduction is a failure of this precondition, not a
   partial success.
2. **The handle is not itself a role predictor.** The 48 handles must be
   distinct, must contain none of the substrings `-A`, `-C`, `-U`, `R5-`, and
   must not separate the three roles: a majority-vote classifier fitted on any
   fixed-length prefix of the handle must score informedness `0.0` for every
   prefix length from 1 to 12. Replacing a role token with a hash that still
   sorts by role would be the same defect with more steps.

## 5. Claim scope, fixed now

> **FROZEN_DETERMINISTIC_HOST_ONLY.** A pass licenses the statement that the R6
> primary and its attribution ablation do not depend on the leaked pair role,
> *on this host*. It does not license a superiority claim on a semantic model, it
> does not discharge `P1-U-T2`'s 2019 replication — separately blocked by the
> evaluator hardcoding `source_year == 2020` — and it does not make the leak
> harmless in general. The `claude_t3` audit already measured that anonymising
> the identifier changes 0 of 44 ARD choices under this host; that is a property
> of a frozen deterministic provider, and the next planned step for this line of
> work is a changed semantic host, where a leaked label is exactly the kind of
> thing a model can use and this bound does not carry.

## 6. Anti-tuning

Every constant above — the salt, the handle length, the eight surfaces, both
preconditions, the informedness ceiling of `0.0` and the prefix range 1–12 — is
fixed by this document. If any is changed after an outcome is seen, this freeze
is superseded by a new dated one that says what changed and why, and the result
produced under this one stands beside it.
