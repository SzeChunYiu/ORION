#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <limits>
#include <tuple>
#include <vector>

using V3 = std::array<int, 3>;

static bool is_prime(int n) {
    if (n < 2) return false;
    if (n % 2 == 0) return n == 2;
    for (int d = 3; 1LL * d * d <= n; d += 2)
        if (n % d == 0) return false;
    return true;
}

static int inverse_mod(int a, int p) {
    for (int x = 1; x < p; ++x) if (a * x % p == 1) return x;
    assert(false);
    return 0;
}

static bool coefficient_atom(int p, int c, int r, int t) {
    for (int n = 2; n < p; ++n)
        if ((n * c) % p <= c && (n * r) % p <= r && (n * t) % p <= t)
            return false;
    return true;
}

// Independently computes the shortest realization of d*e3 using the actual
// support resources in U*V: e3^(c+2), g4^(p-2), e1^(p-1), e2^(p-1).
static std::vector<int> radial_costs(int p, int c) {
    const int u = inverse_mod(2, p);
    const int INF = std::numeric_limits<int>::max() / 4;
    std::vector<int> best(p, INF);
    for (int q = 0; q <= p - 2; ++q) {
        const int axes = (u * q) % p;
        for (int z = 0; z <= c + 2; ++z) {
            const int d = (z + q) % p;
            best[d] = std::min(best[d], z + q + 2 * axes);
        }
    }
    assert(best[0] == 0);
    return best;
}

static std::vector<std::tuple<int, int, int, int>> scalar_residuals(int first_p, int last_p) {
    std::vector<std::tuple<int, int, int, int>> residuals;
    for (int p = first_p; p <= last_p; p += 2) {
        if (!is_prime(p)) continue;
        const int h = (p - 1) / 2;
        const int m = 3 * h + 1;
        for (int c : {1, 2}) {
            const auto radial = radial_costs(p, c);
            for (int r = 1; r < p; ++r) {
                const int t = m - c - r;
                if (t < r || t <= 0 || t >= p) continue;
                if (!coefficient_atom(p, c, r, t)) continue;
                bool killed = false;
                for (int n = 2; n < p; ++n) {
                    const int d = n * c % p;
                    const int a = n * r % p;
                    const int b = n * t % p;
                    if (a <= r && b <= t && radial[d] + a + b < m) {
                        killed = true;
                        break;
                    }
                }
                if (!killed) residuals.emplace_back(p, c, r, t);
            }
        }
    }
    return residuals;
}

struct P5Mutation {
    static constexpr int p = 5;
    static constexpr int N = p * p * p;
    static constexpr int m = 7;
    V3 e1{1, 0, 0}, e2{0, 1, 0}, s{0, 0, 1}, g4{2, 2, 1};
    std::vector<int> rho;

    static int enc(const V3 &x) { return (x[0] * p + x[1]) * p + x[2]; }
    static V3 decode(int id) { return V3{id / (p * p), (id / p) % p, id % p}; }
    static V3 add(const V3 &x, const V3 &y) {
        return V3{(x[0] + y[0]) % p, (x[1] + y[1]) % p, (x[2] + y[2]) % p};
    }
    static V3 neg(const V3 &x) {
        return V3{(p - x[0]) % p, (p - x[1]) % p, (p - x[2]) % p};
    }
    static V3 mul(int k, const V3 &x) {
        k %= p; if (k < 0) k += p;
        return V3{k * x[0] % p, k * x[1] % p, k * x[2] % p};
    }
    static int det(const V3 &a, const V3 &b, const V3 &c) {
        long long d = 1LL*a[0]*(b[1]*c[2]-b[2]*c[1])
                    - 1LL*a[1]*(b[0]*c[2]-b[2]*c[0])
                    + 1LL*a[2]*(b[0]*c[1]-b[1]*c[0]);
        d %= p; if (d < 0) d += p; return static_cast<int>(d);
    }

    P5Mutation() { build_depth(); }

    void add_term_min(std::vector<int> &dp, const V3 &term) const {
        const auto old = dp;
        for (int id = 0; id < N; ++id) {
            if (old[id] >= 1000000) continue;
            const int nid = enc(add(decode(id), term));
            dp[nid] = std::min(dp[nid], old[id] + 1);
        }
    }

    void build_depth() {
        rho.assign(N, 1000000);
        rho[0] = 0;
        for (int i = 0; i < 4; ++i) add_term_min(rho, e1);
        for (int i = 0; i < 4; ++i) add_term_min(rho, e2);
        for (int i = 0; i < 2; ++i) add_term_min(rho, s);
        for (int i = 0; i < 3; ++i) add_term_min(rho, g4);
    }

    bool in_maximal_support(const V3 &x) const {
        return x == e1 || x == e2 || x == s || x == g4;
    }
    bool scalar_s(const V3 &x) const {
        for (int k = 1; k < p; ++k) if (x == mul(k, s)) return true;
        return false;
    }

    void add_term_lengths(std::vector<uint16_t> &dp, const V3 &term) const {
        const auto old = dp;
        for (int id = 0; id < N; ++id) {
            if (!old[id]) continue;
            const int nid = enc(add(decode(id), term));
            dp[nid] |= static_cast<uint16_t>(old[id] << 1);
        }
    }

    bool exact_pair(const V3 &x, const V3 &y, int r, int t) const {
        std::vector<uint16_t> lengths(N, 0);
        lengths[0] = 1;
        add_term_lengths(lengths, s);
        add_term_lengths(lengths, s);
        for (int i = 0; i < r; ++i) add_term_lengths(lengths, x);
        for (int i = 0; i < t; ++i) add_term_lengths(lengths, y);
        for (int id = 0; id < N; ++id) {
            const int d = rho[enc(neg(decode(id)))];
            for (int len = 1; len < m; ++len)
                if (((lengths[id] >> len) & 1u) && len + d < m)
                    return false;
        }
        return true;
    }

    int run() const {
        int survivors = 0;
        for (int r = 1; r < p; ++r) {
            const int t = m - 2 - r;
            if (t <= 0 || t >= p || !coefficient_atom(p, 2, r, t)) continue;
            const int inv_t = inverse_mod(t, p);
            for (int id = 1; id < N; ++id) {
                const V3 x = decode(id);
                if (in_maximal_support(x) || scalar_s(x)) continue;
                if (det(s, x, e1) == 0 || det(s, x, e2) == 0 || det(s, x, g4) == 0) continue;
                const V3 rhs = add(mul(2, s), mul(r, x));
                const V3 y = mul(-inv_t, rhs);
                if (y == V3{0,0,0} || in_maximal_support(y) || y == x || y == s) continue;
                if (exact_pair(x, y, r, t)) ++survivors;
            }
        }
        return survivors;
    }
};

int main() {
    const auto residuals = scalar_residuals(7, 1009);
    assert(residuals.empty());

    const auto p5_residuals = scalar_residuals(5, 5);
    const std::vector<std::tuple<int,int,int,int>> expected_p5{
        {5, 2, 1, 4}, {5, 2, 2, 3}
    };
    assert(p5_residuals == expected_p5);

    const P5Mutation p5;
    const int exact_p5 = p5.run();
    assert(exact_p5 == 4);

    std::cout << "{\"status\":\"A2_LIGHT_SUPPORT3_C1_C2_INDEPENDENT_GREEN\","
              << "\"prime_scan_through\":1009,"
              << "\"p_ge_7_scalar_residuals\":0,"
              << "\"p5_c2_scalar_residual_rows\":2,"
              << "\"p5_c2_exact_survivors\":" << exact_p5 << "}\n";
}
