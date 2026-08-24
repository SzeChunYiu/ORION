"""P12 price-aware successor allocator V1 (NR-13 revival lever).

Pre-registered rule (P12_PRICE_AWARE_SUCCESSOR_PROTOCOL_PREREG_V1.json):
exact budgeted argmin of the SAME objective the charging environment
charges. The environment publishes, per structure, a charge-ledger
certificate pair (reason_serve_certificate, state_serve_certificate)
plus the declared construction cost, and the price vector
(p_build, p_serve). Selection = 0/1 knapsack: take the budget-feasible
subset maximizing total priced saving

    saving[s] = p_serve * (reason_cert[s] - state_cert[s])
                - p_build * declared[s]

solved exactly by dynamic programming over integer declared weights;
on equal DP value the branch that does NOT take the item is preferred.
Eligibility is the sign of the priced marginal delta itself: there is
no multiplicity threshold, no tuned constant, no domain knowledge.

Readable surface (and nothing else): sid, declared_cost,
reason_serve_certificate, state_serve_certificate, B_budget (passed
in), p_build / p_serve (passed in). The only numeric literals in this
module are the structural loop constants 0, 1 and -1 (indices and
range steps); every parameter is an input.
"""


def price_aware_selection(ledger, prices, budget):
    """ledger: list of records in frozen structure order, each
        {"sid", "declared_cost",
         "reason_serve_certificate", "state_serve_certificate"}
    prices: (p_build, p_serve); budget: nominal S1 budget (int).
    Returns the sorted sid list of the selected subset.
    """
    p_build, p_serve = prices
    items = [(rec["sid"], rec["declared_cost"],
              p_serve * (rec["reason_serve_certificate"]
                         - rec["state_serve_certificate"])
              - p_build * rec["declared_cost"])
             for rec in ledger]
    n = len(items)
    dp = [[0] * (budget + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        _, w, v = items[i - 1]
        row, prev = dp[i], dp[i - 1]
        for c in range(budget + 1):
            best = prev[c]
            if w <= c and prev[c - w] + v > best:
                best = prev[c - w] + v
            row[c] = best
    selected = []
    c = budget
    for i in range(n, 0, -1):
        if dp[i][c] != dp[i - 1][c]:
            selected.append(items[i - 1][0])
            c -= items[i - 1][1]
    return sorted(selected)
