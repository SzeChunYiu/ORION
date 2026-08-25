/* Exact support-nine discriminator for a hypothetical length-31
 * zero-sum short-free sequence over C_5^3.
 *
 * A symbolic reduction in the manuscript shows that a saturated short-free
 * sequence has no multiplicity-3 support point.  For
 * support size 9 and total length 31, the only surviving multiplicity pattern is
 *
 *                    4^7 2^1 1^1.
 *
 * This program searches ALL rank-3 zero-sum short-free sequences with that
 * pattern after GL(3,5) basis normalization.  It does not assume saturation
 * during the search, so an UNSAT result is stronger than the branch needed.
 *
 * Completeness of normalization:
 * every rank-3 support contains an ordered independent triple; an element of
 * GL(3,5) maps that triple to e1,e2,e3.  We loop every multiplicity assignment
 * to the three normalized basis points consistent with 4^7 2 1.  The six
 * remaining support points are ordered canonically.  Five are enumerated and
 * the sixth is forced by the total-sum equation; every multiplicity 1,2,4 is
 * invertible mod 5.
 *
 * Two exact engines use different reachability representations and opposite
 * candidate orderings:
 *
 *   A. byte exact-weight subset-sum reachability, ascending support order;
 *   B. two-word bitset exact-weight reachability, descending support order.
 *
 * Both reject immediately when adding a source term creates a nonempty
 * zero-sum subsequence of length <=5.
 *
 * Interpretation: bounded same-package replay.  The program does not re-prove
 * the symbolic reduction that defines its finite search domain.
 */

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define P 5
#define N 125
#define T 5
#define SUPPORT 9

static unsigned char ADD[N][N];
static int SUP[SUPPORT];
static int MUL[SUPPORT];

typedef struct { unsigned char r[T + 1][N]; } ByteReach;
typedef struct { uint64_t lo[T + 1], hi[T + 1]; } BitReach;

typedef struct {
    long long nodes;
    long long forced_final_candidates;
    long long solutions;
} Counts;

static int is_basis(int v) { return v == 25 || v == 5 || v == 1; }

static int negv(int v) {
    int x = v / 25, y = (v / 5) % 5, z = v % 5;
    return ((P - x) % P) * 25 + ((P - y) % P) * 5 + ((P - z) % P);
}

static int scalev(int c, int v) {
    int x = v / 25, y = (v / 5) % 5, z = v % 5;
    return ((c * x) % P) * 25 + ((c * y) % P) * 5 + ((c * z) % P);
}

static int add_multiple_sum(int sum, int v, int m) {
    for (int i = 0; i < m; ++i) sum = ADD[sum][v];
    return sum;
}

static int inv_mod5(int m) {
    if (m == 1) return 1;
    if (m == 2) return 3;
    if (m == 4) return 4;
    fprintf(stderr, "noninvertible/invalid multiplicity %d\n", m);
    exit(2);
}

static int forced_final_point(int current_sum, int multiplicity) {
    /* current_sum + multiplicity * q = 0 */
    return scalev(inv_mod5(multiplicity), negv(current_sum));
}

static int remaining_point_count(const int cnt[5]) {
    return cnt[1] + cnt[2] + cnt[4];
}

static int sole_remaining_multiplicity(const int cnt[5]) {
    int m = 0;
    for (int x = 1; x <= 4; ++x) {
        if (cnt[x] == 0) continue;
        if (cnt[x] != 1 || m != 0) return 0;
        m = x;
    }
    return m;
}

static int consume_basis_counts(int m1, int m2, int m3, int out[5]) {
    memset(out, 0, 5 * sizeof(int));
    out[1] = 1;
    out[2] = 1;
    out[4] = 7;
    int ms[3] = {m1, m2, m3};
    for (int i = 0; i < 3; ++i) {
        int m = ms[i];
        if (!(m == 1 || m == 2 || m == 4) || out[m] == 0) return 0;
        --out[m];
    }
    return remaining_point_count(out) == 6;
}

/* ---------------- Engine A: byte exact-weight reachability ---------------- */

static int byte_add_one(const ByteReach *in, int v, ByteReach *out) {
    memcpy(out, in, sizeof(*out));
    for (int w = T; w >= 1; --w) {
        for (int s = 0; s < N; ++s) {
            if (!in->r[w - 1][s]) continue;
            int q = ADD[s][v];
            if (q == 0) return 0;
            out->r[w][q] = 1;
        }
    }
    return 1;
}

