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

int rankMod7(const vector<int>& elems){
    vector<array<int,3>> rows;
    for(int q:elems) rows.push_back(decv(q));
    int rank=0;
    for(int col=0;col<3 && rank<(int)rows.size();col++){
        int piv=-1;
        for(int i=rank;i<(int)rows.size();i++) if(rows[i][col]){piv=i;break;}
        if(piv<0) continue;
        swap(rows[rank],rows[piv]);
        int iv=inv7(rows[rank][col]);
        for(int c=col;c<3;c++) rows[rank][c]=rows[rank][c]*iv%7;
        for(int i=0;i<(int)rows.size();i++) if(i!=rank && rows[i][col]){
            int f=rows[i][col];
            for(int c=col;c<3;c++) rows[i][c]=(rows[i][c]-f*rows[rank][c]%7+7)%7;
        }
        rank++;
    }
    return rank;
}

int main(){
    for(int i=0;i<343;i++){
        auto a=decv(i);
        NEG[i]=enc((7-a[0])%7,(7-a[1])%7,(7-a[2])%7);
        for(int j=0;j<343;j++){
            auto b=decv(j);
            ADDT[i][j]=enc((a[0]+b[0])%7,(a[1]+b[1])%7,(a[2]+b[2])%7);
        }
    }

    map<int,long long> total,face;
    for(int a=1;a<=3;a++){
        Counts U=fromU(a);
        set<int> us;
        for(int g=0;g<343;g++) if(U[g]) us.insert(g);
        enumerateCompanions(U,10,9,[&](const vector<int>& v){
            total[a]++;
            map<int,int> vc;
            for(int x:v) vc[x]++;
            set<int> uni=us;
            vector<int> ve;
            for(auto [g,m]:vc){uni.insert(g);ve.push_back(g);}
            if(uni.size()!=6) return;
            face[a]++;
            // This branch is expected to be empty.  If it is ever nonempty,
            // assert the previously proved support-six normal form before reporting it.
            assert(ve.size()==3 || ve.size()==4);
            int r=rankMod7(ve);
            assert((ve.size()==3 && r==2) || (ve.size()==4 && r==3));
        });
    }

    assert(total[1]==538 && total[2]==24 && total[3]==0);
    assert(face[1]==0 && face[2]==0 && face[3]==0);
    cout << "{\"status\":\"SUPPORT6_PAIR_FACE_81019_INDEPENDENT_GREEN\","
         << "\"pair_totals\":[" << total[1] << "," << total[2] << "," << total[3] << "],"
         << "\"support6_faces\":[" << face[1] << "," << face[2] << "," << face[3] << "]}\n";
}
