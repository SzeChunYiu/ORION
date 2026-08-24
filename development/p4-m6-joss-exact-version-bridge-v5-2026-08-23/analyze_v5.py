#!/usr/bin/env python3
"""Analyze the frozen P4 V5 exact-version bridge without outcomes or adjudication."""
from __future__ import annotations
import collections, datetime as dt, hashlib, json, pathlib
ROOT=pathlib.Path(__file__).resolve().parent
V4=ROOT.parent/'p4-m6-source-provider-successor-v4'
H={r['publication_doi']:r for r in map(json.loads,(ROOT/'HARVEST_RECORDS_V5.jsonl').open())}
G={r['publication_doi']:r for r in map(json.loads,(ROOT/'GITHUB_ARCHIVE_RELATION_RESOLUTION_V5.jsonl').open())}
V={r['publication_doi']:r for r in map(json.loads,(V4/'CANDIDATES_V4.jsonl').open())}
M={x['publication_doi']:x for x in json.loads((ROOT/'FROZEN_JOSS_IDENTITIES_V5.json').read_text())['identities']}
V3=json.loads((ROOT/'V3_M6_IDENTITY_RECOVERY_V5.json').read_text())['identities']
ZR={r['publication_doi']:r for r in map(json.loads,(ROOT/'ZENODO_SAME_IDENTITY_RESUME_V5.jsonl').open())}
DOMAINS=['EARTH_ENVIRONMENT','LIFE_BIOMEDICAL','SCIENTIFIC_SOFTWARE','PHYSICAL_ENGINEERING']
ACCEPTED={'MIT','Apache-2.0','GPL-2.0-only','GPL-2.0-or-later','GPL-3.0-only','GPL-3.0-or-later','BSD-2-Clause','BSD-3-Clause','MPL-2.0','ISC','LGPL-2.1-only','LGPL-2.1-or-later','LGPL-3.0-only','LGPL-3.0-or-later'}
ALIASES={'gpl-3.0+':'GPL-3.0-or-later','gpl-3.0':'GPL-3.0-only','gpl-2.0+':'GPL-2.0-or-later','gpl-2.0':'GPL-2.0-only','lgpl-3.0+':'LGPL-3.0-or-later','lgpl-3.0':'LGPL-3.0-only','lgpl-2.1+':'LGPL-2.1-or-later','lgpl-2.1':'LGPL-2.1-only'}
V3_PUBLICATIONS={x['publication_doi'] for x in V3}
V3_OBJECTS={x['object_doi_exact'] for x in V3}|{x['object_concept_doi'] for x in V3}

def now():return dt.datetime.now(dt.timezone.utc).isoformat()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def canon_spdx(value):
    if not isinstance(value,str) or not value.strip():return None
    raw=value.strip(); return ALIASES.get(raw.casefold(),next((x for x in ACCEPTED if x.casefold()==raw.casefold()),raw))
def archive_rights(row):
    vals=[]
    for x in (row.get('datacite',{}).get('metadata') or {}).get('rightsList') or []:
        if str(x.get('rightsIdentifierScheme') or '').casefold()!='spdx':continue
        c=canon_spdx(x.get('rightsIdentifier'))
        if c in ACCEPTED:vals.append(c)
    return sorted(set(vals))
def concept_dois(row):
    out=[]
    for x in (row.get('datacite',{}).get('metadata') or {}).get('relatedIdentifiers') or []:
        if x.get('relationType')=='IsVersionOf' and x.get('relatedIdentifierType')=='DOI':
            d=str(x.get('relatedIdentifier') or '').strip().lower()
            if d and d!=row['archive_doi']:out.append(d)
    return sorted(set(out))
def commit_rights(row):
    raw=(((row.get('license_at_commit') or {}).get('metadata') or {}).get('spdx_id'))
    c=canon_spdx(raw); return c if c in ACCEPTED else None
def native_metadata(doi):
    first=(H[doi].get('zenodo') or {}).get('metadata')
    resumed=(ZR.get(doi) or {}).get('metadata')
    return resumed or first
def native_status(doi):
    z=H[doi].get('zenodo')
    if not z:return 'CANNOT_CHECK_NON_ZENODO_SOURCE_NATIVE_ENDPOINT_NOT_FROZEN'
    a=z.get('attempts') or []; s=(a[-1].get('http_status') or 0) if a else 0
    if s//100==2:return 'PASS_FIRST_CAPTURE'
    ra=(ZR.get(doi) or {}).get('attempts') or []; rs=(ra[-1].get('http_status') or 0) if ra else 0
    if rs//100==2:return 'PASS_SAME_IDENTITY_RESUME'
    return f'CANNOT_CHECK_SOURCE_NATIVE_TRANSPORT_HTTP_{rs or s or "NONE"}'

