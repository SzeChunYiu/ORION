# Top-tier execution ledger — 2026-08-23

Status: **post-outcome evidence binding; no authority widening**

This ledger binds protected executions that completed after the P6–P15 upward-claim promotion contracts were frozen. A workflow's technical success is not itself a positive scientific result. Positive, negative, and `CANNOT_CHECK` outcomes are recorded symmetrically.

## P9 — representation accessibility

### Real-data accessibility intervention — SUPPORTED, bounded

Frozen study: `papers/paper-09-structured-epistemic-learning/top_tier/P9_REAL_ACCESSIBILITY_SCALING_PROTOCOL_V1.md`

Terminal: `P9_REAL_ACCESSIBILITY_SCALING_V1_SUPPORTED`

- protocol SHA-256: `486195eddc9e56cd9a2cdb38903183745f60ef32fa47ff9cfe4e4c2e1b78c726`
- receipt SHA-256: `349004efd942979223547ea09db61565c29f33176b3bfd0771f6655e517f0dd7`
- protected workflow run: `32645458668`
- artifact id: `9495004064`
- artifact ZIP SHA-256: `a615a60497a961b5de7a08db9e287e2ba83f686c9dd0581859d76d213ea9003b`
- deterministic byte replay: GREEN
- rows: 180
- same-information reconstruction: GREEN; maximum reconstruction errors remain floating-point roundoff scale (`<= 7.11e-15`)

Preregistered accessibility gap:

- breast cancer: native linear mean `0.9806862288`; cubic-bijection linear mean `0.9455053563`; mean gap `0.0351808725`; inverse-repaired linear mean `0.9806862288`; recovered fraction `1.0`;
- digits: native linear mean `0.9699489322`; cubic-bijection linear mean `0.9460213556`; mean gap `0.0239275766`; inverse-repaired linear mean `0.9699489322`; recovered fraction `1.0`;
- wine: preregistered accessibility gap did not appear (`-0.0001587302` mean), so this dataset is a null/negative cell rather than evidence for universality.

Allowed claim movement: an information-preserving representation intervention can change accessibility for a fixed access class on real datasets, and deterministic representation repair can recover the lost accessibility. The wine null cell prevents a universal-dataset claim.

### Protected Qwen2.5 scaling recovery — NOT SUPPORTED

The original PR #618 Qwen evaluations completed for all three frozen models; only the downstream artifact-path integration failed. The recovery changes file discovery only and invokes the frozen analyzer logic on the immutable source JSON outputs.

Terminal: `LLM_STRUCTURE_SCALING_FRONTIER_NOT_SUPPORTED`

Primary-budget effects (`R2_TYPED_STATE - R1_SAME_INFO`):

- Qwen2.5 0.5B Q4_K_M: `-0.140625` (`0.4010416667 - 0.5416666667`);
- Qwen2.5 1.5B Q4_K_M: `0.0` (`0.25 - 0.25`);
- Qwen2.5 3B Q4_K_M: `0.0` (`0.25 - 0.25`).

Frozen scientific checks:

- positive delta at every size: FAIL;
- largest-model domain-block bootstrap lower bound > 0: FAIL;
- observed smaller-structured substitution exists: FAIL;
- all hostile controls green: FAIL;
- largest-model nonnegative-domain fraction >= 0.60: PASS.

The ORDER hostile control is negative at 0.5B (`-0.3125`) and 3B (`-0.0208333333`). The recovery workflow and deterministic replay are GREEN; that makes the negative scientific terminal authoritative rather than turning it into a technical failure.

Immutable source JSON SHA-256 values:

- 0.5B: `2b068dab20036b3a481680bde52a0bdebbaf7eac8611c73e5ca58bb63c8b4e26`
- 1.5B: `46aa863ac8360f9f7b09f1f0dc7d27d3f7b49f810e36a250f1b0853a9c0a6817`
- 3B: `8deba9a82f23495fdc38d0eb0fb312f0a01c3b81064f17088dcb46f86afdfa12`

