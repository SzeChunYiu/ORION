# ORION16.REAL_SYSTEM_MINIMAL_REVALIDATION.v1 — Frozen-Study Protocol Sketch (DRAFT, not registered)

Status: design sketch for the #1649 Tier-A empirical discriminator. To become authoritative it
must be frozen (schema + EXPECTED_TERMINALS + SHA-256-bound gold) BEFORE any arm output is read.
Promotion-budget note: the Wave-2 packet records ORION-16's #1649 promotion attempt as SPENT for
the theory lane; whether a fresh empirical lane is authorized is a governance decision, not this
document's.

## 0. Systems

- S1: RTPTorrent (20 Java/Maven projects, real Travis per-test failures). Zenodo 4046180, CC BY 4.0.
- S2: envoyproxy/envoy Bazel target graph (+ abseil-cpp or grpc as sibling), ~300-commit window.
- S3: paritytech/polkadot-sdk cargo workspace graph, ~300-commit window.
- Reserve: Defects4J v3 (+ Ekstazi/STARTS as the strongest-incremental baseline host).

All extraction on laptop billy / LUNARC (never Mac): S1 is a 5.0 GB zip; S2/S3 need checkouts.

## 1. Objects (one schema for all systems)

Per system: node set V (module / target / crate / class), authoritative edge set E with a
recorded extraction command and tier (T1/T2), obligation set O ⊆ V×{verify}, and a change
sequence Δ_1..Δ_n (per-commit changed files mapped to nodes by a registered deterministic rule).
A_G(Δ) = reverse-transitive closure of Δ in G. One shared closure implementation
(`closure.py`, independently checkable, no ORION-16 module imported) computes every arm's set —
including the planted controls (§3).

## 2. Arms (fixed, five)

| arm | selected set | prediction |
|---|---|---|
| A1 full revalidation | O (everything) | safe; zero savings |
| A2 direct-neighbour | Δ ∪ N^1(Δ) (1-hop reverse) | unsafe: strands every depth-≥2 obligation; separation witnesses exist |
| A3 changed-set only | Δ | unsafe; maximal savings; most witnesses |
| A4 dependency closure | A_G(Δ) | safe (0 retained-invalid on the true graph) AND materially cheaper than A1; savings exactly |O| − |A_G(Δ)| |
| A5 strongest incremental baseline | tool-selected set | per ecosystem: Ekstazi (dynamic RTS, S1/Defects4J), bazel-diff (S2), cargo fingerprint dirtiness (S3). Prediction: safe only where its graph ⊇ true edges; cost ≥ A4 wherever it over-approximates (Wave-2 Thm 2 surplus = w(A_G\A_G*)) |

## 3. Planted controls (route through the SAME closure computation)

- **MISSING-EDGE control (per system, k=10 pre-registered edges)**: remove a true edge e=(u→v)
  from G to form G⁻; re-run A4 with `closure.py` on G⁻ over the recorded Δ sequence. MUST fire:
  for at least one registered Δ containing u, the obligation on a v-dependent node is stranded
  (selected by A4(G) but not A4(G⁻)) and, where real failure data exists, a really-failing
  obligation escapes selection. Checker terminal on detected incompleteness: CANNOT_CHECK
  (Wave-2 Thm 3 corollary), never a silent pass. A control that does not fire falsifies the
  harness, not the theory — halt and repair before unblinding.
- **CONSERVATIVE-EDGE control (k=10 added false edges → G⁺)**: A4(G⁺) must remain safe
  (0 violations) with measured surplus exactly w(A_{G⁺}(Δ) \ A_G(Δ)) (Thm 2 exactness, verified
  numerically per Δ).
- Controls use the same code path, same Δ stream, same metrics pipeline as the real arms; only
  the graph object differs. Planting is recorded (edge list SHA-256) before any arm runs.

## 4. Metrics

