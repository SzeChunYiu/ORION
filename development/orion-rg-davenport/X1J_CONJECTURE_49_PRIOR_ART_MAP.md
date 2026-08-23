# PRIOR-ART VERDICT — Gao-Geroldinger Survey Conjecture 4.9

## VERDICT
NOT open as a fresh problem. It is a named, actively-worked conjecture ("Gao's conjecture on
normal sequences" / Gao-Zhuang Conjecture 1.1). It is NOT settled in full generality, BUT
EVERY group class in the assigned task list is already a PUBLISHED THEOREM.

## IDENTITY (certain, not inferred)
Survey Conj 4.9 == Conjecture 1.1 of:
  W.D. Gao, J.J. Zhuang, "Sequences not containing long zero-sum subsequences",
  European J. Combin. 27 (2006), 777-787.
Girard states it as "Conjecture 1", attributes it to Gao, and explicitly cross-references
"[8, Conjecture 4.9]" where [8] is the Gao-Geroldinger survey. Identification is explicit
in the literature.

Verified statement (survey PDF, pdftotext, lines 512-514):
  "Conjecture 4.9. Let G = Cn1 + ... + Cnr with 1 < n1 | ... | nr, k in [1, n1-1] and
   S in F(G) a sequence of length |S| = k + d(G). If S has no zero-sum subsequence S'
   of length |S'| > k, then S = 0^k T where T in F(G) is zero-sumfree."
Lead's paraphrase is exact. (Survey typo in the following example: "v_g(S) = ord(g)-1"
should read v_g(T) = ord(g)-1.)

## PROVED CASES
P1. G cyclic .......................... Gao-Zhuang Thm 1.6(i)                    PROVED
P2. any G, k <= min(6, p-1) ........... Gao-Zhuang Thm 1.5   (p = least prime divisor)
P3. G = Cn (+) Cn, n has Property B ... Gao-Zhuang Thm 1.6(ii) / Thm 1.4
P4. G = Cp^r, p in {2,3,5,7} .......... Gao-Zhuang Thm 1.6(iii)  (implied by P2)
P5. any p-group, k in [1, p-1] ........ Girard Thm 2.1 (Alon-Friedland-Kalai)
P6. G = Cp (+) H, H any ab. p-group ... Girard Cor 2.2   FULL RANGE -> ALL elementary
                                        abelian Cp^r, every prime p.
P7. ALL rank-two groups Cm (+) Cmn .... Girard Thm 2.5, conditional on m having Property B.
    Girard's own "Note added in proof": Reiher proved Property B for all primes; with
    Gao-Geroldinger-Grynkiewicz "Inverse zero-sum problems III", Acta Arith. 141 (2010)
    103-152, ALL n >= 2 have Property B. Hence Thm 2.5 is UNCONDITIONAL:
    "gives a positive answer to Conjecture 1 for all Abelian groups of rank two."
P8. H. Guan, P. Yuan, X. Zeng, "Normal sequences over finite abelian groups",
    JCTA 118 (2011) 1519-1524, DOI 10.1016/j.jcta.2010.11.009. Girard: "Further progress
    has since been made on this conjecture [15]."
    S2 TLDR: "structure of short normal sequences over a finite Abelian p-group or a finite
    abelian group of rank two is obtained, thus answering positively a conjecture of Gao
    and Zhuang for various groups."
    *** CANNOT_CHECK_ACCESS: ScienceDirect 403. Exact strength unknown. It may or may not
    settle ALL p-groups (which would close my smallest open target). ***

## CONSEQUENCE FOR TASK 2 (small-group verification) - ALL TARGETS ALREADY THEOREMS
  C_4, C_5, C_6         cyclic              -> P1
  C_2^2, C_2^3          elem. abelian p=2   -> P6 (also P2, k<=1)
  C_3^2, C_3^3          elem. abelian p=3   -> P6 (also P2, k<=2)
  C_5^2                 elem. abelian p=5   -> P6 (also P2, k<=4)
  C_2 (+) C_4           rank two            -> P7 (also P2, k<=1)
NO COUNTEREXAMPLE CAN EXIST IN ANY ASSIGNED TARGET. Exhaustive search there can only
re-confirm published theorems (useful as enumerator validation, worthless as research).

## CONSEQUENCE FOR TASK 3 (structural attack) - ALL PROPOSED CLASSES ALREADY DONE
  cyclic -> P1 ; elementary p-groups -> P6 (all p) ; rank two -> P7 (unconditional).

## WHAT IS GENUINELY OPEN
Open exactly where k >= p AND G is neither cyclic, nor rank <= 2, nor of the form Cp (+) H.
I.e. rank >= 3 with n_1 composite (n_1 not prime).
Smallest computationally reachable target: G = C_4^3, |G| = 64, D(G) = 10, d(G) = 9,
  k in {2,3}  (|S| = 11 or 12).  Not covered by P1-P7.
Then: C_4 (+) C_4 (+) C_8, C_8^3, C_9^3, C_4^4; non-p-groups of rank >= 3 with n_1
composite, e.g. C_6^3 (k in [2,5]).
Caveat: if Guan-Yuan-Zeng (P8) settles all p-groups, the p-group targets above are closed
and only the non-p-group rank->=3 composite-n_1 zone remains.

Related open sub-problem: Gao-Zhuang Conjecture 5.3 - if W is zero-sum-free with
|W| = D(G)-1 and v_g(W) = ord(g)-1 for some g, then ord(g) >= n_1. This rules out the
obvious counterexample shape g^{ord(g)} W and is the natural obstruction.

## NAME COLLISIONS (traps avoided)
- arXiv:2311.02387 "A note on a Conjecture of Gao and Zhuang for groups of order 27"
  (Godara-Sarkar, 2024) is a DIFFERENT Gao-Zhuang conjecture: small Davenport constant
  d(G) of NON-abelian groups, product-one sequences. Not ours.
- Girard-Schmid rank-three papers' "Conjecture 2.2" is a different Gao conjecture
  (eta / EGZ constants). Not ours.

## SEARCHED / NOT SEARCHED
SEARCHED: web search on the conjecture name + full statement + adjacent phrasings;
retrieved and pdftotext-extracted FULL TEXT of: Gao-Zhuang preprint (Nankai, dated
2005-06-06), Girard arXiv:0903.3458v4 (= Rocky Mountain J. Math. 42 (2012) 583-596),
the Gao-Geroldinger survey PDF, Godara-Sarkar arXiv:2311.02387; Ebert-Grynkiewicz
arXiv:2211.08515 (abstract); Hui-Li arXiv:2510.14215 (Oct 2025, checked - unrelated);
Zhao arXiv:2506.21383 (Jun 2025, checked - different invariant s_{<=k}(G));
Crossref (exact record for GYZ); Semantic Scholar metadata + FULL citation graph of GYZ
(7 citing papers, all enumerated and triaged); arXiv API.
COULD NOT SEARCH / ACCESS: ScienceDirect full texts (HTTP 403) -> Gao-Zhuang published
EJC version (used the Nankai preprint instead) and Guan-Yuan-Zeng JCTA 2011 full text
are UNREAD. No MathSciNet, no zbMATH, no Google Scholar available.
