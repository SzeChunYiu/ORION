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

static bool atom_coefficients(int p, int c, int r, int t) {
    for (int q = 2; q < p; ++q)
        if ((q * c) % p <= c && (q * r) % p <= r && (q * t) % p <= t)
            return false;
    return true;
}

static int s_cost(int C) { return C <= 3 ? C : 3 * C - 6; }

static std::vector<std::tuple<int, int, int, int>> brute_scalar_residuals(int limit) {
    std::vector<std::tuple<int, int, int, int>> residuals;
    for (int p = 7; p <= limit; p += 2) {
        if (!is_prime(p)) continue;
        const int h = (p - 1) / 2;
        const int m = 3 * h + 1;
        for (int r = 1; r < p; ++r) {
            const int t = m - 2 - r;
            if (t < r || t <= 0 || t >= p) continue;
            if (!atom_coefficients(p, 2, r, t)) continue;
            bool killed = false;
            for (int q = 2; q < p; ++q) {
                const int C = (2 * q) % p;
                const int R = (q * r) % p;
                const int T = (q * t) % p;
                if (R <= r && T <= t && s_cost(C) + R + T < m) {
                    killed = true;
                    break;
                }
            }
            if (!killed) residuals.emplace_back(p, 2, r, t);
        }
    }
    return residuals;
}

struct P13Engine {
    static constexpr int p = 13;
    static constexpr int N = p * p * p;
    static constexpr int m = 19;
    static constexpr uint32_t KEEP_LENGTHS = (1u << 20) - 1u;

    V3 s{1, 1, 1};
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
        return V3{k * x[0] % p, k * x[1] % p, k * x[2] % p};
    }

    P13Engine() { build_depth_by_occurrences(); }

    void add_term_to_min_dp(std::vector<int> &dp, const V3 &term) const {
        const std::vector<int> old = dp;
        for (int id = 0; id < N; ++id) {
            if (old[id] == std::numeric_limits<int>::max()) continue;
            const int nid = enc(add(decode(id), term));
            dp[nid] = std::min(dp[nid], old[id] + 1);
        }
    }

    void build_depth_by_occurrences() {
        rho.assign(N, std::numeric_limits<int>::max());
        rho[0] = 0;
        const std::array<V3, 4> values{V3{1, 0, 0}, V3{0, 1, 0}, V3{0, 0, 1}, s};
        for (int j = 0; j < 3; ++j)
            for (int copy = 0; copy < 12; ++copy)
                add_term_to_min_dp(rho, values[j]);
        add_term_to_min_dp(rho, s);
    }

    void add_term_to_length_dp(std::vector<uint32_t> &dp, const V3 &term) const {
        const std::vector<uint32_t> old = dp;
        for (int id = 0; id < N; ++id) {
            if (!old[id]) continue;
            const int nid = enc(add(decode(id), term));
            dp[nid] |= (old[id] << 1) & KEEP_LENGTHS;
        }
    }

    int pair_min_score(const V3 &x, const V3 &y) const {
        std::vector<uint32_t> lengths(N, 0u);
        lengths[0] = 1u;
        for (int i = 0; i < 2; ++i) add_term_to_length_dp(lengths, s);
        for (int i = 0; i < 6; ++i) add_term_to_length_dp(lengths, x);
        for (int i = 0; i < 11; ++i) add_term_to_length_dp(lengths, y);

        int best = std::numeric_limits<int>::max();
        for (int id = 0; id < N; ++id) {
            const int depth = rho[enc(neg(decode(id)))];
            for (int len = 1; len < m; ++len) {
                if ((lengths[id] >> len) & 1u)
                    best = std::min(best, len + depth);
            }
        }
        return best;
    }

    std::tuple<int, int, std::array<int, 20>> run() const {
        int structural = 0;
        int singleton = 0;
        std::array<int, 20> score_hist{};
        for (int a = 0; a < p; ++a) {
            for (int b = 0; b < p; ++b) {
                for (int c = 0; c < p; ++c) {
                    if (a == b || a == c || b == c) continue;
                    ++structural;
                    const V3 x{a, b, c};
                    const V3 y = add(s, mul(3, x));
                    if (1 + rho[enc(neg(x))] >= m && 1 + rho[enc(neg(y))] >= m)
                        ++singleton;
                    const int score = pair_min_score(x, y);
                    assert(0 <= score && score < static_cast<int>(score_hist.size()));
                    ++score_hist[score];
                }
            }
        }
        return {structural, singleton, score_hist};
    }
};

int main() {
    const auto residuals = brute_scalar_residuals(1009);
    assert(residuals.size() == 1);
    assert(residuals[0] == std::make_tuple(13, 2, 6, 11));

    const P13Engine engine;
    const auto [structural, singleton, score_hist] = engine.run();
    assert(structural == 1716);
    assert(singleton == 312);
    const std::array<int, 20> expected_hist{
        0, 0, 0, 0, 12, 42, 108, 210, 318, 390,
        330, 132, 36, 42, 78, 18, 0, 0, 0, 0
    };
    assert(score_hist == expected_hist);

    int exact_survivors = 0;
    int relaxed_mutation_survivors = 0;
    for (int score = 0; score < static_cast<int>(score_hist.size()); ++score) {
        if (score >= 19) exact_survivors += score_hist[score];
        if (score >= 15) relaxed_mutation_survivors += score_hist[score];
    }
    assert(exact_survivors == 0);
    assert(relaxed_mutation_survivors == 18);

    std::cout << "{\"status\":\"A1_LIGHT_SUPPORT3_TWO_SHARE_INDEPENDENT_GREEN\","
              << "\"scalar_residual\":[13,2,6,11],"
              << "\"p13_structural\":" << structural << ","
              << "\"p13_singleton_survivors\":" << singleton << ","
              << "\"p13_exact_pair_survivors\":" << exact_survivors << ","
              << "\"p13_relaxed_threshold15_survivors\":" << relaxed_mutation_survivors
              << "}\n";
}
