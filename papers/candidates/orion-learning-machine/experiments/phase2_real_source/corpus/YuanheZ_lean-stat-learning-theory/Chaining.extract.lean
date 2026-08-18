-- Source extract from SLT/Chaining.lean @ db9ee417b837a76cf2af9169d2d6a44ef3990053
lemma dyadicScale_pos {D : ℝ} (hD : 0 < D) (k : ℕ) : 0 < dyadicScale D k := by
  unfold dyadicScale
  apply mul_pos hD
  apply zpow_pos (by norm_num : (0 : ℝ) < 2)

lemma dyadicScale_mono {D : ℝ} (hD : 0 < D) {k₁ k₂ : ℕ} (h : k₁ ≤ k₂) :
    dyadicScale D k₂ ≤ dyadicScale D k₁ := by
  unfold dyadicScale
  apply mul_le_mul_of_nonneg_left _ (le_of_lt hD)
  apply zpow_le_zpow_right₀ (by norm_num : (1 : ℝ) ≤ 2)
  simp only [neg_le_neg_iff, Int.ofNat_le]
  exact h

lemma dyadicScale_zero (D : ℝ) : dyadicScale D 0 = D := by
  unfold dyadicScale
  simp

lemma dyadicScale_succ (D : ℝ) (k : ℕ) : dyadicScale D (k + 1) = dyadicScale D k / 2 := by
  unfold dyadicScale
  simp only [Nat.cast_add, Nat.cast_one, neg_add, zpow_add₀ (by norm_num : (2 : ℝ) ≠ 0)]
  ring

theorem exists_dyadicNets {s : Set A} (hs : TotallyBounded s) {D : ℝ} (hD : 0 < D) :
    Nonempty (DyadicNets s D) := by
  have h : ∀ k, ∃ t : Finset A, IsENet t (dyadicScale D k) s ∧ (t : Set A) ⊆ s := by
    intro k
    exact exists_finset_isENet_subset_of_totallyBounded (dyadicScale_pos hD k) hs
  choose nets hnets using h
  exact ⟨⟨nets, fun k => (hnets k).1, fun k => (hnets k).2⟩⟩

lemma exists_near_in_net {t : Finset A} {eps : ℝ} {s : Set A}
    (hnet : IsENet t eps s) {x : A} (hx : x ∈ s) :
    ∃ y ∈ t, dist x y ≤ eps := by
  have := hnet hx
  rw [mem_iUnion₂] at this
  obtain ⟨y, hy_mem, hy_ball⟩ := this
  exact ⟨y, hy_mem, mem_closedBall.mp hy_ball⟩

theorem telescoping_bound {D : ℝ} (k : ℕ)
    {x y_k : A} (hy_k_near : dist x y_k ≤ dyadicScale D k)
    {y_k1 : A} (hy_k1_near : dist x y_k1 ≤ dyadicScale D (k + 1)) :
    dist y_k y_k1 ≤ dyadicScale D k + dyadicScale D (k + 1) := by
  calc dist y_k y_k1 ≤ dist y_k x + dist x y_k1 := dist_triangle _ _ _
    _ ≤ dyadicScale D k + dyadicScale D (k + 1) := by
        apply add_le_add
        · rw [dist_comm]; exact hy_k_near
        · exact hy_k1_near

theorem telescoping_bound' {D : ℝ} (k : ℕ)
    {x y_k : A} (hy_k_near : dist x y_k ≤ dyadicScale D k)
    {y_k1 : A} (hy_k1_near : dist x y_k1 ≤ dyadicScale D (k + 1)) :
    dist y_k y_k1 ≤ 3 / 2 * dyadicScale D k := by
  calc dist y_k y_k1
    _ ≤ dyadicScale D k + dyadicScale D (k + 1) := telescoping_bound k hy_k_near hy_k1_near
    _ = dyadicScale D k + dyadicScale D k / 2 := by rw [dyadicScale_succ]
    _ = 3 / 2 * dyadicScale D k := by ring

lemma nearestInFinset_mem (t : Finset A) (ht : t.Nonempty) (x : A) :
    nearestInFinset t ht x ∈ t := by
  unfold nearestInFinset
  exact (Classical.choose_spec (Finset.exists_mem_eq_inf' ht (fun y => dist x y))).1

lemma dist_nearestInFinset_le (t : Finset A) (ht : t.Nonempty) (x : A) (y : A) (hy : y ∈ t) :
    dist x (nearestInFinset t ht x) ≤ dist x y := by
  unfold nearestInFinset
  have hspec := Classical.choose_spec (Finset.exists_mem_eq_inf' ht (fun y => dist x y))
  rw [← hspec.2]
  exact Finset.inf'_le _ hy
