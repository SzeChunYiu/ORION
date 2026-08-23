# Introduction

A system can possess all information required for a task and still make that information expensive for a bounded learner or reasoner to use. Computationally usable information formalizes one version of this observation. Partial evaluation and knowledge compilation move work upstream. Materialized views trade preprocessing and storage for later query cost. Current agent systems retrieve, compress, summarize or restructure context before generation. Recent LLM evidence also shows that state design itself can materially change dynamic reasoning while model parameters remain fixed.

Those results make several weak novelty claims untenable. P11 does **not** claim that representation matters, that computation can create usable information, that query-conditioned memory is new, or that compression can reduce downstream cost. The unresolved question is:

> **When task-relevant structure can be discovered either while constructing state or later by a decoder/search process, where is the computation paid, how much downstream burden can be removed, and what future optionality is lost by specialization?**

We call this view *state as computation*. A compiler `C(R,q)` receives raw state `R` and query `q`, constructs task-facing state, and hands it to a bounded downstream access mechanism. Compilation is never free: compiler operations, state bytes, training cost, cache/recovery cost, downstream samples/search, verifier/tool calls, latency and reproducible energy belong to one resource receipt.

The paper contributes accessible-rank theory, controlled compilation gaps, hostile decoder substitution and future-optionality laws. The strongest conclusion is mechanistic: **representation construction and downstream access are two loci at which structural-search work can be paid**.