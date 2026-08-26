# Donor boundary and novelty

## Adaptive test-time compute is prior-owned

Recent systems allocate inference compute dynamically based on predicted difficulty, value or resource constraints. Bandit formulations, constrained policy optimization, adaptive demonstration/generation strategies and “when to think” policies already own the primitive that different examples deserve different reasoning budgets. ORION-22 therefore does not claim adaptive inference allocation itself.

## Dynamic state construction is also prior-owned

Retrieval, compression, context selection, query-conditioned memory and structured-state construction already adapt what a model sees. ORION-21 additionally supplies controlled evidence that construction can change accessibility. ORION-22 does not claim dynamic state selection as a new primitive.

## Residual after subtraction

The live residual is the **competition between those actions under one resource boundary**:

> State construction and downstream reasoning are two places to spend test-time computation. A valid joint-allocation result must hold total resource fixed and strictly improve over policies allowed to adapt either axis alone.

Current adaptive-compute donors optimize downstream reasoning, sampling, search or generation control. They do not make costed state construction and downstream reasoning symmetric decision variables under the same matched envelope, then require superiority over both one-axis adaptive controls.
