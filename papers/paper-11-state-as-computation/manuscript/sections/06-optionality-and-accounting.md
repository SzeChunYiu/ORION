# Future optionality and accessibility-work accounting

Current accessibility and future optionality are different objectives. Let a universal state contain `N` independent query coordinates and a compiled state retain `r`.

If raw source is lost, one-step coverage for a uniformly random future query is exactly `r/N`. If `K` independently selected size-`r` compilations are cached, expected coverage is `1-(1-r/N)^K`. Under uniform demand, the expected number of distinct requested components after `K` queries is `N[1-(1-1/N)^K]`.

These laws produce four policy regimes: compile only; compile + cache; retain raw + compile; and universal materialization. In the frozen workload study, the first grid point where universal bulk compilation becomes cheaper than expected cache compilation occurs at `0.5N`, `1.0N`, and `2.0N` future-query horizons for batch-efficiency factors 0.25, 0.50, and 0.75. Concentrated Zipf-like workloads delay crossover because fewer distinct coordinates are demanded.

Any comparison that treats representation construction as free is invalid. P11 therefore keeps separate receipt coordinates for compiler/preprocessing operations and latency, state bytes/tokens and memory traffic, downstream model identity/capacity, training examples or generated/recurrent steps, search nodes/verifier/tool calls, cache and reuse, raw recovery/reconstruction/recompilation, end-to-end latency and reproducible energy where available.

Learned-compiler training cost must be reported separately and amortized only under a prospectively stated reuse horizon. Unless an application supplies exchange rates, comparisons should be Pareto surfaces rather than post-hoc scalar costs.