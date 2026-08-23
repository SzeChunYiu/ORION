# P16A Result Receipt V1

Status: **CONTROLLED POSITIVE / NOVELTY NOT AUTHORIZED**  
Date: 2026-08-20

Protocol: `P16A_COMPILE_DECIDE_ORDER_REVERSAL_PROTOCOL_V1.md`  
Runner: `run_p16a_compile_decide_order_reversal_v1.py`  
Result: `results/P16A_COMPILE_DECIDE_ORDER_REVERSAL_V1.json`

Terminal:

`P16_RESOURCE_BOUNDED_COMPILE_DECIDE_REVERSAL_CONSTRUCTED`

## Exact result

- `E_raw` reveals `(x,c)` and classically Blackwell-dominates `E_rel`, because `E_rel` is the deterministic garbling `z=x*c`.
- unrestricted raw optimum: `1.0`;
- best affine threshold directly on raw `(x,c)`: `0.75`;
- affine threshold on relation `z`: `1.0`;
- budget 1: raw `0.75`, relation `1.0`;
- budget 2: raw compiles relation and reaches `1.0`, tying relation.
- independent linear-program enumeration found 14 affine-separable dichotomies of the four-point support and agrees with the `0.75` raw bound.

Two fresh-process result replays were byte-identical:

`sha256:ea411cf9f5fc40c04b92d6aa28f9921b1a4d17b0512434109ad10e57f3be2009`

## Scientific boundary

This is a finite construction showing that a classically more informative experiment can be worse under a deliberately restricted and explicitly costed compile-then-decide pipeline. Restricted informativeness, costly computation, Blackwell comparison, Le Cam deficiency, predictive V-information and metareasoning are direct parents. The receipt grants no novelty claim for a new information order.

The surviving P16 research question is whether a dynamic compiler-menu/resource preorder or deficiency object remains materially distinct after full donor subtraction.
