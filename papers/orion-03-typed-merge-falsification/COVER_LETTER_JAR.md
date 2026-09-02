# Cover letter — Journal of Automated Reasoning

**Prepared:** 2026-09-02 (supersedes the packaged `submission/tier-b-final-20260901/journal/COVER_LETTER.md`; replace that copy at rebuild)

Dear Editors,

Please consider "Typed Evidence Licenses for Fail-Closed Nonpromotion in Finite Rule
Systems" by Sze Chun Yiu for the Journal of Automated Reasoning as an original research
article.

The manuscript contributes a formal license-propagation system: a finite positive
conjunctive rule system in which an evidence license crosses a rule only when every
premise carries it and the rule's explicit cap permits it, and directly refuted claims
are fixed to the empty label. The properties are proved rather than simulated — a finite
least fixed point reached by synchronous monotone iteration, an equivalent typed
proof-tree semantics, monotone loss of licenses under additional refutations, and exact
retraction of the claim-license pairs whose typed proof trees no longer survive. The
decidable transfer rule makes nonpromotion an invariant of propagation: a conclusion
needing mixed-origin or mixed-class support never acquires the license, rather than
being filtered out after evaluation. A deterministic evaluator, a validation schema, and
regression tests make the semantics executable, and three bounded scientific-record case
encodings separate Boolean reachability from licensed use.

The empirical part is deliberately one measured phenomenon. In a separately frozen
OpenSSL 3.6.4 instantiation, flat trust-store union produced 46 hybrid authorizations
among 1,962 third-party merge tasks that neither parent store authorized; alternative
merge policies pay different measured costs, and retaining origin witnesses costs
exactly two parent evaluations per task. Outcome definitions and gates were registered
before evaluation, including a 95% upstream anchoring gate passed at 97.38% with five
FIPS-provider disagreements retained rather than excluded. The origin-witness policy's
zero errors are analytic identities and the manuscript presents them as such; the Cedar
domain-transfer attempt that could not adjudicate the intended residual is retained as a
null result. No general provenance theory, security evaluation, or usability claim is
made.

One boundary is stated openly in the Limitations: the relationship to annotated-logic,
provenance-semiring, and assumption-based truth-maintenance neighbours is declared as a
donor relationship, not demonstrated as a formal expressiveness separation; whether a
separation exists at the level of propagation-time enforcement or per-decision cost
remains open.

The fit to the Journal is direct: the paper is an automated-reasoning contribution whose
nearest neighbours are truth maintenance (Doyle; de Kleer), generalized annotated logic
(Kifer and Subrahmanian), semiring provenance and its recursive-Datalog extensions
(Green et al.; Bourgaux et al.; Abo Khamis et al.), and minimal-support causality and
deletion robustness in recursive Datalog (Thapa and Staab). The stated deltas to each
family are precise, and the executable evaluator plus the frozen third-party
instantiation are supplied as review materials with checksums. The work is original, is
not under consideration elsewhere, and the author will confirm both facts again in the
live portal immediately before filing.

Sincerely,

Sze Chun Yiu
Stockholm University
sze-chun.yiu@fysik.su.se
