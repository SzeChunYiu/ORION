(set-logic QF_UF)
(declare-const donor_valid Bool)
(declare-const scientific_coordinates_complete Bool)
(define-fun p6_lift_valid () Bool
  (and donor_valid scientific_coordinates_complete))
(define-fun ideal_product_valid () Bool
  (and donor_valid scientific_coordinates_complete))
; A satisfying assignment would violate at least one registered bounded law:
; exact ideal-product equivalence, donor conservativity, or no manufacture of a
; missing scientific coordinate. The conjunction is expected UNSAT.
(assert
  (or
    (not (= p6_lift_valid ideal_product_valid))
    (and p6_lift_valid (not donor_valid))
    (and donor_valid (not scientific_coordinates_complete) p6_lift_valid)))
(check-sat)
