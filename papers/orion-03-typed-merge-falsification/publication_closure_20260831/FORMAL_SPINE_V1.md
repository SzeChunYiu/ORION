# ORION-03 formal-spine inventory

**Target:** Journal of Automated Reasoning research article  
**Canonical source:** `../MANUSCRIPT_V3.md`  
**Status:** preserved in the main text; scientific authority unchanged

| ID | Kind | Canonical object or statement | Scientific role | Status | Main-text requirement |
|---|---|---|---|---|---|
| FS-1 | primitives | finite claim set \(Q\), finite license set \(\Lambda\), labels in \(2^\Lambda\), seeds \(\sigma(q)\) | Defines the scientific object and evidence vocabulary carrier. | Defined | Required |
| FS-2 | rule and transfer | \(r=(A_r\to h_r,K_r)\), \(\tau_r(x)=K_r\cap\bigcap_{a\in A_r}x_a\) | Makes cap-preserving conjunctive transmission explicit. | Defined | Required |
| FS-3 | refutation operator | synchronous \(F_R\) with refuted nodes fixed to \(\varnothing\) | Defines the executable falsification semantics. | Defined | Required |
| FS-4 | fixed point | \(\operatorname{Auth}_\Lambda(R)=\operatorname{lfp}(F_R)\) | Identifies the current licensed assignment. | Defined | Required |
| FS-5 | finite convergence | synchronous iteration reaches the least fixed point after at most \(|Q||\Lambda|\) strict pair additions plus a stability check | Establishes termination at the paper's exact schedule boundary. | Proven | Required |
| FS-6 | typed proof trees | finite unrefuted tree whose leaves and caps all carry \(\lambda\) | Gives the derivational interpretation of a licensed pair. | Defined | Required |
| FS-7 | proof-tree equivalence | \(\lambda\in\operatorname{Auth}_\Lambda(R)_q\) iff a valid finite typed proof tree exists | Connects the fixed-point and proof views. | Proven | Required |
| FS-8 | nonpromotion | every surviving license appears in each leaf and cap on at least one proof tree | Yields unsupported-cycle bottom and fail-closed cap behavior. | Proven corollary | Required |
| FS-9 | refutation monotonicity | \(R\subseteq R'\Rightarrow\operatorname{Auth}_\Lambda(R')_q\subseteq\operatorname{Auth}_\Lambda(R)_q\) | Prevents added refutations from creating authority. | Proven | Required |
| FS-10 | exact relative retraction | pre/post label difference equals the pairs whose typed proof trees are all destroyed | States the strongest retraction claim without generic causality/minimality novelty. | Proven relative to the declared algebra | Required |
| FS-11 | external outcome definitions | \(P=v_A\lor v_B\), \(H=v_U\land\neg v_A\land\neg v_B\), unsafe \(d\land H\), needless \(\neg d\land P\) | Defines all empirical rows and makes the security non-implication explicit. | Defined | Required |
| FS-12 | analytic identity | origin witness \(d=P\), hence zero unsafe and needless counts by construction | Separates a specification identity from measured performance. | Analytic identity | Required |

## Delta audit

- Every required item is present before its first claim-bearing use.
- Object, operator, scope, definition/proof status, and dependency relations remain explicit.
- The paper proves synchronous convergence only; it does not imply arbitrary scheduling or negation.
- The empirical definitions do not turn a hybrid authorization into a security vulnerability.
- The source and final PDF preserve the same equations and theorem boundaries.

**Decision:** `PASS__FORMAL_SPINE_PRESERVED`.
