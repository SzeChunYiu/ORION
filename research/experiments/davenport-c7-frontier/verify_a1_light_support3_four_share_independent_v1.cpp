#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <limits>
#include <map>
#include <set>
#include <sstream>
#include <string>
#include <tuple>
#include <vector>

using Vec = std::array<int, 3>;

static bool is_prime(int n) {
    if (n < 2) return false;
    if (n % 2 == 0) return n == 2;
    for (int d = 3; 1LL * d * d <= n; d += 2) {
        if (n % d == 0) return false;
    }
    return true;
}

static int mod(int x, int p) {
    x %= p;
    if (x < 0) x += p;
    return x;
}

static int inverse_mod(int a, int p) {
    int t = 0, new_t = 1;
    int r = p, new_r = mod(a, p);
    while (new_r != 0) {
        int q = r / new_r;
        int tmp_t = t - q * new_t;
        t = new_t;
        new_t = tmp_t;
        int tmp_r = r - q * new_r;
        r = new_r;
        new_r = tmp_r;
    }
    assert(r == 1);
    return mod(t, p);
}

static int lambda_cost(int d) {
    // Five actual copies of s occur in U V: four in V and one in U.
    return d <= 5 ? d : 5 + 3 * (d - 5);
}

static bool atom_compatible(int p, int r, int t) {
    for (int n = 2; n < p; ++n) {
        int d = mod(4 * n, p);
        int a = mod(r * n, p);
        int b = mod(t * n, p);
        if (d <= 4 && a <= r && b <= t) return false;
    }
    return true;
}

static bool has_multiplier_certificate(int p, int r, int t) {
    int m = p + (p - 1) / 2;
    for (int n = 1; n < p; ++n) {
        int d = mod(4 * n, p);
        int a = mod(r * n, p);
        int b = mod(t * n, p);
        if (a <= r && b <= t && lambda_cost(d) + a + b <= m - 1) return true;
    }
    return false;
}

static int encode(const Vec& v, int p) {
    return (v[0] * p + v[1]) * p + v[2];
}

static Vec decode(int id, int p) {
    Vec v{};
    v[2] = id % p;
    id /= p;
    v[1] = id % p;
    id /= p;
    v[0] = id;
    return v;
}

static Vec add(const Vec& a, const Vec& b, int p) {
    return Vec{mod(a[0] + b[0], p), mod(a[1] + b[1], p), mod(a[2] + b[2], p)};
}

static std::vector<int> build_u_depth(int p) {
    const int states = p * p * p;
    const int inf = std::numeric_limits<int>::max() / 4;
    std::vector<int> depth(states, inf);
    depth[0] = 0;

    std::vector<Vec> terms;
    const Vec f1{1, 0, 0}, f2{0, 1, 0}, f3{0, 0, 1}, s{1, 1, 1};
    for (int i = 0; i < p - 1; ++i) terms.push_back(f1);
    for (int i = 0; i < p - 1; ++i) terms.push_back(f2);
    for (int i = 0; i < p - 1; ++i) terms.push_back(f3);
    terms.push_back(s);

    for (const Vec& term : terms) {
        std::vector<int> next = depth;
        for (int id = 0; id < states; ++id) {
            if (depth[id] == inf) continue;
            Vec v = add(decode(id, p), term, p);
            int target = encode(v, p);
            next[target] = std::min(next[target], depth[id] + 1);
        }
        depth.swap(next);
    }
    return depth;
}

struct BaseResult {
    std::map<int, std::int64_t> histogram;
    std::int64_t parameters = 0;
    std::int64_t theorem_survivors = 0;
    int max_mu = -1;
};

static BaseResult audit_base(int p, int r, int t) {
    const int q = (p - 1) / 2;
    const int m = p + q;
    const int inv_r = inverse_mod(r, p);
    const Vec s{1, 1, 1};
    const std::vector<int> depth = build_u_depth(p);

    BaseResult result;
    for (int y0 = 0; y0 < p; ++y0) {
        for (int y1 = 0; y1 < p; ++y1) {
            for (int y2 = 0; y2 < p; ++y2) {
                Vec y{y0, y1, y2};
                if (y == Vec{0, 0, 0}) continue;
                Vec x{
                    mod(-inv_r * (4 + t * y0), p),
                    mod(-inv_r * (4 + t * y1), p),
                    mod(-inv_r * (4 + t * y2), p),
                };
                if (x == Vec{0, 0, 0}) continue;
                ++result.parameters;

                int mu = std::numeric_limits<int>::max();
                for (int a = 0; a <= 4; ++a) {
                    for (int b = 0; b <= r; ++b) {
                        for (int c = 0; c <= t; ++c) {
                            int length = a + b + c;
                            if (length == 0 || length == m) continue;
                            Vec sum{
                                mod(a * s[0] + b * x[0] + c * y[0], p),
                                mod(a * s[1] + b * x[1] + c * y[1], p),
                                mod(a * s[2] + b * x[2] + c * y[2], p),
                            };
                            Vec neg{mod(-sum[0], p), mod(-sum[1], p), mod(-sum[2], p)};
                            int score = length + depth[encode(neg, p)];
                            mu = std::min(mu, score);
                        }
                    }
                }
                assert(mu != std::numeric_limits<int>::max());
                ++result.histogram[mu];
                result.max_mu = std::max(result.max_mu, mu);
                if (mu >= m) ++result.theorem_survivors;
            }
        }
    }
    return result;
}

