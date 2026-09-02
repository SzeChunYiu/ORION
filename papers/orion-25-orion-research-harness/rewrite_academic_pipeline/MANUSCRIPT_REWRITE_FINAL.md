# Effective Trust-Domain Diversity in Chained Scientific Attestation

## Abstract

A chained attestation system can name several trust domains while remaining no stronger than a one-domain system if every decisive role is held in the same place. We give an exact law for forgeability in a three-role scientific-attestation harness. Let \(\alpha\) assign the registered roles to trust domains, let \(\operatorname{supp}(\alpha)\) be the domains that actually hold at least one role, and let \(C\) be the set of compromised domains. A forged chain is possible exactly when

\[
\operatorname{supp}(\alpha)\subseteq C.
\]

The effective security parameter is therefore \(d_{\mathrm{eff}}=|\operatorname{supp}(\alpha)|\), not the provisioned domain count, attestation-chain length, or role labels. We prospectively freeze the theorem and exhaustively evaluate every assignment of the three roles to \(d\in\{1,2,3\}\) cryptographically independent domains, crossed with every compromise set, using real signed receipts. All 1,000 cells match the theorem: zero sufficiency failures and zero necessity failures. Every predicted forgery succeeds (260/260), honest chains verify in 1,000/1,000 cells, and no-compromise cells resist forgery in 144/144 cases. Five collapsing assignments have \(d>1\) but \(d_{\mathrm{eff}}=1\); one compromise forges every one of them.

The result establishes effective trust-domain diversity under independent key material. It does not establish organizational independence: every key remains under the same research programme's custody. The broader resilience claim is therefore withheld even on the favourable outcome. The contribution is a bounded exact law and a deployment warning—adding domains buys no security unless decisive roles are actually spread across independently compromisable roots.

## 1. Introduction

Research systems increasingly attach receipts to data acquisition, computation, verification, and claim promotion. Chaining those receipts can make tampering visible, but the security of the chain depends on where signing authority is located. A diagram may contain several services, agents, or key stores while all decisive roles remain controlled by one trust root. Counting named components then exaggerates independence.

This paper asks a precise question: for a fixed three-role attestation protocol, which combinations of role placement and domain compromise permit an attacker to produce a chain accepted by the verifier?

The answer is simpler than several plausible alternatives. Chain length does not determine resistance. The number of provisioned domains does not determine resistance. The identity of the role placed in a domain does not determine resistance. What matters is whether every domain that actually carries a required role has been compromised.

The resulting theorem clarifies two levels of evidence. Cryptographically independent keys can make one domain unable to derive another's signature. They do not create independent organizational custody when the same programme controls all keys. The experiment proves the former law and explicitly stops before the latter claim.

## 2. Attestation model

The harness contains three registered attestation roles. The exact role names are implementation-specific; scientifically, each contributes one required signed statement to the accepted chain. A placement map

\[
\alpha:R\rightarrow D
\]

assigns each role in the role set \(R\) to a trust domain in \(D\).

The support of the placement is

\[
\operatorname{supp}(\alpha)=\{d\in D:\exists r\in R,\ \alpha(r)=d\}.
\]

Only domains in this support affect the accepted chain. Provisioned but unused domains cannot improve resistance.

A compromise set \(C\subseteq D\) gives the attacker every private key and signing capability in those domains, while uncompromised-domain secrets remain cryptographically independent and unavailable. The verifier accepts only a chain carrying valid signatures for all registered roles and consistent content bindings.

## 3. Forgeability theorem

**Theorem 1 (effective trust-domain law).** Under the registered signature and verification semantics, an attacker can forge an accepted attestation chain if and only if

\[
\operatorname{supp}(\alpha)\subseteq C.
\]

### Sufficiency

If every role-bearing domain is compromised, the attacker holds the signing material for every required role. It can construct a content-consistent chain and produce every required signature. Forgery succeeds.

### Necessity

If some role-bearing domain lies outside \(C\), at least one required signature must be produced under an uncompromised independent key. The attacker cannot derive that key or replace the missing role under the frozen verifier. Forgery fails.

The theorem depends on the declared cryptographic model, role completeness, and exact verifier. It is not a universal theorem about every provenance or threshold-signature system.

## 4. Effective diversity

Define

\[
d_{\mathrm{eff}}=|\operatorname{supp}(\alpha)|.
\]

This is the number of distinct trust domains that actually hold the roles required for acceptance. It is the operative diversity parameter in the registered harness.

Several consequences follow.

1. Increasing chain length without changing role placement does not increase \(d_{\mathrm{eff}}\).
2. Provisioning more domains while leaving all roles in one domain does not increase \(d_{\mathrm{eff}}\).
3. Role labels do not matter to the compromise threshold once every role is required symmetrically by the verifier; only their domain support matters.
4. Resistance to compromise increases only when role placement increases the number of independently protected required roots.

These statements convert an architectural intuition into an exact surface over every placement and compromise pattern.

## 5. Frozen exhaustive evaluation

The theorem and protocol are frozen before outcomes. The evaluation enumerates:

- domain counts \(d\in\{1,2,3\}\);
- every assignment of the three roles to those domains;
- every compromise subset \(C\);
- real signed receipts under the registered verifier.

The cross-product contains 1,000 cells. Each cell records the theorem prediction, whether an attack is attempted and accepted, and whether an honest chain verifies.

