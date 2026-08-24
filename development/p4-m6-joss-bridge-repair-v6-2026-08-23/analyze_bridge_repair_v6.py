#!/usr/bin/env python3
from __future__ import annotations
import collections,datetime as dt,hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;REPO=HERE.parents[1];V5=REPO/'development/p4-m6-joss-exact-version-bridge-v5-2026-08-23'
DOMAINS=['EARTH_ENVIRONMENT','LIFE_BIOMEDICAL','SCIENTIFIC_SOFTWARE','PHYSICAL_ENGINEERING']
V3={'EARTH_ENVIRONMENT':2,'LIFE_BIOMEDICAL':0,'SCIENTIFIC_SOFTWARE':6,'PHYSICAL_ENGINEERING':1}
def now():return dt.datetime.now(dt.timezone.utc).isoformat()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def jl(p):return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
def dump(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
rows=jl(HERE/'BRIDGE_REPAIR_ROWS_V6.jsonl');v5=jl(V5/'BRIDGE_ROWS_V5.jsonl')
q=[r for r in v5 if r['gates']['v4_provider_qualified_predecessor_preserved']]
v5pass=[r for r in q if r['exact_publication_archive_repository_commit_rights_bridge_pass']]
repaired=[r for r in rows if r['v6_exact_bridge_repaired']];unresolved=[r for r in rows if not r['v6_exact_bridge_repaired']]
assert len(v5)==200 and len(q)==80 and len(v5pass)==39 and len(rows)==41 and len(repaired)+len(unresolved)==41
assert {r['frozen_index'] for r in rows}=={r['frozen_index'] for r in q if not r['exact_publication_archive_repository_commit_rights_bridge_pass']}
assert not ({r['frozen_index'] for r in repaired}&{r['frozen_index'] for r in v5pass})
# Mutually exclusive unresolved classification, ordered by earliest failed exact gate.
def primary(r):
 if not r['source_native_exact_version_doi_match']:return 'FROZEN_ARCHIVE_DOI_IS_CONCEPT_OR_MUTABLE_LATEST_REDIRECT__EXACT_PUBLICATION_VERSION_CANNOT_CHECK'
 if not r['source_native_archive_spdx']:return 'EXACT_ARCHIVE_SOFTWARE_RIGHTS_CANNOT_CHECK_OR_NOT_ACCEPTED'
 if not r['accepted_content_identity']:return 'SOURCE_ARCHIVE_TO_IMMUTABLE_REPOSITORY_COMMIT_CONTENT_IDENTITY_CANNOT_CHECK'
 if not r['commit_spdx']:return 'EXACT_COMMIT_RIGHTS_CANNOT_CHECK_OR_NOT_ACCEPTED'
 return 'UNCLASSIFIED_CANNOT_CHECK'
primary_counts=collections.Counter(primary(r) for r in unresolved)
overlap_counts=collections.Counter(x for r in rows for x in r['v6_failure_causes'])
primary_by_domain={d:dict(collections.Counter(primary(r) for r in unresolved if r['domain']==d)) for d in DOMAINS}
repairs_by_domain=collections.Counter(r['domain'] for r in repaired); unresolved_by_domain=collections.Counter(r['domain'] for r in unresolved)
v5pass_by_domain=collections.Counter(r['domain_discovery'] for r in v5pass); qualified_by_domain=collections.Counter(r['domain_discovery'] for r in q)
final_by_domain={d:v5pass_by_domain[d]+repairs_by_domain[d] for d in DOMAINS}
cell_counts={}
for d in DOMAINS:
 union=V3[d]+final_by_domain[d]
 cell_counts[d]={'v4_provider_qualified_frozen':qualified_by_domain[d],'v5_exact_pass':v5pass_by_domain[d],'v6_same_identity_repairs':repairs_by_domain[d],'v6_remaining_unresolved':unresolved_by_domain[d],'final_exact_joss_bridge':final_by_domain[d],'v3_figshare_strict':V3[d],'deduplicated_v3_plus_final_exact':union,'total_quota_48_pass':union>=48,'joss_primary_quota_24_pass':final_by_domain[d]>=24,'figshare_source_disjoint_replication_quota_8_pass':V3[d]>=8,'full_cell_frame_pass':union>=48 and final_by_domain[d]>=24 and V3[d]>=8,'gap_to_48':max(0,48-union),'gap_to_replication_8':max(0,8-V3[d])}
methods=collections.Counter(r['accepted_content_identity']['content_identity_method'] for r in repaired)
result={
 'schema_version':'orion.p4.m6.joss-bridge-repair.result.v6','protocol_id':'P4.PUBLIC.M6.JOSS.SAME.IDENTITY.CONTENT.ADDRESSED.BRIDGE.REPAIR.DEV.V6','created_at':now(),
 'terminal':'P4_M6_JOSS_SAME_IDENTITY_CONTENT_ADDRESSED_BRIDGE_REPAIR_PARTIAL_17_OF_41__FINAL_EXACT_56_OF_80__AUTHOR_LINEAGE_AND_NATURAL_PAIR_CANNOT_CHECK',
 'preserved_programme_terminal':'P4_NATURAL_PAIR_SOURCE_TRANSPORT_CANNOT_CHECK',
 'authority':'PUBLIC_SOURCE_NATIVE_METADATA_AND_BYTES_ONLY__DEVELOPMENT_TRANSPORT_EVIDENCE__NO_NATURAL_PAIR_OR_PERFORMANCE_AUTHORITY',
 'counts':{'same_frozen_publication_dois':200,'v4_provider_qualified_frozen':80,'v5_exact_pass':39,'v5_exact_failures_entering_v6':41,'v6_same_identity_repairs':17,'v6_remaining_unresolved':24,'final_exact_bridge':56,'new_or_replacement_publication_dois':0,'files_versions_tags_commits_requests_counted_as_units':0,'content_identities_bound_in_41':sum(bool(r['accepted_content_identity']) for r in rows),'repaired_by_archive_manifest_identity':methods['SOURCE_NATIVE_ARCHIVE_MANIFEST_EQUALS_GITHUB_IMMUTABLE_COMMIT_ARCHIVE_MANIFEST'],'repaired_by_qualified_swhid_git_tree_identity':methods['QUALIFIED_SWHID_PATH_DIRECTORY_EQUALS_GIT_COMMIT_ROOT_TREE'],'source_native_transport_bound':sum(bool(r['source_native_metadata']) for r in rows),'source_native_exact_version_doi_match':sum(r['source_native_exact_version_doi_match'] for r in rows),'accepted_commit_rights_bound':sum(bool(r['commit_spdx']) for r in rows),'author_lineage_independence_adjudicated':0,'natural_pairs_adjudicated':0,'eligible_natural_pairs':0},
 'repairs_by_domain':dict(repairs_by_domain),'remaining_unresolved_by_domain':dict(unresolved_by_domain),'final_exact_bridge_by_domain':final_by_domain,
 'primary_mutually_exclusive_unresolved_cause_counts':dict(primary_counts),'overlapping_failure_gate_counts':dict(overlap_counts),'primary_unresolved_causes_by_domain':primary_by_domain,
 'cells':cell_counts,
 'repair_methods':dict(methods),
 'repaired_identities':[{'frozen_index':r['frozen_index'],'publication_doi':r['publication_doi'],'archive_doi':r['archive_doi'],'repository':r['repository'],'domain':r['domain'],'commit_sha':r['exact_commit_sha'],'commit_spdx':r['commit_spdx'],'content_identity_method':r['accepted_content_identity']['content_identity_method']} for r in repaired],
 'unresolved_identities':[{'frozen_index':r['frozen_index'],'publication_doi':r['publication_doi'],'archive_doi':r['archive_doi'],'repository':r['repository'],'domain':r['domain'],'primary_cause':primary(r),'overlapping_causes':r['v6_failure_causes']} for r in unresolved],
 'claim_boundary':{'global_transport_claim':False,'natural_pair_readiness_claim':False,'author_lineage_independence_claim':False,'model_performance_or_superiority_claim':False,'protected_or_system_outcomes_accessed':False,'confirmatory_claim':False,'pilot_disclosure_preserved':True,'scientific_software_total_quota_pass_does_not_override_replication_failure':True},
 'scientific_conclusion':'Content-addressed same-identity repair converts 17 of the 41 V5 failures without adding or replacing a DOI unit, raising exact JOSS bridges from 39/80 to 56/80. The 17 repairs comprise 15 Scientific Software, one Earth/Environment and one Physical/Engineering identity. Twenty-four remain CANNOT_CHECK. Deduplicated V3 plus final exact totals are Earth 6, Life 4, Scientific Software 51 and Physical 4; Scientific Software clears the total and JOSS-primary counts but still fails its frozen Figshare source-disjoint replication requirement at 6/8, while the other three domains remain far below 48. Therefore every full cell fails and natural-pair readiness remains CANNOT_CHECK.',
 'next_discriminator':'For the same 24 frozen unresolved identities only, require a source-native exact version DOI rather than a mutable concept/latest redirect, an authenticated source-archive-to-immutable-commit content identity, and accepted exact archive and commit software rights. Separately, close the unchanged source-disjoint replication quotas with already-frozen nonreplacement provider identities before any external outcome-blind lineage/natural-pair adjudication; do not widen to global transport.'
}
for k,p in {'protocol':HERE/'PROTOCOL_V6.json','protocol_freeze':HERE/'PROTOCOL_FREEZE_RECEIPT_V6.json','rows':HERE/'BRIDGE_REPAIR_ROWS_V6.jsonl','harvest_receipt':HERE/'HARVEST_RECEIPT_V6.json','runner':HERE/'run_bridge_repair_v6.py','v5_result':V5/'RESULT_V5.json','v5_rows':V5/'BRIDGE_ROWS_V5.jsonl'}.items():result.setdefault('artifact_hashes',{})[k]=sha(p)
dump(HERE/'CELL_COUNTS_V6.json',cell_counts);dump(HERE/'RESULT_V6.json',result)
neg=[]
for ident,cause,observed,residual,nxt in [
 ('EXACT_PUBLICATION_VERSION_IDENTITY','A frozen JOSS archive DOI is a concept DOI or the captured source-native response identifies a different version DOI. Mutable latest resolution is not an exact publication-version bridge.',f"{primary_counts['FROZEN_ARCHIVE_DOI_IS_CONCEPT_OR_MUTABLE_LATEST_REDIRECT__EXACT_PUBLICATION_VERSION_CANNOT_CHECK']}/24 unresolved identities fail this primary gate.",'No version string, date, filename or current-latest response is substituted.','Obtain a source-native immutable version relation for the same DOI identity or retain CANNOT_CHECK.'),
 ('CONTENT_ADDRESSED_ARCHIVE_COMMIT_IDENTITY','No deterministic source-native tag/commit candidate resolved to a commit with an exact qualified-SWHID/Git-tree or normalized archive-manifest identity.',f"{overlap_counts['SOURCE_ARCHIVE_TO_IMMUTABLE_REPOSITORY_COMMIT_CONTENT_IDENTITY_CANNOT_CHECK']} identities retain this overlapping failure; content identity nevertheless repaired {len(repaired)} and bound {result['counts']['content_identities_bound_in_41']} of 41 overall.",'Unmatched manifests, missing/deleted refs and absent candidates remain zero repair.','Use an authenticated source-native origin/revision relation for the same archive bytes and repository; never select a latest release.'),
 ('EXACT_ARCHIVE_SOFTWARE_RIGHTS','Source-native or DOI-registered exact-version rights are missing or are content licences rather than accepted software SPDX rights.',f"{overlap_counts['EXACT_ARCHIVE_SOFTWARE_RIGHTS_CANNOT_CHECK_OR_NOT_ACCEPTED']} identities fail this overlapping gate.",'CC BY and absent rights are not hand-mapped to software rights.','Bind accepted software rights on the same immutable archive version and commit.'),
 ('M6_CELL_FRAME','Exact bridging cannot override frozen per-domain total, primary and source-disjoint replication gates.',f"Final exact unions are Earth 6/48, Life 4/48, Scientific Software 51/48 and Physical 4/48; replication arms remain 2/8, 0/8, 6/8 and 1/8.",'Scientific Software passes total and primary counts but fails replication; all four full cells fail.','Close the same frozen replication quotas with nonreplacement disjoint-provider identities before adjudication.'),
 ('AUTHOR_LINEAGE_AND_NATURAL_PAIR','Content identity proves snapshot continuity, not independent authors, same scientific claim, one-coordinate intervention or material resolvability.','Author-lineage decisions 0; natural-pair adjudications 0; eligible natural pairs 0.','P4_NATURAL_PAIR_SOURCE_TRANSPORT_CANNOT_CHECK remains unchanged.','Commission a frozen outcome-blind external panel only after all source-cell gates pass.'),
 ('DEVELOPMENT_ONLY_PILOT_DISCLOSURE','One SWH release-route feasibility probe preceded the V6 protocol freeze and is disclosed in the protocol.','All positive rows require exact content-address equality, but this remains a development repair, not a confirmatory study.','No global transport, natural-pair, performance or superiority claim is licensed.','Run a separately frozen independent verification if the bounded bridge is to support confirmatory language.')]:
 neg.append({'identity':ident,'cause':cause,'observed':observed,'residual':residual,'next_discriminator':nxt})
negative={'schema_version':'orion.p4.m6.joss-bridge-repair.negative-ledger.v6','created_at':now(),'terminal':result['terminal'],'preserved_programme_terminal':result['preserved_programme_terminal'],'entries':neg,'unresolved_identity_count':24,'primary_mutually_exclusive_counts':dict(primary_counts),'overlapping_gate_counts':dict(overlap_counts),'by_domain':primary_by_domain,'row_level_unresolved':result['unresolved_identities']}
dump(HERE/'NEGATIVE_RESULT_LEDGER_V6.json',negative)
lines=['# P4 M6 JOSS same-identity provenance-bridge repair V6','',f"**Terminal:** `{result['terminal']}`",'',f"**Preserved programme terminal:** `{result['preserved_programme_terminal']}`",'', 'The V6 development repair re-used exactly the 41 failed members of the frozen same-200 DOI frame. It added or replaced **zero** publication identities. Exact source-native archive bytes or qualified Software Heritage directory identities were required to equal an immutable Git commit snapshot, and accepted rights were required at both the exact archive and commit.','', '## Exact result','',f"- Repaired: **17/41**; unresolved: **24/41**.",'- Final exact JOSS bridges: **56/80** (V5 39 + V6 17).','- Repair methods: **12** exact normalized source-archive/GitHub-commit manifest equalities and **5** qualified-SWHID-path/Git-tree equalities.','- Content identities bound among the 41: **20**; three still fail another exact gate.','- New/replacement DOI identities: **0**; files, tags, commits, versions and requests counted as units: **0**.','', '## Domain accounting','', '| Domain | Frozen V4 qualified | V5 exact | V6 repair | Final exact | Remaining | V3 strict | Dedup union /48 | Replication /8 | Full cell |','|---|---:|---:|---:|---:|---:|---:|---:|---:|---|']
for d in DOMAINS:
 c=cell_counts[d];lines.append(f"| {d} | {c['v4_provider_qualified_frozen']} | {c['v5_exact_pass']} | {c['v6_same_identity_repairs']} | {c['final_exact_joss_bridge']} | {c['v6_remaining_unresolved']} | {c['v3_figshare_strict']} | {c['deduplicated_v3_plus_final_exact']}/48 | {c['v3_figshare_strict']}/8 | {'PASS' if c['full_cell_frame_pass'] else 'FAIL'} |")
lines += ['', 'Scientific Software now exceeds 48 total and 24 JOSS-primary candidates, but its unchanged Figshare replication arm is **6/8**, so its full cell still fails. Earth, Life and Physical remain below 48 and 8. Surplus never transfers across domains or gates.','', '## Remaining primary cause (mutually exclusive)','']
for k,v in sorted(primary_counts.items()):lines.append(f'- `{k}`: **{v}**')
lines += ['', 'These primary counts sum to 24. Overlapping gate counts and every unresolved DOI are retained in `NEGATIVE_RESULT_LEDGER_V6.json`.','', '## Claim boundary','', '- Development transport evidence only; the disclosed pre-freeze feasibility probe forbids a confirmatory characterization.','- No global transport, provider-generality, natural-pair-readiness, author-lineage-independence, performance or superiority claim.','- Author-lineage adjudications, natural-pair adjudications and eligible natural pairs all remain **0**.','- No protected data, case labels or system outcomes were accessed.','', '## Next discriminator','',result['next_discriminator']]
(HERE/'RESULTS_V6.md').write_text('\n'.join(lines)+'\n')
ml=['# P4 M6 JOSS bridge repair V6 negative-result ledger','',f"**Terminal:** `{result['terminal']}`",'',f"**Preserved:** `{result['preserved_programme_terminal']}`",'']
for i,e in enumerate(neg,1):ml += [f"## {i}. `{e['identity']}`",'',f"**Cause.** {e['cause']}",'',f"**Observed.** {e['observed']}",'',f"**Residual.** {e['residual']}",'',f"**Next discriminator.** {e['next_discriminator']}",'']
(HERE/'NEGATIVE_RESULT_LEDGER_V6.md').write_text('\n'.join(ml))
print(json.dumps({'repaired':17,'unresolved':24,'final_exact':56,'cells':cell_counts,'primary':dict(primary_counts)},sort_keys=True))
