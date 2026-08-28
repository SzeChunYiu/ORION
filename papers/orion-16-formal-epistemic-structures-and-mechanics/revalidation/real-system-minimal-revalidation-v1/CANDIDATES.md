# ORION-16 Real-System Revalidation — Candidate Graph Sources (scouting, 2026-08-28)

Campaign: `ORION16.REAL_SYSTEM_MINIMAL_REVALIDATION.v1` (issue #1649 Tier A empirical discriminator).
Scouting only — nothing here is executed evidence. No downloads > a few MB performed.

## Formalism mapping target (read first)

From `papers/orion-16-formal-epistemic-structures-and-mechanics/` (revalidation/compare_p6_revalidation_v1.py,
CLAIM_LEDGER_V4 rows V4.4/V4.6, and the Wave-2 packet `theory/graph-quality-revalidation-v1/` on branch
`claude/orion16-graph-quality-20260828`, PR #1684 — NOT on origin/main as of this scan):

- **Obligation / certificate**: "unit U was verified at state X". Its read-set is U's transitive
  dependency closure in G.
- **Change set Δ**: files/units touched by a commit, mapped to graph nodes.
- **A_G(Δ)**: reverse-transitive closure of Δ — the unique minimal sound revalidation set
  (V4.4: every proper subset is unsound; Wave-2 Thm 4: exactness uniquely cost-optimal;
  Thm 2: over-approx surplus = w(A_G \ A_G*); Thm 3: a missing true edge strands an obligation →
  only safe terminal is CANNOT_CHECK).
- **Safety violation**: retained-invalid certificate = an obligation outside the selected set whose
  read-set intersects Δ (or, with real failure data: a recorded real failure whose obligation the
  arm did not select).
- **Savings**: obligations retained vs full reset; predicted by |A_G(Δ)|.

**Why prior in-repo evidence does not discharge #1649**: P6's numpy/scipy/flask comparison and
ORION-17's P7_CLOSURE_RETENTION_V1 both use **ast-extracted Python import graphs** — heuristic
extraction (dynamic imports invisible). #1649 requires the graph itself to be **authoritative**:
the artifact the system *actually executes against*, not an inference. That is the selection
criterion below.

Authoritativeness tiers used below:
- **T1 — authoritative by construction**: the system consults this exact graph to decide what to
  rebuild/retest; a wrong graph would break the system itself, not just our study.
- **T2 — authoritative for a declared static scope**: derived from ground-truth artifacts
  (bytecode constant pool, pom manifests) with a *registrable* residual edge class (reflection,
  dynamic loading) — the residual maps onto the missing-edge control regime, it is not silent.
- **T3 — heuristic**: parsed/learned. Ineligible as a primary graph (this is what we are escaping).

---

## C1 — Bazel target graphs of large OSS monorepos (envoy, abseil-cpp, grpc) — T1

- **Sources**: https://github.com/envoyproxy/envoy (Apache-2.0), https://github.com/abseil/abseil-cpp
  (Apache-2.0), https://github.com/grpc/grpc (Apache-2.0). All Bazel-native.
- **Graph**: `bazel query 'deps(//...)' --output streamed_proto` (target graph) and
  `bazel aquery '//...'` (action graph). This is the graph Bazel itself schedules builds from —
  **T1**: Bazel's incremental correctness *is* this graph.
- **Change history**: full git history; Δ = changed files of a commit mapped to targets via
  `bazel query 'rdeps(//..., set(<files as source targets>))'` — the same primitive CI target
  determination uses (cf. Tinder/bazel-diff, bazel-contrib/target-determinator).
- **Obligation**: a target's "built+tested at commit X" certificate; test targets = `kind(test, //...)`.
- **Ground truth for "needed revalidation"**: two-layer —
  (a) Bazel's own invalidation: build at commit N with warm cache from N-1; the set of re-executed
  actions is the system's *deployed* revalidation decision (read from `--execution_log_json_file`).
  (b) Real failure data: per-commit CI check conclusions via GitHub Checks API (runner-side).
- **Extraction (record only, run on laptop/LUNARC)**:
  ```
  git clone https://github.com/envoyproxy/envoy && cd envoy
  for SHA in $(git rev-list --first-parent -n 300 origin/main); do
    git checkout -q $SHA
    bazel query 'deps(//...)' --output streamed_proto > graphs/$SHA.deps.pb
    git diff-tree --no-commit-id --name-only -r $SHA > changes/$SHA.files
  done
  # per-commit affected set (arm 4): bazel query "rdeps(//..., set($(files-as-labels)))"
  # deployed-invalidation gold: bazel test //... --execution_log_json_file=exec/$SHA.json
  ```
- **Size estimate**: envoy tens of thousands of targets; 300-commit window feasible on LUNARC
  (query-only passes need no compilation; execution-log gold needs builds — budget the window).
- **Kill risk**: historical-commit bit-rot — old WORKSPACE external deps 404 or need old Bazel
  versions (bazelisk mitigates via .bazelversion). If a commit can't be queried, it is
  CANNOT_CHECK for that commit, never interpolated. Aspect notes bazel-diff *the tool* can miss
  targets — so the study must use raw `bazel query rdeps` (exact w.r.t. Bazel's graph), with
  bazel-diff relegated to the "strongest incremental baseline" arm.

## C2 — RTPTorrent (MSR 2020): 20 Java/Maven projects, real Travis failure histories — T2 graph, gold failure data

- **Source**: https://zenodo.org/records/4046180 (v1.1, DOI 10.5281/zenodo.4046180),
  file `rtp-torrent-v11.zip`, **5.0 GB**, **CC BY 4.0**. Paper DOI 10.1145/3379597.3387458.
- **Contents (verified via Zenodo page + paper)**: 20 OSS Java projects, >100k real TravisCI
  build logs over ~9 years, per-build parsed Surefire test results (test class/method, pass/fail/
  error/skip, timing), included git repositories, plus baseline RTP results and a structure README.
- **Graph**: Maven reactor/module dependency graph from the checked-in `pom.xml` tree at each
  commit (`mvn -q dependency:tree` or direct pom parsing of `<modules>` + inter-module
  `<dependency>` entries). Authoritative for build ordering/module scope (Maven executes exactly
  this); **T2** at module granularity. Optional finer layer: `jdeps` class-graph per module.
- **Change history**: dataset's own git repos; Δ = commit's changed files → owning module.
- **Obligation**: test class T (in module M) "passed at build B". **Failure ground truth is the
  dataset's core asset**: real recorded failures per build — the arm-level safety check is
  "every really-failing test's obligation is inside the selected revalidation set".
- **Fetch (record only; LUNARC/laptop)**:
  ```
  curl -L -o rtp-torrent-v11.zip 'https://zenodo.org/records/4046180/files/rtp-torrent-v11.zip?download=1'
  md5sum rtp-torrent-v11.zip   # expect 1f7fa822b0cf155bd007a94d1a24a336
  ```
- **Kill risk**: flaky failures — a real failure whose test is *outside* A_G(Δ) may be flakiness,
  not a missing edge; must pre-register the adjudication rule (e.g., failure also present on
  unchanged re-runs ⇒ flaky; exclude symmetrically across arms) BEFORE unblinding, or the safety
  metric is corrupted. Second risk: module granularity is coarse (few nodes/project) — mitigate
  with the jdeps class-level layer, clearly tiered.

## C3 — Cargo workspace graphs (paritytech/polkadot-sdk; rust-lang/cargo; servo/servo) — T1

- **Sources**: https://github.com/paritytech/polkadot-sdk (workspace with several hundred member
  crates; GPL-3.0/Apache-2.0 mix per crate), https://github.com/rust-lang/cargo,
  https://github.com/servo/servo (MPL-2.0).
- **Graph**: `cargo metadata --format-version 1 --locked` → the `resolve` object is the exact
  acyclic PackageId graph cargo compiles from — **T1**. Workspace-member subgraph = the system
  under study; external crates collapse to boundary nodes.
- **Change history**: git; Δ = changed files → owning crate by manifest dir
  (`.packages[].manifest_path`).
- **Obligation**: crate C "built+tested at commit X" (`cargo test -p C`).
- **Ground truth**: cargo's own dirtiness propagation — warm-cache rebuild at N from N-1; the
  recompiled unit set (from `cargo build --unit-graph -Zunstable-options` + fingerprint logs
  `CARGO_LOG=cargo::core::compiler::fingerprint=info`) is the deployed revalidation decision.
  CI failure data via GitHub Checks API where retained.
- **Extraction (record only)**:
  ```
  git clone https://github.com/paritytech/polkadot-sdk && cd polkadot-sdk
  for SHA in $(git rev-list --first-parent -n 300 origin/master); do
    git checkout -q $SHA
    cargo metadata --format-version 1 --locked --no-deps > graphs/$SHA.members.json
    cargo metadata --format-version 1 --locked > graphs/$SHA.full.json   # resolve graph
    git diff-tree --no-commit-id --name-only -r $SHA > changes/$SHA.files
  done
  ```
- **Size estimate**: polkadot-sdk ≈ hundreds of workspace members (count on runner via
  `cargo metadata --no-deps | jq '.workspace_members | length'`); metadata JSON per commit is
  tens of MB — LUNARC storage fine, not Mac.
- **Kill risk**: feature unification makes the resolved graph configuration-dependent — the
  registered graph must pin one feature configuration (the workspace default) and say so; a
  failure under another feature set is out of registered scope. Lockfile churn commits create
  Δ touching everything (whole-graph closures) — legitimate data, but report their share.

## C4 — Defects4J v3 + Ekstazi/STARTS (Java, real bugs with known triggering tests) — T2

- **Source**: https://github.com/rjust/defects4j (MIT license framework; 17 projects, 835
  reproducible real bugs, each with the exact set of triggering tests). Baseline tools:
  Ekstazi (http://ekstazi.org), STARTS (https://github.com/TestingResearchIllinois/starts).
- **Graph**: `jdeps` bytecode class-dependency graph — derived from the constant pool of the
  compiled artifact, i.e., ground truth for *static* references (**T2**; reflection/DI edges are
  the registered residual class).
- **Change/Δ**: the buggy→fixed commit diff per bug. **Ground truth is the strongest of any
  candidate**: the triggering tests are *known exactly* — the closure arm is safe iff every
  triggering test lies in A_G(Δ) for every bug.
- **Role**: (a) fourth/reserve system; (b) the natural host for the **strongest-incremental-
  baseline arm** (Ekstazi = dynamic per-test class-level RTS = the published state of the art;
  STARTS = static counterpart, structurally closest to the closure method — the sharpest
  possible comparison).
- **Kill risk**: reflection edges — a triggering test reachable only via reflection falls outside
  the static closure. This is exactly the missing-edge regime: per Wave-2 Thm 3 the sound
  response is CANNOT_CHECK, and the study must pre-register the reflection-edge class rather
  than discover it post hoc. If reflection misses are common, the T2 graph fails
  authoritativeness for this ecosystem — that outcome itself feeds the stop rule.

## C5 — rustc incremental query dep-graph (`-Zquery-dep-graph`) — T1, exploratory only

- **Source**: any Rust crate compiled with nightly rustc, `RUSTFLAGS="-Zquery-dep-graph"`,
  dumps the red/green query DAG the compiler's incremental engine consults
  (rustc_incremental::assert_dep_graph / dump_graph; nightly-only).
- **Fit**: the graph is maximally authoritative (**T1**, finest granularity anywhere), and
  red/green marking *is* dependency-closed revalidation deployed in a production compiler.
- **Kill risk (why not top-3)**: obligations are compiler queries, not user-facing verification
  units; per-session dumps are hard to align with commit-level Δ; unstable flags. Valuable as a
  qualitative "the law is deployed practice" citation, weak as a benchmark substrate.

## C6 — Chromium GN graph + CQ/ResultDB test results — T1, stretch

- **Sources**: chromium/src GN build graph (`gn desc`, `gn refs` — the graph the "analyze" CQ
  step uses for per-CL affected-target computation, i.e., dependency-closed selection deployed
  at the largest public scale); test outcomes via LUCI ResultDB BigQuery export
  (e.g. `chrome-luci-data` project tables; docs: docs/infra/cq.md, docs/testing/resultdb.md).
- **Kill risk**: bulk access needs a GCP account + query budget; some CQ builders are
  Google-internal (partial visibility); checkout+GN at historical commits is heavy (100+ GB
  class). Keep as a named stretch goal, not a dependency of the campaign.

## Rejected / auxiliary

- **GSDTSR** (Google Shared Dataset of Test Suite Results, Elbaum et al.): real execution
  history, **no dependency graph, no source, no change sets** → cannot instantiate A_G(Δ).
  Mirror: https://github.com/yourkevin/atcs-data. Auxiliary only.
- **This repo's own CI / ORION-17 P7 closure data**: same-programme custody — explicitly
  ineligible for #1649 independence (P7_CLOSURE_RETENTION_V1 is adjacent evidence to cite,
  never a substitute; its graphs are also T3 ast-extracted).
- **TravisTorrent alone**: build-level outcomes without per-test results; superseded by
  RTPTorrent for this purpose.

## Ranking

1. **C2 RTPTorrent** — the only candidate with curated, real, per-test failure ground truth at
   scale (>100k builds), fixed forever (Zenodo, CC BY 4.0), zero re-execution needed for the
   failure signal; graph layer (Maven reactor) is exactly what the build system executes.
2. **C1 Bazel/envoy(+abseil or grpc)** — strongest authoritativeness story (T1 by construction),
   ecosystem-independent of C2, and the deployed-invalidation gold (execution logs) measures the
   *system's own* closure decision, closing the "extraction is heuristic" gap completely.
3. **C3 Cargo/polkadot-sdk** — third independent ecosystem, T1 resolved graph in one command per
   commit, cheap query-only extraction; ground-truth layer (fingerprint dirtiness) available at
   moderate cost.
4. C4 Defects4J+STARTS/Ekstazi — reserve system and mandatory home of the strongest-baseline arm.
5. C5, C6 — exploratory/stretch.

Three top sources = three ecosystems (Java/Maven+Travis, C++/Bazel, Rust/Cargo), three
independent custodians (HPI/Zenodo, Envoy/CNCF, Parity) — satisfies "2–3 independently sourced
systems" with margin.
