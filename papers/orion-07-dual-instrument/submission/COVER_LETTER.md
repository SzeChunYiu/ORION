# Cover letter — ORION-07

To the Editors, Transactions on Machine Learning Research

**Manuscript:** Controller--Host Agreement on Live Research Decisions: A
Receipted Benchmark and a First Three-Question Series

Dear Editors,

We submit the manuscript above for consideration in TMLR.

Most research-agent benchmarks score a decision against a known answer or an
environment reward. Live research decisions do not come with either. When an
agent proposes the next move on a question nobody has answered yet, there is no
gold label to score it against at the time the decision is made. This paper
defines a benchmark for that setting and reports its first series of
measurements.

The construction is deliberately simple. Two architecturally distinct
instruments receive the same frozen evidence packet and the same open frontier
question. One is an LLM-driven research lane whose external interactions are
bound to immutable capability receipts. The other is a typed controller with no
LLM anywhere in its decision path, whose choices are constrained by explicit
obligations. We score whether they diagnose the same responsible layer, choose
compatible next moves, and draw on overlapping admissible evidence. Scoring
against the eventual research outcome is deferred, not contemporaneous.

We think the most useful result is a negative one, and we would ask reviewers
to weigh it accordingly. Across three prospectively frozen questions, the two
instruments agreed with each other every time. In the third, they were both
wrong: they converged on the same diagnosis of the responsible layer, and the
frontier result that arrived later identified a different one. The agreement
was real, was recorded before any outcome was available, and carried no
information about correctness.

That single case is the paper's main contribution to how such benchmarks should
be read. Cross-instrument agreement is routinely treated as a proxy for
validity when ground truth is unavailable. Here is a receipted instance where
it is not, produced under a protocol that froze the question, the packet, and
the scoring branch before either instrument ran.

We are explicit about what three questions cannot support. We report no
agreement rate, no confidence interval, no calibration measure, and no
predictive-validity statistic. The instance records withhold aggregate
reliability authority by construction, and the two candidate questions
withdrawn for outcome contamination are retained visibly in the series audit
rather than dropped. Two harness defects documented in an earlier draft have
since been repaired and regression-tested; they are reported as accepted
fail-closed limitations rather than as repaired-away.

We believe TMLR is the right venue because the contribution is a measurement
contract and an honest small series, judged on correctness and clarity rather
than on a performance claim. Every scored instance resolves to committed
artifacts with byte-identical independent replay, as described in the Data and
Code Availability statement.

The manuscript is original and is not under consideration elsewhere.

Thank you for your consideration.

Sincerely,

*[Author names, affiliations, and corresponding-author contact to be supplied
at filing.]*
