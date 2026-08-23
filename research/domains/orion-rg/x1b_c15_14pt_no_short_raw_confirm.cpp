// Independent raw verifier for the C15 14-point terminal quotient residual.
// Protocol: X1B_C15_14PT_NO_SHORT_RAW_CONFIRM_PROTOCOL.md
// No GL(3,3) quotient is used.
#include <array>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <vector>
using namespace std;
using V=array<int,3>;

vector<V> E;
uint64_t supports7=0,supports8=0,candidates=0,packed3=0,failures=0;

bool support_add_ok(int idx,const vector<int>&support){
    const V v=E[idx];
    for(int j:support)
        if((v[0]+E[j][0])%3==0 && (v[1]+E[j][1])%3==0 && (v[2]+E[j][2])%3==0)
            return false;
    for(int a=0;a<(int)support.size();a++) for(int b=a+1;b<(int)support.size();b++)
        if((v[0]+E[support[a]][0]+E[support[b]][0])%3==0 &&
           (v[1]+E[support[a]][1]+E[support[b]][1])%3==0 &&
           (v[2]+E[support[a]][2]+E[support[b]][2])%3==0)
            return false;
    return true;
}

bool has_three_disjoint_zero_sums(const vector<int>&pos){
    vector<uint16_t> zero_masks;
    int sumcode[1<<14]; sumcode[0]=0;
    int encoded[14];
    for(int i=0;i<14;i++){
        V v=E[pos[i]];
        encoded[i]=9*v[0]+3*v[1]+v[2];
    }

    // It suffices to keep zero sums of lengths 4..7. The terminal residual has
    // no zero sum <=3, and every zero-sum sequence contains a minimal zero-sum
    // subsequence of length <=D(C_3^3)=7.
    for(int mask=1;mask<(1<<14);mask++){
        int bit=__builtin_ctz((unsigned)mask);
        int prev=mask&(mask-1);
        int code=sumcode[prev];
        int a=code/9,b=(code/3)%3,c=code%3;
        int x=encoded[bit],xa=x/9,xb=(x/3)%3,xc=x%3;
        sumcode[mask]=9*((a+xa)%3)+3*((b+xb)%3)+((c+xc)%3);
        int card=__builtin_popcount((unsigned)mask);
        if(card>=4 && card<=7 && sumcode[mask]==0)
            zero_masks.push_back((uint16_t)mask);
    }

    for(int i=0;i<(int)zero_masks.size();i++)
        for(int j=i+1;j<(int)zero_masks.size();j++) if((zero_masks[i]&zero_masks[j])==0){
            uint16_t used=zero_masks[i]|zero_masks[j];
            for(int k=j+1;k<(int)zero_masks.size();k++)
                if((zero_masks[k]&used)==0) return true;
        }
    return false;
}

void evaluate(const vector<int>&support,const vector<char>&doubled){
    vector<int> pos;
    for(int i=0;i<(int)support.size();i++){
        pos.push_back(support[i]);
        if(doubled[i]) pos.push_back(support[i]);
    }
    if(pos.size()!=14){cerr<<"bad multiplicity\n";exit(2);}
    ++candidates;
    if(has_three_disjoint_zero_sums(pos)) ++packed3;
    else {
        ++failures;
        cout<<"FAILURE ";
        for(int i=0;i<(int)support.size();i++){
            V v=E[support[i]];
            cout<<"("<<v[0]<<","<<v[1]<<","<<v[2]<<")x"<<(doubled[i]?2:1)<<" ";
        }
        cout<<"\n";
    }
}

void process_support(const vector<int>&support){
    if(support.size()==7){
        ++supports7;
        vector<char>doubled(7,1);
        evaluate(support,doubled);
    } else {
        ++supports8;
        for(int a=0;a<8;a++) for(int b=a+1;b<8;b++){
            vector<char>doubled(8,1);
            doubled[a]=doubled[b]=0;
            evaluate(support,doubled);
        }
    }
}

void enumerate_supports(vector<int>&support,int start,int target){
    if((int)support.size()==target){process_support(support);return;}
    int need=target-(int)support.size();
    for(int i=start;i<=26-need;i++) if(support_add_ok(i,support)){
        support.push_back(i);
        enumerate_supports(support,i+1,target);
        support.pop_back();
    }
}

int main(){
    for(int a=0;a<3;a++) for(int b=0;b<3;b++) for(int c=0;c<3;c++)
        if(a||b||c) E.push_back({a,b,c});
    vector<int> support;
    enumerate_supports(support,0,7);
    enumerate_supports(support,0,8);
    cout<<"supports7 "<<supports7
        <<" supports8 "<<supports8
        <<" candidates "<<candidates
        <<" packed3 "<<packed3
        <<" failures "<<failures<<"\n";
    return failures?1:0;
}
