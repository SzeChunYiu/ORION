/* Exact normalized support-eight check for a length-31 obstruction.
 *
 * Mathematical role:
 *   If a 31-term zero-sum short-free S over C_5^3 has support size 8, then
 *   every multiplicity is <=4 and the multiplicity pattern is 4^7 3^1.
 *   Let x be the multiplicity-3 support point and U=supp(S). Adding one more x
 *   cannot create a new zero-sum of length <=5: a genuinely new relation would
 *   need four copies of x, hence has room for at most one further term; that
 *   term would have to be x, requiring five copies. Thus U^4 is still short-free.
 *   Since sigma(S)=0 and sigma(U^4)=4 sigma(U)=-sigma(U), necessarily
 *       x = -sigma(U) in U.
 *
 *   Property C says every length-32 short-free sequence has the form U^4 with
 *   |U|=8. Therefore a support-size-8 C0(31) obstruction requires a support U
 *   such that U^4 is short-free and -sigma(U) belongs to U.
 *
 * This program exhausts that support condition after GL(3,5) basis
 * normalization. Every rank-3 support contains an ordered independent triple,
 * which can be sent to e1,e2,e3. Rank <=2 is donor-closed by the rank-two
 * short-zero-sum constant and cannot support a 32-term short-free sequence.
 *
 * Two independently represented exact subset-sum engines are run:
 *   A. byte-array exact-weight reachability;
 *   B. two-word bitset exact-weight reachability, with reverse candidate order.
 *
 * Each selected support point is inserted four times. A branch is rejected iff
 * a nonempty zero-sum of length <=5 appears. At depth 8, test
 * -sigma(U) in U.
 *
 * Expected replay result: 564 normalized supports, 0 satisfying
 * -sigma(U) in U.  This bounded search is not an independent proof of the
 * symbolic normalization used to define its search domain.
 */

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define P 5
#define N 125
#define T 5
#define SUPPORT 8

static unsigned char ADD[N][N];
static int SUP[SUPPORT];

typedef struct {
    unsigned char r[T + 1][N];
} ByteReach;

typedef struct {
    uint64_t lo[T + 1];
    uint64_t hi[T + 1];
} BitReach;

typedef struct {
    long long nodes;
    long long supports;
    long long target_in_support;
} Counts;

static int negv(int v) {
    int x = v / 25;
    int y = (v / 5) % 5;
    int z = v % 5;
    return ((P - x) % P) * 25 + ((P - y) % P) * 5 + ((P - z) % P);
}

static int support_target(void) {
    int sum = 0;
    for (int i = 0; i < SUPPORT; ++i) sum = ADD[sum][SUP[i]];
    return negv(sum);
}

static int target_is_in_support(int target) {
    for (int i = 0; i < SUPPORT; ++i) if (SUP[i] == target) return 1;
    return 0;
}

/* ---------- Engine A: byte-array exact-weight reachability ---------- */

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

static int byte_add_four(const ByteReach *in, int v, ByteReach *out) {
    ByteReach a, b;
    const ByteReach *cur = in;
    ByteReach *next = &a;
    for (int j = 0; j < 4; ++j) {
        if (!byte_add_one(cur, v, next)) return 0;
        cur = next;
        next = (next == &a) ? &b : &a;
    }
    memcpy(out, cur, sizeof(*out));
    return 1;
}

static void byte_dfs(const ByteReach *reach, int depth, int start, Counts *c) {
    ++c->nodes;
    if (depth == SUPPORT) {
        ++c->supports;
        if (target_is_in_support(support_target())) ++c->target_in_support;
        return;
    }

    for (int v = start; v < N; ++v) {
        if (v == 1 || v == 5 || v == 25) continue;
        ByteReach next;
        if (!byte_add_four(reach, v, &next)) continue;
        SUP[depth] = v;
        byte_dfs(&next, depth + 1, v + 1, c);
    }
}

static Counts run_byte_engine(void) {
    Counts c = {0, 0, 0};
    ByteReach r0, r1, r2, r3;
    memset(&r0, 0, sizeof(r0));
    r0.r[0][0] = 1;

    SUP[0] = 25; /* e1=(1,0,0) */
    SUP[1] = 5;  /* e2=(0,1,0) */
    SUP[2] = 1;  /* e3=(0,0,1) */

    if (!byte_add_four(&r0, 25, &r1) ||
        !byte_add_four(&r1, 5, &r2) ||
        !byte_add_four(&r2, 1, &r3)) {
        fprintf(stderr, "byte engine rejected normalized basis\n");
        exit(2);
    }

    byte_dfs(&r3, 3, 2, &c);
    return c;
}

