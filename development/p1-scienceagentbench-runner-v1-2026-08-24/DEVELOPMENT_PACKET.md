# P1 ScienceAgentBench verified runner V1 — development packet

**Development question:** Can a standalone, network-free contract runner close the verified-split adapter gap identified by the outcome-blind ScienceAgentBench preflight, while making wrong-population execution, unmatched RR/OS/NR budgets, evaluator-feedback leakage, and missing-as-failure coercion structurally inadmissible?

**Base subject:** `bdc21dc7266f2b2469b7d51f4548b4782a0857b0`.

**Preflight dependency:** `development/p1-scienceagentbench-preflight-2026-08-24/` from merged PR #1095 (`7fb75d0dc341bee829db8e590aea5a9595ff7371`).

**Authority:** local runner-contract engineering only. No benchmark task, candidate program, official evaluator, gold program, rubric, evaluator program, result body, or historical outcome is opened or executed here. Scientific authority delta remains `NONE`.

## Atomic development questions

1. Can production entry points make `verified` the only admissible explicit split, rejecting an omitted split and the upstream `validation` default rather than silently correcting either?
2. Can the runner bind the verified Parquet by SHA-256 `c6f937863a220bd1762a00c20a0f79cc8dfca900b819bdb552150310731ae147`, the mask manifest by SHA-256 `442d9793024a91c752d34b9ad3185af612d1db3759458e91a61911b385cbe758`, and task identifiers exactly `1..102` without redistributing or inspecting benchmark text?
3. Can RR, OS, and NR be required for every task and attempt, with three attempts per task/arm and identical prospective input-token, output-token, tool-call, wall-time, local-execution, and candidate-count caps?
4. Can exact model, provider, tokenizer, prompts, seeds, credentials, and runtime remain explicit `AUTHOR_INPUT_NEEDED` or `CANNOT_CHECK` blockers until an owner supplies immutable values, rather than being guessed by the runner?
5. Can candidate-generation records preserve task-paired attempt identity, actual token/tool/time/cost usage, failures, nulls, `CANNOT_CHECK`, and raw-output hashes without admitting evaluator feedback, gold/rubric/result fields, or best-attempt-only accounting?
6. Can evaluator planning occur only after the full candidate set is sealed, emit an argv vector for the pinned official source commit `c26e151ed601ba109dc4d35e057ff8e73fec469d`, contain exactly one `--split verified`, and remain impossible for this module to execute?
7. Can all of those properties be challenged on synthetic nonbenchmark fixtures using only Python standard-library file, JSON, hash, and static checks?

## Incumbent mechanics and negative history recovered

- The preflight bound all 102 verified task IDs and a hash-only field manifest without opening outcome, gold, evaluator, or rubric bodies.
- The verified Parquet differs materially from `validation`: nine task instructions changed. Upstream `run_infer.py` hardcodes `validation`, and the official evaluator defaults to `validation`. An omitted split is therefore not a harmless convenience.
- The official evaluator source is pinned but its Docker/credential/model route is not runnable on the audited host and is stochastic. Runtime success remains `CANNOT_CHECK`.
- The full encrypted benchmark archive was intentionally not downloaded. Its payload hash, decryption, extracted manifest, and runtime identity remain outside this packet.
- The protocol design fixes RR/OS/NR, 102 task-paired inference units, three attempts, all-attempt cost accounting, and missing/partial/runtime/evaluator failures as `CANNOT_CHECK`; model, prompt, tokenizer, seed, and budget bytes remain unbound.
- The repository retention boundary forbids benchmark ZIPs, extracted datasets, gold/evaluation programs, rubrics, gold results, evaluator bodies, container layers, credentials, and raw benchmark outputs.

## Bounded saturation assessment

### Knowledge saturation

The relevant knowledge is bounded to the merged preflight bindings, the official public README command surface at the pinned source commit, the upstream split-default hazard already recorded in the preflight, and standard fail-closed validation/content-addressing practice. This packet does not claim runner novelty, reproduce benchmark science, or expand the causal theory.

### Search-universe saturation

The admissible implementation universe is deliberately narrow: Python standard-library parsing and hashing; immutable production constants; exact-set validation; explicit runtime bindings; sealed candidate ledgers; static command construction; and synthetic fixtures. Network clients, model SDKs, Parquet readers, subprocess evaluators, Docker control, benchmark payloads, and outcome analysis are excluded because they would widen authority and leakage surfaces without being needed to prove this contract.

### Formulation saturation

