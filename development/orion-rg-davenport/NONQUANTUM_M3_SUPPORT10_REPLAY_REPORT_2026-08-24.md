# Non-quantum math M3 — dual-harness report

Date: 2026-08-24

Owner: `NON_QUANTUM_MATH`

Base revision: `f04e5b27da6d88ac8c62638671c331f6e6b6b8bf`

## Admitted scientific result

Every length-31 total-zero sequence over `C_5^3` without a nonempty zero-sum subsequence of length at most five, if one exists, has support at least eleven.

M3 advances only the support-10 stratum. The parent M2 theorem excludes supports at most nine and proves the no-multiplicity-three saturation lemma. The support and length equations leave exactly `1 2^3 4^6` and `1^3 4^7`; four multiplicity-four points force rank three, and both complete normalized finite searches are UNSAT in two exact state representations.

## Exact evidence identities

- Protocol SHA-256: `86eedd383f12d8a88ffc030a919aa7a8cc47e315f44e6043d42efd1effce387c`.
- M2 parent signed digest: `846ffcc2329c13fb6a1811028beeca21cfd7f69f1203bc4a4b269d5d98f2f697`.
- M2 parent file SHA-256: `dab3811dd903c37adbcd0cb4379aac424b795b4a2925d2db83e32afd9cd77fb1`.
- u128 C source SHA-256: `a3cd33e09dfa972c62ce2844a8ec2caeda218ca7870ce14c28b3ad3a427f055a`.
- byte C source SHA-256: `03d5f54a7a63ddb05d2c75fbb608e8ebaa4e2dc5da1809f09f9a72c3d8d12dd3`.
- Source signed result digest: `bc1a727fe936a3cd3ddf033bb0ac9c6ebad6d6969a9e10c45c8d53fd2732e044`.
- Source result file SHA-256: `1789a7d606eda7c787aaca9dc88fe4f89572cb9b11eb953111de1cd6f04f980f`.
- Generic signed verification digest: `0e9ba2725953409baab3ce38e95a106a4798feb54cb109263b0d04803595acb1`.
- Generic result file SHA-256: `e868420fe2bb7374860d76300951dd94c2c342d3e0efe4e634941dff24eb7426`.
- Native manifest digest: `6ed1ec9714d6f5cd8c3708908233240928754599ec2dae68b0c549eae49b0cd2`.
- Dual receipt digest: `00c9a49e209abe89080d0429a17a3215edcd58f245df6a6870f411e464710369`.
- Dual receipt file SHA-256: `81859e07e0e7e76a7759ddcef66415930d9d8d098dd8e3d7e6414fdc3a9af0b4`.

## Exact replay rows

- `1 2^3 4^6`: 272,119 nodes, zero leaves, zero solutions in each engine.
- `1^3 4^7`: 210,700 nodes, 3,558 leaves, zero solutions in each engine.

The u128 translation-mask engine and explicit byte reachability engine agreed exactly on every serialized row.

## Terminal and validation

Source, generic, and native lanes agreed on:

`NONQUANTUM_M3_C5CUBED_SUPPORT10_BOTH_DEFICIT_PATTERNS_EXCLUDED__OBSTRUCTION_SUPPORT_AT_LEAST11`

Generic decision: `ACCEPT_SUPPORT10_EXCLUSION`.

Native decision: `ACCEPT_SUPPORT10_EXCLUSION`; phase `ACCEPT_RECORDED`; run status `TERMINAL`; two cycles with statuses `ADVANCED`, `TERMINAL`.

The five focused tests passed. All Python executables and the test file compiled. Four complete final-protocol runs rebuilt both C executables in fresh temporary directories and produced byte-identical source, generic, and dual receipt files. `git diff --check` passed. There is no visual artifact, so visual QA is not applicable.

## Post-outcome and adverse record

The support-10 zero-solution outcomes were archived before M3 and reproduced by a timing scout before the signed protocol. M3 is post-outcome confirmation, not prospective validation.

The scout compiled the u128 source under strict ISO C with `-pedantic`, which emitted the expected warning that `__int128` is a GNU extension. The formal build uses `-std=gnu11 -Wall -Wextra -Werror`; the extension is admitted deliberately and every actual warning rejects the build.

The first signed source execution returned `NONQUANTUM_M3_SUPPORT10_REPLAY_REJECTED` with digest `25ce07a9888fb17afcb251f832476c3b15ef53aceee9e4ea21422c2c5fb1038f`. Both exhaustive searches were already UNSAT; the failure was an ordering mismatch between the canonical pattern enumerator and the registered two-element tuple. The tuple was reordered lexicographically. No pattern, count, threshold, search object, or outcome changed.

## Remaining scientific authority boundary

M3 excludes only support ten on top of the M2 parent. It does not exclude support eleven or greater, upgrade the archived support-23 packet, prove `31 in C_0(C_5^3)`, or decide exact `D_4(C_5^3)`.

The replay is local and post-outcome, not external independent replication or prospective evidence. No novelty, venue, quantum, physical-resource, or CI authority is admitted. The next meaningful rung is support eleven, but the top-tier blocker remains a reusable symbolic incompatibility or complete `C_0(31)` theorem rather than a long list of bounded rows.
