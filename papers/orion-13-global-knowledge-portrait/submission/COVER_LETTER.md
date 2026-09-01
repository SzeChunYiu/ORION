# Cover letter — ORION-13

To the Editors, Semantic Web Journal

**Manuscript:** Scientific Identity Authority for Recoverable Cross-Domain Knowledge Integration
**Article type:** Full paper

Dear Editors,

We submit the manuscript above for consideration in the Semantic Web Journal.

The paper studies whether a structured, provider-native representation carries
information that a text-derived representation does not, and whether that extra
information translates into benefit. We treat those as two separate questions,
because our results say yes to the first and no to the second.

The mapping result is positive and exact. The full binary identification
envelope reaches gold-in-envelope coverage of 1.0 and ties its
information-equivalent ideal exactly. We then report, in the same section, that
coverage reaching its ceiling did not imply benefit, and that against the
matched comparator the outcome was no harm superiority, with the candidate-minus
comparator harm positive in every frozen regime. Both results are in the
abstract.

We would highlight three things a reviewer may want to test directly.

First, the claim is scoped on purpose. Our scoped publication track holds two
claim identifiers explicitly as not claimed, and the limitations state that the
broad study has not been executed. We are not submitting a general
knowledge-graph result and the manuscript does not read as one.

Second, the repair line is auditable rather than described. The baseline
ontology matcher required a source repair to run at all. Rather than
characterising that patch in prose, we pin the upstream commits, the unrepaired
source, the patch, the repaired source, and the decoded artifact by digest, so
that a reviewer can confirm the patch changes exactly one attribute access and
nothing else. That chain is in the availability section.

Third, the failures are reported at their own authority. Where a parser could
not establish the native artifact contract, we record the outcome as
undetermined and report it separately from an outcome determined to be false. We
do not convert an unexecutable run into a null.

The manuscript is compiled and checked by a dedicated repository CI job that
refuses unresolved or duplicate references and audits the headline sections
against a list of claims that must not reappear. That job is part of what we are
offering reviewers, not a private convenience.

The manuscript is original and is not under consideration elsewhere.

Thank you for your consideration.

Sincerely,

*[Author names, affiliations, and corresponding-author contact to be supplied
at filing.]*