Recovery artifact id: `9495185874`; artifact ZIP SHA-256: `79a1c8eac67128013b36a95cd2e51e8ab59fd7efd120d09ff550518c0781b940`.

Allowed claim movement: **do not claim a monotone LLM-size structure-accessibility law for this protected Qwen family.** P9's higher claim must be access-class- and system-conditional. The real-data causal accessibility result survives; the proposed universal Qwen scaling frontier does not.

## P10 — obstruction-certified method expansion

The prospectively frozen OCME formal non-vacuity study remains GREEN with byte-identical replay: two exact obstruction certificates, two verified hand-declared outside-closure primitive edits, six held-out transfers, and zero false expansions on old-language controls.

Allowed claim movement: OCME is a falsifiable formal object with exact obstruction and outside-closure expansion witnesses. This does **not** establish autonomous method invention because the successful candidate primitives were declared before execution.

The older native-Lean PR #618 lane remains `CANNOT_CHECK_NATIVE_STATE_COVERAGE`: the frozen eligibility contract produced zero eligible transitions out of 11,842 extracted transitions. Extraction success is not scientific permission to relax coverage rules post hoc.

## P11 — state as computation

### Real learned compiler — SUPPORTED, bounded

Terminal: `P11_REAL_LEARNED_COMPILER_V1_SUPPORTED`

- protocol SHA-256: `9593d063fd70e45cea26a6810736cf14f38972803b276455401b3c0d1a208797`
- receipt SHA-256: `6efa19942363917289c12287900b3e63f7dea03bd9276498898b5b631e40e548`
- protected workflow run: `32647030864`
- artifact id: `9495296005`
- artifact ZIP SHA-256: `819709ccc728a16964e3d58b7f562528c3aac03316435d193327cb2baa46c5f1`
- deterministic byte replay: GREEN
- positive datasets under the frozen gate: `wine`, `digits` (2/3); breast cancer is a negative cell.

State/compiler compression and accuracy:

- wine: state dimension `13 -> 7` (`0.53846` ratio), coefficient ratio `0.57143`; compiled linear mean `0.9776190476` vs universal linear `0.9833333333`; compiled forest `0.9774603175` vs universal forest `0.9830158730`;
- digits: state dimension `64 -> 32` (`0.5` ratio), coefficient ratio `0.50769`; compiled linear `0.9577050449` vs universal linear `0.9682776230`; compiled forest `0.9666155989` vs universal forest `0.9732869081`;
- breast cancer: state dimension `30 -> 15`, but the frozen performance gate is not met; compiled linear `0.9489675516` vs universal linear `0.9753609688`.

Allowed claim movement: a non-oracle learned compiler can reduce task-state dimension substantially while satisfying the frozen near-performance criterion on two real datasets. This is not yet a universal compiler theorem and does not by itself establish a model-capacity substitution law beyond the measured state/model-resource proxies.

## P12 — resource-location metareasoning

### Verifier-backed SAT study — SUPPORTED

Terminal: `P12_VERIFIER_RESOURCE_LOCATION_V1_SUPPORTED`

- cases SHA-256: `978c2d4883052f1d0a7048a847036d336be92949ce131bfdbf5f7b20402d6199`
- protocol SHA-256: `055c37146d065bdaa89560e604b47954aedca405db8fa03113787782a4ab010f`
- receipt SHA-256: `116940de30d77606dd38027b6ccbba145f11df32e9ca294c1193ff6f427ab3f6`
- protected workflow run: `32647030824`
- artifact id: `9495222687`
- artifact ZIP SHA-256: `133179ef6a1f0b4a64d33e0b9baf1812e226afe2b8fb0c216176bdbd10342cc7`
- deterministic byte replay: GREEN
- frozen work budget: 2,000 literal evaluations; cases: 16.

Results:

