#include <bits/stdc++.h>
using namespace std;

// Prime-uniform depth-oracle replay for the first maximal corridor j=1.
// It intentionally does not materialize bounded subset-sum tables of U.

struct Engine {
    int p, N, a, b, m, H, inv;
    vector<int> neg, cap, rho;
    vector<vector<int>> add;
    vector<vector<unsigned char>> ss;
    vector<int> mult, chosen, allowed;
    long long count = 0;

    int enc(int x, int y, int z) const { return (x * p + y) * p + z; }
    array<int,3> dec(int q) const { return {q / (p*p), (q/p) % p, q % p}; }

    int invmod(int x) const {
        for (int y = 1; y < p; ++y) if (x * y % p == 1) return y;
        return 0;
    }

    int addv(int x, int y) const {
        auto A = dec(x), B = dec(y);
        return enc((A[0] + B[0]) % p,
                   (A[1] + B[1]) % p,
                   (A[2] + B[2]) % p);
    }

    Engine(int P, int A) : p(P), a(A) {
        N = p * p * p;
        b = (p - 1) / 2;       // first corridor j=1
        m = p + b;
        H = m - 1;
        inv = invmod(a);

        neg.resize(N);
        add.assign(N, vector<int>(N));
        cap.assign(N, p - 1);
        rho.assign(N, INT_MAX / 4);
        mult.assign(N, 0);

        for (int x = 0; x < N; ++x) {
            auto d = dec(x);
            neg[x] = enc((p - d[0]) % p,
                         (p - d[1]) % p,
                         (p - d[2]) % p);
            for (int y = 0; y < N; ++y) add[x][y] = addv(x, y);
        }

        const int e1 = enc(1,0,0);
        const int e2 = enc(0,1,0);
        const int e3 = enc(0,0,1);
        const int g4 = enc((p - inv) % p, (p - inv) % p, 1);

        // p-short-freeness of UV gives v_x(V) <= p-1-v_x(U).
        cap[e1] = 0;
        cap[e2] = 0;
        cap[e3] = p - 1 - a;
        cap[g4] = a - 1;

        // Exact one-parameter representation depth on the canonical U.
        for (int q = 0; q < N; ++q) {
            auto d = dec(q);
            int best = INT_MAX / 4;
            for (int t = 0; t <= p - a; ++t) {
                int c1 = (d[0] + inv * t) % p;
                int c2 = (d[1] + inv * t) % p;
                int c3 = (d[2] - t) % p;
                if (c3 < 0) c3 += p;
                if (c3 <= a) best = min(best, c1 + c2 + c3 + t);
            }
            rho[q] = best;
        }
        rho[0] = 0;

        ss.assign(m + 1, vector<unsigned char>(N));
        ss[0][0] = 1;

        // Singleton form of r + rho_U(-sum) >= m.
        for (int x = 1; x < N; ++x)
            if (cap[x] > 0 && 1 + rho[neg[x]] > H)
                allowed.push_back(x);
    }

    bool valid_add(int x, int depth, vector<vector<int>>& news) {
        news.assign(depth + 2, {});
        for (int k = 1; k <= depth + 1; ++k) {
            for (int s = 0; s < N; ++s) if (ss[k-1][s])
                news[k].push_back(add[s][x]);

            sort(news[k].begin(), news[k].end());
            news[k].erase(unique(news[k].begin(), news[k].end()), news[k].end());

            for (int q : news[k])
                if (k + rho[neg[q]] <= H)
                    return false;
        }
        return true;
    }

    void dfs(int start, int depth, int total) {
        if (depth == m - 1) {
            int x = neg[total];
            auto it = lower_bound(allowed.begin(), allowed.end(), x);
            if (it == allowed.end() || *it != x) return;
            if (!chosen.empty() && x < chosen.back()) return;
            if (mult[x] >= cap[x]) return;

            vector<vector<int>> news;
            if (!valid_add(x, depth, news)) return;
            ++count;
            return;
        }

        for (int pos = start; pos < (int)allowed.size(); ++pos) {
            int x = allowed[pos];
            if (mult[x] >= cap[x]) continue;

            vector<vector<int>> news;
            if (!valid_add(x, depth, news)) continue;

            vector<vector<int>> added(depth + 2);
            for (int k = 1; k <= depth + 1; ++k) {
                for (int q : news[k]) if (!ss[k][q]) {
                    ss[k][q] = 1;
                    added[k].push_back(q);
                }
            }

            ++mult[x];
            chosen.push_back(x);
            dfs(pos, depth + 1, add[total][x]);
            chosen.pop_back();
            --mult[x];

            for (int k = 1; k <= depth + 1; ++k)
                for (int q : added[k]) ss[k][q] = 0;
        }
    }
};

int main() {
    map<pair<int,int>, long long> got;

    for (int p : {5, 7}) {
        for (int a = 1; a <= (p - 1) / 2; ++a) {
            Engine E(p, a);
            E.dfs(0, 0, 0);
            got[{p,a}] = E.count;
        }
    }

    assert(got[{5,1}] == 169);
    assert(got[{5,2}] == 30);
    assert(got[{7,1}] == 538);
    assert(got[{7,2}] == 24);
    assert(got[{7,3}] == 0);

    cout << "{\"status\":\"SUPPORT4_MAXIMAL_PAIR_DEPTH_ORACLE_GREEN\","
         << "\"p5_counts\":[" << got[{5,1}] << "," << got[{5,2}] << "],"
         << "\"p7_counts\":[" << got[{7,1}] << "," << got[{7,2}] << "," << got[{7,3}] << "]}"
         << "\n";
}
