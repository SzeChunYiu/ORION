# Role Distribution, Not Attestation-Chain Length, Determines Cryptographic Compromise Resistance

## Abstract

Longer attestation chains are often treated as stronger evidence, but repeated links controlled by one key domain do not create independent resistance to compromise. We formalize a three-role execution-integrity chain with execution, environment, and publication attestations. Let
\[
\alpha:\text{ROLES}\to\text{DOMAINS}
\]
assign each role to the cryptographic domain holding its key, and let \(C\) be the set of compromised domains. Write
\[
\operatorname{supp}(\alpha)=\alpha(\text{ROLES}),
\qquad
d_{\mathrm{eff}}=|\operatorname{supp}(\alpha)|.
\]

An adversary can forge an accepted chain if and only if
\[
\operatorname{supp}(\alpha)\subseteq C.
\]
The minimum number of domains that must be compromised is therefore \(d_{\mathrm{eff}}\). It does not depend on chain length or on how many nominal domains exist unless roles are actually distributed across them.

An exhaustive finite sweep evaluates 1,000 combinations of role assignment and compromised-domain set. All 1,000 match the theorem, with zero necessity or sufficiency failures. Planted forgeries succeed in all 260 cases in which the theorem predicts forgeability; honest chains verify in all 1,000 cases; and no uncompromised case forges in 144 tested cells. Five collapsing assignments provision multiple domains while placing every role in one, and a single compromise forges in every such case.

The boundary is material. The domains use independently generated cryptographic keys but remain under one programme's custody. The result establishes a law under cryptographic independence, not organizational independence or general trust-domain resilience.

## 1. Introduction

An integrity chain can contain several signed links and still have one point of failure. If the same trust domain controls every signing key, compromising that domain allows an adversary to reconstruct the entire chain, regardless of its length.

The structural security question is therefore not “how many attestations are present?” It is:

> How many independently keyed domains must an adversary compromise to control every role required by verification?

We answer this exactly for a frozen three-role chain. The result separates chain length, nominal domain count, and effective role distribution.

## 2. Model

The chain has three roles:
\[
\text{execution},\quad
\text{environment},\quad
\text{publication}.
\]

A chain verifies only when every role's link carries that role's expected public key and a valid signature over the registered content.

A domain is a cryptographic key-independence class. Keys in different domains are generated from independent randomness. Compromising a domain reveals every role key assigned to that domain and no key assigned to an uncompromised domain.

The assignment
\[
\alpha:\text{ROLES}\to\{1,\ldots,d\}
\]
need not use every provisioned domain. Its effective support is
\[
\operatorname{supp}(\alpha)=\{\alpha(r):r\in\text{ROLES}\}.
\]

The adversary compromises exactly the domains in \(C\).

## 3. Forgeability theorem

**Theorem 1.** An adversary can forge an accepted chain if and only if
\[
\operatorname{supp}(\alpha)\subseteq C.
\]

**Proof.**

If \(\operatorname{supp}(\alpha)\subseteq C\), the adversary holds every role key. It can sign a complete chain over an arbitrary claim, so verification accepts.

Conversely, suppose some role \(r\) is assigned to a domain outside \(C\). Its private key was generated independently and is unavailable to the adversary. Verification requires a valid signature under that role's expected public key. The adversary cannot produce the required link, so the forged chain is rejected. \(\square\)

The theorem assumes standard unforgeability for uncompromised keys. Its structural content lies in the role-to-domain assignment.

## 4. Effective-domain corollary

**Corollary 2.** The minimum number of domains that must be compromised is
\[
d_{\mathrm{eff}}=|\operatorname{supp}(\alpha)|.
\]

Chain length does not enter the expression. Repeating a role, adding redundant links under the same domain, or provisioning unused domains does not increase the compromise threshold.

**Corollary 3 (collapse).** If every role is assigned to one domain, then \(d_{\mathrm{eff}}=1\) regardless of nominal domain count. One compromise suffices.

The security parameter is therefore role support, not the number printed in an infrastructure diagram.

## 5. Honest-chain corollary

With no compromised domains, the adversary holds none of the role keys. A forged chain cannot satisfy every signature check. The honest chain verifies because each role signs under its own expected key.

This gives resistance without a false-rejection tradeoff inside the model.

## 6. Exhaustive finite sweep

The registered sweep covers every assignment of the three roles to \(d\in\{1,2,3\}\) domains and every subset of compromised domains under the declared construction. Across 1,000 cells:

- theorem matches: 1,000;
- sufficiency failures: 0;
- necessity failures: 0;
- honest-chain verification: 1,000 of 1,000.

A planted-forgery control tests whether the attack mechanism is active. In all 260 cells where the theorem predicts forgeability, the constructed forgery succeeds. With no compromised domain, no forgery occurs in 144 of 144 cells.

Five assignments have more than one nominal domain but effective support one. In every case, a single compromised domain forges the chain.

The sweep checks the implementation over the complete registered finite space. The theorem, not the count, carries the general structural claim for the model.

## 7. Chain length as a negative control

A prior slice holds effective support at one while varying chain length. False promotion remains 1.0. The result is predicted by Theorem 1: every required key belongs to the compromised domain, so additional links add no independent barrier.

A second slice fixes three roles and one compromised domain while varying effective domain support. Forgeability drops when the roles are spread beyond the compromised set. These slices are one-dimensional consequences of the same law.

## 8. Design implications

The theorem yields a direct design rule.

1. Identify the roles whose signatures are required for acceptance.
2. Assign those roles across independently keyed domains.
3. Measure the number of domains actually used.
4. Do not credit redundant chain links or unused domains as compromise resistance.
5. Recompute the support after any role consolidation.

The result concerns prevention of complete chain forgery. It does not by itself address key theft probability, side channels, denial of service, compromise detection, or recovery.

## 9. Cryptographic versus organizational independence

The registered domains have independently generated keys, so compromise of one key domain does not mathematically reveal another domain's secret. All domains nevertheless remain under the same programme's custody.

Independent randomness is not independent governance. One operator may still control provisioning, software, access, and incident response across all domains. The experiment therefore cannot establish resilience to organizational compromise, collusion, common-mode software failure, or institutional capture.

This limitation was fixed before the favorable outcome and is part of the claim, not a post hoc caveat.

## 10. Relation to prior work

Threshold trust, separation of duties, multisignature protocols, provenance chains, and supply-chain attestations own the general idea that independent trust roots can reduce single-point compromise. The paper does not claim those primitives.

The residual is an exact role-support law for the declared execution-integrity chain and a complete finite instantiation showing how nominal domain count and chain length can misstate the actual compromise threshold.

## 11. Limitations

The theorem assumes uncompromised keys cannot be forged and treats domain compromise as binary. It does not model correlated key-generation defects, partial leakage, adaptive compromise cost, revocation, or recovery. The role set is fixed at three in the experiment.

Most importantly, all domains share one programme's custody. The work establishes cryptographic key independence only.

## 12. Conclusion

Attestation-chain length is not the security parameter in this model. An adversary can forge exactly when it compromises every domain that holds at least one required role key. The compromise threshold is the effective role support \(d_{\mathrm{eff}}\). Adding links or nominal domains buys nothing unless roles are actually spread across independently keyed domains. The law is exact under cryptographic independence and deliberately stops before organizational trust.