static std::string histogram_string(const std::map<int, std::int64_t>& histogram) {
    std::ostringstream out;
    bool first = true;
    for (const auto& [score, count] : histogram) {
        if (!first) out << ',';
        first = false;
        out << score << ':' << count;
    }
    return out.str();
}

int main(int argc, char** argv) {
    int prime_limit = 5000;
    if (argc == 3 && std::string(argv[1]) == "--prime-limit") {
        prime_limit = std::stoi(argv[2]);
        assert(prime_limit >= 17);
    } else {
        assert(argc == 1);
    }
    const std::set<std::tuple<int, int, int>> expected{
        {7, 1, 5},
        {13, 3, 12},
        {17, 8, 13},
    };

    std::set<std::tuple<int, int, int>> residuals;
    std::int64_t multiplicity_states = 0;
    std::int64_t atom_compatible_states = 0;

    for (int p = 7; p <= prime_limit; p += 2) {
        if (!is_prime(p)) continue;
        int q = (p - 1) / 2;
        int m = p + q;
        for (int r = 1; r < p; ++r) {
            int t = m - 4 - r;
            if (!(r <= t && t <= p - 1)) continue;
            ++multiplicity_states;
            if (atom_compatible(p, r, t)) ++atom_compatible_states;
            if (!has_multiplier_certificate(p, r, t)) residuals.emplace(p, r, t);
        }
    }
    assert(residuals == expected);
    for (const auto& row : residuals) {
        auto [p, r, t] = row;
        assert(atom_compatible(p, r, t));
    }

    std::map<std::tuple<int, int, int>, BaseResult> results;
    for (const auto& row : residuals) {
        auto [p, r, t] = row;
        results[row] = audit_base(p, r, t);
        assert(results[row].theorem_survivors == 0);
    }

    const std::map<int, std::int64_t> expected7{{2,8},{3,26},{4,52},{5,75},{6,93},{7,81},{8,6}};
    const std::map<int, std::int64_t> expected13{{2,8},{3,32},{4,71},{5,148},{6,192},{7,328},{8,375},{9,483},{10,366},{11,120},{12,72}};
    const std::map<int, std::int64_t> expected17{{2,8},{3,33},{4,67},{5,152},{6,222},{7,379},{8,423},{9,630},{10,663},{11,750},{12,561},{13,486},{14,174},{15,132},{16,30},{17,69},{18,114},{19,12},{20,6}};
    const auto key7 = std::make_tuple(7, 1, 5);
    const auto key13 = std::make_tuple(13, 3, 12);
    const auto key17 = std::make_tuple(17, 8, 13);
    assert(results[key7].histogram == expected7);
    assert(results[key13].histogram == expected13);
    assert(results[key17].histogram == expected17);

    // Positive mutation controls: lowering the artificial threshold to the
    // largest observed score must admit genuine parameters.
    assert(results[key7].histogram.at(results[key7].max_mu) == 6);
    assert(results[key13].histogram.at(results[key13].max_mu) == 72);
    assert(results[key17].histogram.at(results[key17].max_mu) == 6);

    std::cout << "A1_C4_INDEPENDENT_GREEN"
              << " prime_limit=" << prime_limit
              << " multiplicity_states=" << multiplicity_states
              << " atom_compatible_states=" << atom_compatible_states
              << " residuals=7:1,5;13:3,12;17:8,13"
              << " p7_parameters=" << results[key7].parameters
              << " p7_hist=" << histogram_string(results[key7].histogram)
              << " p13_parameters=" << results[key13].parameters
              << " p13_hist=" << histogram_string(results[key13].histogram)
              << " p17_parameters=" << results[key17].parameters
              << " p17_hist=" << histogram_string(results[key17].histogram)
              << '\n';
    return 0;
}