bridge=[]
stages=collections.Counter(); failures=collections.Counter(); exact_by_domain=collections.Counter(); exact_dois=[]
for doi in sorted(H,key=lambda d:H[d]['frozen_index']):
    h=H[doi]; g=G[doi]; v=V[doi]; m=M[doi]
    concepts=concept_dois(h); ar=archive_rights(h); cr=commit_rights(g)
    vrepo=(v.get('repository') or {}).get('full_name'); jrepo=(g.get('joss_repository') or {}).get('full_name_casefolded')
    v4_repo_same=bool(vrepo and jrepo and vrepo.casefold()==jrepo)
    overlaps={
      'publication_doi':doi in V3_PUBLICATIONS,
      'archive_version_doi':h.get('archive_doi') in V3_OBJECTS,
      'archive_concept_doi':bool(set(concepts)&V3_OBJECTS),
    }
    gates={
      'v4_provider_qualified_predecessor_preserved':v.get('strict_eligible') is True,
      'joss_labelled_publication_to_archive_and_repository':h['joss'].get('archive_relation_status')=='PASS' and h['joss'].get('repository_relation_status')=='PASS',
      'datacite_exact_archive_doi_bound':(h.get('datacite',{}).get('metadata') or {}).get('doi','').casefold()==str(h.get('archive_doi') or '').casefold(),
      'exact_archive_version_to_single_distinct_concept_doi':len(concepts)==1,
      'exact_archive_spdx_rights_accepted':bool(ar),
      'archive_explicit_tag_or_commit_matches_joss_repository':g.get('selection_status')=='PASS_UNIQUE_ARCHIVE_EXPLICIT_GITHUB_IDENTITY',
      'archive_explicit_tag_or_commit_resolves_to_immutable_commit':(g.get('resolution') or {}).get('status')=='PASS',
      'accepted_spdx_license_bound_at_immutable_commit':cr is not None,
      'source_native_archive_record_transport':native_status(doi).startswith('PASS'),
      'v4_repository_identity_unchanged':v4_repo_same,
      'v4_frozen_domain_assignment_unchanged':(v.get('domain_classification') or {}).get('status')=='PASS',
      'v3_v5_publication_and_object_dedup_pass':not any(overlaps.values()),
    }
    for k,x in gates.items():stages[k]+=bool(x)
    causes=[]
    names={
      'v4_provider_qualified_predecessor_preserved':'V4_FAILED_IDENTITY_PRESERVED_NOT_REPLACED',
      'joss_labelled_publication_to_archive_and_repository':'JOSS_ARCHIVE_OR_REPOSITORY_RELATION_CANNOT_CHECK',
      'datacite_exact_archive_doi_bound':'ARCHIVE_DOI_REGISTRATION_IDENTITY_CANNOT_CHECK',
      'exact_archive_version_to_single_distinct_concept_doi':'EXACT_ARCHIVE_VERSION_CONCEPT_RELATION_CANNOT_CHECK',
      'exact_archive_spdx_rights_accepted':'EXACT_ARCHIVE_RIGHTS_CANNOT_CHECK_OR_NOT_ACCEPTED',
      'archive_explicit_tag_or_commit_matches_joss_repository':'ARCHIVE_TO_REPOSITORY_TAG_OR_COMMIT_RELATION_CANNOT_CHECK',
      'archive_explicit_tag_or_commit_resolves_to_immutable_commit':'ARCHIVE_TAG_OR_COMMIT_RESOLUTION_CANNOT_CHECK',
      'accepted_spdx_license_bound_at_immutable_commit':'EXACT_COMMIT_RIGHTS_CANNOT_CHECK_OR_NOT_ACCEPTED',
      'source_native_archive_record_transport':'SOURCE_NATIVE_ARCHIVE_TRANSPORT_CANNOT_CHECK',
      'v4_repository_identity_unchanged':'V4_TO_V5_REPOSITORY_IDENTITY_CHANGED_OR_UNBOUND',
      'v4_frozen_domain_assignment_unchanged':'V4_DOMAIN_ASSIGNMENT_CANNOT_CHECK',
      'v3_v5_publication_and_object_dedup_pass':'V3_V5_PUBLICATION_OR_OBJECT_OVERLAP',
    }
    for k,x in gates.items():
        if not x: causes.append(names[k]);failures[names[k]]+=1
    exact=all(gates.values())
    domain=(v.get('domain_classification') or {}).get('assigned_domain') if (v.get('domain_classification') or {}).get('status')=='PASS' else None
    if exact:exact_dois.append(doi);exact_by_domain[domain]+=1
    zmd=native_metadata(doi) or {}
    bridge.append({
      'frozen_index':h['frozen_index'],'publication_doi':doi,'archive_version_doi':h.get('archive_doi'),'archive_concept_dois':concepts,
      'archive_provider':(h.get('datacite',{}).get('metadata') or {}).get('publisher'),'archive_version':(h.get('datacite',{}).get('metadata') or {}).get('version'),
      'archive_spdx_rights':ar,'source_native_archive_status':native_status(doi),'source_native_archive_license':zmd.get('license'),'source_native_file_count':len(zmd.get('files') or []),
      'joss_repository':jrepo,'v4_repository':vrepo,'archive_explicit_github_identity':g.get('selected_candidate'),'immutable_commit_sha':(g.get('resolution') or {}).get('commit_sha'),
      'commit_spdx_rights':cr,'domain_discovery':domain,'v3_overlap':overlaps,'gates':gates,'failure_causes':causes,
      'exact_publication_archive_repository_commit_rights_bridge_pass':exact,
      'provider_family_axis':{'publication_provider':'JOSS','repository_provider':'GITHUB','archive_content_provider':(h.get('datacite',{}).get('metadata') or {}).get('publisher'),'datacite_counted_as_provider':False},
      'author_lineage_independence':'CANNOT_CHECK_EXTERNAL_ADJUDICATION_REQUIRED','natural_pair_eligibility':'CANNOT_CHECK_EXTERNAL_ADJUDICATION_REQUIRED',
    })