The task is not “run ScienceAgentBench.” The frozen formulation is: validate the identities and matched envelopes needed before generation, validate and seal complete candidate-generation receipts after generation, and separately emit—but never invoke—the sole admissible official evaluator command. This closes a contract/adapter gap only; it does not close archive, credential, prompt, model, runtime, analysis, preregistration, or independent-custody gates.

## Challenge to the saturation basis

This design could appear safe while remaining scientifically wrong if it accepts an implicit split, checks only row count rather than the exact `1..102` set, hashes the wrong artifact, trusts a self-declared mask digest, permits one arm to omit attempts or receive larger caps, accepts strings such as `0` for missing outcomes, records only selected-attempt cost, lets forbidden evaluator feedback hide in nested keys, treats a command string as safely tokenized argv, or provides any generic “execute” helper that can run the evaluator. Synthetic validation must attack those boundary cases rather than only a valid fixture.

## Missed-knowledge hypotheses

1. A future upstream CLI may rename or duplicate `--split`, making the pinned command shape stale even if the source commit label is retained.
2. A provider may report tokens, tools, billed cost, or wall time with different null/zero semantics; generic numeric coercion could erase missingness.
3. Prompt identity may span system, user, tool-schema, recovery, and serialization bytes rather than one prompt hash.
4. Seed determinism may be unsupported or only partial for a provider; recording a number must not be treated as proof of deterministic replay.
5. Candidate filenames or directory roots may encode forbidden gold/evaluator/result locations even when JSON keys look benign.
6. A complete 918-row ledger can still be invalid if `(task, arm, attempt)` tuples are duplicated and other tuples are missing.
7. Sealing only the ledger but not each raw model output may permit later candidate substitution.
8. An evaluator command can contain one `--split` token yet bind an additional conflicting `--split=validation` token.
9. A syntactically correct command does not prove Docker, credentials, exact judge route, dependencies, or archive identity; runtime remains `CANNOT_CHECK`.

## Frozen implementation hypothesis

> If production constants fix the verified input, mask, task population, arm set, attempt count, official source commit, and sole evaluator split; if owner-supplied runtime bindings fail closed until concrete and matched; if candidate receipts are exact-set, content-hash, null-preserving, leakage-scanned, and sealed before command construction; and if the module exposes no process-execution path, then the runner can prevent the known population, matching, leakage, and missingness failures without opening any benchmark or evaluator outcome.

This is a local engineering hypothesis only. It does not authorize a benchmark run or change P1 scientific authority.

## Frozen hostile validation cases

- omitted split, `validation`, and any non-`verified` split are rejected;
- wrong Parquet bytes/hash, missing Parquet path, wrong mask-manifest bytes/hash, duplicate IDs, missing IDs, and extra IDs are rejected;
- missing RR/OS/NR arms, attempts other than exactly 1--3, duplicate task/arm/attempt tuples, missing tuples, and extra tuples are rejected;
- placeholder, null, empty, or otherwise unbound model/provider/tokenizer/prompt/seed/runtime inputs are rejected for production readiness;
- unequal token, tool, wall-time, local-execution, or candidate-count caps across arms are rejected;
- negative or over-cap usage, booleans masquerading as numbers, best-attempt-only cost summaries, missing raw-output hashes, invalid hashes, and solved coercion are rejected;
- forbidden nested keys and path components naming gold, evaluator, rubric, score, feedback, or result bodies are rejected;
- null failure/usage/status values remain null; runtime and evaluator failures remain `CANNOT_CHECK`, never `solved=0`;
- evaluator planning before a complete sealed ledger is rejected;
- evaluator argv with omitted, duplicated, `--split=...`, or non-`verified` split is rejected;
- the emitted argv identifies the pinned official source commit and contains exactly the adjacent tokens `--split`, `verified`;
- static inspection confirms the module imports no network, subprocess, shell, Docker, Parquet, or model-provider execution library.

## Reopen triggers

Reopen design rather than patch around the failure if the pinned upstream evaluator CLI no longer accepts the frozen argv; verified task identity cannot be established from the pinned Parquet plus manifest without inspecting forbidden material; a provider cannot supply comparable usage or immutable prompt/runtime bindings; an arm requires a scientifically justified unequal envelope; raw-output sealing cannot be performed before evaluator access; any official runtime exposes candidate generation to scores or evaluator feedback; the archive/runtime cannot preserve the no-redistribution and secret-handling boundary; or a synthetic hostile case demonstrates that missingness, population identity, or command identity can be bypassed.