- **Safety**: retained-invalid count per arm (graph-defined), plus — where real failure data
  exists (S1, Defects4J) — real-failure escapes: failing test's obligation ∉ selected set.
  Flakiness adjudication rule registered before unblinding (failure also present on unchanged
  re-run ⇒ excluded symmetrically from all arms).
- **Cost**: |selected set| per Δ (and wall-clock proxy where obligation costs are recorded, w≥0).
- **Prediction fit** (primary quantitative claim): savings_A4(Δ) = |O| − |A_G(Δ)| exactly by
  construction on the registered graph; the empirical fit tested is |A_G(Δ)| vs *observed*
  system revalidation (S2: Bazel re-executed action count from execution logs; S3: cargo
  recompiled-unit count; S1: |A| vs failure-capture-sufficient set size). Report rank
  correlation + calibration plot per system; pre-register the pass threshold.
- **Terminal accounting**: every commit where extraction fails = CANNOT_CHECK (exit 3), reported,
  never interpolated (distinct from "checked and fine").

## 5. Holdout (org/system level)

Any tunable (node-mapping rules, flakiness rule, thresholds) is fixed on the DEV slice only:
S1 projects 1–10. Holdout = S1 projects 11–20 + ALL of S2 + ALL of S3, evaluated once, after
freeze. No per-system re-tuning; a holdout failure is reported as-is.

## 6. EXPECTED_TERMINALS (draft)

```json
{"schema":"ORION.ORION16.RealSystemMinimalRevalidation.ExpectedTerminals.DRAFT",
 "terminal_set":[
  {"terminal":"EMPIRICAL_DISCRIMINATOR_EARNED",
   "condition":"on >=2 independently sourced systems: A4 has 0 safety violations on the registered graph AND cost materially below A1 AND savings predicted by |A_G(Delta)| at the registered fit threshold AND all planted missing-edge controls fire AND A2/A3 exhibit concrete separation witnesses"},
  {"terminal":"BASELINE_PARITY",
   "condition":"A5 matches A4 on safety and cost within registered tolerance on all systems; closure law holds but confers no advantage over deployed practice — reported as confirmation-without-advantage, not spun"},
  {"terminal":"GRAPH_NOT_AUTHORITATIVE",
   "condition":"real-failure escapes occur under A4 on the registered graph outside registered missing-edge classes, or extraction CANNOT_CHECK rate exceeds the registered ceiling on >=2 systems",
   "required_action":"stop rule applies verbatim"},
  {"terminal":"CONTROL_HARNESS_FAILURE",
   "condition":"any planted control fails to fire, or conservative-edge surplus deviates from Thm-2 exactness",
   "required_action":"halt before unblinding; repair harness; re-freeze"},
  {"terminal":"CANNOT_CHECK","condition":"a system's data or extraction unavailable; reported per system, never as a pass"}]}
```

## 7. Stop rule (#1649, verbatim)

"If real dependency extraction cannot be made authoritative, keep the general theorem and
bounded paper; do not manufacture deployed-system claims."

Evaluation hooks: T1 systems (S2, S3) are authoritative by construction — for them the stop
rule can only trigger via extraction failure (bit-rot ceiling). S1's Maven-reactor layer is what
Maven executes (T1 at module scope); its finer jdeps layer is T2 with a registered residual.
Any system failing its authoritativeness bar is dropped, not patched; if fewer than 2 systems
survive, the campaign terminates under the stop rule.

## 8. Run plan (laptop/LUNARC; commands recorded in CANDIDATES.md)

1. Fetch S1 zip (5.0 GB, md5-checked) on LUNARC; S2/S3 clones on laptop or LUNARC.
2. Extraction pass per system → graphs/ + changes/ + obligations/ artifacts, SHA-256 manifest.
3. Freeze: schema, arms, controls (edge lists), metrics thresholds, holdout split,
   EXPECTED_TERMINALS → single frozen JSON, hash-bound.
4. Execute arms + controls via the one closure implementation; write per-system result JSON.
5. Evaluate terminals; report adverse/CANNOT_CHECK verbatim.