(ROOT/'BRIDGE_ROWS_V5.jsonl').write_text(''.join(json.dumps(r,sort_keys=True,separators=(',',':'))+'\n' for r in bridge))

v3_by=collections.Counter(x['domain_discovery'] for x in V3)
cells={}
for domain in DOMAINS:
    v3n=v3_by[domain]; v5n=exact_by_domain[domain]; union=v3n+v5n
    cells[domain]={
      'mechanism':'M6_ARTICLE_TO_CODE_RELEASE','v3_hash_recovered_figshare_units':v3n,'v5_exact_joss_archive_bridge_units':v5n,
      'deduplicated_v3_strict_plus_v5_exact_union':union,'gap_to_48':max(0,48-union),
      'v5_primary_24_pass':v5n>=24,'v3_source_disjoint_replication_8_pass':v3n>=8,'total_48_pass':union>=48,
      'full_source_cell_frame_pass':v5n>=24 and v3n>=8 and union>=48,
      'provider_family_note':'V5 exact bridges use JOSS publication + GitHub repository + Zenodo archive; V3 uses Figshare. Structural provider-family disjointness is separate from author-lineage and natural-pair adjudication.',
      'author_lineage_independence_adjudicated':0,'natural_pairs_adjudicated':0,
    }
cell_result={'schema_version':'orion.p4.m6.joss-exact-version-bridge.cell-counts.v5','created_at':now(),'authority':'PUBLIC_METADATA_SOURCE_FEASIBILITY_ONLY','cells':cells,'all_four_m6_cells_pass':all(x['full_source_cell_frame_pass'] for x in cells.values()),'natural_pair_count':0}
(ROOT/'CELL_COUNTS_V5.json').write_text(json.dumps(cell_result,indent=2,sort_keys=True)+'\n')

