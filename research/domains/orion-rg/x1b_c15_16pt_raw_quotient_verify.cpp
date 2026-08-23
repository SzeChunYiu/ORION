// Prospective raw verification of the C15 16-point terminal quotient residual.
// Protocol: X1B_C15_16PT_RAW_QUOTIENT_PROTOCOL.md
// No GL(3,3) quotient is used.
#include <array>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <unordered_set>
#include <vector>
using namespace std;
using V=array<int,3>;
vector<V>E;
uint64_t support_count=0,candidates=0,packed4=0,failures=0;
int min_four_masks=1<<30,max_four_masks=0;

bool support_add_ok(int idx,const vector<int>&s){
    V v=E[idx];
    for(int j:s) if((v[0]+E[j][0])%3==0&&(v[1]+E[j][1])%3==0&&(v[2]+E[j][2])%3==0) return false;
    for(int a=0;a<(int)s.size();a++)for(int b=a+1;b<(int)s.size();b++)
        if((v[0]+E[s[a]][0]+E[s[b]][0])%3==0&&
           (v[1]+E[s[a]][1]+E[s[b]][1])%3==0&&
           (v[2]+E[s[a]][2]+E[s[b]][2])%3==0) return false;
    return true;
}

bool four_partition(const vector<int>&support,int&mask_count){
    vector<V>pos;
    for(int i:support){pos.push_back(E[i]);pos.push_back(E[i]);}
    vector<uint16_t> masks;
    unordered_set<uint16_t> maskset;
    for(int a=0;a<13;a++)for(int b=a+1;b<14;b++)for(int c=b+1;c<15;c++)for(int d=c+1;d<16;d++){
        int s0=(pos[a][0]+pos[b][0]+pos[c][0]+pos[d][0])%3;
        int s1=(pos[a][1]+pos[b][1]+pos[c][1]+pos[d][1])%3;
        int s2=(pos[a][2]+pos[b][2]+pos[c][2]+pos[d][2])%3;
        if(s0||s1||s2)continue;
        uint16_t m=(1u<<a)|(1u<<b)|(1u<<c)|(1u<<d);
        masks.push_back(m);maskset.insert(m);
    }
    mask_count=(int)masks.size();
    const uint16_t full=0xFFFFu;
    // Four disjoint zero sums must each have size 4 because the residual has no
    // zero sum <=3 and there are only 16 positions.  Break partition symmetry
    // by requiring the first block to contain position 0 and subsequent blocks
    // to contain the least remaining position.
    for(uint16_t A:masks) if(A&1u){
        uint16_t rem1=full^A,bit1=rem1&-rem1;
        for(uint16_t B:masks) if((B&bit1)&&!(A&B)){
            uint16_t rem2=rem1^B,bit2=rem2&-rem2;
            for(uint16_t C:masks) if((C&bit2)&&!(C&(A|B))){
                uint16_t D=rem2^C;
                if(maskset.count(D))return true;
            }
        }
    }
    return false;
}

void process(const vector<int>&support){
    ++support_count;++candidates;
    int n=0;bool ok=four_partition(support,n);
    min_four_masks=min(min_four_masks,n);max_four_masks=max(max_four_masks,n);
    if(ok)++packed4;else{
        ++failures;cout<<"FAILURE ";for(int i:support){auto v=E[i];cout<<"("<<v[0]<<","<<v[1]<<","<<v[2]<<") ";}cout<<"\n";
    }
}
void rec(vector<int>&s,int start){
    if(s.size()==8){process(s);return;}
    int need=8-(int)s.size();
    for(int i=start;i<=26-need;i++)if(support_add_ok(i,s)){s.push_back(i);rec(s,i+1);s.pop_back();}
}
int main(){
    for(int a=0;a<3;a++)for(int b=0;b<3;b++)for(int c=0;c<3;c++)if(a||b||c)E.push_back({a,b,c});
    vector<int>s;rec(s,0);
    cout<<"supports8 "<<support_count<<" candidates "<<candidates<<" packed4 "<<packed4
        <<" failures "<<failures<<" min_zero4_masks "<<min_four_masks<<" max_zero4_masks "<<max_four_masks<<"\n";
    return failures?1:0;
}
