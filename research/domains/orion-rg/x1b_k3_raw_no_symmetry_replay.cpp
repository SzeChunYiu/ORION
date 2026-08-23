// Independent raw replay for the X1-B k=3 / 10-point scalar residual.
// No GL(3,3) quotient is used. Every raw multiplicity candidate is checked.
#include <array>
#include <cstdint>
#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
using V=array<int,3>;

vector<V> E;
uint64_t raw_candidates=0, no_disjoint_candidates=0, inconsistent_candidates=0, consistent_candidates=0;
int max_zero_sum_masks=0;

static inline V add2(V a,V b){return {(a[0]+b[0])%3,(a[1]+b[1])%3,(a[2]+b[2])%3};}
static inline V add3(V a,V b,V c){return {(a[0]+b[0]+c[0])%3,(a[1]+b[1]+c[1])%3,(a[2]+b[2]+c[2])%3};}
static inline bool iszero(V v){return v[0]==0&&v[1]==0&&v[2]==0;}

bool support_add_ok(int idx,const vector<int>& support){
    V v=E[idx];
    for(int a:support) if(iszero(add2(E[a],v))) return false;
    for(size_t i=0;i<support.size();i++) for(size_t j=i+1;j<support.size();j++)
        if(iszero(add3(E[support[i]],E[support[j]],v))) return false;
    return true;
}

bool common_rhs_inconsistent(const vector<int>& masks){
    vector<array<int,11>> rows;
    rows.reserve(masks.size());
    for(int mask:masks){
        array<int,11> row{};
        for(int i=0;i<10;i++) row[i]=(mask>>i)&1;
        row[10]=1;
        rows.push_back(row);
    }
    int rank=0;
    for(int col=0;col<10;col++){
        int pivot=-1;
        for(int r=rank;r<(int)rows.size();r++) if(rows[r][col]%5){pivot=r;break;}
        if(pivot<0) continue;
        swap(rows[rank],rows[pivot]);
        int v=rows[rank][col]%5, inv=1;
        for(int t=1;t<5;t++) if(v*t%5==1){inv=t;break;}
        for(int j=col;j<=10;j++) rows[rank][j]=(rows[rank][j]*inv)%5;
        for(int r=0;r<(int)rows.size();r++) if(r!=rank && rows[r][col]%5){
            int f=rows[r][col]%5;
            for(int j=col;j<=10;j++){
                rows[r][j]=(rows[r][j]-f*rows[rank][j])%5;
                if(rows[r][j]<0) rows[r][j]+=5;
            }
        }
        ++rank;
    }
    for(auto &row:rows){
        bool zero_coeff=true;
        for(int c=0;c<10;c++) if(row[c]%5){zero_coeff=false;break;}
        if(zero_coeff && row[10]%5) return true;
    }
    return false;
}

void evaluate(const vector<int>& pos){
    ++raw_candidates;
    vector<int> masks;
    for(int mask=1;mask<(1<<10);mask++){
        V sum{0,0,0};
        for(int i=0;i<10;i++) if((mask>>i)&1)
            for(int c=0;c<3;c++) sum[c]=(sum[c]+E[pos[i]][c])%3;
        if(iszero(sum)) masks.push_back(mask);
    }
    for(int mask:masks) if(__builtin_popcount((unsigned)mask)<=3){
        cerr<<"short-zero-sum generator mismatch\n"; exit(2);
    }
    for(size_t i=0;i<masks.size();i++) for(size_t j=i+1;j<masks.size();j++)
        if((masks[i]&masks[j])==0) return;

    ++no_disjoint_candidates;
    max_zero_sum_masks=max(max_zero_sum_masks,(int)masks.size());
    if(common_rhs_inconsistent(masks)) ++inconsistent_candidates;
    else ++consistent_candidates;
}

void enumerate_multiplicities(const vector<int>& support,int at,int remaining,vector<int>& pos){
    if(at==(int)support.size()){
        if(remaining==0 && pos.size()==10) evaluate(pos);
        return;
    }
    int later=(int)support.size()-at-1;
    for(int mult=1;mult<=2;mult++){
        if(remaining-mult<later || remaining-mult>2*later) continue;
        for(int k=0;k<mult;k++) pos.push_back(support[at]);
        enumerate_multiplicities(support,at+1,remaining-mult,pos);
        for(int k=0;k<mult;k++) pos.pop_back();
    }
}

void enumerate_supports(int start,int target,vector<int>& support){
    if((int)support.size()==target){
        vector<int> pos;
        enumerate_multiplicities(support,0,10,pos);
        return;
    }
    int need=target-(int)support.size();
    for(int i=start;i<=26-need;i++) if(support_add_ok(i,support)){
        support.push_back(i);
        enumerate_supports(i+1,target,support);
        support.pop_back();
    }
}

int main(){
    for(int a=0;a<3;a++) for(int b=0;b<3;b++) for(int c=0;c<3;c++)
        if(a||b||c) E.push_back({a,b,c});
    vector<int> support;
    // With multiplicities <=2 and total length 10, support size is at least 5.
    // The no-short-zero-sum support cap in F_3^3 is at most 8.
    for(int size=5;size<=8;size++) enumerate_supports(0,size,support);

    cout<<"raw_candidates "<<raw_candidates
        <<" no_disjoint "<<no_disjoint_candidates
        <<" inconsistent "<<inconsistent_candidates
        <<" consistent "<<consistent_candidates
        <<" max_masks "<<max_zero_sum_masks<<"\n";
    return consistent_candidates?1:0;
}
