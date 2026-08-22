// Independent replay for X1-B rank-3 forbidden-prefix NO results.
// Deliberately does NOT use memoization, layerwise DP, or minimum-last dominance.
// It enumerates the canonical nondecreasing multiset tree directly.
#include <array>
#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <vector>
using namespace std;
struct Bits{uint64_t lo,hi;};
static inline void set_bit(Bits&a,int i){if(i<64)a.lo|=1ULL<<i;else a.hi|=1ULL<<(i-64);}static inline bool test_bit(Bits a,int i){return i<64?((a.lo>>i)&1ULL):((a.hi>>(i-64))&1ULL);}static inline Bits bit_or(Bits a,Bits b){return{a.lo|b.lo,a.hi|b.hi};}
using Vec=array<int,3>;
static vector<Vec> forbidden_class(int c){if(c==10)return{{0,0,0},{0,0,1},{0,0,2},{0,1,0},{0,1,1},{1,0,0},{1,0,1},{1,4,1},{2,4,4},{4,1,2}};if(c==11)return{{0,0,0},{0,0,1},{0,0,2},{0,1,0},{0,1,1},{0,4,3},{1,0,0},{1,0,1},{1,1,0},{1,1,4},{1,2,2}};if(c==12)return{{0,0,0},{0,0,1},{0,0,2},{0,1,0},{0,1,1},{0,2,3},{0,4,3},{1,0,0},{1,0,1},{1,1,0},{1,1,4},{1,4,2}};throw runtime_error("class must be 10, 11, or 12");}
struct Solver{
    array<array<array<Bits,256>,16>,125>* lut;
    Bits forbidden{0,0};
    uint64_t nodes=0;
    int max_depth=0, cls;
    explicit Solver(int c):cls(c){
        for(auto v:forbidden_class(c))set_bit(forbidden,25*v[0]+5*v[1]+v[2]);
        lut=new array<array<array<Bits,256>,16>,125>();
        for(int x=0;x<125;x++){
            int xa=x/25,xb=(x/5)%5,xc=x%5;
            for(int chunk=0;chunk<16;chunk++)for(int pattern=0;pattern<256;pattern++){
                Bits out{0,0};
                for(int b=0;b<8;b++)if((pattern>>b)&1){
                    int g=chunk*8+b;if(g>=125)continue;
                    int a=g/25,bb=(g/5)%5,cc=g%5;
                    set_bit(out,25*((a-xa+5)%5)+5*((bb-xb+5)%5)+(cc-xc+5)%5);
                }
                (*lut)[x][chunk][pattern]=out;
            }
        }
    }
    ~Solver(){delete lut;}
    Bits shift_minus(Bits s,int x)const{
        Bits out{0,0};
        for(int chunk=0;chunk<8;chunk++)out=bit_or(out,(*lut)[x][chunk][(s.lo>>(8*chunk))&255]);
        for(int chunk=8;chunk<16;chunk++)out=bit_or(out,(*lut)[x][chunk][(s.hi>>(8*(chunk-8)))&255]);
        return out;
    }
    bool dfs(Bits I,int depth,int last){
        ++nodes;
        if(depth>max_depth)max_depth=depth;
        if(depth==10)return true;
        for(int pos=last;pos<124;pos++){
            int x=pos+1;
            if(test_bit(I,x))continue;
            if(dfs(bit_or(I,shift_minus(I,x)),depth+1,pos))return true;
        }
        return false;
    }
    void run(){bool found=dfs(forbidden,0,0);cout<<"class "<<cls<<" found "<<found<<" nodes "<<nodes<<" max_depth "<<max_depth<<"\n";}
};
int main(int argc,char**argv){int cls=argc>1?atoi(argv[1]):10;Solver s(cls);s.run();return 0;}
