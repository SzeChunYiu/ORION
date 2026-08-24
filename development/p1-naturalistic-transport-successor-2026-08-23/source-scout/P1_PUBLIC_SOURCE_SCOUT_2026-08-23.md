# P1 outcome-blind public-source scout

**Date:** 2026-08-23  
**Authority:** source metadata, documentation, schemas, licences, and counts only  
**Content boundary:** no task row, reason label, outcome, issue body, patch, case text, or candidate output was displayed or inspected

## Decision

The best lawful development source found is the **Crossref Retraction Watch
database**, pinned to an immutable GitLab commit. It is unusually well matched
to P1 because it contains natural scientific update events spanning subjects,
publishers, countries, update types, and controlled reason codes, and Crossref
explicitly places the Retraction Watch database in **CC0**. It can support a
large, noisy, non-filename-based *development* panel if all update/reason fields
remain evaluator-side and an independent custodian constructs matched
candidate-visible evidence dossiers.

It is not sufficient for confirmatory naturalistic transport by itself. Labels
are public, update reasons are curated after the event, corrections and
expressions of concern are incomplete relative to retractions, and the CSV does
not automatically license linked article or notice full text. A protected
future-update wave or an owner-disjoint second corpus remains necessary.

## Ranked sources

### 1. Crossref Retraction Watch data — recommended P1 development backbone

**Exact source identity**

- Official repository: `crossref/retraction-watch-data`, GitLab project ID
  `61336882`.
- Exact commit: `7bb2ced143b764974c53c6c61abfdd2379f5307d`, committed
  `2026-08-21T23:00:10Z`.
- CSV blob: `40a049f02044fab8286c0304fd296bf1fa2cb8ca`.
- Raw CSV SHA-256 supplied by GitLab:
  `ceaab201d728dfcf9929ec1e229acd2ad88c650c847ec922ba9ffe831e366abb`.
- Exact byte count: `65,984,968`.
- Parsed data-row count: **71,944**, obtained by streaming the immutable CSV
  through a CSV row counter without displaying or retaining fields.
- Repository: <https://gitlab.com/crossref/retraction-watch-data>
- Exact commit: <https://gitlab.com/crossref/retraction-watch-data/-/commit/7bb2ced143b764974c53c6c61abfdd2379f5307d>
- Documentation and schema: <https://www.crossref.org/documentation/retrieve-metadata/retraction-watch/>

**Licence and content-class rights**

- Crossref's metadata-retrieval documentation explicitly lists the
  **Retraction Watch database as CC0**:
  <https://www.crossref.org/documentation/retrieve-metadata/>.
- The CC0 authority covers the Retraction Watch CSV fields, including the
  controlled update/reason metadata and database notes.
- It does **not** automatically cover linked publisher article bodies,
  abstracts, retraction-notice full text, attachments, or Retraction Watch blog
  posts. Crossref explicitly says abstracts retain publisher/author copyright.
  Any such bytes require per-object licence adjudication or must be excluded.
- The GitLab repository itself contains no `LICENSE` file; the controlling
  rights evidence is Crossref's official metadata-licence statement, which
  should be archived verbatim with the protocol.

**Accessible pre-outcome structure**

The official documentation specifies 20 fields, including original/update
identifiers and dates, subject, article type, update nature, controlled reasons,
paywall state, and notes. The database is refreshed each working day. A separate
zero-record Crossref REST count on 2026-08-23 returned **74,828** works under
`update-type:retraction`; this is a dynamic API availability ceiling, not the
same population as the pinned 71,944-row CSV, because API records can include
publisher and Retraction Watch sources.

**Feasible independent unit**

Use the **connected scientific-update family**, not the CSV row: collapse all
records sharing an original DOI/PMID, update-notice DOI/PMID, or explicit
reinstatement chain. Cluster inference further by journal/publisher and prevent
authors/update families from crossing development and replication waves.

**P1 fit**

- Scientific rather than generic software incidents.
- No need to encode gold in filenames or authored templates.
- Large enough to require multiple independent clusters per rule/action cell,
  eliminating the current 32/66 singleton-rule authority.