dedup={
 'schema_version':'orion.p4.m6.joss-exact-version-bridge.cross-provider-dedup.v5','created_at':now(),
 'v3_source':{'recovered_identity_count':len(V3),'publication_doi_count':len(V3_PUBLICATIONS),'object_version_or_concept_doi_count':len(V3_OBJECTS),'source_sha256':sha(ROOT/'V3_M6_IDENTITY_RECOVERY_V5.json')},
 'v5_source':{'frozen_publication_count':len(bridge),'archive_version_doi_count':len({r['archive_version_doi'] for r in bridge}),'archive_concept_doi_count':len({x for r in bridge for x in r['archive_concept_dois']})},
 'overlap':{'publication_doi_count':sum(r['v3_overlap']['publication_doi'] for r in bridge),'archive_version_doi_count':sum(r['v3_overlap']['archive_version_doi'] for r in bridge),'archive_concept_doi_count':sum(r['v3_overlap']['archive_concept_doi'] for r in bridge)},
 'dedup_gate_pass_count':sum(r['gates']['v3_v5_publication_and_object_dedup_pass'] for r in bridge),
 'omitted_payload_absence_treated_as_zero_overlap':False,'files_releases_tags_versions_or_search_hits_counted_as_units':False,
 'terminal':'P4_V3_M6_EXACT_CONCEPT_PUBLICATION_IDENTITIES_RECOVERED__V3_V5_CROSS_PROVIDER_DEDUP_COMPLETE_NO_OVERLAP_OBSERVED',
 'boundary':'Deduplication establishes no observed identity collision under frozen V3 concept/publication keys; it does not prove author-lineage independence or natural-pair eligibility.'
}
(ROOT/'V3_V5_CROSS_PROVIDER_DEDUP_AUDIT_V5.json').write_text(json.dumps(dedup,indent=2,sort_keys=True)+'\n')

provider={
 'schema_version':'orion.p4.m6.joss-exact-version-bridge.provider-lineage-audit.v5','created_at':now(),
 'provider_family':{
   'v3_content_provider_family':'FIGSHARE','v5_publication_provider':'JOSS','v5_repository_provider':'GITHUB','v5_exact_bridge_archive_provider_distribution':dict(collections.Counter(r['archive_provider'] for r in bridge if r['exact_publication_archive_repository_commit_rights_bridge_pass'])),
   'v5_exact_bridge_structurally_disjoint_from_v3_figshare_count':len(exact_dois),'datacite_counted_as_provider_family':False,
   'multiple_publications_repositories_archives_files_versions_tags_commits_create_additional_units':False,
 },
 'author_lineage':{'externally_adjudicated_independence_count':0,'noncollision_treated_as_proof':False,'status':'CANNOT_CHECK_EXTERNAL_ADJUDICATION_REQUIRED'},
 'natural_pair':{'adjudicated_count':0,'eligible_count':0,'metadata_bridge_treated_as_natural_pair':False,'status':'CANNOT_CHECK_EXTERNAL_ADJUDICATION_REQUIRED'},
 'boundary':'Provider-family disjointness is a transport-source property. It is not author-lineage independence, statistical independence, same-claim preservation, one-coordinate intervention, or natural-pair adjudication.'
}
(ROOT/'PROVIDER_FAMILY_AND_LINEAGE_AUDIT_V5.json').write_text(json.dumps(provider,indent=2,sort_keys=True)+'\n')

