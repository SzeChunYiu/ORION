# Effective Role Support Is the Compromise Threshold of a Multi-Role Attestation Chain

## Abstract

An attestation chain can be long and still have a single cryptographic point of failure. Consider three required roles, execution, environment, and publication. Let \(\alpha\) assign each role to the key domain that controls its signature, and let \(C\) be the compromised domains. We prove
\[
\text{forgeable}
\quad\Longleftrightarrow\quad
\operatorname{supp}(\alpha)\subseteq C.
\]
The exact compromise threshold is therefore
\[
d_{\mathrm{eff}}=|\operatorname{supp}(\alpha)|,
\]
the number of domains that actually hold required roles. Neither chain length nor nominal domain count contributes unless it increases this support.

A complete registered sweep contains 1,000 role-assignment and compromise cells. Every cell matches the theorem. Planted forgeries succeed in all 260 predicted-forgeable cells, honest chains verify in all 1,000 cells, and no-compromise forgeries fail in all 144 registered controls. Five configurations provision multiple domains but place all roles in one; every one remains forgeable after a single compromise.

The result is exact for independently generated cryptographic keys. All domains remain under one programme's custody, so the paper does not claim organizational independence, protection from common-mode compromise, or general trust-domain resilience.

## 1. The wrong security count

Counting attestations is attractive because links are visible. Counting provisioned domains is also attractive because infrastructure diagrams display them. Neither quantity measures compromise resistance when the same domain controls every required key.

The relevant object is the support of the role assignment:
\[
\operatorname{supp}(\alpha)
=
\{\text{domains holding at least one required role}\}.
\]

A chain gains cryptographic compromise resistance only when a new required role key is placed outside the domains an adversary already controls.

## 2. Verification model

The verifier requires valid links for three roles:
\[
R=\{\text{execution},\text{environment},\text{publication}\}.
\]

For every \(r\in R\), the link must verify under the expected public key for that role. Domains generate keys independently. Compromising domain \(j\) reveals every private key assigned to \(j\) and no key assigned elsewhere.

This model abstracts away compromise probability and focuses on the exact structural condition for complete forgery.

## 3. Exact law

**Theorem 1.**
\[
\text{An accepted forged chain exists}
\iff
\operatorname{supp}(\alpha)\subseteq C.
\]

If every role-holding domain is compromised, the adversary owns every required private key and can re-sign the chain. If at least one role remains in an uncompromised domain, the adversary cannot produce that role's required signature under the expected key.

The theorem immediately gives the minimum compromise cardinality:
\[
\min |C|=d_{\mathrm{eff}}.
\]

## 4. Collapse of nominal redundancy

Suppose an organization provisions three domains but assigns all roles to one. Then
\[
d_{\mathrm{eff}}=1.
\]
The two unused domains do not affect forgeability.

Likewise, adding more signed links under keys from the same compromised domain does not help. The adversary can reproduce all of them.

The design consequence is simple: report role distribution, not chain length or nominal domain count.

## 5. Complete finite instantiation

The registered experiment crosses all three-role assignments over one to three domains with every declared compromised-domain subset. It contains 1,000 cells.

Observed results are:

- theorem agreement: 1,000 of 1,000;
- predicted-forgeable but failed attack: 0;
- predicted-resistant but accepted forgery: 0;
- honest verification: 1,000 of 1,000;
- planted forgery activation: 260 of 260;
- no-compromise resistance: 144 of 144.

The five collapsing assignments all behave as Theorem 1 predicts: a single compromise suffices.

These counts validate the implementation over the complete finite protocol. They are not a statistical sample.

## 6. Chain-length and domain-count slices

When effective support is fixed at one, increasing chain length leaves false promotion at 1.0. The result is not surprising under the theorem; all required keys remain compromised.

When one domain is compromised and required roles are distributed over more than one independent key domain, complete forgery fails as soon as
\[
\operatorname{supp}(\alpha)\nsubseteq C.
\]

The two earlier slices are therefore consequences of one support law rather than separate phenomena.

## 7. Security design rule

A multi-role attestation design should state:

- which roles are mandatory for acceptance;
- which domain controls each role key;
- the effective support \(d_{\mathrm{eff}}\);
- which compromises the threat model permits;
- whether key independence is cryptographic, organizational, or both.

A larger \(d_{\mathrm{eff}}\) raises the minimum number of cryptographic domains required for complete forgery. It does not quantify the probability or cost of compromising those domains.

## 8. Custody boundary

Independent key generation prevents derivation of one domain's secret from another's. It does not create independent organizations.

One programme controls every domain in the current experiment. Common software, provisioning, operators, or administrative credentials may therefore create correlated failure outside the model. No result here establishes protection from institutional compromise, collusion, or common-mode control-plane failure.

The strongest supported phrase is “cryptographically independent key domains under common custody.”

## 9. Limits and donor boundary

The law assumes unforgeability of uncompromised keys and binary domain compromise. It omits partial leakage, revocation, adaptive attack cost, recovery, denial of service, and correlated randomness failures.

Separation of duties, threshold trust, multisignatures, and attestation systems own the general security principle. The residual contribution is the exact effective-support formulation and its complete registered instantiation for this role chain.

## 10. Conclusion

The compromise threshold of a multi-role attestation chain is the number of independently keyed domains that actually hold required roles. A chain is forgeable exactly when every such domain is compromised. Extra links and nominal domains are irrelevant unless they change that support. This law gives a precise cryptographic design metric while preserving the boundary the experiment cannot cross: independent keys under one custodian are not independent governance.