- Update nature, reason vocabulary, and notes can support genuinely different
  evidence-dependent transitions rather than a 33/66 constant-responder panel.

**Contamination and construct risks**

1. `RetractionNature`, `Reason`, `Notes`, URLs, DOIs, record IDs, publisher,
   journal, and notice titles can reveal the answer or permit memorization.
2. Retraction Watch reason codes are curated post-event annotations, not direct
   proof of P1 causal responsibility. Two independent adjudicators must map
   source evidence to P1 responsibility classes and may return `UNRESOLVED`.
3. Multiple rows can represent one scientific event; row-level inference would
   pseudoreplicate.
4. Public labels make this development evidence. A final claim needs a
   protected future-update wave collected after the freeze, with network access
   disabled for evaluated systems, or an owner-disjoint corpus.
5. Retractions dominate; corrections and expressions of concern are explicitly
   less comprehensive, so raw prevalence cannot be treated as a population
   distribution of scientific transitions.

### 2. NIST National Vulnerability Database JSON 2.0 — recommended adversarial implementation-only panel

**Exact source identity**

- Feed: `nvdcve-2.0-2025`, NVD JSON schema 2.0.
- Metadata snapshot: `2026-08-23T03:00:42-04:00`.
- Uncompressed bytes: `284,733,144`; ZIP bytes: `23,799,996`.
- Uncompressed feed SHA-256:
  `2EC34AF94C2CCC7F6AF6B0280F266E53F35EB0F987DC927C3E575A6965382E7B`.
- Pre-outcome count from four <=120-day NVD API count queries: **49,972** CVEs
  published during 2025 (`12,412 + 12,205 + 12,207 + 13,148`).
- Feed metadata: <https://nvd.nist.gov/feeds/json/cve/2.0/nvdcve-2.0-2025.meta>
- Schema: <https://csrc.nist.gov/schema/nvd/api/2.0/cve_api_json_2.0.schema>
- Feed documentation: <https://nvd.nist.gov/vuln/data-feeds>

**Rights**

- NIST states that, except for specifically marked copyrighted material,
  information on NIST sites is public information that may be distributed or
  copied: <https://www.nist.gov/oism/copyrights>.
- NVD is supplied as a public service under its database disclaimer:
  <https://nvd.nist.gov/general/legal-disclaimer>.
- Use only NVD JSON fields. Linked vendor advisories, patches, source code, and
  attachments remain separate content classes and are not licensed by this
  statement.

**Feasible unit and role**

Collapse related CVEs/advisories into an incident family and cluster by vendor
or repository. This source is useful as a high-volume negative/control panel
for implementation/environment responsibility and for testing that P1 does not
over-escalate to model/problem reformulation.

**Why it is not the primary panel**

CVE/CWE identifiers, severity fields, descriptions, and vendor names are strong
answer shortcuts; public benchmark exposure is severe; and the corpus is
overwhelmingly implementation/security responsibility. It cannot establish
wide scientific-transition transport.

### 3. Defects4J 3.0.1 — metadata-feasible, rights- and construct-blocked

- Repository: `rjust/defects4j`.
- Commit: `8c16da8230843cdc918eaf4ddb449637f02b83c6`.
- README-declared version: `3.0.1`.
- README-declared counts: **854 active plus 10 deprecated bugs across 17
  projects**.
- Exact source: <https://github.com/rjust/defects4j/tree/8c16da8230843cdc918eaf4ddb449637f02b83c6>
- No root licence file exists at the pinned commit. The framework, upstream
  project code, tracker prose, and patches therefore cannot be treated as one
  uniformly licensed content class.
- Independent unit: upstream fixing commit/issue, clustered by project.
- Construct blocker: every admitted case is a source-code fix with a
  fail-before/pass-after trigger. A blind `IMPLEMENTATION_REPAIR` responder is
  therefore structurally strong; Defects4J cannot repair P1's 33/66 shortcut or
  provide broad K/W/M responsibility without additional strata.

