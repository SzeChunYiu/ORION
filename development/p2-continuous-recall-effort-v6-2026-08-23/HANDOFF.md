# P2 KIFMS continuous recall--effort V6 handoff

Terminal:

`P2_KIFMS_V6_LAWFUL_EXACT_SOURCE_AND_LABEL_BLIND_DISJOINT_POPULATION_FROZEN__INDEPENDENT_PROTECTED_EXECUTION_CANNOT_CHECK`

- New source: OSF `vt3n4`, 14 Dutch medical-guideline review decisions,
  revision-one files, CC-BY-4.0.
- Population: 5,074 raw rows; 4,934 canonical rows after outcome-blind
  exclusions; zero final SWIFT/V5 content overlap. KIFMS PMID values are all
  empty, so PMID overlap is vacuous rather than corroborative.
- Adverse preflight findings retained: one raw V5 content match; 65 cross-review
  KIFMS content identities affecting 132 rows.
- New coprimary: normalized recall--effort area `CRE20` over effort `[0,0.20]`.
- Retained coprimary: R@10 with threshold/sign rule unchanged.
- Active u4 and every V5 harm/work-saving gate remain unchanged.
- No label values, class counts, seeds, rankings or comparative outcomes opened.
- Historical public ASReview simulation artifact paths exist for the family;
  their metric contents were not inspected. Do not call the family globally
  unstudied or historically outcome-sealed.
- Lawful exact source-body interface found; confirmatory execution is **not**
  ready until independent custody, label semantics/classes and a signed runner
  are bound.

Integrators should use `SOURCE_FEASIBILITY_RESULT_V6.json` for exact counts and
`PROTOCOL_FREEZE_V6.json` for the gate definitions.  Do not describe this as a
performance result or as independent custody.
