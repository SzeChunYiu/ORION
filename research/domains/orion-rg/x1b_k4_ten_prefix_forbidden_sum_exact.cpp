#include <bits/stdc++.h>
using namespace std;
using U128 = unsigned __int128;

struct Key {
    uint64_t lo, hi;
    uint16_t last;
    uint8_t depth;
    bool operator==(Key const& o) const {
        return lo == o.lo && hi == o.hi && last == o.last && depth == o.depth;
    }
};
struct KeyHash {
    size_t operator()(Key const& k) const {
        uint64_t h = k.lo ^ (k.hi * 0x9e3779b97f4a7c15ULL);
        h ^= ((uint64_t)k.last << 17) ^ ((uint64_t)k.depth << 49);
        h ^= h >> 33;
        h *= 0xff51afd7ed558ccdULL;
        h ^= h >> 33;
        return (size_t)h;
    }
};

int index3(int x, int y, int z) { return x + 5 * y + 25 * z; }
array<array<int, 125>, 125> add_map;
array<U128, 125> predecessor_bad;
vector<int> canonical_order;
uint64_t nodes = 0;
int best_depth = 1;
vector<int> best_sequence;
unordered_set<Key, KeyHash> memo;

inline U128 shift_state(U128 state, int x) {
    U128 out = 0;
    uint64_t lo = (uint64_t)state;
    uint64_t hi = (uint64_t)(state >> 64);
    while (lo) {
        int bit = __builtin_ctzll(lo);
        lo &= lo - 1;
        out |= ((U128)1) << add_map[x][bit];
    }
    while (hi) {
        int bit = __builtin_ctzll(hi);
        hi &= hi - 1;
        int source = bit + 64;
        if (source < 125) out |= ((U128)1) << add_map[x][source];
    }
    return out;
}

inline bool legal_extension(U128 state, int x) {
    return (state & predecessor_bad[x]) == 0;
}

bool dfs(U128 state, int depth, int last_order_index, vector<int>& sequence) {
    ++nodes;
    if (depth > best_depth) {
        best_depth = depth;
        best_sequence = sequence;
    }
    if (depth == 10) {
        cout << "FOUND_LENGTH10\n";
        for (int value : sequence) {
            int z = value / 25;
            int rem = value % 25;
            int y = rem / 5;
            int x = rem % 5;
            cout << x << ',' << y << ',' << z << ' ';
        }
        cout << '\n';
        return true;
    }

    Key key{(uint64_t)state, (uint64_t)(state >> 64),
            (uint16_t)last_order_index, (uint8_t)depth};
    if (memo.find(key) != memo.end()) return false;

    for (int oi = last_order_index; oi < (int)canonical_order.size(); ++oi) {
        int x = canonical_order[oi];
        if (!legal_extension(state, x)) continue;
        U128 next = state | shift_state(state, x);
        sequence.push_back(x);
        if (dfs(next, depth + 1, oi, sequence)) return true;
        sequence.pop_back();
    }

    memo.insert(key);
    return false;
}

int main() {
    for (int a = 0; a < 125; ++a) {
        int az = a / 25, ar = a % 25, ay = ar / 5, ax = ar % 5;
        for (int b = 0; b < 125; ++b) {
            int bz = b / 25, br = b % 25, by = br / 5, bx = br % 5;
            add_map[a][b] = index3((ax + bx) % 5, (ay + by) % 5, (az + bz) % 5);
        }
    }

    const vector<array<int, 3>> bad_values = {
        {0, 0, 0}, {0, 1, 0}, {2, 1, 0}, {0, 3, 0},
        {3, 1, 0}, {4, 0, 0}, {2, 3, 0}
    };
    for (int x = 0; x < 125; ++x) {
        int xz = x / 25, xr = x % 25, xy = xr / 5, xx = xr % 5;
        U128 mask = 0;
        for (auto b : bad_values) {
            int sx = (b[0] - xx + 5) % 5;
            int sy = (b[1] - xy + 5) % 5;
            int sz = (b[2] - xz + 5) % 5;
            mask |= ((U128)1) << index3(sx, sy, sz);
        }
        predecessor_bad[x] = mask;
    }

    // Fixed multiset ordering. The distinguished normalized e3 term is separate;
    // the remaining nine terms are enumerated nondecreasingly in this order.
    for (int z = 1; z < 5; ++z)
        for (int y = 0; y < 5; ++y)
            for (int x = 0; x < 5; ++x)
                canonical_order.push_back(index3(x, y, z));
    for (int y = 0; y < 5; ++y)
        for (int x = 0; x < 5; ++x)
            if (x || y) canonical_order.push_back(index3(x, y, 0));

    int zero = index3(0, 0, 0);
    int e3 = index3(0, 0, 1);
    U128 state = ((U128)1) << zero;
    state |= shift_state(state, e3);
    vector<int> sequence{e3};
    best_sequence = sequence;

    bool found = dfs(state, 1, 0, sequence);

    cout << "STATUS=" << (found ? "FOUND_LENGTH10" : "NO_LENGTH10") << '\n';
    cout << "NODES=" << nodes << '\n';
    cout << "MEMO_DEAD_STATES=" << memo.size() << '\n';
    cout << "MAX_LENGTH=" << best_depth << '\n';
    cout << "BEST_WITNESS=";
    for (int value : best_sequence) {
        int z = value / 25;
        int rem = value % 25;
        int y = rem / 5;
        int x = rem % 5;
        cout << x << ',' << y << ',' << z << ' ';
    }
    cout << '\n';
    return found ? 1 : 0;
}
