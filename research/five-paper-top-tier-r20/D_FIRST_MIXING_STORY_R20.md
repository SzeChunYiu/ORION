# D R20 — local first-mixing certificates for typed authority splicing

Date: 2026-08-27

Status: analytic integration of the typed least-fixed-point calculus, minimum hybrid-splicing complexity, the first-mixing localization theorem, the RFC-grounded hostile control, and the real Agentgateway safe control.

## Typed authority model

Each evidence origin `i` owns a separate positive Horn fact coordinate. Rules are evaluated inside the declared licence/origin coordinate unless an explicit bridge authorizes a transfer. Refutations remove seeds before least-fixed-point closure. Authority is the least fixed point of the surviving typed program.

A coordinate-erased baseline pools facts from selected origins before closure. A target has a **hybrid-splicing witness** when the pooled closure derives it although no selected origin's independent typed closure does.

## Theorem D-R20.1 — first-mixing localization

For every acyclic positive derivation of a hybrid target in the coordinate-erased pooled program, there is a lowest derivation node whose descendant leaves contain facts from more than one origin. Its children are individually origin-pure, and that node is a local first-mixing certificate.

### Proof

The target derivation is mixed, while every leaf is origin-pure. Traverse downward from the root while a mixed child exists. Acyclic finiteness terminates at a mixed node with no mixed child. Every child is therefore pure, while their union contains at least two origins. The node and its child origins are the claimed certificate.

The certificate localizes the first rule application at which coordinate erasure manufactures a cross-origin proof. It does not say that every cross-origin rule application is unsafe; an explicit typed bridge may authorize the same combination.

## Theorem D-R20.2 — merge audit versus dangerous-combination search

Checking one proposed merge for a hybrid target is linear in the finite positive program and proof DAG. Finding whether some set of at most `k` independently nonauthorizing origins can manufacture the target after coordinate erasure is NP-complete, even with one licence, no refutations, one acyclic depth-one conjunctive rule, and no individually authorizing origin.

### Proof sketch

Membership uses the selected origins and a pooled Horn derivation as a certificate. For hardness, reduce SET COVER. An origin represents a selected set and contributes the covered element facts. The single target rule requires every universe element. Fresh singleton guards ensure that no one origin already authorizes the target. A pooled derivation with at most `k` origins exists exactly when the set system has a cover of size at most `k`.

Generic SET COVER and Datalog witness complexity are donor-owned. The residual is the typed-origin erasure mapping and its local first-mixing certificate.

## Real safe control

For pinned Agentgateway authorization rule sets, each origin has request-relative summaries:

- `D_i`: some deny matches;
- `R_i`: every mandatory require matches;
- `H_i`: an allowlist exists;
- `A_i`: some allow matches.

Origin acceptance is

`Accept_i = !D_i && R_i && (!H_i || A_i)`.

Concatenating rule sets gives

`Accept_merge = (all !D_i) && (all R_i) && ((all !H_i) || (some A_i))`.

Therefore a merged allow cannot launder a constituent deny or failed require, and every merged allow has at least one individually allowing origin. This same-field merge operator has no Paper-D hybrid witness of the form “merge authorizes but no origin authorizes.” MCP authorization inherits the result because it delegates to the same rule-set semantics.

This is a **safe control**, not evidence of an Agentgateway vulnerability. Cross-field authentication-to-authorization composition remains a distinct bridge subject.

## Registered finite corroboration

The first-mixing verifier covers 10,192 finite systems. It records 68 hybrid atoms and a local first-mixing certificate for all 68. Two thousand origin-preserving unary controls produce zero hybrid atoms. These numbers corroborate the implementation; the theorem is analytic.

The RFC-grounded OAuth/JWT/DPoP corpus remains a synthetic hostile erasure control: typed evaluation agrees with all 14 expected cases, while coordinate erasure falsely authorizes nine. It does not establish deployed prevalence.

## Strongest defensible story

D may claim:

> Coordinate erasure in positive authority programs has locally checkable first-mixing witnesses; auditing one submitted merge is easy, while finding a minimum dangerous collection of independently valid origins is NP-complete. A source-bound real gateway merge is certified safe, sharply delimiting the failure to integrations that actually erase the relevant origin coordinate.

D may not claim:

- a vulnerability in Agentgateway, OAuth, JWT, DPoP, MCP, Cedar, or any deployed system;
- that generic provenance or evidence binding is new;
- that positive Horn semantics fit every policy domain;
- operational safety without independently maintained cases and external adjudication;
- novelty or journal authority from same-owner source audit and finite replay.

## Remaining external gate

Freeze one independently maintained multi-record integration in which separate validated records contribute to one downstream authorization decision. Before labels are revealed, bind the record/origin/bridge semantics, typed and coordinate-erased evaluators, harmless controls, first-mixing explanations, and independent adjudicators. A safe/null result is admissible and may further narrow the paper.