### 4. BugsInPy — scientifically relevant projects, but reject until rights are bound

- Repository: `soarsmu/BugsInPy`.
- Commit: `11c5f1eea954a42132cfd06bf257766a7963e0fd`.
- Metadata-only directory census: **502 bug directories across 17 projects**.
- Exact source: <https://github.com/soarsmu/BugsInPy/tree/11c5f1eea954a42132cfd06bf257766a7963e0fd>
- The root contains no licence file. Several constituent projects are
  scientific (`keras`, `matplotlib`, `pandas`), but every upstream project and
  issue/patch content class requires separate rights binding.
- Like Defects4J, the benchmark encodes buggy/fixed state in paths and its case
  universe is almost entirely implementation repair. It is a poor main P1
  panel even if rights are later repaired.

BugSwarm and Bears were also checked at metadata/documentation level. Their
infrastructure repositories are respectively BSD-3-Clause and GPL-3.0, but
those licences do not automatically cover the mined GitHub/CI artifacts and
upstream project branches. They are not recommended over the sources above.

## Patch-ready protocol recommendation

Freeze `P1.RW.CC0.NATURALISTIC.DEVELOPMENT.V1` at Crossref commit
`7bb2ced143b764974c53c6c61abfdd2379f5307d` with the following gates:

1. **Outcome-blind census:** an external source custodian reports only connected
   family counts by candidate mapping cell before any row content or mapped
   responsibility is released. No cell used for a rule may contain fewer than
   20 independent update families.
2. **Evaluator-only fields:** retain `Record ID`, DOI/PMID, URLs, journal,
   publisher, `RetractionNature`, `Reason`, `Paywalled`, `Notes`, filenames, and
   provider identity outside the candidate interface until the specific field
   is opened as a registered evidence probe.
3. **Natural evidence interface:** candidates receive randomized opaque case
   handles, a role-free initial scientific symptom, and a common action/probe
   set. Any candidate-visible evidence must come only from CC0 CSV bytes or
   separately licensed notice text.
4. **Independent responsibility gold:** two blinded adjudicators map evidence to
   the P1 responsibility/transition ontology; disagreement goes to a third
   adjudicator or `UNRESOLVED`. Retraction Watch reason codes are features for
   adjudication, not automatic P1 gold.
5. **Template-leakage falsifier:** an evaluator using only serialized template,
   field presence, filenames, ordering, length, IDs, provider, and punctuation
   must perform at chance/equivalence-null level. Failure regenerates the
   interface before any candidate scoring.
6. **Blind-responder falsifier:** construct matched action-contrast blocks in
   which the same initial symptom requires different transitions after a
   registered evidence probe. A policy that ignores probe values must fail the
   paired utility/safety gate.
7. **No singleton authority:** report rule/action effects only at update-family
   level with frozen minimum cluster counts and simultaneous uncertainty;
   singleton successes receive zero promotion authority.
8. **Development/replication separation:** develop on the pinned 2026-08-21
   commit. Pre-register a future date window and let an independent custodian
   acquire later daily records as a protected temporal wave. Keep journals,
   publishers, authors, update chains, and original works disjoint across waves.
9. **Claim boundary:** success supports public-label naturalistic scientific
   transition *development* under one curator/provider family. It does not
   establish general responsibility inference, causal truth of Retraction Watch
   reasons, or cross-provider superiority.

## Outcome-blind audit trail

- Crossref documentation and licence statements were read.
- GitLab project/commit/tree/README metadata and response headers were read.
- The immutable CSV was streamed only through byte/line and CSV-row counters;
  no record fields were emitted or stored.
- NVD documentation, feed metadata, schema identity, legal statements, and API
  counts were read; no CVE record was displayed.
- GitHub repository metadata, root documentation, licence presence, and
  directory counts were read; no bug case, patch, issue, test result, or label
  content was opened.
- No ORION repository file, manuscript, frozen protocol, test, CI job, branch,
  or Git state was modified.
