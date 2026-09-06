#include <bits/stdc++.h>
using namespace std;

static int ADDT[343][343], NEG[343];
int enc(int x,int y,int z){return x*49+y*7+z;}
array<int,3> decv(int q){return {q/49,(q/7)%7,q%7};}
int inv7(int a){for(int x=1;x<7;x++)if(a*x%7==1)return x;return 0;}
using Counts=array<int,343>;

vector<pair<int,int>> makeU(int a){
    int ia=inv7(a);
    return {{enc(1,0,0),6},{enc(0,1,0),6},{enc(0,0,1),a},
            {enc((7-ia)%7,(7-ia)%7,1),7-a}};
}
Counts fromU(int a){Counts c{};for(auto [g,m]:makeU(a))c[g]=m;return c;}

vector<int> minDepth(const Counts& c,int h){
    const int INF=99; vector<int> dp(343,INF); dp[0]=0;
    for(int g=0;g<343;g++) if(c[g]){
        auto old=dp;
        for(int s=0;s<343;s++) if(old[s]<=h){
            int acc=0;
            for(int t=1;t<=c[g]&&old[s]+t<=h;t++){
                acc=ADDT[acc][g]; int ns=ADDT[s][acc];
                dp[ns]=min(dp[ns],old[s]+t);
            }
        }
    }
    return dp;
}

bool appendValid(const vector<int>& chosen,int x,int h,const vector<int>& md){
    int d=chosen.size(),lim=1<<d;
    for(int mask=0;mask<lim;mask++){
        int sz=1+__builtin_popcount((unsigned)mask); if(sz>h)continue;
        int s=x; for(int i=0;i<d;i++) if(mask>>i&1) s=ADDT[s][chosen[i]];
        if(md[NEG[s]]<=h-sz) return false;
    }
    return true;
}

void enumerateIndependent(const Counts& base,int m,int h,
                          function<void(const vector<int>&)> cb){
    auto md=minDepth(base,h); vector<int> allowed;
    for(int x=0;x<343;x++) if(base[x]<6 && md[NEG[x]]>h-1) allowed.push_back(x);
    array<int,343> mult{}; vector<int> chosen;
    function<void(int,int,int)> dfs=[&](int start,int depth,int total){
        if(depth==m-1){
            int x=NEG[total]; auto it=lower_bound(allowed.begin(),allowed.end(),x);
            if(it==allowed.end()||*it!=x)return;
            if(!chosen.empty()&&x<chosen.back())return;
            if(mult[x]>=6-base[x])return;
            if(!appendValid(chosen,x,h,md))return;
            auto seq=chosen;seq.push_back(x);cb(seq);return;
        }
        for(int pos=start;pos<(int)allowed.size();pos++){
            int x=allowed[pos]; if(mult[x]>=6-base[x])continue;
            if(!appendValid(chosen,x,h,md))continue;
            mult[x]++;chosen.push_back(x);
            dfs(pos,depth+1,ADDT[total][x]);
            chosen.pop_back();mult[x]--;
        }
    };
    dfs(0,0,0);
}

vector<vector<int>> zeroVectors(const Counts& c,vector<int>& elems){
    elems.clear();for(int g=0;g<343;g++)if(c[g])elems.push_back(g);
    int s=elems.size();vector<vector<int>> out;vector<int> cur(s);
    function<void(int,int,int)> rec=[&](int i,int len,int sum){
        if(len>13)return;
        if(i==s){if(len>=8&&sum==0)out.push_back(cur);return;}
        int g=elems[i],acc=0;
        for(int t=0;t<=c[g];t++){
            cur[i]=t;rec(i+1,len+t,ADDT[sum][acc]);acc=ADDT[acc][g];
        }
        cur[i]=0;
    };
    rec(0,0,0);return out;
}

uint64_t code(const vector<int>& v){uint64_t z=0,m=1;for(int x:v){z+=m*x;m*=7;}return z;}

bool hasPack4PairComplement(const Counts& c){
    vector<int> elems;auto z=zeroVectors(c,elems);vector<int> cap;
    for(int g:elems)cap.push_back(c[g]);
    unordered_set<uint64_t> pairCodes;vector<vector<int>> unions;
    for(int i=0;i<(int)z.size();i++)for(int j=i;j<(int)z.size();j++){
        vector<int> u(cap.size());bool ok=true;
        for(int k=0;k<(int)cap.size();k++){
            u[k]=z[i][k]+z[j][k];if(u[k]>cap[k]){ok=false;break;}
        }
        if(ok){auto c0=code(u);if(pairCodes.insert(c0).second)unions.push_back(move(u));}
    }
    for(auto &u:unions){
        vector<int> v(cap.size());for(int k=0;k<(int)cap.size();k++)v[k]=cap[k]-u[k];
        if(pairCodes.count(code(v)))return true;
    }
    return false;
}

string keyCounts(const Counts& c){
    string s;for(int i=0;i<343;i++)if(c[i])s+=to_string(i)+":"+to_string(c[i])+",";return s;
}

int main(){
    for(int i=0;i<343;i++){
        auto a=decv(i);NEG[i]=enc((7-a[0])%7,(7-a[1])%7,(7-a[2])%7);
        for(int j=0;j<343;j++){
            auto b=decv(j);ADDT[i][j]=enc((a[0]+b[0])%7,(a[1]+b[1])%7,(a[2]+b[2])%7);
        }
    }
    map<int,long long> pairs,extendable,completions,pack4;set<string> distinctB;
    for(int a=1;a<=3;a++){
        Counts U=fromU(a);
        enumerateIndependent(U,10,9,[&](const vector<int>& v){
            pairs[a]++;Counts P=U;for(int x:v)P[x]++;long long local=0;
            enumerateIndependent(P,8,7,[&](const vector<int>& w){
                local++;completions[a]++;Counts B=P;for(int x:w)B[x]++;
                distinctB.insert(keyCounts(B));if(hasPack4PairComplement(B))pack4[a]++;
            });
            if(local)extendable[a]++;
        });
    }
    assert(pairs[1]==538&&pairs[2]==24&&pairs[3]==0);
    assert(extendable[1]==229&&extendable[2]==6&&extendable[3]==0);
    assert(completions[1]==2772&&completions[2]==24&&completions[3]==0);
    assert(distinctB.size()==1572);
    assert(pack4[1]==2772&&pack4[2]==24&&pack4[3]==0);
    cout<<"{\"status\":\"SUPPORT4_81019_CLOSURE_INDEPENDENT_GREEN\","
        <<"\"method\":\"occurrence-mask min-depth cover plus pair-complement pack4\","
        <<"\"pair_candidates\":["<<pairs[1]<<","<<pairs[2]<<","<<pairs[3]<<"],"
        <<"\"extendable_pairs\":["<<extendable[1]<<","<<extendable[2]<<","<<extendable[3]<<"],"
        <<"\"factor_triples\":"<<(completions[1]+completions[2])<<","
        <<"\"distinct_sequences\":"<<distinctB.size()<<","
        <<"\"four_pack_triples\":"<<(pack4[1]+pack4[2])<<"}\n";
}
