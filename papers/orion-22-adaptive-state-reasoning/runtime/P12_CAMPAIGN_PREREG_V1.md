# ORION-22 stop/go campaign — signal prereg and substrate blocker

**Status:** `PREREGISTERED__CAMPAIGN_BLOCKED_ON_SUBSTRATE`

`p12_stopgo_frozen_menus_v1.json` requires the signal implementations to be
frozen *"at campaign prereg, before any protected evaluation"*. This freezes
them. It also records why the campaign cannot execute, which is a substrate
problem rather than a design one.

## Structural minimums — met

| requirement | available | source |
|---|---|---|
| ≥20 task families | **24** | `subtask_categories`, after excluding instances 3, 32, 46, 53, 54, 84 |
| ≥3 domains | **4** | Comp. Chemistry 19, GIS 22, Bioinformatics 27, Psych/CogSci 28 |
| ≥2 model families | **4** | Qwen, Llama, Phi, Gemma — GGUF on LUNARC, all verified generating |

96 of 102 instances survive the license exclusion.

## Signal implementations — frozen here

All four are computed from **pre-outcome licensed metadata only**.
`gold_program_name` and `eval_script_name` are outcome-side and are excluded
by construction, not by convention.

| signal | frozen implementation | range observed |
|---|---|---|
| `S_PENDING_MULTIPLICITY` | count of comma-separated entries in `subtask_categories` | 1–4, 4 distinct |
| `S_DECLARED_MATERIALIZATION_COST` | charge units per state-construction unit | **constant 1** |
| `S_DECLARED_SERVE_EXCHANGE_RATE` | state-unit charge ÷ reasoning-unit charge | **constant 1.0** |
| `S_FAMILY_DIFFICULTY_PRIOR` | family-level median of `len(task_inst) + len(domain_knowledge)`, tertiled to LOW/MID/HIGH | 3 levels |

### Two of the four signals carry no information

Under the protocol's own `charging_semantics` the price regime is `FLAT`, and
the action menu prices every unit identically: `A_STATE_MAX` is (2,0) for 2
charge units, `A_REASON_MAX` is (0,2) for 2. So the materialization cost is 1
per unit for every family, and the serve exchange rate is 1.0 for every
family. Neither varies, so neither can discriminate.

This is recorded now, before any outcome is visible, because discovering it
afterwards would look like post-hoc explanation of a weak `ADAPTIVE` arm.
`ADAPTIVE` effectively reads **two** informative signals, not four. That is a
consequence of the frozen FLAT regime, which itself follows from
`P12_ROBUSTNESS_STRESS_V1` returning `price_axis=BROKEN`.

## Policies — frozen here

| arm | reads | rule |
|---|---|---|
| `ONE_SIGNAL_STATE` | multiplicity | ≥ median → `A_STATE_MAX`, else `A_RETAIN_MINIMAL` |
| `ONE_SIGNAL_REASON` | difficulty | `HIGH` → `A_REASON_MAX`, else `A_RETAIN_MINIMAL` |
| `ADAPTIVE` | both | high+high → `A_BALANCED`; high mult only → `A_STATE_MAX`; high diff only → `A_REASON_MAX`; neither → `A_RETAIN_MINIMAL` |

`ADAPTIVE` is the complementarity hypothesis: it can reach `A_BALANCED`,
which neither one-signal arm can, and only when both surfaces agree.

## Why the campaign cannot run

The stop/go gate compares arms on **task outcomes**. Scoring an outcome means
executing the generated program and running the task's `eval_script_name`
against its output. Neither is available:

- `benchmark/datasets/` holds 76 directory names totalling **53 KB** — empty
  shells, not data.
- `benchmark/eval_programs/` contains only `gold_results`; the eval scripts
  are absent.
- The HF dataset repo publishes `ScienceAgentBench.csv` and a 129 KB
  `verified` parquet — task metadata, no datasets.
- The upstream GitHub `benchmark/` directory contains one README, which reads
  *"This file is left blank intentionally as a placeholder."*
- The project README directs users to a password-protected OneDrive archive.
  Fetched from LUNARC it returns **HTTP 401**; the link needs an interactive
  session. That README also states *"Please DO NOT redistribute the unzipped
  data files online."*

## What was deliberately not done

No proxy outcome was invented.

A structural surrogate — "does the program parse", "does it name the output
file" — is available and would have produced numbers, a bootstrap, and a
gate verdict. It would also have measured whether a model emits syntactically
valid Python, not whether an allocation policy helps solve science tasks. A
gate run on that surrogate would carry the frozen protocol's authority while
answering a different question, which is the failure this programme has
recorded three times already.

The gate stays unexecuted, and `campaign_executed` stays false.

## What unblocks it

One manual download by someone with an interactive browser session, unzipped
under `ScienceAgentBench/` on LUNARC. Everything else is in place: substrate
counts met, four model families generating, generation feasibility measured
at 4/6 parseable with the failures bounded by the token cap rather than by
capability (`P12_CEILING_PROBE_V1.json`).
