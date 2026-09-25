#include <algorithm>
#include <cassert>
#include <iostream>
#include <limits>
#include <tuple>
#include <vector>

static bool is_prime(int n) {
    if (n < 2) return false;
    if (n % 2 == 0) return n == 2;
    for (int d = 3; 1LL * d * d <= n; d += 2)
        if (n % d == 0) return false;
    return true;
}

static int inverse_mod(int a, int p) {
    for (int x = 1; x < p; ++x)
        if (a * x % p == 1) return x;
    assert(false);
    return 0;
}

static bool coefficient_atom(int p, int c, int r, int t) {
    for (int n = 2; n < p; ++n)
        if ((n * c) % p <= c && (n * r) % p <= r && (n * t) % p <= t)
            return false;
    return true;
}

// Shortest realization of d*e3 using the actual support resources in U*V:
// e3^5, g4^(p-2), e1^(p-1), e2^(p-1).
static std::vector<int> radial_costs(int p) {
    const int INF = std::numeric_limits<int>::max() / 4;
    const int u = inverse_mod(2, p);
    std::vector<int> best(p, INF);
    for (int q = 0; q <= p - 2; ++q) {
        const int axes = u * q % p;
        for (int z = 0; z <= 5; ++z) {
            const int d = (z + q) % p;
            best[d] = std::min(best[d], z + q + 2 * axes);
        }
    }
    return best;
}

struct ScanResult {
    int atom_rows = 0;
    std::vector<std::tuple<int, int, int, int>> exact_residuals;
    std::vector<std::tuple<int, int, int, int>> mutation_residuals;
};

static ScanResult scan(int limit) {
    ScanResult out;
    for (int p = 7; p <= limit; p += 2) {
        if (!is_prime(p)) continue;
        const int h = (p - 1) / 2;
        const int m = 3 * h + 1;
        if (3 > 2 * (h / 2)) continue;  // exact light multi-copy ceiling
        const auto radial = radial_costs(p);

        for (int r = 1; r < p; ++r) {
            const int t = m - 3 - r;
            if (t < r || t <= 0 || t >= p || !coefficient_atom(p, 3, r, t))
                continue;
            ++out.atom_rows;

            bool killed = false;
            for (int n = 2; n < p; ++n) {
                const int D = 3 * n % p;
                const int A = r * n % p;
                const int B = t * n % p;
                if (A <= r && B <= t && radial[D] + A + B < m) {
                    killed = true;
                    break;
                }
            }
            if (!killed) out.exact_residuals.emplace_back(p, 3, r, t);

            // Hostile mutation: suppress the 2e3=2g4+e1+e2 synthesis and
            // permit only the five actual copies of e3.
            bool killed_without_synthesis = false;
            for (int n = 2; n < p; ++n) {
                const int D = 3 * n % p;
                const int A = r * n % p;
                const int B = t * n % p;
                const int actual_only = D <= 5 ? D : std::numeric_limits<int>::max() / 4;
                if (A <= r && B <= t && actual_only + A + B < m) {
                    killed_without_synthesis = true;
                    break;
                }
            }
            if (!killed_without_synthesis)
                out.mutation_residuals.emplace_back(p, 3, r, t);
        }
    }
    return out;
}

int main() {
    const auto out = scan(1009);
    assert(out.atom_rows == 9826);
    assert(out.exact_residuals.empty());
    assert(out.mutation_residuals.size() == 1309);

    const std::vector<std::tuple<int, int, int, int>> first_mutations{
        {13, 3, 6, 10},
        {19, 3, 9, 16},
        {31, 3, 15, 28},
        {31, 3, 18, 25},
        {37, 3, 18, 34},
        {37, 3, 21, 31},
        {43, 3, 21, 40},
        {43, 3, 24, 37},
    };
    assert(std::equal(first_mutations.begin(), first_mutations.end(),
                      out.mutation_residuals.begin()));
    assert(out.mutation_residuals.back() == std::make_tuple(1009, 3, 603, 907));

    for (int p = 11; p <= 1009; p += 2) {
        if (!is_prime(p)) continue;
        const auto radial = radial_costs(p);
        assert(radial[4] == 4);
        assert(radial[5] == 5);
        assert(radial[6] == 8);
        assert(radial[7] == 9);
    }

    std::cout << "{\"status\":\"A2_LIGHT_SUPPORT3_C3_INDEPENDENT_GREEN\","
              << "\"atom_rows_after_multicopy_ceiling\":" << out.atom_rows << ","
              << "\"exact_radial_residuals\":" << out.exact_residuals.size() << ","
              << "\"no_synthesis_mutation_residuals\":"
              << out.mutation_residuals.size() << "}\n";
}