counts={
 'frozen_joss_publication_dois':len(bridge),'joss_labelled_archive_doi_relations':sum(r['gates']['joss_labelled_publication_to_archive_and_repository'] for r in bridge),
 'datacite_archive_doi_records_bound':sum(r['gates']['datacite_exact_archive_doi_bound'] for r in bridge),'single_distinct_archive_concept_relation':sum(r['gates']['exact_archive_version_to_single_distinct_concept_doi'] for r in bridge),
 'accepted_exact_archive_spdx_rights':sum(r['gates']['exact_archive_spdx_rights_accepted'] for r in bridge),'archive_explicit_tag_or_commit_same_repository':sum(r['gates']['archive_explicit_tag_or_commit_matches_joss_repository'] for r in bridge),
 'archive_explicit_tag_or_commit_resolved':sum(r['gates']['archive_explicit_tag_or_commit_resolves_to_immutable_commit'] for r in bridge),'accepted_spdx_rights_at_immutable_commit':sum(r['gates']['accepted_spdx_license_bound_at_immutable_commit'] for r in bridge),
 'source_native_archive_transport_bound':sum(r['gates']['source_native_archive_record_transport'] for r in bridge),'v4_repository_identity_unchanged':sum(r['gates']['v4_repository_identity_unchanged'] for r in bridge),
 'v4_unique_domain_assignments':sum(r['gates']['v4_frozen_domain_assignment_unchanged'] for r in bridge),'v3_v5_dedup_pass':sum(r['gates']['v3_v5_publication_and_object_dedup_pass'] for r in bridge),
 'v4_provider_qualified_predecessor_concepts':sum(r['gates']['v4_provider_qualified_predecessor_preserved'] for r in bridge),'exact_bridge_pass':len(exact_dois),'unique_exact_publication_doi_repository_concepts':len({(r['publication_doi'],r['joss_repository']) for r in bridge if r['exact_publication_archive_repository_commit_rights_bridge_pass']}),'exact_bridge_fail_within_v4_provider_qualified':sum(r['gates']['v4_provider_qualified_predecessor_preserved'] and not r['exact_publication_archive_repository_commit_rights_bridge_pass'] for r in bridge),
 'author_lineage_independence_adjudicated':0,'natural_pairs_adjudicated':0,'eligible_natural_pairs':0,
}
result={
 'schema_version':'orion.p4.m6.joss-exact-version-bridge.result.v5','created_at':now(),'protocol_id':'P4.PUBLIC.M6.JOSS.ARCHIVE.EXACT.VERSION.BRIDGE.DEV.V5',
 'authority':'PUBLIC_METADATA_SOURCE_FEASIBILITY_ONLY__NO_CASE_TEXT_LABELS_SYSTEM_OUTCOMES_OR_NATURAL_PAIR_DECISIONS','execution_status':'BOUNDED_FROZEN_200_DOI_BRIDGE_COMPLETE',
 'counts':counts,'exact_bridge_by_domain':dict(sorted(exact_by_domain.items())),'cells':cells,'failure_counts':dict(sorted(failures.items())),
 'v5_terminal':'P4_M6_JOSS_ARCHIVE_EXACT_VERSION_BRIDGE_PARTIAL_39_OF_80__M6_CELL_FRAME_AUTHOR_LINEAGE_AND_NATURAL_PAIR_CANNOT_CHECK',
 'preserved_terminals':['P4_NATURAL_PAIR_SOURCE_TRANSPORT_CANNOT_CHECK','P4_M6_JOSS_GITHUB_BOUNDED_TRANSPORT_COMPLETE__EXACT_PUBLICATION_RELEASE_VERSION_RELATION_AND_AUTHOR_LINEAGE_CANNOT_CHECK__M6_CELL_FRAME_NOT_READY','P4_NATURAL_PAIR_SOURCE_CELL_SHORTFALL__EXPAND_DISJOINT_SOURCE_UNIVERSE','P4_NATURALISTIC_V2_IDENTITY_COMPLETE__FEASIBILITY_AND_EXTERNAL_PANEL_CANNOT_CHECK','P4_NATURAL_PAIR_SOURCE_EXPANSION_FROZEN__ROUTES_R2_TO_R5_UNBOUND','P4_NATURAL_PAIR_METADATA_SIGNALS_COUNTED__32_CELL_ELIGIBILITY_CANNOT_CHECK','P4_ZENODO_RELATED_OBJECT_V2_SOURCE_CELL_SHORTFALL__EXPAND_DISJOINT_PROVIDER','PUBLIC_NATURALISTIC_SOURCE_AUDIT_V1','P4_ZENODO_RELATED_OBJECT_CENSUS_V1_TRANSPORT_CANNOT_CHECK_HTTP_400'],
 'predecessor_v4_negative_identities_preserved':['CROSS_PROVIDER_CONCEPT_AND_PUBLICATION_DEDUPLICATION','EXACT_PUBLICATION_TO_RELEASE_VERSION_RELATION','EARTH_LIFE_PHYSICAL_CELL_SHORTFALL','SCIENTIFIC_SOFTWARE_SOURCE_DISJOINT_REPLICATION_SHORTFALL','EXACT_RELEASE_RIGHTS','RELEASE_AND_RELATION_ABSENCE','DOMAIN_IDENTIFICATION','AUTHOR_LINEAGE_AND_NATURAL_PAIR_IDENTITY','PREDECESSOR_TRANSPORT'],
 'predecessor_v3_provider_evidence_terminals_preserved':{'DATACITE':'DISCOVERY_ONLY__NOT_INDEPENDENT_CONTENT_PROVIDER','DRYAD':'CANNOT_CHECK_ANONYMOUS_DIRECT_DOWNLOAD_AUTHORITY','FIGSHARE':'ENDPOINT_CAPABILITIES_OBSERVED__PAIR_ELIGIBILITY_ITEM_SPECIFIC','HARVARD_DATAVERSE':'ENDPOINT_CAPABILITIES_OBSERVED__STRUCTURED_PUBLICATION_DOI_REQUIRED'},
 'scientific_conclusion':'The no-extension bridge converts 39 of the 80 V4 provider-qualified JOSS/GitHub concepts into exact public publication-to-archive-version-to-repository-tag-to-immutable-commit candidates with accepted DOI-registered archive rights, accepted commit rights, source-native archive transport, unchanged domain/repository identity and verified no-overlap against the nine recovered V3 M6 identities. It does not create natural pairs. Deduplicated V3-strict plus V5-exact public-source candidate totals are Earth 5, Life 4, Scientific Software 36 and Physical 3, so every cell remains below 48 and every Figshare replication side remains below 8.',
 'claim_boundary':{'new_doi_identities_added':0,'failed_v4_identities_replaced':0,'files_versions_tags_commits_or_search_hits_counted_as_n':False,'provider_disjointness_is_author_independence':False,'eligible_natural_pairs':0,'performance_or_superiority_claim':False,'protected_or_system_outcomes_accessed':False},
 'next_discriminator':'For the same frozen 200 DOI identities, resolve only the 41 V4-qualified bridge failures through explicit source-native archive provenance or immutable Software Heritage origin/revision relations under a new pre-freeze; in parallel, a separately frozen non-GitHub domain-provider frame is still required because even all 80 V4 concepts cannot close Earth, Life or Physical and the Software Figshare side remains 6/8.',
 'artifact_hashes':{}
}
for k,p in {'bridge_rows':ROOT/'BRIDGE_ROWS_V5.jsonl','cell_counts':ROOT/'CELL_COUNTS_V5.json','cross_provider_dedup':ROOT/'V3_V5_CROSS_PROVIDER_DEDUP_AUDIT_V5.json','provider_lineage':ROOT/'PROVIDER_FAMILY_AND_LINEAGE_AUDIT_V5.json','harvest':ROOT/'HARVEST_RECORDS_V5.jsonl','github_resolution':ROOT/'GITHUB_ARCHIVE_RELATION_RESOLUTION_V5.jsonl','protocol':ROOT/'PROTOCOL_V5.json','frozen_identities':ROOT/'FROZEN_JOSS_IDENTITIES_V5.json'}.items():result['artifact_hashes'][k]=sha(p)
(ROOT/'RESULT_V5.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')