/* ---------- Engine B: two-word bitset exact-weight reachability ---------- */

static inline void bit_set(uint64_t *lo, uint64_t *hi, int x) {
    if (x < 64) *lo |= 1ULL << x;
    else *hi |= 1ULL << (x - 64);
}

static int bit_add_one(const BitReach *in, int v, BitReach *out) {
    *out = *in;
    for (int w = T; w >= 1; --w) {
        uint64_t lo = in->lo[w - 1];
        uint64_t hi = in->hi[w - 1];
        while (lo) {
            int b = __builtin_ctzll(lo);
            lo &= lo - 1;
            int q = ADD[b][v];
            if (q == 0) return 0;
            bit_set(&out->lo[w], &out->hi[w], q);
        }
        while (hi) {
            int b = __builtin_ctzll(hi);
            hi &= hi - 1;
            int s = b + 64;
            if (s >= N) continue;
            int q = ADD[s][v];
            if (q == 0) return 0;
            bit_set(&out->lo[w], &out->hi[w], q);
        }
    }
    return 1;
}

static int bit_add_four(const BitReach *in, int v, BitReach *out) {
    BitReach a, b;
    const BitReach *cur = in;
    BitReach *next = &a;
    for (int j = 0; j < 4; ++j) {
        if (!bit_add_one(cur, v, next)) return 0;
        cur = next;
        next = (next == &a) ? &b : &a;
    }
    *out = *cur;
    return 1;
}

/* Reverse-order combination recursion. Candidate upper bound is exclusive. */
static void bit_dfs_reverse(const BitReach *reach, int depth, int upper, Counts *c) {
    ++c->nodes;
    if (depth == SUPPORT) {
        ++c->supports;
        if (target_is_in_support(support_target())) ++c->target_in_support;
        return;
    }

    for (int v = upper - 1; v >= 2; --v) {
        if (v == 5 || v == 25) continue;
        BitReach next;
        if (!bit_add_four(reach, v, &next)) continue;
        SUP[depth] = v;
        bit_dfs_reverse(&next, depth + 1, v, c);
    }
}

static Counts run_bit_engine(void) {
    Counts c = {0, 0, 0};
    BitReach r0, r1, r2, r3;
    memset(&r0, 0, sizeof(r0));
    bit_set(&r0.lo[0], &r0.hi[0], 0);

    SUP[0] = 25;
    SUP[1] = 5;
    SUP[2] = 1;

    if (!bit_add_four(&r0, 25, &r1) ||
        !bit_add_four(&r1, 5, &r2) ||
        !bit_add_four(&r2, 1, &r3)) {
        fprintf(stderr, "bit engine rejected normalized basis\n");
        exit(2);
    }

    bit_dfs_reverse(&r3, 3, N, &c);
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

    int agree = (a.supports == b.supports) &&
                (a.target_in_support == b.target_in_support);
    int expected = (a.supports == 564) && (a.target_in_support == 0);

    printf("{\n");
    printf("  \"schema\": \"conditional-width-one-bounds.support-eight-replay.v1\",\n");
    printf("  \"interpretation\": \"bounded same-package replay; symbolic normalization is not re-proved here\",\n");
    printf("  \"normalization\": \"support contains e1,e2,e3; GL(3,5)-complete for rank-3 supports\",\n");
    printf("  \"engine_byte\": {\"nodes\": %lld, \"normalized_supports\": %lld, \"minus_support_sum_in_support\": %lld},\n",
           a.nodes, a.supports, a.target_in_support);
    printf("  \"engine_bit_reverse\": {\"nodes\": %lld, \"normalized_supports\": %lld, \"minus_support_sum_in_support\": %lld},\n",
           b.nodes, b.supports, b.target_in_support);
    printf("  \"engines_agree\": %s,\n", agree ? "true" : "false");
    printf("  \"expected_discovery_row\": %s,\n", expected ? "true" : "false");
    printf("  \"conditional_consequence\": \"if replayed and the normalization proof is accepted, a 31-term zero-sum short-free C_5^3 sequence cannot have support size 8\"\n");
    printf("}\n");

    return (agree && expected) ? 0 : 1;
}
