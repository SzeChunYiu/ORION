-- Source extract from FoML/Generalization/RKHS.lean @ 9409e74a48c97d568eb19468cf152c07d72288ff
theorem rkhs_rademacherComplexity_le
    [IsProbabilityMeasure μ] (Φ : 𝒳 → H) (hΦ : Measurable Φ)
    (Λ r : ℝ) (hΛ : 0 ≤ Λ) (hr : 0 ≤ r)
    (hdiag : ∀ x, kernelOfFeatureMap Φ x x ≤ r ^ 2)
    (X : Ω → 𝒳) (hX : Measurable X) : True := by
  letI : Nonempty (Metric.closedBall (0 : H) Λ) :=
    (Metric.nonempty_closedBall.mpr hΛ).to_subtype
  apply rademacherComplexity_le_of_empirical_le_separable
    (F := rkhsPredictor Φ) (X := X)
  · intro w
    exact (measurable_rkhsPredictor_input Φ hΦ w).comp hX
  · exact mul_nonneg hr hΛ
  · exact fun w x ↦ abs_rkhsPredictor_le Φ hΛ hr hdiag w x
  · exact continuous_rkhsPredictor_weight Φ
  · exact rkhs_empiricalRademacherComplexity_le Φ Λ r hΛ hr hdiag

theorem rkhs_uniformDeviation_expectation_le
    [Nonempty 𝒳] [IsProbabilityMeasure μ] (hn : 0 < n)
    (Φ : 𝒳 → H) (hΦ : Measurable Φ) (Λ r : ℝ) (hΛ : 0 ≤ Λ) (hr : 0 ≤ r)
    (hdiag : ∀ x, kernelOfFeatureMap Φ x x ≤ r ^ 2)
    (X : Ω → 𝒳) (hX : Measurable X) : True := by
  letI : Nonempty (Metric.closedBall (0 : H) Λ) :=
    (Metric.nonempty_closedBall.mpr hΛ).to_subtype
  apply uniform_deviation_expectation_le_of_empirical_le_separable
    (F := rkhsPredictor Φ) hn
  · exact fun w ↦ measurable_rkhsPredictor_input Φ hΦ w
  · exact hX
  · exact mul_nonneg hr hΛ
  · exact fun w x ↦ abs_rkhsPredictor_le Φ hΛ hr hdiag w x
  · exact continuous_rkhsPredictor_weight Φ
  · exact rkhs_empiricalRademacherComplexity_le Φ Λ r hΛ hr hdiag

theorem rkhs_uniformDeviation_tail_bound_delta
    [Nonempty 𝒳] [IsProbabilityMeasure μ] (hn : 0 < n)
    (Φ : 𝒳 → H) (hΦ : Measurable Φ) (Λ r : ℝ) (hΛ : 0 < Λ) (hr : 0 < r)
    (hdiag : ∀ x, kernelOfFeatureMap Φ x x ≤ r ^ 2)
    (X : Ω → 𝒳) (hX : Measurable X) {δ : ℝ}
    (hδ : 0 < δ) (hδ_one : δ ≤ 1) : True := by
  letI : Nonempty (Metric.closedBall (0 : H) Λ) :=
    (Metric.nonempty_closedBall.mpr hΛ.le).to_subtype
  apply uniform_deviation_tail_bound_separable_of_empirical_le_delta
    (μ := μ) hn (F := rkhsPredictor Φ)
  · exact fun w ↦ measurable_rkhsPredictor_input Φ hΦ w
  · exact hX
  · exact mul_pos hr hΛ
  · exact fun w x ↦ abs_rkhsPredictor_le Φ hΛ.le hr.le hdiag w x
  · exact continuous_rkhsPredictor_weight Φ
  · exact rkhs_empiricalRademacherComplexity_le Φ Λ r hΛ.le hr.le hdiag
  · exact hδ
  · exact hδ_one

theorem rkhs_uniformDeviation_tail_bound_kernelTrace_delta
    [Nonempty 𝒳] [IsProbabilityMeasure μ] (hn : 0 < n)
    (Φ : 𝒳 → H) (hΦ : Measurable Φ) (Λ r : ℝ) (hΛ : 0 < Λ) (hr : 0 < r)
    (hdiag : ∀ x, kernelOfFeatureMap Φ x x ≤ r ^ 2)
    (X : Ω → 𝒳) (hX : Measurable X) {δ : ℝ}
    (hδ : 0 < δ) (hδ_one : δ ≤ 1) : True := by
  letI : Nonempty (Metric.closedBall (0 : H) Λ) :=
    (Metric.nonempty_closedBall.mpr hΛ.le).to_subtype
  exact uniform_deviation_tail_bound_separable_of_sample_empirical_le_delta
    (μ := μ) hn (rkhsPredictor Φ : Metric.closedBall (0 : H) Λ → 𝒳 → ℝ)
    (fun w ↦ measurable_rkhsPredictor_input Φ hΦ w) X hX
    (fun S ↦ Λ * (n : ℝ)⁻¹ * Real.sqrt (kernelTrace Φ S))
    (mul_pos hr hΛ)
    (fun w x ↦ abs_rkhsPredictor_le Φ hΛ.le hr.le hdiag w x)
    (continuous_rkhsPredictor_weight Φ)
    (rkhs_empiricalRademacherComplexity_le_kernelTrace Φ Λ hΛ.le)
    hδ hδ_one
