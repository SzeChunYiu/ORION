#include <bits/stdc++.h>
using namespace std;
struct V{int x,y,z;};
int inv7[7]={0,1,4,5,2,3,6};
int pow7a[8]={1,7,49,343,2401,16807,117649,823543};
inline V addv(V a,V b){return {(a.x+b.x)%7,(a.y+b.y)%7,(a.z+b.z)%7};}
inline V negv(V a){return {(7-a.x)%7,(7-a.y)%7,(7-a.z)%7};}
inline V mulv(V a,int s){return {a.x*s%7,a.y*s%7,a.z*s%7};}
inline bool zero(V a){return a.x==0&&a.y==0&&a.z==0;}
inline int scode(V a){return a.x+7*a.y+49*a.z;}

bool shortfree_rec(const array<V,7>&v,const array<int,7>&m,int idx,int rem,V sum,int used){
    if(used>0 && zero(sum)) return false;
    if(idx==7 || rem==0) return true;
    int mx=min(m[idx],rem); V cur=sum;
    for(int r=0;r<=mx;r++){
        if(r>0) cur=addv(cur,v[idx]);
        if(!shortfree_rec(v,m,idx+1,rem-r,cur,used+r)) return false;
    }
    return true;
}
bool shortfree(const array<V,7>&v,const array<int,7>&m){return shortfree_rec(v,m,0,7,{0,0,0},0);} 

void genw_rec(int idx,int left,array<int,7>&w,vector<array<int,7>>&out){
 if(idx==6){ if(left>=1&&left<=6){w[6]=left;out.push_back(w);} return; }
 for(int a=1;a<=6;a++){ if(left-a < 6-idx || left-a > (6-idx)*6) continue; w[idx]=a; genw_rec(idx+1,left-a,w,out);} }

struct Part{int len; V sum; int state;};
void enum_side(const array<V,7>&v,const array<int,7>&m,int lo,int hi,int idx,int len,V sum,int state,vector<Part>&out){
 if(idx==hi){out.push_back({len,sum,state});return;}
 V cur=sum; int st=state;
 for(int r=0;r<=m[idx];r++){
   if(r>0){cur=addv(cur,v[idx]); st += pow7a[idx];}
   if(len+r<=13) enum_side(v,m,lo,hi,idx+1,len+r,cur,st,out);
 }
}
inline bool add_states_leq(int a,int b,const array<int,7>&m,int &out){
 int res=0, place=1;
 for(int i=0;i<7;i++){int da=a%7, db=b%7; a/=7;b/=7; int s=da+db; if(s>m[i])return false;res+=s*place;place*=7;} out=res;return true;
}
inline int complement_state(int a,const array<int,7>&m){
 int res=0,place=1; for(int i=0;i<7;i++){int da=a%7;a/=7;res+=(m[i]-da)*place;place*=7;}return res;
}

bool leq_state(int a,int b){
 for(int i=0;i<7;i++){if(a%7>b%7)return false;a/=7;b/=7;}return true;
}
int sub_state(int a,int b){int r=0,pl=1;for(int i=0;i<7;i++){int da=a%7,db=b%7;a/=7;b/=7;r+=(da-db)*pl;pl*=7;}return r;}
int state_len(int a){int s=0;for(int i=0;i<7;i++){s+=a%7;a/=7;}return s;}