The exhaustive design tests both directions. Merely observing failed attacks would be insufficient because an inert attack implementation could manufacture apparent security. Conversely, observing successful attacks alone would not establish that the verifier accepts honest chains.

## 6. Results

All 1,000 cells match Theorem 1.

| Quantity | Result |
|---|---:|
| Cells evaluated | 1,000 |
| Cells matching the theorem | 1,000 |
| Sufficiency failures | 0 |
| Necessity failures | 0 |
| Predicted-forgery attacks that succeed | 260/260 |
| Honest chains accepted | 1,000/1,000 |
| No-compromise cells resisting forgery | 144/144 |
| Collapsing multi-domain assignments | 5 |

The attack-positive control is load-bearing. In all 260 cells where the theorem predicts forgeability, the attack actually succeeds. A test harness that never generated a valid forgery would have made every negative security result uninterpretable.

The honest-chain control rules out another trivial explanation: a verifier that rejects all inputs would appear perfectly resistant. Instead, every honest chain verifies.

## 7. Domain count without role spread buys nothing

Five assignments provision more than one domain but place all three roles in a single domain. They satisfy \(d>1\) and \(d_{\mathrm{eff}}=1\). In every such assignment, compromising the one role-bearing domain is sufficient to forge the chain.

This is the operationally important result. “Three-domain architecture” is not a security property if two domains are spectators. A deployment claim should report role support, compromise assumptions, and custody rather than the number of boxes in the architecture diagram.

The same principle applies when multiple named services share one root key, one recovery process, or one administrator capable of extracting all keys. The present theorem models independent key material only; other common-mode failures require a richer compromise model.

## 8. Relation to the frozen predecessor hypotheses

Two earlier hypotheses are one-dimensional slices of the same law.

- One slice varies chain length while \(d_{\mathrm{eff}}=1\) and correctly finds no security change.
- Another fixes three roles and one compromised domain, locating the transition at the point where \(d_{\mathrm{eff}}\) exceeds the compromise budget.

The theorem subsumes both without treating their repeated cells as independent evidence. It explains why the earlier patterns occur and predicts every remaining placement/compromise combination in the registered universe.

## 9. Cryptographic independence is not organizational independence

Every trust domain in the experiment uses key material generated from independent randomness. No domain can derive another's secret under the declared model. This is genuine cryptographic separation.

All domains nevertheless remain under one research programme's custody. The same organization controls provisioning, execution, and evidence release. An institutional adversary or common administrator may therefore compromise several nominal domains through one governance failure even when the keys are mathematically independent.

The protocol freezes this distinction before outcomes. The favourable 1,000/1,000 result does not upgrade the claim to general trust-domain resilience. A second custodian, independent governance, or a materially different trust model cannot be manufactured by re-labelling same-programme components.

## 10. Donor boundary

Digital signatures, threshold systems, multisignatures, provenance chains, transparency logs, supply-chain attestations, trust management, and Byzantine fault models are mature donor areas. The paper does not claim that distributing keys can raise compromise cost or that common-mode custody defeats nominal redundancy.

The residual contribution is the exact harness law, its pre-outcome exhaustive test, and its explicit separation of provisioned domain count from effective role-bearing diversity. The result is also a methodological control for research-agent infrastructure: evidence from multiple agents or services is not independent merely because it is signed at multiple steps.

## 11. Claim ceiling

The evidence supports:

- exact forgeability equivalence \(\operatorname{supp}(\alpha)\subseteq C\) for the registered harness;
- \(d_{\mathrm{eff}}\) as the operative cryptographic diversity parameter;
- no dependence on chain length or role identity beyond their effect on support;
- zero false rejection of honest chains in the 1,000 registered cells;
- the failure of nominal multi-domain deployments whose roles collapse to one domain.

The evidence does not support:

- organizational independence;
- resilience across arbitrary attestation protocols or signature schemes;
- external-custodian replication;
- a claim about real organizations with unknown compromise correlations;
- a completed frontier study over structurally different deployed trust models.

## 12. Reproducibility

A release should include the frozen role and verifier definitions, key-generation procedure, every role-placement map, every compromise set, signed receipts, attack constructor, honest-chain controls, theorem checker, and the exact 1,000-cell result table. The release should make collapsing assignments easy to inspect rather than hiding them in aggregate counts.

The scientific manuscript should describe roles and domains conceptually. Key identifiers, file paths, commands, and internal workflow labels belong in the artifact documentation.

## 13. Limitations and next study

The theorem assumes uncompromised keys are unforgeable and independently generated, compromised domains grant complete signing ability, and every role is required by one fixed verifier. Threshold or optional-role protocols change the support condition. Key-recovery channels, administrator overlap, and correlated compromise are outside the model.

The preregistered successor requires at least two real systems with structurally different trust models and genuinely separate governance. It has not executed. A valid study must establish organizational independence through evidence external to the present programme; same-programme agents cannot supply it.

## 14. Conclusion

Trust-domain security depends on where authority actually resides. In the registered three-role attestation harness, forgery is possible exactly when every role-bearing domain is compromised. All 1,000 frozen placement/compromise cells obey this law, honest chains always verify, and attacks succeed in every predicted-forgeable case. Nominally adding domains provides no protection when all roles remain in one. The result is exact under cryptographic independence and deliberately stops there: key diversity inside one programme is not organizational independence.