static int byte_add_m(const ByteReach *in, int v, int m, ByteReach *out) {
    ByteReach a, b;
    const ByteReach *cur = in;
    ByteReach *next = &a;
    for (int i = 0; i < m; ++i) {
        if (!byte_add_one(cur, v, next)) return 0;
        cur = next;
        next = (next == &a) ? &b : &a;
    }
    memcpy(out, cur, sizeof(*out));
    return 1;
}

static void byte_dfs(const ByteReach *reach, int depth, int start,
                     const int cnt_in[5], int current_sum, Counts *c) {
    ++c->nodes;
    int rem = remaining_point_count(cnt_in);
    if (rem == 1) {
        int m = sole_remaining_multiplicity(cnt_in);
        if (!m) { fprintf(stderr, "bad remaining count in byte engine\n"); exit(2); }
        int q = forced_final_point(current_sum, m);
        if (q == 0 || q < start || q >= N || is_basis(q)) return;
        ++c->forced_final_candidates;
        ByteReach final;
        if (!byte_add_m(reach, q, m, &final)) return;
        SUP[depth] = q;
        MUL[depth] = m;
        if (add_multiple_sum(current_sum, q, m) != 0) {
            fprintf(stderr, "forced-point arithmetic defect\n"); exit(2);
        }
        ++c->solutions;
        return;
    }

    for (int v = start; v < N; ++v) {
        if (is_basis(v)) continue;
        for (int m_index = 0; m_index < 3; ++m_index) {
            static const int labels[3] = {4, 2, 1};
            int m = labels[m_index];
            if (cnt_in[m] == 0) continue;
            ByteReach next;
            if (!byte_add_m(reach, v, m, &next)) continue;
            int cnt[5]; memcpy(cnt, cnt_in, sizeof(cnt)); --cnt[m];
            SUP[depth] = v; MUL[depth] = m;
            byte_dfs(&next, depth + 1, v + 1, cnt,
                     add_multiple_sum(current_sum, v, m), c);
        }
    }
}

static Counts run_byte_engine(void) {
    Counts c = {0, 0, 0};
    static const int labels[3] = {4, 2, 1};
    for (int a = 0; a < 3; ++a)
    for (int b = 0; b < 3; ++b)
    for (int d = 0; d < 3; ++d) {
        int m1 = labels[a], m2 = labels[b], m3 = labels[d];
        int cnt[5];
        if (!consume_basis_counts(m1, m2, m3, cnt)) continue;

        ByteReach r0, r1, r2, r3;
        memset(&r0, 0, sizeof(r0)); r0.r[0][0] = 1;
        if (!byte_add_m(&r0, 25, m1, &r1)) continue;
        if (!byte_add_m(&r1, 5,  m2, &r2)) continue;
        if (!byte_add_m(&r2, 1,  m3, &r3)) continue;

        SUP[0] = 25; MUL[0] = m1;
        SUP[1] = 5;  MUL[1] = m2;
        SUP[2] = 1;  MUL[2] = m3;
        int sum = 0;
        sum = add_multiple_sum(sum, 25, m1);
        sum = add_multiple_sum(sum, 5,  m2);
        sum = add_multiple_sum(sum, 1,  m3);
        byte_dfs(&r3, 3, 2, cnt, sum, &c);
    }
    return c;
}

/* ---------------- Engine B: bitset reachability / reverse order ----------- */

static inline void bit_set(uint64_t *lo, uint64_t *hi, int x) {
    if (x < 64) *lo |= 1ULL << x;
    else *hi |= 1ULL << (x - 64);
}

static int bit_add_one(const BitReach *in, int v, BitReach *out) {
    *out = *in;
    for (int w = T; w >= 1; --w) {
        uint64_t lo = in->lo[w - 1], hi = in->hi[w - 1];
        while (lo) {
            int s = __builtin_ctzll(lo); lo &= lo - 1;
            int q = ADD[s][v];
            if (q == 0) return 0;
            bit_set(&out->lo[w], &out->hi[w], q);
        }
        while (hi) {
            int bit = __builtin_ctzll(hi); hi &= hi - 1;
            int s = bit + 64;
            if (s >= N) continue;
            int q = ADD[s][v];
            if (q == 0) return 0;
            bit_set(&out->lo[w], &out->hi[w], q);
        }
    }
    return 1;
}

static int bit_add_m(const BitReach *in, int v, int m, BitReach *out) {
    BitReach a, b;
    const BitReach *cur = in;
    BitReach *next = &a;
    for (int i = 0; i < m; ++i) {
        if (!bit_add_one(cur, v, next)) return 0;
        cur = next;
        next = (next == &a) ? &b : &a;
    }
    *out = *cur;
    return 1;
}

