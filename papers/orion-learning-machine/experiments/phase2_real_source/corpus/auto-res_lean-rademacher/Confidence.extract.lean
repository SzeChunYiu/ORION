-- Source extract from FoML/Generalization/Confidence.lean @ 53c6d96d9cab50a3ada834141510d93336edd67b
lemma deterministicConfidenceRadius_nonneg
    {b δ : ℝ} (hb : 0 ≤ b) :
    0 ≤ deterministicConfidenceRadius b δ n := by
  exact mul_nonneg hb (Real.sqrt_nonneg _)

lemma sampleConfidenceRadius_nonneg
    {b δ : ℝ} (hb : 0 ≤ b) :
    0 ≤ sampleConfidenceRadius b δ n := by
  exact mul_nonneg hb (Real.sqrt_nonneg _)

lemma exp_neg_deterministicConfidenceRadius_sq
    (hn : 0 < n) {b δ : ℝ}
    (hb : 0 < b) (hδ : 0 < δ) (hδ_one : δ ≤ 1) :
    (-deterministicConfidenceRadius b δ n ^ 2 * n /
        (2 * b ^ 2)).exp = δ := by
  have h := mul_exp_neg_confidenceRadius_sq
    hn (κ := 1) (b := b) (δ := δ) zero_lt_one hb hδ hδ_one
  simpa [deterministicConfidenceRadius] using h

lemma two_mul_exp_neg_sampleConfidenceRadius_sq
    (hn : 0 < n) {b δ : ℝ}
    (hb : 0 < b) (hδ : 0 < δ) (hδ_one : δ ≤ 1) :
    2 * (-sampleConfidenceRadius b δ n ^ 2 * n /
        (2 * b ^ 2)).exp = δ := by
  apply mul_exp_neg_confidenceRadius_sq
    hn (κ := 2) (b := b) (δ := δ) (by norm_num) hb hδ
  linarith

theorem uniform_deviation_tail_bound_countable_of_rademacher_le_delta
    [MeasurableSpace 𝒳] [Nonempty 𝒳] [Nonempty H] [Countable H]
    [IsProbabilityMeasure μ]
    (hn : 0 < n) (F : H → 𝒳 → ℝ) (hF_meas : ∀ h, Measurable (F h))
    (X : Ω → 𝒳) (hX : Measurable X)
    {b C δ : ℝ} (hb : 0 < b) (hF_bound : ∀ h x, |F h x| ≤ b)
    (hC : rademacherComplexity n F μ X ≤ C)
    (hδ : 0 < δ) (hδ_one : δ ≤ 1) : True := by
  calc
    _ ≤ (-deterministicConfidenceRadius b δ n ^ 2 * n /
          (2 * b ^ 2)).exp :=
      uniform_deviation_tail_bound_countable_of_rademacher_le
        (μ := μ) F hF_meas X hX hb hF_bound hC
        (deterministicConfidenceRadius_nonneg hb.le)
    _ = δ :=
      exp_neg_deterministicConfidenceRadius_sq hn hb hδ hδ_one

theorem uniform_deviation_tail_bound_countable_of_empirical_le_delta
    [MeasurableSpace 𝒳] [Nonempty 𝒳] [Nonempty H] [Countable H]
    [IsProbabilityMeasure μ]
    (hn : 0 < n) (F : H → 𝒳 → ℝ) (hF_meas : ∀ h, Measurable (F h))
    (X : Ω → 𝒳) (hX : Measurable X) {b C δ : ℝ}
    (hb : 0 < b) (hF_bound : ∀ h x, |F h x| ≤ b)
    (hC : ∀ S : Fin n → 𝒳, empiricalRademacherComplexity n F S ≤ C)
    (hδ : 0 < δ) (hδ_one : δ ≤ 1) : True := by
  apply uniform_deviation_tail_bound_countable_of_rademacher_le_delta
    (μ := μ) hn F hF_meas X hX hb hF_bound _ hδ hδ_one
  exact rademacherComplexity_le_of_empirical_le_countable
    (fun h ↦ (hF_meas h).comp hX) hb.le hF_bound hC

theorem uniform_deviation_tail_bound_separable_of_empirical_le_delta
    [MeasurableSpace 𝒳] [Nonempty 𝒳] [Nonempty H]
    [TopologicalSpace H] [SeparableSpace H] [FirstCountableTopology H]
    [IsProbabilityMeasure μ]
    (hn : 0 < n) (F : H → 𝒳 → ℝ) (hF_meas : ∀ h, Measurable (F h))
    (X : Ω → 𝒳) (hX : Measurable X) {b C δ : ℝ}
    (hb : 0 < b) (hF_bound : ∀ h x, |F h x| ≤ b)
    (hF_cont : ∀ x : 𝒳, Continuous fun h ↦ F h x)
    (hC : ∀ S : Fin n → 𝒳, empiricalRademacherComplexity n F S ≤ C)
    (hδ : 0 < δ) (hδ_one : δ ≤ 1) : True := by
  simpa [deterministicConfidenceRadius, confidenceRadius] using
    uniform_deviation_tail_bound_separable_of_rademacher_le_delta
      (μ := μ) hn F hF_meas X hX hb hF_bound hF_cont
      (rademacherComplexity_le_of_empirical_le_separable
        F X (fun h ↦ (hF_meas h).comp hX) hb.le hF_bound hF_cont hC)
      hδ hδ_one