bool has4pack(const array<V,7>&v,const array<int,7>&m,int *zero_count=nullptr,int *pair_count=nullptr){
 vector<Part>L,R; L.reserve(343);R.reserve(2401);
 enum_side(v,m,0,3,0,0,{0,0,0},0,L);
 enum_side(v,m,3,7,3,0,{0,0,0},0,R);
 static vector<int> buckets[14][343];
 for(int l=0;l<14;l++)for(int s=0;s<343;s++)buckets[l][s].clear();
 for(auto &r:R) if(r.len<=13) buckets[r.len][scode(r.sum)].push_back(r.state);
 vector<int> bylen[14]; int totalz=0;
 for(auto &l:L){V ns=negv(l.sum);int ss=scode(ns);for(int total=8;total<=13;total++){int rl=total-l.len;if(rl<0||rl>13)continue;for(int rs:buckets[rl][ss]){bylen[total].push_back(l.state+rs);totalz++;}}}
 for(int L0=8;L0<=13;L0++){auto &z=bylen[L0];sort(z.begin(),z.end());z.erase(unique(z.begin(),z.end()),z.end());}
 totalz=0;for(int L0=8;L0<=13;L0++)totalz+=bylen[L0].size();if(zero_count)*zero_count=totalz;if(pair_count)*pair_count=0;
 int full=0,pl=1;for(int i=0;i<7;i++){full+=m[i]*pl;pl*=7;}
 // Every 4-partition has a block of length 8 or 9. After removing it, every
 // 3-partition has a block of length 8 or 9. The final complement is zero-sum automatically.
 for(int la=8;la<=9;la++)for(int A:bylen[la]){
   int r1=sub_state(full,A); int len1=37-la;
   for(int lb=8;lb<=9;lb++)for(int B:bylen[lb]) if(leq_state(B,r1)){
      int r2=sub_state(r1,B); int len2=len1-lb; int maxc=len2-8;
      for(int lc=8;lc<=min(13,maxc);lc++)for(int C:bylen[lc]) if(leq_state(C,r2)) return true;
   }
 }
 return false;
}

int main(int argc,char**argv){
 if(argc<2){cerr<<"reps file\n";return 2;}
 ifstream in(argv[1]); string line; vector<array<V,7>> reps;
 while(getline(in,line)){ if(line.empty())continue; stringstream ss(line); array<V,7> q; string tok; for(int i=0;i<7;i++){ss>>tok; replace(tok.begin(),tok.end(),',',' '); stringstream tt(tok); tt>>q[i].x>>q[i].y>>q[i].z;} reps.push_back(q); }
 vector<array<int,7>> ws; array<int,7>w; genw_rec(0,12,w,ws);
 long long total=0,sf=0,pack4=0; vector<string> bad;
 auto t0=chrono::steady_clock::now();
 for(int ri=0;ri<(int)reps.size();ri++){
   auto&q=reps[ri]; vector<array<int,7>> cs; array<int,7> c;c[0]=1;
   for(int a=1;a<7;a++)for(int b=1;b<7;b++)for(int d=1;d<7;d++)for(int e=1;e<7;e++)for(int f=1;f<7;f++)for(int g=1;g<7;g++){
     c={1,a,b,d,e,f,g}; V s{0,0,0};for(int i=0;i<7;i++)s=addv(s,mulv(q[i],c[i]));if(zero(s))cs.push_back(c);
   }
   int localSF=0,localBad=0;
   for(auto&ww:ws){array<int,7>m;for(int i=0;i<7;i++)m[i]=7-ww[i];
    for(auto&cc:cs){total++;array<V,7>vv;for(int i=0;i<7;i++)vv[i]=mulv(q[i],cc[i]*inv7[ww[i]]%7);
      if(!shortfree(vv,m))continue;sf++;localSF++;
      int zc=0,pc=0; bool ok=has4pack(vv,m,&zc,&pc); if(ok){pack4++;} else {localBad++;ostringstream os;os<<"class="<<ri<<" w=";for(int x:ww)os<<x<<',';os<<" c=";for(int x:cc)os<<x<<',';os<<" zc="<<zc<<" pc="<<pc;bad.push_back(os.str());}
    }
   }
   cerr<<"class "<<ri<<" shortfree="<<localSF<<" bad="<<localBad<<"\n";
 }
 double sec=chrono::duration<double>(chrono::steady_clock::now()-t0).count();
 cout<<"total="<<total<<" shortfree="<<sf<<" pack4="<<pack4<<" bad="<<bad.size()<<" seconds="<<sec<<"\n";
 for(auto&s:bad)cout<<s<<'\n';
 return bad.empty()?0:1;
}
