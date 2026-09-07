/* Independent re-implementation of step 5 of the D_3(C_7^3) = 36 proof:
 * the spectrum enumeration, the closure+corridor cut, and the complement-system
 * elimination.
 *
 * Deliberately different from verify_D3_C7_end_to_end_v3.py in three ways, so
 * that agreement is evidence about the mathematics and not about shared code:
 *
 *   (a) binomials come from Pascal's triangle built mod 7, not from exact
 *       integer binomials reduced afterwards;
 *   (b) consistency of each linear system is decided by the DUAL (Fredholm:
 *       compute the left null space of A and check every null vector kills b)
 *       rather than by the primal "is b in the column span" elimination;
 *   (c) length sets are 12-bit masks enumerated in C, not Python combinations.
 *
 * Caveat recorded in the accompanying note: this is a second implementation by
 * the same author.  It reduces implementation-error risk; it does not remove
 * author-level systematic risk, which needs a third party.
 */
#include <stdio.h>
#include <string.h>

#define P 7
#define NT 37
#define DD 19
#define LO 8
#define HI 19
#define NL (HI - LO + 1)          /* 12 admissible atom lengths */
#define MAXN 64
#define MAXR 64
#define MAXC 32

static int C[MAXN][MAXN];         /* Pascal mod 7 */

static void pascal(void) {
    for (int n = 0; n < MAXN; n++) {
        C[n][0] = 1;
        for (int k = 1; k <= n; k++)
            C[n][k] = (C[n-1][k-1] + (k <= n-1 ? C[n-1][k] : 0)) % P;
        for (int k = n+1; k < MAXN; k++) C[n][k] = 0;
    }
}

static int inv(int a) { int r = 1; for (int i = 0; i < P-2; i++) r = r*a % P; return r; }

/* Fredholm: A is nr x nc, b is nr.  Return 1 if A x = b is CONSISTENT.
 * Method: row-reduce [A | I] to find the left null space of A, then check that
 * every left null vector lambda satisfies lambda . b == 0. */
static int consistent(int A[MAXR][MAXC], int b[MAXR], int nr, int nc) {
    int M[MAXR][MAXC + MAXR];
    memset(M, 0, sizeof M);
    for (int i = 0; i < nr; i++) {
        for (int j = 0; j < nc; j++) M[i][j] = A[i][j] % P;
        M[i][nc + i] = 1;
    }
    int piv = 0;
    for (int c = 0; c < nc && piv < nr; c++) {
        int r = -1;
        for (int i = piv; i < nr; i++) if (M[i][c] % P) { r = i; break; }
        if (r < 0) continue;
        for (int j = 0; j < nc + nr; j++) { int t = M[piv][j]; M[piv][j] = M[r][j]; M[r][j] = t; }
        int iv = inv(M[piv][c]);
        for (int j = 0; j < nc + nr; j++) M[piv][j] = M[piv][j] * iv % P;
        for (int i = 0; i < nr; i++) {
            if (i == piv || !(M[i][c] % P)) continue;
            int f = M[i][c];
            for (int j = 0; j < nc + nr; j++) M[i][j] = ((M[i][j] - f * M[piv][j]) % P + P) % P;
        }
        piv++;
    }
    /* rows piv..nr-1 have zero A-part: their I-part is a left null vector */
    for (int i = piv; i < nr; i++) {
        int s = 0;
        for (int j = 0; j < nr; j++) s = (s + M[i][nc + j] * b[j]) % P;
        if (s % P) return 0;              /* lambda.b != 0  =>  inconsistent */
    }
    return 1;
}

/* The spectrum system for T at length NT, with the length set given by `mask`.
 * Columns: one per present length L (atom + complement contribution), plus one
 * per overlap length in {18,19} that is present. */
static int feas_T(int mask) {
    int A[MAXR][MAXC], b[MAXR];
    int nc = 0, col[MAXC], kind[MAXC];
    for (int i = 0; i < NL; i++) if (mask >> i & 1) { col[nc] = LO + i; kind[nc] = 0; nc++; }
    for (int L = 18; L <= 19; L++) if (mask >> (L - LO) & 1) { col[nc] = L; kind[nc] = 1; nc++; }
    int nr = 0;
    for (int d = 0; d <= NT - DD; d++, nr++) {
        for (int j = 0; j < nc; j++) {
            int L = col[j], sg = (L & 1) ? P - 1 : 1;
            A[nr][j] = kind[j] == 0
                ? (int)((long)sg * ((C[L][d] - C[NT-L][d] + P) % P) % P)
                : (int)((long)(P - sg) % P * C[L][d] % P);
        }
        b[nr] = ((-(C[0][d] - C[NT][d]) % P) + P) % P;
    }
    return consistent(A, b, nr, nc);
}

/* The complement system: C = T A^{-1} of length m, allowed proper zero-sum
 * lengths S, paired under l <-> m-l. */
