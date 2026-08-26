# Typed Authority R9 Addendum: RFC-Grounded OAuth Token-Splicing Corpus

## Purpose

The formal merge theorem is only useful if erased provenance can create a recognizable authorization error. This addendum instantiates the typed calculus on a deliberately small OAuth evidence-integration problem derived from RFC 8707, RFC 9068, RFC 9449, and RFC 9700.

The benchmark is **not** a claim that compliant OAuth resource servers normally merge arbitrary claims from multiple access tokens. It models an authorization or provenance graph that ingests facts emitted by several token validators and then loses the content-bound token/request coordinate before applying a downstream authorization rule. That erased-coordinate baseline is precisely the graph-merge failure mode studied in the paper.

## Frozen authorization query

The query is whether Alice may perform an `admin` action at resource server RS1.

The bearer rule requires one validated JWT access-token context carrying:

- access-token type;
- valid signature;
- expected issuer;
- unexpired status;
- RS1 audience;
- Alice subject; and
- admin scope.

The DPoP variant additionally requires, on the same token/request coordinate:

- a DPoP-bound access token;
- a valid DPoP proof signature;
- proof-key/token-key agreement;
- `ath` agreement with the presented access token;
- HTTP method agreement; and
- target-URI agreement.

The coordinate is a content-bound tuple containing the token identifier and the issuer, subject, audience, and, where applicable, proof key and request binding. Complementary validator records may compose when the coordinate is identical. They fail closed when no alignment is available.

## Standards basis

RFC 9068 requires resource servers to validate access-token type, issuer, audience, signature, and expiration, and states that scope strings must have meaning for the resources in the token audience. RFC 8707 and RFC 9700 reinforce audience and resource/action restriction. RFC 9449 requires a DPoP resource server to check that the proof key matches the token binding, that `ath` matches the presented token, and that the proof matches the request.

The source registry records the exact sections used by each benchmark fact. The expected decisions are an executable policy fixture derived from those requirements, not an independent IETF adjudication.

## Typed and untyped evaluators

Both evaluators run the same acyclic positive Horn rules.

The typed evaluator computes a closure independently for every content-bound token/request coordinate. A conjunctive rule fires only when all premises survive under one coordinate.

The untyped baseline projects the coordinates away, unions every surviving fact, and then runs the same rules. It can therefore combine a trusted issuer from one token, an audience from another, a subject from a third, or a DPoP check from a different request.

A second direct Boolean evaluator independently checks every Horn decision, preventing the result from depending on the worklist implementation alone.

## Registered corpus

The corpus contains fourteen cases:

- clean bearer and DPoP authorizations;
- a legitimate same-token multi-validator merge;
- a declared multi-audience token;
- a read-only denial;
- audience/scope, subject/scope, and issuer/scope splices;
- expiration and direct-refutation laundering;
- DPoP key, access-token-hash, and target-URI splices; and
- an unaligned-fragment case that must fail closed.

The typed evaluator agrees with all fourteen frozen decisions with zero false positives and zero false negatives. The coordinate-erased baseline agrees on five and produces nine false-positive authorizations. In particular, it authorizes every registered audience, subject, issuer, expiry, retraction, and DPoP splicing case.

## Interpretation

The result supplies an operational witness for the paper's central distinction: reachability after graph union is not the same as authority carried by one valid proof context. It also demonstrates that origin sensitivity need not block legitimate distributed validation: records for the same content-bound token coordinate compose successfully.

The benchmark does not measure deployed OAuth products, attack prevalence, latency, or legal compliance. It does not replace a review by OAuth/security practitioners. Its value is to move Paper D from a generic synthetic graph to a standards-grounded hostile corpus with a falsifiable baseline and explicit source ownership.

## Independent review gate

A journal-grade validation requires a second encoding team to:

1. derive the policy facts directly from the registered RFC sections without seeing the expected decisions;
2. implement the baseline and typed evaluator independently;
3. adjudicate whether each case is a faithful token/request-binding scenario;
4. add null and counterexample cases where coordinate erasure is harmless;
5. test at least one real gateway, authorization-graph, or provenance integration path; and
6. preserve disagreement, semantic-model rejection, and no-baseline-error terminals.

A positive external result may support a security or authorization-systems claim. Until then, the artifact is an RFC-grounded formal case study, not evidence of real-world prevalence.
