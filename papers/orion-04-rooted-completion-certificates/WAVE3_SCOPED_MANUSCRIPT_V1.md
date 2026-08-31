# A one-unit generalized-Davenport corridor and an exact support-14 reduction in \(C_5^3\)

## Abstract

We study the remaining low-index uncertainty in the generalized Davenport constants of the elementary abelian group \(C_5^3\). The committed symbolic arguments place the eventual sequence in a one-unit corridor: for every \(k\ge 4\),
\[
5k+10\le D_k(C_5^3)\le 5k+11,
\]
and the lower value at \(D_4\) would force the lower line for every later index. We combine this corridor with a saturation-defect theorem for short-zero-sum-free sequences and a content-bound exact replay of every multiplicity pattern having support 11, 12 or 13. Two exact state representations independently reproduce the registered search fingerprints and return no obstruction in any branch. Consequently, any length-31 total-zero sequence over \(C_5^3\) with no nonempty zero-sum subsequence of length at most five, if such a sequence exists, has support at least 14. This is a bounded structural theorem, not a determination of \(D_4(C_5^3)\): support 14 and above remain open, the larger support-through-22 computation is retained as internal exploratory evidence only, and neither \(31\in C_0(C_5^3)\) nor an upper-line extremal is established. The contribution is therefore a sharply delimited reduction, an exact dual-replay method and a fail-closed authority record for the remaining boundary.

## 1. Problem and decision axis

Let \(D_k(G)\) denote the generalized Davenport constant of a finite abelian group \(G\). For \(G=C_5^3\), the current evidence does not leave a broad asymptotic question. It leaves a one-unit decision: whether the sequence enters the lower step-five line or retains a final one-unit defect controlled by the unresolved value of \(D_4\).

The paper addresses three questions.

1. How much of the later generalized-Davenport sequence is already determined symbolically?
2. What local multiplicity and saturation restrictions must any length-31 upper-line obstruction satisfy?
3. How far can exact finite replay reduce the support of such an obstruction without being mistaken for an exact solution of \(D_4\)?

The answer to the third question is support at least 14. The exact \(D_4\) decision remains open.

## 2. Symbolic corridor

The committed theorem chain yields the following bounded statements.

### Theorem 1: one-unit corridor

For every \(k\ge 4\),
\[
5k+10\le D_k(C_5^3)\le 5k+11.
\]

The recurrence and localization ingredients used to obtain this corridor are donor-owned mathematical inputs. This manuscript claims the assembled consequence for the registered \(C_5^3\) boundary, not ownership of the general recurrence machinery.

### Theorem 2: conditional lower-line tail

If
\[
D_4(C_5^3)=30,
\]
then
\[
D_k(C_5^3)=5k+10
\]
for every \(k\ge 2\).

Thus the unresolved low-index value is not an isolated numerical curiosity. A lower-line decision at \(k=4\) determines the later sequence under the committed implication.

### Corollary 3: exact remaining interval

The current symbolic evidence proves
\[
D_4(C_5^3)\in\{30,31\}.
\]

No statement in this manuscript selects one value from that pair.

## 3. Saturation-defect structure

The finite search is not performed over arbitrary 31-term sequences. It is constrained by a structural theorem.

### Theorem 4: saturation defect

For an odd prime \(p\), consider a saturated \(p\)-short-free sequence and a point \(x\) occurring with multiplicity \(m<p\). The sequence decomposes as
\[
x^mR,
\]
where
\[
|R|\le p-1-m,
\qquad
\sigma(R)=-(m+1)x.
\]

For \(p=5\), this excludes multiplicity three in the relevant obstruction grammar. The admissible nonzero multiplicities are therefore \(1\), \(2\) and \(4\).

For a length-31 candidate with \(a_1\) singleton support points, \(b_2\) doubleton support points and \(c_4\) quadrupleton support points,
\[
a_1+b_2+c_4=s,
\qquad
a_1+2b_2+4c_4=31,
\]
where \(s\) is the support size. These equations give a complete, auditable multiplicity grammar at each fixed support.

## 4. Exact support-11-to-13 programme

### 4.1 Registered object

The Wave 3 M4 packet studies every multiplicity solution for \(s\in\{11,12,13\}\). The complete list contains nine patterns:

| Support | \((a_1,b_2,c_4)\) | Required branches |
|---:|---:|---|
| 11 | \((1,5,5)\) | rank three |
| 11 | \((3,2,6)\) | rank three |
| 12 | \((1,7,4)\) | rank three |
| 12 | \((3,4,5)\) | rank three |
| 12 | \((5,1,6)\) | rank three |
| 13 | \((1,9,3)\) | rank three and rank two |
| 13 | \((3,6,4)\) | rank three |
| 13 | \((5,3,5)\) | rank three |
| 13 | \((7,0,6)\) | rank three |

The rank-two branch is required only for \((1,9,3)\). Omitting it would leave a genuine coverage hole; the independent checker and hostile controls therefore bind its seed count and exact aggregate fingerprints.

### 4.2 Two exact state representations

The replay uses two materially different representations of the same exact reachability problem.

- The primary engine stores exact weights in an `unsigned __int128` representation.
- The corroborating engine stores the same reachability state as explicit bytes.

Both engines use exact arithmetic and deterministic ordering. For every registered row, they must agree on node counts, leaf counts and solution counts. The rank-two branch must additionally agree on its normalized seed candidates, executed and pre-DFS rejected seeds, per-seed fingerprints and aggregate totals.

Agreement is checked against prospective source hashes and a deterministic result digest. A favorable process exit code is not sufficient.

### 4.3 Independent static verification

