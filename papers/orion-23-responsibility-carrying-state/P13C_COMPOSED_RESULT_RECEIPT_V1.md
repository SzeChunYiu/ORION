# P13C composed safety-efficacy — result receipt V1

**Terminal:** `P13C_COMPOSED_SAFETY_EFFICACY_SUPPORTED` (first execution; all eleven frozen gates green)

**Freeze-before-execution:** protocol, gold spec, and runner committed (`609df8a6` + two pre-execution path amendments) before the first benchmark execution on this branch. Two fresh-subprocess replay, cores byte-identical (`sha256 645961cf01afe15f1b5976244b76b846c31d3c6119af4fbbc031e4b2a3611e57`). Runtime ~3 s per subprocess, single process, stdlib only.

## What was executed

The P13B authenticated-certificate machinery (imported unchanged from `src/orion/study/p13/authenticated_successor.py`, parameterized by the registered `P13C_COMPOSED_GOLD_SPEC_V1.json`) transplanted onto the P13A randomized efficacy benchmark: seed `2026082113`, 24 families × 512 episodes = **12,288** episodes, six-form certificate class (support sizes {2,2,3,4,5,5} of five tasks — larger than either parent's), four-world corruption register interleaved at the frozen 1-in-5 schedule (**2,457 corrupted episodes**, every one rejected by the validator).

## Gate results

| Gate | Result |
|---|---|
| G1 gold spec = P13A truth model | GREEN — subset rule reproduces P13A support sets (Z5↔P13A Z1, Z1↔P13A Z2) and the exhaustive responsibility matrix for all six forms |
| G2 authenticated zero unsafe reuse, overall | GREEN — 0 of 12,288, corrupted episodes included |
| G3 zero unnecessary reopen, valid panel | GREEN — 0 of 9,831 |
| G4 correctness ≥ ALWAYS_RAW − 0.01 | GREEN — 0.97933 vs 0.95247 |
| G5 correctness ≥ UNVERIFIED_RCS − 0.01 | GREEN — 0.97933 vs 0.98063 (margin +0.0087) |
| G6 cost ≤ 0.70 × ALWAYS_RAW, overall | GREEN — 3.0921 vs 5.7337 (ratio 0.5388) |
| G7 every scheduled corruption rejected | GREEN — 2,457/2,457 |
| G8 unverified live violations each world | GREEN — unsafe: FORGED 66, OVERBROAD 87, STALE 177; OMITTED unnecessary reopens 123 |
| G9 cannot-check exactness | GREEN — 254 = independently recounted expectation |
| G10 parent-form subpanel reproduces P13A | GREEN — 3,322 valid Z5/Z1 episodes: 0 unsafe, 0 unnecessary reopen, cost ratio 0.4983 |
| G11 byte-identical replay | GREEN |

## Scientific result

P13A proved exact responsibility-relative support on randomized families **without an adversary**; P13B proved corruption safety on a registered panel **without randomized families or an exactness matrix**. The composed theorem establishes the conjunction on one benchmark, over a certificate class strictly larger than either parent's:

1. **Safety composes with exactness.** The authenticated arm (validate-then-reuse) made **zero** gold-scored unsafe reuses across all 12,288 episodes — 2,457 of them under active corruption — while preserving every P13A exactness property on valid certificates: zero unnecessary reopens, cannot-check exactness, and verified-correct 0.985 on the valid panel.
2. **Authentication beats blind trust on correctness, not just safety.** Against the strongest trusting comparator (UNVERIFIED_RCS, which reuses declared support without validation), the authenticated arm is noninferior within 0.01 (0.97933 vs 0.98063) **while the trusting arm commits 330 unsafe reuses** (rate 0.0269 overall; per-world FORGED 66, OVERBROAD 87, STALE 177) and 123 adversary-induced unnecessary reopens under OMITTED_SUPPORT. Trusting declarations is not free: the corrupted lies it accepts predict wrong more often than recovery fails.
3. **The cost advantage survives the adversary.** Overall authenticated mean cost 3.0921 = **0.539 ×** always-raw (gate ≤ 0.70), even though 2,349 adversary-forced reopens were taken on rejected certificates; on the parent-form valid subpanel the ratio is 0.498, reproducing the parent P13A economy.
4. **The gold reconciliation is exact.** The P13C spec's subset rule over the six P13B forms reproduces the P13A truth-model support semantics and the exhaustive responsibility matrix for every form (G1), so both parents' gold definitions are one registered object.

## Authority boundary

Registered composed finite world: seeded randomized families, six-form certificate class, four-world corruption register at a frozen schedule. No external validation, real-agent safety, population generalization, certificate-authority independence, or deployment authority is claimed. All frozen P13A/P13B artifacts are untouched (certificate functions imported, never copied); both parents' forbidden-promotions lists are inherited unchanged.

## Replay

```
python papers/orion-23-responsibility-carrying-state/run_p13c_composed_safety_efficacy_v1.py
```

Success condition: terminal `P13C_COMPOSED_SAFETY_EFFICACY_SUPPORTED` with all eleven gates green and byte-identical two-subprocess replay. Failure terminal: `P13C_COMPOSED_SAFETY_EFFICACY_GATE_NOT_MET` (exit 1).