- `ADAPTIVE_LOCATION`: 16/16 solved, 0 budget exhaustions, mean solved work `50.25`, max work `272`;
- `PROPAGATE_FIRST`: 16/16 solved, mean solved work `52.375`, max `272`;
- `REASON_ONLY`: 4/16 solved, 12 budget exhaustions, solve rate `0.25`;
- adaptive policy regret versus the per-case oracle: max `0`, mean `0.0` over all 16 cases;
- all returned SAT/UNSAT dispositions pass the independent verifier.

The low-unit easy family is the required anti-preprocessing control: adaptive mean work `11.75` equals reason-only and improves over always-propagate `20.25`. Unit-heavy/contradiction families require state construction to avoid budget exhaustion.

Allowed claim movement: on this verifier-backed frozen SAT family, *where* computation is spent is causally consequential; the preregistered structural signal selects the per-case optimal resource location with zero observed oracle regret. Cross-domain generality remains unearned.

## P13 — responsibility-carrying state

### Real responsibility-shift study — SUPPORTED

Terminal: `P13_REAL_RESPONSIBILITY_SHIFT_V1_SUPPORTED`

- protocol SHA-256: `eaadfa8568d8fdf13f372d0ad486fb524cdf4cf9afeb852b5afc55d37e7e2b5d`
- receipt SHA-256: `f20b762c5e76d4c60133a21a59f72c97fe37c8f9da45274cd26adb8521bedf70`
- protected workflow run: `32647030801`
- artifact id: `9495213108`
- artifact ZIP SHA-256: `297b59eef069d84b148cadfca0dc0667bb065e856a615786838d8a3fb66880ed`
- deterministic byte replay: GREEN
- episodes: 17,970.

Fold-by-fold component equality is exact: RCS equals always-raw for parity and for exact-digit responsibility in every fold.

Aggregate results:

- RCS: combined accuracy `0.9435169727`, digit accuracy `0.9699499165`, parity accuracy `0.9170840289`, 33 floats read/episode, reopen rate `0.5`, unsupported digit reuse `0`;
- ALWAYS_RAW: identical accuracy, 64 floats read/episode, reopen rate `1.0`;
- RCS state-read reduction vs always-raw: `0.484375` (48.4375%);
- CONFIDENCE_ONLY: digit accuracy `0.3956594324`, unsupported digit reuse rate `0.7774067891`;
- PROVENANCE_ONLY / UNQUALIFIED: digit accuracy `0.2376182526`, unsupported digit reuse rate `1.0`.

The raw-vs-compact exact-digit accuracy gap is `0.7323316639`, demonstrating that a compact state sufficient for the old parity responsibility can be current, provenanced and confident yet structurally inadequate for a later exact-digit responsibility.

Allowed claim movement: responsibility-scoped support, not confidence or provenance alone, determines safe reuse in this real-data responsibility shift. RCS matches always-raw accuracy while avoiding half of raw-state reads in the frozen alternating-responsibility design. Broader domains and independent replications remain pending.

## P14 — governance as a research-decision machine

The machine-readable blinded external-evaluation contract is GREEN (`P14_EXTERNAL_GOVERNANCE_CONTRACT_V1_GREEN`) on current-head CI.

Allowed claim movement: the external study is executable and fail-closed. It does **not** supply the independent scientific authority it requires. The protected >=60-packet, >=3-domain, same-evidence paired evaluation with independent adjudication remains `CANNOT_CHECK` until external candidate outputs and judgments exist.

## Portfolio consequence

The strongest newly earned empirical authority is now concentrated in P9 real-data accessibility, P11 learned compilation, P12 verifier-backed resource allocation, and P13 responsibility-scoped reuse. P9's Qwen scaling hypothesis is an authoritative negative and must narrow, not enlarge, the manuscript. P14's remaining gap is deliberately external rather than an internal implementation omission.

No row in this ledger grants `TOP_TIER_SUBMISSION_READY` by itself. Promotion remains paper-specific and requires the corresponding frozen gate, donor-complete novelty boundary, independent-authority conditions where required, and submission-byte binding.