A separate non-generating checker reconstructs the multiplicity pattern list directly from the defining equations. It does not import the replay generator or its search-state implementation. It verifies:

- protocol and schema identities;
- exact source, theory, manifest and disposition hashes;
- the parent M3 digest and terminal;
- completeness of the nine-pattern grammar;
- exact rank-three and rank-two fingerprints;
- all bounded authority flags; and
- the absence of support-14+, support-23, exact-\(D_4\), novelty, venue and external-replay authority.

The checker is implementation-independent within the repository. It is not described as an external independent replication.

### 4.4 Hostile controls

The packet includes re-signed adversarial mutations. A mutation remains cryptographically self-consistent at the outer result-digest layer, so rejection must come from semantic checking. The committed controls include:

1. altering a rank-three fingerprint while preserving cross-engine agreement;
2. deleting part of the rank-two coverage while repairing the superficial seed counts; and
3. escalating a forbidden theorem-authority flag.

Each mutation must be rejected. This demonstrates that the checker is not merely verifying its own digest format or trusting a producer-supplied `all_checks` field.

## 5. Result

Every support-11, support-12 and support-13 branch returned zero solutions in both exact representations, with exact agreement on the registered fingerprints. Together with the committed parent reduction, this yields the paper's new finite theorem.

### Theorem 5: bounded support exclusion

Let \(S\) be a length-31 sequence over \(C_5^3\) satisfying
\[
\sigma(S)=0
\]
and containing no nonempty zero-sum subsequence of length at most five. If \(S\) exists, then
\[
|\operatorname{supp}(S)|\ge 14.
\]

The theorem says exactly that supports 11, 12 and 13 are excluded after the earlier support-at-most-10 reduction. It does not say that all supports through 22 have been established at the same authority level.

## 6. What the computation does not establish

A larger internal computation records zero survivors through support 22. Its own disposition states that theorem authority is false and that external replay is required. That record is retained because it is useful for search design, but it is not used to strengthen Theorem 5.

At support 23, the multiplicity equations leave three patterns:

- \(1^{15}2^8\);
- \(1^{17}2^54\); and
- \(1^{19}2^24^2\).

Exploratory searches at that frontier do not become publication evidence merely because they returned no local survivor. A proof-producing complete cover or a verified explicit obstruction is still required.

Accordingly, this manuscript does not establish any of the following:

- \(31\in C_0(C_5^3)\);
- \(D_4(C_5^3)=30\);
- \(D_4(C_5^3)=31\);
- a support-at-least-23 theorem;
- external independent replication;
- novelty of the donor recurrence, localization or Property-C machinery; or
- journal or top-tier authority from finite UNSAT alone.

## 7. Interpretation

The main mathematical value of Theorem 5 is a structural reduction. Any unresolved upper-line obstruction must be comparatively diffuse: it cannot be supported on thirteen or fewer group elements, even though the sequence has length 31 and each nonzero multiplicity belongs to \(\{1,2,4\}\). This substantially narrows the remaining object and makes the saturation constraints increasingly informative.

The methodological value is equally bounded. The packet demonstrates how a finite exact argument can carry a stronger audit trail than a bare solver transcript: complete grammar enumeration, two exact state representations, source custody, deterministic receipts, a checker that independently reconstructs the outer combinatorics and hostile re-signed mutations. These controls justify the support-14 theorem. They do not convert an internal computation into external replication.

## 8. Reproducibility

The authoritative packet is:

`research/orion-rg/wave3/orion04-support11-13-v1/`

The central commands are:

```bash
python research/orion-rg/wave3/orion04-support11-13-v1/run_replay.py \
  --output /tmp/ORION04_M4_RESULT.json
cmp research/orion-rg/wave3/orion04-support11-13-v1/RESULT.json \
  /tmp/ORION04_M4_RESULT.json

python research/orion-rg/wave3/orion04-support11-13-v1/independent_checker/check_result.py \
  --input /tmp/ORION04_M4_RESULT.json \
  --output /tmp/ORION04_M4_GENERIC_RESULT.json
cmp research/orion-rg/wave3/orion04-support11-13-v1/GENERIC_RESULT.json \
  /tmp/ORION04_M4_GENERIC_RESULT.json

python -m pytest -q tests/research/test_orion04_wave3_m4_packet.py
```

The dedicated workflow reruns these commands, checks authority boundaries and requires a clean tree. The source manifest binds the exact C implementations used by both engines.

## 9. Limitations and future work

The exact \(D_4\) boundary remains mathematically open in this project. A successor may close it by one of three routes: a proof-producing complete global obstruction, an independently verified explicit extremal, or a reusable human-readable theorem that rules out the remaining support. Any such successor must be prospectively frozen and must preserve failed partitions and counterexamples.

The present paper deliberately stops at the last independently defensible theorem. This is not a placeholder for an assumed exact answer. It is the final Wave 3 paper boundary.

## 10. Conclusion

The generalized Davenport constants of \(C_5^3\) lie in a one-unit eventual corridor, and the lower value at \(D_4\) would determine the lower line thereafter. Saturation defects exclude multiplicity three in a hypothetical length-31 short-zero-sum-free obstruction. Exact dual replay then excludes every support-11, support-12 and support-13 multiplicity branch, proving support at least 14. Exact \(D_4\) is not established. The paper's contribution is the bounded structural theorem and its auditable proof custody, not a stronger unresolved conclusion.

## Data and code availability

All admitted evidence, source manifests, deterministic receipts, checkers and hostile tests are stored in the repository paths named above. No external dataset is required for the bounded replay. External independent replication has not been completed.
