# SAGE: struck for the official metric, not struck as a task set
The official-scorer verdict above is correct and unchanged: SAGE's 200k retrieval corpus and its
evaluator are genuinely unpublished, and no budget fixes that. What did not follow, and what an
earlier reading of this note took from it, is that the family leaves the paper.

The queries and their gold *are* obtainable at the pinned commit, and were parsed rather than read
off the README: 600 short-form records (`paper_id`, `paper_title`, `complete_query`,
`ground_truth{paperId,title}`) and 600 open-ended records (`question`, `generation_plan`,
`source_paper_id`, `cited_paper_id`, `ground_truth{most_relevant,relevant}`), four files each.

Three consequences, recorded in `usable_task_family_under_declared_deviation` in the audit JSON:

- **Short-form is N=600.** That clears the frozen plan's TIER_B (N ≥ 385) and is larger than the
  400 released AutoResearchBench Wide tasks, making it the biggest external task set this paper has.
- **Every SAGE number is a declared deviation.** Short-form exact match needs a host-declared title
  normalisation; open-ended weighted recall needs weights the README never states. Neither may be
  labelled official.
- **Contamination is unchanged and binding.** Gold is public plaintext in the same record as the
  query, so exposure must be measured, not assumed away.

Redistribution also stays blocked — no licence at the pinned revision, so counts and hashes may be
recorded but the data may not be vendored.

One correction of a correction, on the record because it was made publicly: an orchestrator note
claimed this audit had mis-enumerated the repository as "777 KB, 11 entries". That was wrong. 777 KB
is GitHub's repository-size field and the eleven tree entries are the README, eight query files and
two directories — which this audit had enumerated correctly. The gap was the missing usability
verdict, not a bad inventory.
