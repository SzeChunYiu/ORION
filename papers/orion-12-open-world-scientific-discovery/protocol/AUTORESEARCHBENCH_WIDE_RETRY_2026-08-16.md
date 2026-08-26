# AutoResearchBench Wide retry — scorer-compatible task domain

The first two host-side split attempts failed closed before candidate execution. The first exposed legacy arXiv identifier support in the pinned scorer; the second exposed released Wide tasks whose list-valued target field normalizes to an empty set. Neither failure exposed labels to the candidate or produced a score.

This retry uses `run_autoresearchbench_wide_compat.py` v3, which:

- preserves all 400 released Wide tasks;
- supports modern and legacy arXiv identifiers;
- preserves empty target sets exactly as the pinned official scorer does;
- records `legacy_target_id_count` and `empty_target_task_count` in the host split manifest;
- still passes only `{task_id, question}` into candidate custody.

The retry is triggered only after the compatibility regression suite and full repository CI passed on commit `1e5fcc366e50d6e64ee7fdeb57430ba3050c1a26`.