static void bit_dfs_reverse(const BitReach *reach, int depth, int upper,
                            const int cnt_in[5], int current_sum, Counts *c) {
    ++c->nodes;
    int rem = remaining_point_count(cnt_in);
    if (rem == 1) {
        int m = sole_remaining_multiplicity(cnt_in);
        if (!m) { fprintf(stderr, "bad remaining count in bit engine\n"); exit(2); }
        int q = forced_final_point(current_sum, m);
        if (q <= 0 || q >= upper || is_basis(q)) return;
        ++c->forced_final_candidates;
        BitReach final;
        if (!bit_add_m(reach, q, m, &final)) return;
        if (add_multiple_sum(current_sum, q, m) != 0) {
            fprintf(stderr, "forced-point arithmetic defect\n"); exit(2);
        }
        ++c->solutions;
        return;
    }

    for (int v = upper - 1; v >= 1; --v) {
        if (is_basis(v)) continue;
        static const int labels[3] = {1, 2, 4};
        for (int m_index = 0; m_index < 3; ++m_index) {
            int m = labels[m_index];
            if (cnt_in[m] == 0) continue;
            BitReach next;
            if (!bit_add_m(reach, v, m, &next)) continue;
            int cnt[5]; memcpy(cnt, cnt_in, sizeof(cnt)); --cnt[m];
            bit_dfs_reverse(&next, depth + 1, v, cnt,
                            add_multiple_sum(current_sum, v, m), c);
        }
    }
}

static Counts run_bit_engine(void) {
    Counts c = {0, 0, 0};
    static const int labels[3] = {1, 2, 4};
    for (int a = 0; a < 3; ++a)
    for (int b = 0; b < 3; ++b)
    for (int d = 0; d < 3; ++d) {
        int m1 = labels[a], m2 = labels[b], m3 = labels[d];
        int cnt[5];
        if (!consume_basis_counts(m1, m2, m3, cnt)) continue;

        BitReach r0, r1, r2, r3;
        memset(&r0, 0, sizeof(r0)); bit_set(&r0.lo[0], &r0.hi[0], 0);
        if (!bit_add_m(&r0, 25, m1, &r1)) continue;
        if (!bit_add_m(&r1, 5,  m2, &r2)) continue;
        if (!bit_add_m(&r2, 1,  m3, &r3)) continue;

        int sum = 0;
        sum = add_multiple_sum(sum, 25, m1);
        sum = add_multiple_sum(sum, 5,  m2);
        sum = add_multiple_sum(sum, 1,  m3);
        bit_dfs_reverse(&r3, 3, N, cnt, sum, &c);
    }
    return c;
}

int main(void) {
    for (int a = 0; a < N; ++a) {
        int ax = a / 25, ay = (a / 5) % 5, az = a % 5;
        for (int b = 0; b < N; ++b) {
            int bx = b / 25, by = (b / 5) % 5, bz = b % 5;
            ADD[a][b] = (unsigned char)(
                ((ax + bx) % 5) * 25 +
                ((ay + by) % 5) * 5 +
                ((az + bz) % 5));
        }
    }

    Counts a = run_byte_engine();
    Counts b = run_bit_engine();
    int both_unsat = (a.solutions == 0 && b.solutions == 0);

    printf("{\n");
    printf("  \"schema\": \"conditional-width-one-bounds.support-nine-replay.v1\",\n");
    printf("  \"interpretation\": \"bounded same-package replay; symbolic reduction is not re-proved here\",\n");
    printf("  \"group\": \"C_5^3\",\n");
    printf("  \"length\": 31,\n");
    printf("  \"support_size\": 9,\n");
    printf("  \"multiplicity_pattern\": \"4^7 2^1 1^1\",\n");
    printf("  \"normalization\": \"loop every basis multiplicity assignment; enumerate remaining support canonically; force final point from total sum\",\n");
    printf("  \"byte_engine\": {\"nodes\": %lld, \"forced_final_candidates\": %lld, \"solutions\": %lld},\n",
           a.nodes, a.forced_final_candidates, a.solutions);
    printf("  \"bit_reverse_engine\": {\"nodes\": %lld, \"forced_final_candidates\": %lld, \"solutions\": %lld},\n",
           b.nodes, b.forced_final_candidates, b.solutions);
    printf("  \"both_engines_unsat\": %s,\n", both_unsat ? "true" : "false");
    printf("  \"conditional_consequence\": \"combined with the symbolic no-multiplicity-3 lemma and support-8 check, isolated replay would force any length-31 zero-sum short-free obstruction to have support at least 10\"\n");
    printf("}\n");

    return both_unsat ? 0 : 1;
}
