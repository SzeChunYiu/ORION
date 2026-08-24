# Manuscript-ready bounded update: P3 public OAEI development

## Result paragraph

We evaluated a conflict-preserving alignment wrapper on the public OAEI 2004 bibliographic benchmark using AgreementMakerLight v3.2 as a source-native comparator. A first pre-reference identity was invalidated before gold access because fragment-only matching was non-injective (2,153 ambiguous keys) and one AML-emitted class pair lay outside the explicit-declaration signature. In a distinct repaired identity, we froze 68,187 cases and 477,309 predictions before opening public reference alignments. AML executed 19 of 20 ontology pairs, with byte-identical replay for every successful output; test 206 remained unparsable.

After the freeze, the repaired identity still failed two mandatory gates. Candidate-universe recall was 0.930962, not 1.0, and the wrapper's gold-in-envelope coverage was 0.995542, not 1.0. Although candidate-minus-AML mean floor-adjusted harm was negative in all three preregistered regimes (-0.005430, -0.005723, -0.039043), the candidate had 304 envelope failures and therefore did not establish a valid positive result. The exact terminal is `PUBLIC_CANDIDATE_UNIVERSE_INVALID`.

## Scientific interpretation

The failure localizes two substantive problems. First, a referent-only claim cannot be evaluated through a same-construct candidate universe when public alignments cross ontology construct types. Second, AML and exact-label agreement is not sufficient to license a point action: 285 double-negative agreements missed a public equivalence and 19 double-positive agreements asserted equivalence on a public obstruction. Thus conflict preservation must represent shared evidence failure and representation perturbation, not merely disagreement between two channels.

## Required limitation

OAEI 2004 is one systematic bibliographic seed family and the reference is public development evidence. No confidence interval, p-value, cross-domain superiority, protected confirmation, PLURAL claim, temporal claim, or frozen-768-cluster conclusion is authorized. Protected and frozen-768 authority remains `CANNOT_CHECK`.
