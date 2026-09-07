# Donor-derived D2 formula for rank-three prime-power groups — V1

Status: derivation complete; donor-derived; novelty/priority CANNOT_CHECK.

For prime p>=5, a>=1 and n=p^a, the donor ingredients imply

D_2(C_n^3) = (9n-5)/2.

The lower bound is the specialization of Freeze--Schmid Theorem 4.1 with s=3,t=1, using D(C_n^3)=D*(C_n^3)=3n-2 for p-groups.

For the matching upper bound, append g=-sigma(S) to any sequence S of length (9n-5)/2, giving a zero-sum sequence T of length (9n-3)/2. Apply Zhao Lemma 4.4 with q=(3n+1)/2 and i=2. Its coefficient is

  a_2 = C(3n-2,(3n-3)/2) + C(3n-1,(3n-1)/2).

Lucas' theorem gives, with r=(p-1)/2 and epsilon=(-1)^(a r),

  C(3n-2,(3n-3)/2) = epsilon mod p,
  C(3n-1,(3n-1)/2) = 2 epsilon mod p,

so a_2 = 3 epsilon mod p, nonzero for p>=5. Zhao therefore gives a nonempty zero-sum U of length at most (3n-1)/2. Its zero-sum complement has length at least 3n-1. Removing one term leaves at least D(G)=3n-2 terms, hence a nonempty zero-sum V; the remaining complement W is also nonempty and zero-sum. Thus T has three disjoint nonempty zero-sums, and at most one uses the appended g, so S has two.

Characteristic 3 is singular for this route because a_2=0 mod 3. This is recorded only as a mechanism signal, not as a causal explanation of the known C_3^3 behaviour.

Donors: Freeze--Schmid (Discrete Math. 310 (2010), DOI 10.1016/j.disc.2010.07.028, arXiv:0905.4248); Olson (JNT 1 (1969)); Zhao (arXiv:2506.21383, Lemma 4.4).

No priority claim is made.