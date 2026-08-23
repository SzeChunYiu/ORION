// Independent replay for X1-B final rank-2-radical forbidden-prefix NO results.
// Deliberately different from the primary illegal-state DP:
// - carries Sigma_0(T), the exact represented subset-sum set, directly;
// - no memoization;
// - no layerwise state merging;
// - no minimum-last dominance.
// The only quotient is canonical nondecreasing multiset ordering.
#include <array>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <vector>
using namespace std;

struct Bits { uint64_t lo=0, hi=0; };
static inline void setb(Bits& b,int i){ if(i<64)b.lo|=1ULL<<i; else b.hi|=1ULL<<(i-64); }
static inline bool intersects(Bits a,Bits b){ return (a.lo&b.lo)||(a.hi&b.hi); }
static inline Bits bor(Bits a,Bits b){ return {a.lo|b.lo,a.hi|b.hi}; }

static vector<int> forbidden_indices(int cls){
    if(cls==11) return {0,1,2,5,6,10,25,26,46,65,111};
    if(cls==12) return {0,1,2,5,6,10,25,26,30,34,53,107};
    throw runtime_error("class must be 11 or 12");
}

struct Solver {
    int cls;
    Bits forbidden;
    array<array<array<Bits,256>,16>,125>* translate;
    uint64_t nodes=0;
    int maxdepth=0;

    explicit Solver(int c):cls(c){
        for(int g: forbidden_indices(c)) setb(forbidden,g);
        translate=new array<array<array<Bits,256>,16>,125>();
        for(int x=0;x<125;x++){
            int xa=x/25, xb=(x/5)%5, xc=x%5;
            for(int chunk=0;chunk<16;chunk++) for(int pat=0;pat<256;pat++){
                Bits out;
                for(int bit=0;bit<8;bit++) if((pat>>bit)&1){
                    int g=chunk*8+bit;
                    if(g>=125) continue;
                    int a=g/25, b=(g/5)%5, cc=g%5;
                    int h=25*((a+xa)%5)+5*((b+xb)%5)+((cc+xc)%5);
                    setb(out,h);
                }
                (*translate)[x][chunk][pat]=out;
            }
        }
    }
    ~Solver(){ delete translate; }

    Bits plus(Bits s,int x) const {
        Bits out;
        for(int chunk=0;chunk<8;chunk++)
            out=bor(out,(*translate)[x][chunk][(s.lo>>(8*chunk))&255]);
        for(int chunk=8;chunk<16;chunk++)
            out=bor(out,(*translate)[x][chunk][(s.hi>>(8*(chunk-8)))&255]);
        return out;
    }

    bool dfs(Bits sigma,int depth,int last_pos){
        ++nodes;
        if(depth>maxdepth) maxdepth=depth;
        if(depth==10) return true;
        for(int pos=last_pos; pos<124; ++pos){
            int x=pos+1;
            Bits shifted=plus(sigma,x);
            if(intersects(shifted,forbidden)) continue;
            if(dfs(bor(sigma,shifted),depth+1,pos)) return true;
        }
        return false;
    }

    void run(){
        Bits sigma; setb(sigma,0); // empty subset sum
        bool found=dfs(sigma,0,0);
        cout << "class "<<cls<<" found "<<(found?1:0)
             <<" nodes "<<nodes<<" maxdepth "<<maxdepth<<"\n";
    }
};

int main(int argc,char**argv){
    int cls=argc>1?atoi(argv[1]):11;
    Solver s(cls);
    s.run();
    return 0;
}