ledger_entries=[
 {'identity':'V3_M6_OMITTED_IDENTITY_PAYLOAD','cause':'The bounded integrated V3 packet omitted the 2,371-row candidate payload, so V4 could not compare nine M6 concepts across providers.','observed':'The original handoff still held the candidate JSONL under the recorded SHA-256; 9/9 exact reported M6 rows were recovered (Earth 2, Software 6, Physical 1), and all nine concept/publication pairs are unique. No V3/V5 publication, version DOI or concept DOI overlap was observed.','residual':'Recovery licenses only exact identity deduplication; V3 author-lineage and natural-pair status remain CANNOT_CHECK.','next_discriminator':'Use the recovered bounded nine-row identity packet for future source-frame dedup; never treat an omitted payload as zero overlap again.'},
 {'identity':'JOSS_ARCHIVE_TO_REPOSITORY_TAG_RELATION','cause':'An exact JOSS archive DOI does not automatically state a repository tag or commit. Only archive metadata with an explicit GitHub tree/release/commit URL was accepted.','observed':'103/200 had one archive-explicit tag/commit identity matching the JOSS repository; among the 80 V4 provider-qualified rows, 48 did.','residual':'Rows without an explicit archive-to-tag/commit relation remain CANNOT_CHECK; matching version strings or dates were not substituted.','next_discriminator':'For the same failed DOI identities only, pre-freeze a source-native archive provenance or Software Heritage origin/revision route; add no replacement papers.'},
 {'identity':'ARCHIVE_TAG_TO_IMMUTABLE_COMMIT','cause':'Two archive-explicit tag candidates returned GitHub ref HTTP 404; one lies inside the V4-qualified frame.','observed':'101/103 selected identities resolved to 40-hex commits; 47/48 selected V4-qualified identities resolved.','residual':'A named but unresolved tag is not an immutable version relation and contributes zero bridge candidates.','next_discriminator':'Resolve the same tag identity through source-native release metadata or an immutable Software Heritage revision, preserving the HTTP-404 evidence.'},
 {'identity':'ARCHIVE_VERSION_CONCEPT_IDENTITY','cause':'Some DOI registrations omit, self-reference or ambiguously encode the distinct concept DOI for the archived version.','observed':'165/200 expose exactly one distinct DOI IsVersionOf relation; 68/80 V4-qualified rows pass this gate.','residual':'A labelled archive DOI without a distinct version-to-concept relation remains insufficient for cross-version concept control.','next_discriminator':'Query only the same archive identity at its source-native version endpoint under a new freeze; do not infer concept identity from DOI prefix or filename.'},
 {'identity':'EXACT_ARCHIVE_AND_COMMIT_RIGHTS','cause':'Generic copyright, missing rights, nonaccepted licences and NOASSERTION are not hand-mapped to accepted software rights.','observed':'179/200 have at least one accepted DOI-registered SPDX licence; 83/101 resolved commits have an accepted SPDX licence after syntax-only canonicalization. All 39 exact bridge passes satisfy both gates.','residual':'Failed rights rows contribute zero exact bridge candidates; one exact candidate has no Zenodo-native licence field but has matching exact DataCite BSD-3-Clause registration and commit licence.','next_discriminator':'For failed identities, bind exact source-native version rights plus immutable-commit rights; do not infer from the default branch or repository description.'},
 {'identity':'V4_FAILED_IDENTITIES_NOT_REPLACED','cause':'Nine V4 JOSS relation failures and later repository changes cannot be converted into new V4 units by re-reading mutable pages.','observed':'V5 retains all 200 DOI identities but requires the V4 provider-qualified predecessor and unchanged V4 repository/domain identity; exactly 39/80 pass the complete bridge and no V4-failed identity is promoted.','residual':'41 V4-qualified rows remain exact-version bridge failures; the other 120 remain under their original V4 failures.','next_discriminator':'Repair only under same-identity frozen provenance routes; never replace a failed DOI with a new page or count a changed repository as continuity.'},
 {'identity':'M6_EXACT_CELL_FRAME_SHORTFALL','cause':'Exact version bridging reduces the V4 80 provider-qualified concepts to 39, while V3 contributes only nine predecessor-strict Figshare metadata concepts.','observed':'Deduplicated V3-strict plus V5-exact public-source candidate totals are Earth 5/48, Life 4/48, Software 36/48 and Physical 3/48. V3 disjoint replication counts are 2/8, 0/8, 6/8 and 1/8.','residual':'No M6 domain passes total, primary and source-disjoint replication gates; surplus in Software or another cell cannot compensate.','next_discriminator':'After same-identity bridge repair, freeze non-GitHub domain-specific publication-linked release providers; Software still needs at least two additional disjoint-provider concepts even if its V4 bridge expands.'},
 {'identity':'PROVIDER_FAMILY_VS_AUTHOR_LINEAGE','cause':'Different repositories/archive hosts establish a transport-source distinction, not independent authors, independent scientific claims or independent statistical units.','observed':'All 39 exact bridges use JOSS+GitHub+Zenodo and are structurally provider-family disjoint from the nine V3 Figshare identities; externally adjudicated author-lineage independence remains 0.','residual':'Provider-family disjointness cannot license lineage independence, same-claim preservation or natural-pair eligibility.','next_discriminator':'Freeze an outcome-blind external lineage and natural-pair adjudication packet before any case label or system outcome.'},
 {'identity':'NATURAL_PAIR_ADJUDICATION','cause':'Public metadata does not adjudicate same target claim, one-coordinate information-state change, material resolvability or outcome protection.','observed':'0 author-lineage decisions, 0 natural-pair adjudications and 0 eligible natural pairs.','residual':'All 39 exact bridges remain transport candidates only. P4_NATURAL_PAIR_SOURCE_TRANSPORT_CANNOT_CHECK is preserved.','next_discriminator':'Commission the frozen outcome-blind external panel only after the source cells pass identity, relation, rights, dedup, lineage and quota gates.'},
 {'identity':'SOURCE_NATIVE_ARCHIVE_TRANSPORT','cause':'The first Zenodo wave hit HTTP 429 for 46 identities and HTTP 410 for one.','observed':'A same-identity sequential resume recovered all 46 rate-limited records; DOI 10.5281/zenodo.20816805 remains HTTP 410. Original failures are retained, and no DOI was added or replaced.','residual':'The one withdrawn/gone source-native archive remains CANNOT_CHECK and is not among the 39 exact bridge passes.','next_discriminator':'Preserve the 410 and use only an immutable source-native tombstone or Software Heritage identity for that same DOI under a new freeze.'},
]
ledger={'schema_version':'orion.p4.m6.joss-exact-version-bridge.negative-result-ledger.v5','created_at':now(),'preserved_programme_terminal':'P4_NATURAL_PAIR_SOURCE_TRANSPORT_CANNOT_CHECK','entries':ledger_entries}
(ROOT/'NEGATIVE_RESULT_LEDGER_V5.json').write_text(json.dumps(ledger,indent=2,sort_keys=True)+'\n')
md=['# P4 JOSS exact-version bridge V5 negative-result ledger','',f'**Preserved programme terminal:** `P4_NATURAL_PAIR_SOURCE_TRANSPORT_CANNOT_CHECK`','', 'Every failure retains cause, observed result, residual and next discriminator. No null, CANNOT_CHECK or failed V4 identity is overwritten.','']
for i,e in enumerate(ledger_entries,1):
    md += [f"## {i}. `{e['identity']}`",'',f"**Cause.** {e['cause']}",'',f"**Observed.** {e['observed']}",'',f"**Residual.** {e['residual']}",'',f"**Next discriminator.** {e['next_discriminator']}",'']
