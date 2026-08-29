# ArXiv-first author-input gate — release-first ORION papers

Applies first to **ORION-06, 07, 08, 10, 12, 14, 16**. These facts are human-controlled filing metadata, not scientific evidence, and automation must not infer them from Git history or account identity.

## Supply once where shared

- final author list and order;
- affiliations and correspondence details;
- ORCIDs if desired;
- funding statement (or explicit author-approved no-funding statement, if true);
- competing-interest statement;
- author-approved description of generative-AI assistance;
- confirmation that all authors approve public arXiv release and subsequent journal submission;
- any patent/IP timing instruction that should delay public disclosure.

## ArXiv choices per paper

Confirm the primary/cross-list category and license at upload time. Recommended starting categories, subject to the final manuscript:

- ORION-06: `cs.AI`; optional `quant-ph` cross-list only if the quantum case remains scientifically central.
- ORION-07: `cs.AI` (or `cs.LG` if the final framing is primarily evaluation of learning/research agents).
- ORION-08: `cs.AI` / `cs.LG` according to final framing.
- ORION-10: `quant-ph` (also required by the planned Quantum journal route).
- ORION-12: `cs.IR`.
- ORION-14: `cs.AI` / `cs.LG` according to final framing.
- ORION-16: `cs.AI`.

Do not invent an arXiv identifier before upload succeeds. After arXiv deposition, insert the exact identifier/version into the journal-facing availability/front-matter where the target requests it.

## Journal-only filing metadata

- TMLR (07/08/14): maintain anonymous review PDF even if the arXiv version is named; complete OpenReview author profiles/COI/funding metadata separately.
- Quantum (10): final author-contribution statement and author-approved generative-AI disclosure; provide the arXiv `quant-ph` reference.
- Elsevier AIJ/IP&M (06/12/16): final author metadata, declarations, funding/COI, data/code availability and originality/concurrent-submission confirmation under the current journal Guide for Authors.

When the source/PDF checks are green and the fields above are supplied, the only remaining action is the external upload/submission itself.