Dear Editors of Autonomous Agents and Multi-Agent Systems,

Please consider the regular paper **“Epistemic Authority for Autonomous Science: Typed Discharge across Heterogeneous Scientific Effects.”**

The manuscript addresses an interface problem in composed autonomous agents. Modern agent systems already have strong authorization, usage-control, effect, provenance, abstention, and multi-authority mechanisms. The paper therefore does not argue that agents merely need permissions or that evidence should be checked before action. Instead, it asks when a locally valid source-domain judgment actually satisfies the different *scientific obligation* required by a heterogeneous target effect.

The formal contribution is a complete evidence-to-obligation type over domain, evidential kind, scope, content identity, and epoch; protected cross-domain coercions whose entire types must compose; exact revocation over alternative complete derivations; and distinct `AUTHORIZED`, `DENIED`, and `CANNOT_CHECK` terminals. A generic permission/scientific-discharge separation theorem shows why a valid security/policy grant can coexist with an unresolved scientific obligation.

The paper also contains a negative result that constrains its own architectural claims: a shared authority calculus is extensionally equivalent to an ideal product of correctly typed domain gates when both implement the same coercion, freshness, blocker, and revocation semantics. Centralization is therefore not claimed as inherent expressive superiority. Any future engineering advantage must be measured as consistency, revocation coverage, audit/proof economy, or implementation quality.

The latest literature pass explicitly absorbs current close work including UCON/SecPAL, ETAS/FAVA, AgentBound, multi-agent authorization propagation, AgentAbstain, ProvenanceGuard, SteerBench-Work, current action-evidence specifications, and the especially close SAGE-Fin result *Context Is Not Authority*. That close result is reflected directly in the manuscript's nonclaims: exact-artifact binding, stale-obligation tracking, pre-commit authorization, and the broad distinction between context/evidence and authority are donor-owned.

The supporting repository contains deterministic theorem/countermodel checks over the full five-by-five source/target-domain matrix, coercion composition, revocation, stale epochs, terminal distinctions, and shared/product equivalence, plus a frozen 17-case authority manifest with clean authorized controls and laundering attacks. These artifacts establish executable conformance to the theory, not independent real-world safety accuracy.

The submission includes the mandatory JAAMAS information sheet, editable LaTeX source, numbered references, declarations, a transparent LLM-use section, and reproduction paths.

Correspondence: Sze Chun Yiu, Department of Physics, Stockholm University, SE-106 91 Stockholm, Sweden; sze-chun.yiu@fysik.su.se.

Sincerely,

Sze Chun Yiu
