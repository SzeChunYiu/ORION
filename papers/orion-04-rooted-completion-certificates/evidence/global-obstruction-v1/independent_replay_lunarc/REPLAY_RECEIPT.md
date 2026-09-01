# Independent replay receipt — ORION-04 global obstruction

The handoff artifact recorded `external_independent_replay_complete: false`. This
receipt records an independent replay executed on different hardware with a
different compiler, and its outcome.

## What was run

All **156 engine runs** (78 branches × `avx`/`u128`) rebuilt from the artifact's own
six C sources via its own `run_replay.py`, with the artifact's frozen compile flags
`-std=gnu11 -O3 -march=native -Wall -Wextra -Werror`.

| | original artifact | this replay |
|---|---|---|
| host | 5 logical CPUs | LUNARC `cn099`, 32 cores |
| compiler | gcc 14.2.0 (Debian) | **gcc 13.2.0** |
| `-march=native` targets | that host's ISA | a different host's ISA |
| SLURM job | — | 3560211, account `lu2026-2-51` |

Different machine, different compiler major version, different native ISA target.

## Outcome — exact agreement

| field | original | replay |
|---|---|---|
| `result_digest` | `33170969bfd69e95773efd98bf19f97453abbbcad0fe459c5a18babeb500865e` | **identical** |
| `cover_digest` | `06961efc816f56bbcc66c34a06396acc597aa183fc087b22f27e8e65c161ecb7` | **identical** |
| `terminal` | `ORION04_C0_31_PROVED__IMPLIES_D4_C5CUBED_EXACT_30` | **identical** |
| engine runs | 156 | 156 |
| `checks` all true | yes | yes |
| `finite_theorem_authority` | true | true |

The theorem reproduced:

> No length-31 total-zero sequence over `C_5^3` is free of nonempty zero sums of
> lengths at most five. Thus 31 is in `C_0(C_5^3)`; under the committed implication,
> `D_4(C_5^3) = 30`.

## What this does and does not settle

**Does:** the computation is reproducible off its original machine and compiler. A
bit-identical `result_digest` across a gcc major-version change and a different
`-march=native` target is strong evidence the result is a property of the
mathematics and not of one toolchain.

**Does not:**

- `novelty_authority` remains **false** — whether this value is already known in the
  literature is a separate question this replay does not touch.
- The replay's own `external_independent_replay_complete` field still reads false;
  it is set by the artifact's schema, not by the act of replaying. Whether this
  receipt discharges that gate is the paper owner's call — I ran the computation and
  am reporting it, not re-labelling the artifact's field.
- Both runs execute the **same source**. This is an independent *replay*, not an
  independent *implementation*; a second implementation would test more.

## Relationship to PR #1674

#1674 proposes closing ORION-04 at
`ORION04_EXACT_D4_NOT_ESTABLISHED__PAPER_REFRAMED_TO_BOUNDED_STRUCTURAL_RESULT`,
whose bounded claim is that a length-31 5-short-free obstruction, *if one exists*,
has support at least 14. This artifact reports that **no such obstruction exists**,
now reproduced independently. Those two terminals cannot both stand; reconciling
them is the paper owner's decision.
