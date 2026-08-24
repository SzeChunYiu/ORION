# Non-quantum math M2 — dual-harness report

Date: 2026-08-24

Owner: `NON_QUANTUM_MATH`

Base revision: `df58c9d3bd7dedab0011ca2e126bfcf5fcd35429`

## Admitted scientific result

For an odd prime `p`, let `S` be a saturated `p`-short-free sequence over an elementary abelian exponent-`p` group. If a nonzero point `x` has multiplicity `m<p`, saturation forces a certificate

`x^m R`, `|R|<=p-1-m`, `sigma(R)=-(m+1)x`,

with no copy of `x` in `R`. Consequently multiplicity `p-2` is impossible.

For the registered `C_5^3` object, every length-31 total-zero sequence without a nonempty zero-sum subsequence of length at most five has support at least ten. This bounded conclusion combines the human symbolic reductions with isolated exact replay of the frozen support-8 and support-9 programs.

## Exact evidence identities

- Protocol SHA-256: `f30316253fc965b14035e6a174558f649f9329f60d8b2f78afcf8370874fee68`.
- support-8 C source SHA-256: `646c223dfc7d356117e8df01d01129c58fa6fb3648705f3f39927e7f36ce7b84`.
- support-9 C source SHA-256: `65dae6df0c29f5584d1f42d6be8dc553cb4bc5e1e9df64f284427050368c5f04`.
- Source signed result digest: `846ffcc2329c13fb6a1811028beeca21cfd7f69f1203bc4a4b269d5d98f2f697`.
- Source result file SHA-256: `dab3811dd903c37adbcd0cb4379aac424b795b4a2925d2db83e32afd9cd77fb1`.
- Generic signed verification digest: `98d148e9c3fea0359a615b888c02273768d8aebc7a992a786764c8b1f64c302f`.
- Generic result file SHA-256: `cd90691cf2b668dc2194b04306e7427d74cf78432dc624b63f82fbaaa8a0e946`.
- Native manifest digest: `1464416c1787c2ef7534cbad466c29ed7b279ecfc2005b7ae95d3e88bab07ffa`.
- Dual receipt digest: `f66d25db7006524c31cf80b7a612626c3a79bf33f530c8f354028c369598e13e`.
- Dual receipt file SHA-256: `833f130a67061240855e4e6bcb784646299d7b30bcf20de74ad77543d3d64887`.

## Exact replay rows

Support eight:

- byte engine: 80,202 nodes, 564 normalized supports, zero compatible sum targets;
- reverse bitset engine: 80,202 nodes, 564 normalized supports, zero compatible sum targets.

Support nine:

- byte engine: 6,537,270 nodes, 138,785 forced final candidates, zero solutions;
- reverse bitset engine: 6,537,270 nodes, 146,788 forced final candidates, zero solutions.

The distinct support-9 forced-candidate counts are expected because the engines traverse in opposite canonical orders; equality is required for the complete node and solution counts, not this internal pruning counter.

## Terminal and validation

Source, generic, and native lanes agreed on:

`NONQUANTUM_M2_EXPONENT_P_SATURATION_DEFECT_LEMMA__C5CUBED_SUPPORT_LE9_EXCLUDED_BY_ISOLATED_DUAL_REPLAY`

Generic decision: `ACCEPT_SATURATION_DEFECT_SUPPORT_LE9`.

Native decision: `ACCEPT_SATURATION_DEFECT_SUPPORT_LE9`; phase `ACCEPT_RECORDED`; run status `TERMINAL`; two cycles with statuses `ADVANCED`, `TERMINAL`.

The five focused tests passed. All Python executables and the test file compiled. Two complete final-protocol runs rebuilt the C executables in fresh temporary directories and produced byte-identical source, generic, and dual receipt files. Temporary executables and harness workspaces were removed after every run.

## Post-outcome and adverse record

The support-8/9 outcomes were present in the archive before M2. A timing scout reproduced them before the signed protocol, so M2 is confirmatory and post-outcome, not prospective validation. A pre-final source execution emitted digest `6fc64c5c01d965f3a264b703fa1733ece1b84c18a89a6cce635aa46eb3073fa5`; it was superseded when the general statement was narrowed explicitly to odd primes before the final protocol run. No data, success threshold, finite-search object, node count, or solution criterion changed.

The initial timing command returned exit 127 because `/usr/bin/time` is absent. It did not yield a scientific terminal; the frozen binaries were subsequently executed with the shell timing facility and then through the signed harness. No scientific adverse terminal or survivor was observed.

## Remaining scientific authority boundary

This iteration grants only the general symbolic defect lemma and the exact support-at-most-nine exclusion. It does not upgrade the archived support-at-least-23 packet, exclude support ten or greater, establish `31 in C_0(C_5^3)`, or decide `D_4(C_5^3)`.

The replay is isolated and internally dual but not an external independent replication. It is not prospective. No novelty, venue, quantum, physical-resource, or CI authority is admitted. The decisive combinatorics gap remains a symbolic support-10-or-higher obstruction theorem or a complete independently replayed `C_0(31)` proof.
