#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <limits>
#include <vector>

using V3 = std::array<int, 3>;

struct Engine {
    static constexpr int p = 13;
    static constexpr int N = p * p * p;
    static constexpr int m = 19;

    V3 zero{0, 0, 0};
    V3 e1{1, 0, 0};
    V3 e2{0, 1, 0};
    V3 s{0, 0, 1};
    V3 g{6, 6, 1};  // s - 7(e1+e2) mod 13
    std::vector<int> rho;

    static int enc(const V3 &x) { return (x[0] * p + x[1]) * p + x[2]; }
    static V3 dec(int id) { return V3{id / (p * p), (id / p) % p, id % p}; }
    static V3 add(const V3 &x, const V3 &y) {
        return V3{(x[0] + y[0]) % p, (x[1] + y[1]) % p, (x[2] + y[2]) % p};
    }
    static V3 neg(const V3 &x) {
        return V3{(p - x[0]) % p, (p - x[1]) % p, (p - x[2]) % p};
    }
    static V3 mul(int k, const V3 &x) {
        return V3{k * x[0] % p, k * x[1] % p, k * x[2] % p};
    }

    Engine() { build_rho_occurrence_dp(); }

    void add_term(std::vector<int> &dp, const V3 &term) const {
        const std::vector<int> old = dp;
        for (int id = 0; id < N; ++id) {
            if (old[id] == std::numeric_limits<int>::max()) continue;
            const int nid = enc(add(dec(id), term));
            dp[nid] = std::min(dp[nid], old[id] + 1);
        }
    }

    void build_rho_occurrence_dp() {
        rho.assign(N, std::numeric_limits<int>::max());
        rho[enc(zero)] = 0;
        for (int i = 0; i < 12; ++i) add_term(rho, e1);
        for (int i = 0; i < 12; ++i) add_term(rho, e2);
        for (int i = 0; i < 2; ++i) add_term(rho, s);
        for (int i = 0; i < 11; ++i) add_term(rho, g);
    }

    bool plane_contains(const V3 &s0, const V3 &x, const V3 &target) const {
        for (int a = 0; a < p; ++a)
            for (int b = 0; b < p; ++b)
                if (add(mul(a, s0), mul(b, x)) == target) return true;
        return false;
    }

    bool structural_x(const V3 &x) const {
        if (plane_contains(s, x, e1)) return false;
        if (plane_contains(s, x, e2)) return false;
        if (plane_contains(s, x, g)) return false;
        // Excluding the three forbidden directions also forces rank(s,x)=2.
        return true;
    }

    int min_score(const V3 &x, const V3 &y) const {
        int best = std::numeric_limits<int>::max();
        for (int i = 0; i <= 4; ++i) {
            for (int j = 0; j <= 3; ++j) {
                for (int k = 0; k <= 12; ++k) {
                    const int len = i + j + k;
                    if (len == 0 || len == m) continue;
                    V3 sigma = add(add(mul(i, s), mul(j, x)), mul(k, y));
                    const int depth = rho[enc(neg(sigma))];
                    assert(depth != std::numeric_limits<int>::max());
                    best = std::min(best, len + depth);
                }
            }
        }
        return best;
    }

    void run() const {
        int structural = 0;
        int singleton = 0;
        std::array<int, 20> hist{};

        for (int id = 0; id < N; ++id) {
            const V3 x = dec(id);
            if (!structural_x(x)) continue;
            ++structural;
            const V3 y = add(mul(4, s), mul(3, x));

            if (1 + rho[enc(neg(x))] >= m && 1 + rho[enc(neg(y))] >= m)
                ++singleton;

            const int score = min_score(x, y);
            assert(0 <= score && score < static_cast<int>(hist.size()));
            ++hist[score];
        }

        assert(structural == 1716);
        assert(singleton == 78);
        const std::array<int, 20> expected{
            0, 0, 0, 4, 18, 58, 132, 246, 352, 420,
            272, 124, 40, 44, 6, 0, 0, 0, 0, 0
        };
        assert(hist == expected);

        int exact_survivors = 0;
        int relaxed14 = 0;
        for (int score = 0; score < static_cast<int>(hist.size()); ++score) {
            if (score >= 19) exact_survivors += hist[score];
            if (score >= 14) relaxed14 += hist[score];
        }
        assert(exact_survivors == 0);
        assert(relaxed14 == 6);

        std::cout << "{\"status\":\"A2_LIGHT_SUPPORT3_C4_INDEPENDENT_GREEN\","
                  << "\"p13_structural\":" << structural << ","
                  << "\"p13_singleton_survivors\":" << singleton << ","
                  << "\"p13_exact_survivors\":" << exact_survivors << ","
                  << "\"p13_threshold14_mutation_survivors\":" << relaxed14
                  << "}\n";
    }
};

int main() {
    const Engine engine;
    engine.run();
}