static int feas_C(int m, int Smask) {
    if (m <= DD) return 1;
    int A[MAXR][MAXC], b[MAXR];
    int rep[MAXC], nc = 0;
    for (int L = LO; L <= HI; L++) {
        if (!(Smask >> (L - LO) & 1)) continue;
        int r = L < m - L ? L : m - L, seen = 0;
        for (int j = 0; j < nc; j++) if (rep[j] == r) seen = 1;
        if (!seen) rep[nc++] = r;
    }
    if (!nc) return 0;
    int nr = 0;
    for (int d = 0; d <= m - DD; d++, nr++) {
        for (int j = 0; j < nc; j++) A[nr][j] = 0;
        for (int L = LO; L <= HI; L++) {
            if (!(Smask >> (L - LO) & 1)) continue;
            int r = L < m - L ? L : m - L, jj = -1;
            for (int j = 0; j < nc; j++) if (rep[j] == r) jj = j;
            int sg = (L & 1) ? P - 1 : 1;
            A[nr][jj] = (A[nr][jj] + sg * C[L][d]) % P;
        }
        int par = (m & 1) ? P - 1 : 1;
        b[nr] = ((-(C[0][d] + par * C[m][d]) % P) + P) % P;
    }
    return consistent(A, b, nr, nc);
}

static int corridor6[6][3] = {{8,10,19},{9,9,19},{9,10,18},{9,11,17},{9,12,16},{10,10,17}};
static int corridor4[4][3] = {{8,10,19},{9,9,19},{9,10,18},{10,10,17}};

static int has(int mask, int L) { return L >= LO && L <= HI && (mask >> (L - LO) & 1); }

static int run(int (*cor)[3], int ncor, const char *tag) {
    int nfeas = 0, nsurv = 0, nkilled = 0;
    for (int mask = 1; mask < (1 << NL); mask++) {
        if (!feas_T(mask)) continue;
        nfeas++;
        int s = 0; for (int L = LO; L <= HI; L++) if (has(mask, L)) { s = L; break; }
        /* closure: every present length must sit in some 3-atom profile inside
         * the set, unless it pairs with its own complement (18/19) */
        int ok = 1;
        for (int L = LO; L <= HI && ok; L++) {
            if (!has(mask, L)) continue;
            int found = 0;
            for (int u = s; u <= NT - L - u; u++)
                if (has(mask, u) && has(mask, NT - L - u) && NT - L - u >= s) { found = 1; break; }
            if (!found && !((L == 18 || L == 19) && has(mask, NT - L))) ok = 0;
        }
        if (!ok) continue;
        /* every profile that uses the shortest length must be a corridor triple */
        for (int L = LO; L <= HI && ok; L++) {
            if (!has(mask, L)) continue;
            for (int u = s; u <= NT - L - u && ok; u++) {
                int v = NT - L - u;
                if (!has(mask, u) || !has(mask, v) || v < s) continue;
                int t[3] = {L, u, v};
                for (int a = 0; a < 3; a++) for (int bb = a+1; bb < 3; bb++)
                    if (t[a] > t[bb]) { int z = t[a]; t[a] = t[bb]; t[bb] = z; }
                if (t[0] != s && t[1] != s && t[2] != s) continue;
                int inc = 0;
                for (int c = 0; c < ncor; c++)
                    if (t[0]==cor[c][0] && t[1]==cor[c][1] && t[2]==cor[c][2]) inc = 1;
                if (!inc) ok = 0;
            }
        }
        if (!ok) continue;
        int anycor = 0;
        for (int c = 0; c < ncor; c++)
            if (has(mask, cor[c][0]) && has(mask, cor[c][1]) && has(mask, cor[c][2])) anycor = 1;
        if (!anycor) continue;
        nsurv++;
        /* complement systems */
        int alive = 1;
        for (int L = LO; L <= HI && alive; L++) {
            if (!has(mask, L)) continue;
            int m = NT - L, Sm = 0;
            for (int x = LO; x <= HI; x++)
                if (has(mask, x) && x <= m - LO && has(mask, m - x)) Sm |= 1 << (x - LO);
            if (!feas_C(m, Sm)) alive = 0;
        }
        if (!alive) nkilled++;
    }
    printf("%s  feasible spectra %d ; after closure+corridor %d ; eliminated by "
           "complement systems %d ; SURVIVING %d\n",
           tag, nfeas, nsurv, nkilled, nsurv - nkilled);
    return nsurv - nkilled;
}

int main(void) {
    pascal();
    /* control: Pascal mod 7 must satisfy Lucas on a sample */
    if (C[14][7] != 2 || C[19][0] != 1 || C[10][3] != 1 ||
        C[13][5] != 6 || C[27][7] != 3 || C[37][9] != 5) {
        printf("PASCAL CONTROL FAILED\n"); return 2;
    }
    int a = run(corridor6, 6, "recorded 6-triple corridor:");
    int b = run(corridor4, 4, "tightened 4-triple corridor:");
    if (a == 0 && b == 0) { printf("PASS: no obstruction survives, both corridors\n"); return 0; }
    printf("MISMATCH\n"); return 1;
}
