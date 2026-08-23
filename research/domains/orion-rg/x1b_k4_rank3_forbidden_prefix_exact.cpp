// Exact solver for X1-B final rank-3 forbidden-prefix classes.
// Protocol: X1B_K4_RANK3_FORBIDDEN_PREFIX_PROTOCOL.md
// State quotient: X1B_K4_FORBIDDEN_PREFIX_ILLEGAL_STATE_QUOTIENT_2026-08-22.md
// Dominance: X1B_K4_FORBIDDEN_PREFIX_MINLAST_DOMINANCE_2026-08-22.md
//
// Enumerates nondecreasing multisets of nonzero F_5^3 elements.  The state is
// the exact illegal-next-term set I=F-Sigma_0(T).  At fixed depth, identical I
// states retain only the minimum reachable canonical last index.
#include <array>
#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <vector>
using namespace std;

struct Bits { uint64_t lo, hi; };
static inline void set_bit(Bits& a, int i) {
    if (i < 64) a.lo |= 1ULL << i;
    else a.hi |= 1ULL << (i - 64);
}
static inline bool test_bit(Bits a, int i) {
    return i < 64 ? ((a.lo >> i) & 1ULL) : ((a.hi >> (i - 64)) & 1ULL);
}
static inline Bits bit_or(Bits a, Bits b) { return {a.lo | b.lo, a.hi | b.hi}; }
static inline uint64_t hash_bits(uint64_t lo, uint64_t hi) {
    uint64_t x = lo + 0x9e3779b97f4a7c15ULL;
    x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9ULL;
    x ^= hi + 0x94d049bb133111ebULL + (x << 6) + (x >> 2);
    x ^= x >> 27;
    x *= 0x94d049bb133111ebULL;
    return x ^ (x >> 31);
}

struct States {
    vector<uint64_t> lo, hi;
    vector<uint8_t> last;
    size_t size() const { return last.size(); }
    void release() {
        vector<uint64_t>().swap(lo);
        vector<uint64_t>().swap(hi);
        vector<uint8_t>().swap(last);
    }
};

struct FlatMinLast {
    size_t cap, mask, n = 0;
    vector<uint64_t> lo, hi;
    vector<uint8_t> last; // 255 = empty

    explicit FlatMinLast(int power)
        : cap(1ULL << power), mask(cap - 1), lo(cap), hi(cap), last(cap, 255) {}

    void insert(Bits key, uint8_t value) {
        size_t p = hash_bits(key.lo, key.hi) & mask;
        for (size_t probe = 0; probe < cap; ++probe) {
            const uint8_t old = last[p];
            if (old == 255) {
                lo[p] = key.lo;
                hi[p] = key.hi;
                last[p] = value;
                ++n;
                return;
            }
            if (lo[p] == key.lo && hi[p] == key.hi) {
                if (value < old) last[p] = value;
                return;
            }
            p = (p + 1) & mask;
        }
        throw runtime_error("flat hash capacity exhausted");
    }

    States extract() const {
        States out;
        out.lo.reserve(n); out.hi.reserve(n); out.last.reserve(n);
        for (size_t p = 0; p < cap; ++p) {
            if (last[p] != 255) {
                out.lo.push_back(lo[p]);
                out.hi.push_back(hi[p]);
                out.last.push_back(last[p]);
            }
        }
        return out;
    }
};

using Vec = array<int, 3>;

static vector<Vec> forbidden_class(int cls) {
    if (cls == 10) return {
        Vec{0,0,0}, Vec{0,0,1}, Vec{0,0,2}, Vec{0,1,0}, Vec{0,1,1},
        Vec{1,0,0}, Vec{1,0,1}, Vec{1,4,1}, Vec{2,4,4}, Vec{4,1,2}
    };
    if (cls == 11) return {
        Vec{0,0,0}, Vec{0,0,1}, Vec{0,0,2}, Vec{0,1,0}, Vec{0,1,1},
        Vec{0,4,3}, Vec{1,0,0}, Vec{1,0,1}, Vec{1,1,0}, Vec{1,1,4},
        Vec{1,2,2}
    };
    if (cls == 12) return {
        Vec{0,0,0}, Vec{0,0,1}, Vec{0,0,2}, Vec{0,1,0}, Vec{0,1,1},
        Vec{0,2,3}, Vec{0,4,3}, Vec{1,0,0}, Vec{1,0,1}, Vec{1,1,0},
        Vec{1,1,4}, Vec{1,4,2}
    };
    throw runtime_error("class must be 10, 11, or 12");
}

struct Solver {
    array<array<array<Bits, 256>, 16>, 125>* translate;
    Bits forbidden{0,0};
    int cls;

    explicit Solver(int cls_) : cls(cls_) {
        for (auto v : forbidden_class(cls)) set_bit(forbidden, 25*v[0] + 5*v[1] + v[2]);
        translate = new array<array<array<Bits, 256>, 16>, 125>();
        for (int x = 0; x < 125; ++x) {
            const int xa = x / 25, xb = (x / 5) % 5, xc = x % 5;
            for (int chunk = 0; chunk < 16; ++chunk) {
                for (int pattern = 0; pattern < 256; ++pattern) {
                    Bits out{0,0};
                    for (int b = 0; b < 8; ++b) if ((pattern >> b) & 1) {
                        const int g = chunk*8 + b;
                        if (g >= 125) continue;
                        const int a = g/25, bb = (g/5)%5, c = g%5;
                        const int dest = 25*((a-xa+5)%5) + 5*((bb-xb+5)%5) + (c-xc+5)%5;
                        set_bit(out, dest);
                    }
                    (*translate)[x][chunk][pattern] = out;
                }
            }
        }
    }
    ~Solver() { delete translate; }

    Bits shift_minus(Bits s, int x) const {
        Bits out{0,0};
        for (int chunk=0; chunk<8; ++chunk)
            out = bit_or(out, (*translate)[x][chunk][(s.lo >> (8*chunk)) & 255]);
        for (int chunk=8; chunk<16; ++chunk)
            out = bit_or(out, (*translate)[x][chunk][(s.hi >> (8*(chunk-8))) & 255]);
        return out;
    }

    void run() {
        // Capacities are implementation storage only; the search criterion is unchanged.
        const int powers[10] = {8,14,19,23,25,24,23,22,21,20};
        States cur;
        cur.lo = {forbidden.lo}; cur.hi = {forbidden.hi}; cur.last = {0};
        uint64_t transitions = 0;
        cout << "class " << cls << " depth 0 states 1\n";

        for (int depth=0; depth<10; ++depth) {
            FlatMinLast next(powers[depth]);
            for (size_t si=0; si<cur.size(); ++si) {
                Bits I{cur.lo[si], cur.hi[si]};
                const int last = cur.last[si];
                for (int pos=last; pos<124; ++pos) {
                    const int x = pos + 1; // lexicographic group index, zero excluded
                    if (test_bit(I, x)) continue;
                    Bits J = bit_or(I, shift_minus(I, x));
                    next.insert(J, static_cast<uint8_t>(pos));
                    ++transitions;
                }
            }
            cout << "class " << cls << " depth " << (depth+1)
                 << " states " << next.n << " transitions " << transitions << "\n";
            if (next.n == 0) {
                cout << "NO max_length " << depth << "\n";
                return;
            }
            States ns = next.extract();
            cur.release();
            cur = move(ns);
        }
        cout << "YES depth10_states " << cur.size() << "\n";
    }
};

int main(int argc, char** argv) {
    const int cls = argc > 1 ? atoi(argv[1]) : 10;
    Solver solver(cls);
    solver.run();
    return 0;
}
