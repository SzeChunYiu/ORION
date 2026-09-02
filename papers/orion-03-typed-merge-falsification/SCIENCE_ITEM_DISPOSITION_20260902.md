# ORION-03 open-science-item disposition — 2026-09-02

**Closes:** the one open science item of the ORION-03 Tier-B closure
(issue SzeChunYiu/ORION-paper#78, ORION-03 section)
**Ladder:** (1) formal separation → (2) second-live-corpus preflight → (3) honest narrowing
**Landed:** **(3) HONEST NARROWING**, with a documented failed attempt at (1) and a
completed preflight at (2).
**scientific_authority_delta:** `NONE` (narrowing/clarification only; no ledger status changed)

## Rung (1) — formal separation: ATTEMPTED, did not land

Full record: `FORMAL_SEPARATION_ATTEMPT_20260902.md`. Summary of the failure: the
proposition "no provenance-semiring or ATMS encoding at matched interface can express
origin-witness nonpromotion" is not airtight because it is false as naturally matched —

- the manuscript's own transfer (`τ_r = K_r ∩ ⋂ x_a`, heads aggregated by union) *is*
  annotated evaluation at the powerset annotation configuration of the cited donors;
- per-rule caps simulate exactly inside the paper's own definition space by a seeded
  premise (`σ(c_r) = K_r`), so even "no caps" is not a separating interface;
- the refutation clamp cannot be matched to published semiring deletion semantics
  without importing external definitions (smuggled assumptions — forbidden by the
  landing condition);
- ATMS labels admit an origin-homogeneity post-filter that recovers `d = v_A ∨ v_B`
  (minimality pruning cannot erase a homogeneous witness in a positive system).

What survives is not expressiveness but enforcement locus (propagation-time invariant
vs post-hoc label filter), measured cost (3,924 vs 1,962 evaluations,
`evidence/round2-x509-truststore/COST_ROUND2_V2.json`), and vocabulary curation. The
attempt is retained as a valuable negative: it is exactly why the manuscript now states
the gate as OPEN rather than implying an unattempted separation theorem.

## Rung (2) — second-live-corpus preflight (field existence first; no study executed)

Web preflight executed 2026-09-02. Findings per candidate substrate:

| Substrate | Independently authored fields | Licence | Typed binding | Preflight verdict |
|---|---|---|---|---|
| Debian patch provenance headers (DEP-3) | `Origin`, `Applied-Upstream`, `Forwarded`, `Bug-<Vendor>`, `Author`, `Reviewed-by`, `Last-Update` in `debian/patches/*.patch` (spec: dep-team.pages.debian.net/deps/dep3/) | Convention is recommended, not policy-mandated; patch content inherits per-package licences (heterogeneous) | Two-origin merge = union of two patch stacks for one package; hybrid event = merged-stack outcome neither parent yields; `Origin`/`Applied-Upstream` give the per-patch origin witness | Measurable in principle; native adjudicator (patch application + package build) is heavyweight and host-bound → **successor scope, not executed** |
| Distro advisory + changelog merges | Debian Security Tracker: public git (salsa.debian.org/security-tracker-team/security-tracker), structured `data/DSA/list` records, JSON endpoint (security-tracker.debian.org/tracker/data/json); `debian/changelog` in source packages | **Not verified in preflight** — no licence surfaced; must be resolved before any use | Merge two distro views of the same package/version; hybrid = status conclusion licensed by neither parent alone | Weaker field match; licence unresolved → **successor scope, contingent** |
| cargo/npm advisory–licence joins | RustSec `advisory-db`: per-record `license` field — CC0-1.0 native, CC-BY-4.0 on GHSA-imported records; GitHub Advisory DB CC-BY-4.0 in OSV schema; crate-side `license`/`license-file` (SPDX) in `Cargo.toml` authored by crate authors | **Verified usable** (CC0 + CC-BY-4.0 with per-record marking; OSV data-source list, google.github.io/osv.dev/data/) | Two-origin merge = GHSA/OSV view vs RustSec-native view joined to crate licence metadata on package + version range; hybrid = merged-join conclusion (advisory applicability or licence status) supported by neither parent alone; the per-record license field is the closest independently-authored evidence-license-like field found | **Strongest successor candidate**: OSV version-range evaluation is pure computation (no builds) → genuinely reachable in bounded time; **still not executed** per preflight-only instruction |
| in-toto / SLSA attestation chains | in-toto attestation `subject` + `materials` (Link predicate); SLSA Provenance `materials` (v0.1–0.2), renamed `resolvedDependencies` (v1.0) | **Verified usable** (in-toto/attestation and SLSA specs Apache-2.0) | Two-origin merge = two independently authored attestation chains over shared subjects; hybrid = build-level conclusion supported only by mixing attestations across origins | Fields exist, but a public corpus of two independent chains over the *same* subjects is not known to exist → **successor scope, corpus availability unproven** |

### Successor protocol sketch (strongest candidate: advisory–licence joins)

1. Freeze sources: RustSec `advisory-db` at a pinned commit; GitHub Advisory Database
   OSV export at a pinned date; a pinned crates.io crate/version snapshot. Record
   digests, mirroring `evidence/round2-x509-truststore/SOURCE_BINDING_V2.json` practice.
2. Task families: for each crate present in both advisory sources, construct parent
   decisions (per-source OSV range evaluation over the crate version set), the flat-union
   decision (range union), and the join with crate licence metadata.
3. Preregister before evaluation: hybrid definition `H = v_U ∧ ¬v_A ∧ ¬v_B` (identical to
   the X.509 study's), an anchoring gate against a native tool (e.g. `cargo audit` /
   `osv-scanner`) on a sampled subset with a registered threshold, and per-policy cost
   accounting (two parent evaluations vs one merged evaluation).
4. Independent reimplementation + two complete runs with byte-identical receipts,
   mirroring `evidence/round2-x509-truststore/` (run1/run2 receipts, controls that could
   have failed, adverse observations retained).
5. Standing boundary from the ledger: no detector-performance claim for any
   definitionally aligned witness row (D3-C9 remains forbidden in any successor).

## Rung (3) — honest narrowing: LANDED

Manuscript edits (in `MANUSCRIPT_V3.md`, targeted, in-register):

1. **Limitations** now carry a deliberate-boundary paragraph: the donor relationship is
   declared, not demonstrated; no proposition shows the neighbours cannot express
   origin-witness nonpromotion; the filed contribution is a formal license-propagation
   system plus one measured hybrid-authorization phenomenon (46 among 1,962 third-party
   merge tasks); the separation question (enforcement locus, per-decision cost,
   vocabulary curation) is stated OPEN.
2. **Related work** deltas sharpened for all four neighbour families (see the run
   report); `dekleer1986` added and verified before citing (doi
   10.1016/0004-3702(86)90080-9, Artificial Intelligence 28(2):127–162; confirmed via
   ACM DL and ScienceDirect 2026-09-02 — note the DOI check digit is `-9`; a `-7`
   variant circulating from memory is wrong).

No number, result, or citation was invented; every figure above traces to
`evidence/round2-x509-truststore/ROUND2_RESULTS_V2.json` (46, 1,962, 186/191),
`COST_ROUND2_V2.json` (3,924), and the web sources named in the preflight table.

## Status

`SCIENCE_ITEM_CLOSED__LANDED_RUNG_3__SUCCESSOR_SCOPE_RECORDED`

skills-applied: nature-writing, nature-citation, nature-publication-closure