(ROOT/'NEGATIVE_RESULT_LEDGER_V5.md').write_text('\n'.join(md)+'\n')
report=[
 '# P4 JOSS exact-version bridge V5 result','',
 '**V5 terminal:** `P4_M6_JOSS_ARCHIVE_EXACT_VERSION_BRIDGE_PARTIAL_39_OF_80__M6_CELL_FRAME_AUTHOR_LINEAGE_AND_NATURAL_PAIR_CANNOT_CHECK`','',
 '**Preserved programme terminal:** `P4_NATURAL_PAIR_SOURCE_TRANSPORT_CANNOT_CHECK`','',
 'The no-extension bridge retained exactly the same 200 V4 JOSS publication DOIs. All 200 pages exposed one labelled Software archive DOI and one labelled repository relation, and all 200 archive DOI registrations transported. Public DOI metadata exposed 103 unique archive-explicit tag/commit identities for the same JOSS repository; 101 resolved to immutable Git commits. After requiring the original V4 provider-qualified identity, unchanged repository/domain identity, a distinct archive version/concept relation, accepted exact archive and commit rights, source-native archive transport, and hash-recovered V3 dedup, **39/80** V4 concepts pass the exact publication-to-archive-to-tag-to-commit bridge: Earth 3, Life 4, Scientific Software 30, Physical 2.','',
 'These 39 are exact public transport candidates, not natural pairs. Author-lineage independence and natural-pair adjudication remain 0. No file, release, tag, commit, version, search hit or API response becomes an additional unit.','',
 '## Deduplicated V3-strict plus V5-exact M6 cells','',
 '| Domain | V3 Figshare strict metadata identities | V5 exact bridge | Deduplicated candidate total / 48 | V3 disjoint replication / 8 | Cell gate |','|---|---:|---:|---:|---:|---|'
]
for d in DOMAINS:
    c=cells[d]; report.append(f"| {d} | {c['v3_hash_recovered_figshare_units']} | {c['v5_exact_joss_archive_bridge_units']} | {c['deduplicated_v3_strict_plus_v5_exact_union']}/48 | {c['v3_hash_recovered_figshare_units']}/8 | FAIL |")
report += ['', 'All four cells fail. Scientific Software has a V5 primary-sized arm (30), but its exact total is 36/48 and the Figshare replication arm is 6/8. Earth, Life and Physical remain far below quota. Provider-family disjointness is reported separately from author-lineage independence and never substitutes for it.','', '## Transport and preservation','', 'The original 46 Zenodo HTTP-429 results and one HTTP-410 result remain recorded. A same-identity sequential resume recovered all 46 rate-limited records; the 410 remains unresolved and contributes zero. The exact V3 M6 identity recovery verified the original candidate JSONL SHA-256 and recovered 9/9 concept/publication pairs; cross-provider overlap is zero on the frozen publication/version/concept DOI keys. No omitted payload was treated as zero overlap.','', 'No case text, case label, system output, protected result, performance measurement or superiority result was accessed.']
(ROOT/'RESULTS_V5.md').write_text('\n'.join(report)+'\n')
print(json.dumps({'exact_bridge_pass':len(exact_dois),'by_domain':dict(exact_by_domain),'cells':{d:cells[d]['deduplicated_v3_strict_plus_v5_exact_union'] for d in DOMAINS},'eligible_natural_pairs':0},indent=2,sort_keys=True))
