30 August 2026

Editor-in-Chief
Information Processing & Management

Dear Editor,

I submit "The Acquisition--Authority Envelope for Open-World Scientific
Discovery" for consideration as a full research article.

## What the paper contributes

Open-world scientific discovery couples acquisition, screening and closure, but
these stages are almost always evaluated in isolation. A retriever can dominate
an older acquisition layer without answering the question that matters: did the
assembled controller find the decision-relevant evidence, keep useful future
routes alive, and close the task safely?

The paper defines an acquisition--authority envelope that compares controllers
under matched access, budget and authority contracts, and proves three results
within it: an acquisition ceiling, a closure factorization, and a donor
saturation bound. The framework's practical purpose is diagnostic. It states
when new state or new acquisition is *necessary* for a controller to carry
scientific-closure authority, and it separates route stopping from task closure
so that unresolved routes remain open obligations rather than silent
completions. Archived experiments preserve heterogeneous authority levels
instead of averaging them away.

## What the evidence does and does not support

I would rather state the boundaries here than have them discovered in review.

The controlled index covering 390 tasks (1,210 documents, 78 topics, 14
systems, 3 repeats) is **descriptive only**. Its analysis tier is
TIER_B_committed at an achieved half-width of 0.0496, and it is recorded as
underpowered. It is not offered as evidence of superiority.

The registered external comparison is adverse and is reported as such. On
TREC-COVID, recall@100 for the controller arm sits 0.0177 below the strongest
comparator with a paired bootstrap interval of [-0.0273, -0.0091]; the point
estimate falls inside the -0.02 noninferiority margin but the interval's lower
bound does not, and noninferiority is a claim about the interval. Cost fails
outright rather than marginally, at 2.8x the reads where the gate required at
least 25% fewer. One measured result runs the other way -- nDCG@10 is +0.1488
with a bootstrap interval of [+0.1010, +0.1995], ahead on 42 of 50 topics -- but
that criterion is outside the registered gate and **does not rescue it**. The
external superiority verdict therefore remains unestablished on the strength of
a comparison that was actually run. The corpus used is BEIR's 171,332-document
trec-covid derivative rather than the 191,175-docid official round-5 release.

The internal campaign record is likewise negative in places, and the manuscript
reports it directly. In V7, six locked gates fail and the full candidate loses
to its frozen u4 donor. V8 admits no residual. V10 fails four gates. V13
validates a provider-native fibre-separating coordinate, but only 4 of 7
reviews support it. V15 binds a signed coherent snapshot containing 61 dataset
blobs, without index parsing, census or performance; its template error was
never executed, and V15B corrects it only for a successor. Independent custody
remains 0 of 3.

The paper's own conclusion is that the framework identifies when new state or
acquisition is necessary, while **open-world benefit remains unconfirmed**. I do
not claim external retrieval superiority or open-world completeness, and I would
ask that the paper be assessed as a methods and critical-system-design
contribution with retained external falsification, rather than as a performance
result.

## Fit to IP&M

The control problem sits between information retrieval and information science:
what a system may legitimately infer about task completeness from local
acquisition outcomes. I believe the combination of explicit authority semantics,
controlled mechanism evidence, and a preserved failed registered gate is
relevant to IP&M readers working on retrieval, scientific-discovery systems,
evidence synthesis and systematic review automation.

The manuscript is not under consideration elsewhere and has not been published
previously.

## Declarations

Generative AI tools were used for drafting and editing assistance. The author is
responsible for all scientific content.

The author declares no competing interests.

No funding was received for this work.

Sincerely,

Sze Chun Yiu
Department of Physics, Stockholm University, Stockholm, Sweden
sze-chun.yiu@fysik.su.se
