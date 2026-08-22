#include <bits/stdc++.h>
using namespace std;
using U128 = unsigned __int128;

int index3(int x, int y, int z) { return x + 5 * y + 25 * z; }
array<array<uint8_t, 125>, 125> add_map;
array<U128, 125> predecessor_bad;
vector<int> canonical_order;
uint64_t nodes = 0;
int best_depth = 1;
vector<int> best_sequence;

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
    if (depth == 10) return true;

    for (int oi = last_order_index; oi < (int)canonical_order.size(); ++oi) {
        int x = canonical_order[oi];
        if (!legal_extension(state, x)) continue;
        U128 next = state | shift_state(state, x);
        sequence.push_back(x);
        if (dfs(next, depth + 1, oi, sequence)) return true;
        sequence.pop_back();
    }
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
        int z = x / 25, rem = x % 25, y = rem / 5, a = rem % 5;
        U128 mask = 0;
        for (auto b : bad_values)
            mask |= ((U128)1) << index3((b[0] - a + 5) % 5,
                                         (b[1] - y + 5) % 5,
                                         (b[2] - z + 5) % 5);
        predecessor_bad[x] = mask;
    }

    // Deliberately different from the primary verifier:
    // plane first; then off-plane in descending coordinates; no memoization.
    for (int y = 4; y >= 0; --y)
        for (int x = 4; x >= 0; --x)
            if (x || y) canonical_order.push_back(index3(x, y, 0));
    for (int z = 4; z >= 1; --z)
        for (int y = 4; y >= 0; --y)
            for (int x = 4; x >= 0; --x)
                canonical_order.push_back(index3(x, y, z));

    int zero = index3(0, 0, 0);
    int e3 = index3(0, 0, 1);
    U128 state = ((U128)1) << zero;
    state |= shift_state(state, e3);
    vector<int> sequence{e3};
    best_sequence = sequence;

    bool found = dfs(state, 1, 0, sequence);

    cout << "STATUS=" << (found ? "FOUND_LENGTH10" : "NO_LENGTH10") << '\n';
    cout << "NODES=" << nodes << '\n';
    cout << "MAX_LENGTH=" << best_depth << '\n';
    cout << "BEST_WITNESS=";
    for (int value : best_sequence) {
        int z = value / 25, rem = value % 25, y = rem / 5, x = rem % 5;
        cout << x << ',' << y << ',' << z << ' ';
    }
    cout << '\n';
    return found ? 1 : 0;
}
