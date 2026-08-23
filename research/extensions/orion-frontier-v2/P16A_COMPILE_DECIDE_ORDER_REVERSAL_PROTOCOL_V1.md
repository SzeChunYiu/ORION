# P16A Compile-Decide Order Reversal Protocol V1

Status: **FROZEN BEFORE OUTCOME**  
Date: 2026-08-20  
Parent atom: `F0.P16.REVERSAL`

## Question

Can an information structure that classically Blackwell-dominates another be worse for a *resource-bounded compile-then-decide pipeline*, once state transformation and decoder capability are both explicit costs?

This is a donor-pressured controlled study, not a novelty declaration. Blackwell ordering, restricted decision problems, Le Cam deficiency, predictive V-information, rational metareasoning and costly information acquisition are direct parents.

## Finite decision problem

Latent world: independent uniform `x,c in {-1,+1}`.

Decision target:

`y = +1` iff `x*c = +1`, else `-1`.

Information structures:

- `E_raw` reveals `(x,c)` exactly;
- `E_rel` reveals `z=x*c` only.

`E_rel` is a deterministic garbling of `E_raw`, so `E_raw` classically Blackwell-dominates `E_rel` for unrestricted cost-free decision rules.

## Resource-bounded pipeline

Decoder family `V1`: affine linear threshold over the currently exposed coordinates.

Compiler menu from raw:

- `IDENTITY`, cost 0, exposes `(x,c)`;
- `RELATION_PRODUCT`, cost 1, exposes `(x,c,x*c)`.

For `E_rel`, identity exposure of `z` costs 0.

Decision cost is normalized to 1 for one `V1` evaluation. Total integer budget B is swept over `{1,2}`.

## Exact expectations

- unrestricted cost-free decision optimum from `E_raw` is 1.0, confirming no contradiction with Blackwell;
- best affine threshold directly on `(x,c)` has accuracy 0.75 on the four equiprobable worlds;
- affine threshold on `z` has accuracy 1.0;
- at B=1, raw cannot buy `RELATION_PRODUCT`, so resource-bounded optimum is 0.75, while E_rel reaches 1.0;
- at B=2, raw can compile and reaches 1.0, tying E_rel.

## Positive terminal

`P16_RESOURCE_BOUNDED_COMPILE_DECIDE_REVERSAL_CONSTRUCTED` only if exact enumeration confirms every expectation and an independent brute-force enumeration of affine sign patterns agrees with the 0.75 raw bound.

## Interpretation boundary

A positive result constructs a finite **order reversal under an explicitly restricted/costed pipeline**. It does not establish novelty of restricted informativeness or computation-aware information theory. P16 remains in donor subtraction until the dynamic compiler-menu/preorder object is compared against Blackwell extensions, deficiency, V-information, value-of-computation and costly-information formalisms.
