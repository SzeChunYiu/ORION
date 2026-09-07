#include <bits/stdc++.h>
using namespace std;

static int ADDT[343][343], NEG[343];
int enc(int x,int y,int z){return x*49+y*7+z;}
array<int,3> decv(int q){return {q/49,(q/7)%7,q%7};}
int inv7(int a){for(int x=1;x<7;x++)if(a*x%7==1)return x;return 0;}
using BS=bitset<343>;
using Counts=array<int,343>;

vector<pair<int,int>> makeU(int a){
    int ia=inv7(a);
    return {{enc(1,0,0),6},{enc(0,1,0),6},{enc(0,0,1),a},
            {enc((7-ia)%7,(7-ia)%7,1),7-a}};
}
Counts fromU(int a){Counts c{};for(auto [g,m]:makeU(a))c[g]=m;return c;}

vector<BS> subsetSums(const Counts& c,int h){
    vector<BS> dp(h+1); dp[0].set(0);
    for(int g=0;g<343;g++) if(c[g]){
        auto old=dp;
        for(int k=0;k<=h;k++) if(old[k].any()){
            int cur=0;
            for(int take=1;take<=min(c[g],h-k);take++){
                cur=ADDT[cur][g];
                for(int s=0;s<343;s++) if(old[k][s]) dp[k+take].set(ADDT[s][cur]);
            }
        }
    }
    return dp;
}

void enumerateCompanions(const Counts& base,int m,int h,
                         function<void(const vector<int>&)> cb){
    auto dp=subsetSums(base,h);
    vector<BS> forb(h+1);
    for(int j=0;j<=h;j++) for(int k=0;k<=h-j;k++)
        for(int s=0;s<343;s++) if(dp[k][s]) forb[j].set(NEG[s]);

    vector<int> allowed;
    for(int x=0;x<343;x++) if(!forb[1][x] && base[x]<6) allowed.push_back(x);

    vector<BS> ss(m+1); ss[0].set(0);
    array<int,343> mult{};
    vector<int> chosen;

    function<void(int,int,int)> dfs=[&](int start,int depth,int total){
        auto validAdd=[&](int x,int d,vector<BS>& news){
            news.assign(d+2,BS{});
            for(int k=1;k<=d+1;k++){
                for(int s=0;s<343;s++) if(ss[k-1][s]) news[k].set(ADDT[s][x]);
                if(k<=h && (news[k]&forb[k]).any()) return false;
            }
            return true;
        };
        if(depth==m-1){
            int x=NEG[total];
            auto it=lower_bound(allowed.begin(),allowed.end(),x);
            if(it==allowed.end()||*it!=x) return;
            if(!chosen.empty()&&x<chosen.back()) return;
            if(mult[x]>=6-base[x]) return;
            vector<BS> news;
            if(!validAdd(x,depth,news)) return;
            auto seq=chosen; seq.push_back(x); cb(seq); return;
        }
        for(int pos=start;pos<(int)allowed.size();pos++){
            int x=allowed[pos];
            if(mult[x]>=6-base[x]) continue;
            vector<BS> news;
            if(!validAdd(x,depth,news)) continue;
            vector<BS> old(depth+2);
            for(int k=1;k<=depth+1;k++){old[k]=ss[k];ss[k]|=news[k];}
            mult[x]++; chosen.push_back(x);
            dfs(pos,depth+1,ADDT[total][x]);
            chosen.pop_back(); mult[x]--;
            for(int k=1;k<=depth+1;k++) ss[k]=old[k];
        }
    };
    dfs(0,0,0);
}

vector<vector<int>> zeroVectors(const Counts& c,vector<int>& elems){
    elems.clear(); for(int g=0;g<343;g++) if(c[g]) elems.push_back(g);
    int s=elems.size(); vector<vector<int>> out; vector<int> cur(s);
    function<void(int,int,int)> rec=[&](int i,int len,int sum){
        if(len>13) return;
        if(i==s){if(len>=8&&sum==0) out.push_back(cur);return;}
        int g=elems[i],acc=0;
        for(int t=0;t<=c[g];t++){
            cur[i]=t; rec(i+1,len+t,ADDT[sum][acc]); acc=ADDT[acc][g];
        }
        cur[i]=0;
    };
    rec(0,0,0); return out;
}

bool leqv(const vector<int>& a,const vector<int>& b){
    for(int i=0;i<(int)a.size();i++) if(a[i]>b[i]) return false; return true;
}

bool hasPack4(const Counts& c){
    vector<int> elems; auto z=zeroVectors(c,elems); vector<int> cap;
    for(int g:elems) cap.push_back(c[g]);
    vector<vector<int>> small;
    for(auto &v:z){int L=accumulate(v.begin(),v.end(),0);if(L==8||L==9)small.push_back(v);}
    for(int i=0;i<(int)small.size();i++) for(int j=i;j<(int)small.size();j++){
        vector<int> rem(cap.size()); bool ok=true;
        for(int k=0;k<(int)cap.size();k++){
            int u=small[i][k]+small[j][k]; if(u>cap[k]){ok=false;break;} rem[k]=cap[k]-u;
        }
        if(!ok) continue;
        int rl=accumulate(rem.begin(),rem.end(),0);
        for(auto &v:z){
            int L=accumulate(v.begin(),v.end(),0);
            if(L<8||L>13||rl-L<8) continue;
            if(leqv(v,rem)) return true;
        }
    }
    return false;
}

string keyCounts(const Counts& c){
    string s; for(int i=0;i<343;i++) if(c[i]) s+=to_string(i)+":"+to_string(c[i])+","; return s;
}

int main(){
    for(int i=0;i<343;i++){
        auto a=decv(i); NEG[i]=enc((7-a[0])%7,(7-a[1])%7,(7-a[2])%7);
        for(int j=0;j<343;j++){
            auto b=decv(j); ADDT[i][j]=enc((a[0]+b[0])%7,(a[1]+b[1])%7,(a[2]+b[2])%7);
        }
    }
    map<int,long long> pairs,extendable,completions,pack4;
    set<string> distinctB;
    for(int a=1;a<=3;a++){
        Counts U=fromU(a);
        enumerateCompanions(U,10,9,[&](const vector<int>& v){
            pairs[a]++; Counts P=U; for(int x:v)P[x]++; long long local=0;
            enumerateCompanions(P,8,7,[&](const vector<int>& w){
                local++; completions[a]++; Counts B=P; for(int x:w)B[x]++;
                distinctB.insert(keyCounts(B)); if(hasPack4(B))pack4[a]++;
            });
            if(local) extendable[a]++;
        });
    }
    assert(pairs[1]==538&&pairs[2]==24&&pairs[3]==0);
    assert(extendable[1]==229&&extendable[2]==6&&extendable[3]==0);
    assert(completions[1]==2772&&completions[2]==24&&completions[3]==0);
    assert(distinctB.size()==1572);
    assert(pack4[1]==2772&&pack4[2]==24&&pack4[3]==0);
    cout<<"{\"status\":\"SUPPORT4_81019_CLOSURE_GREEN\","
        <<"\"pair_candidates\":["<<pairs[1]<<","<<pairs[2]<<","<<pairs[3]<<"],"
        <<"\"extendable_pairs\":["<<extendable[1]<<","<<extendable[2]<<","<<extendable[3]<<"],"
        <<"\"factor_triples\":"<<(completions[1]+completions[2])<<","
        <<"\"distinct_sequences\":"<<distinctB.size()<<","
        <<"\"four_pack_triples\":"<<(pack4[1]+pack4[2])<<"}\n";
}
