#include <bits/stdc++.h>
using namespace std;
struct V{int x,y,z;};
int inv7[7]={0,1,4,5,2,3,6};
static const int EXPECTED_SF[54]={1000,989,4,0,580,599,588,229,470,229,0,4,12,4,594,606,573,4,434,8,212,219,636,225,0,240,5,228,219,558,456,2,625,229,618,1,10,242,445,471,220,2,214,0,216,0,426,690,4,2,6,236,234,42};
int pow7a[8]={1,7,49,343,2401,16807,117649,823543};
inline V addv(V a,V b){return {(a.x+b.x)%7,(a.y+b.y)%7,(a.z+b.z)%7};}
inline V negv(V a){return {(7-a.x)%7,(7-a.y)%7,(7-a.z)%7};}
inline V mulv(V a,int s){return {a.x*s%7,a.y*s%7,a.z*s%7};}
inline bool zero(V a){return a.x==0&&a.y==0&&a.z==0;}
inline int scode(V a){return a.x+7*a.y+49*a.z;}

vector<array<unsigned char,7>> SHORT_PATTERNS;
void gen_short_pattern(int idx,int left,array<unsigned char,7>&r){
 if(idx==6){if(left<=6){r[6]=(unsigned char)left;SHORT_PATTERNS.push_back(r);}return;}
 for(int x=0;x<=min(6,left);x++){r[idx]=(unsigned char)x;gen_short_pattern(idx+1,left-x,r);}
}
void init_short_patterns(){array<unsigned char,7>r{};for(int L=1;L<=7;L++)gen_short_pattern(0,L,r);}
bool shortfree(const array<V,7>&v,const array<int,7>&m){
 for(const auto&r:SHORT_PATTERNS){V s{0,0,0};bool admissible=true;for(int i=0;i<7;i++){if(r[i]>m[i]){admissible=false;break;}s=addv(s,mulv(v[i],r[i]));}if(admissible&&zero(s))return false;}return true;
}

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

bool has4pack(const array<V,7>&v,const array<int,7>&m,int *zero_count=nullptr,int *pair_count=nullptr){
 vector<Part>L,R; L.reserve(343);R.reserve(2401);
 enum_side(v,m,0,3,0,0,{0,0,0},0,L);
 enum_side(v,m,3,7,3,0,{0,0,0},0,R);
 static vector<int> buckets[14][343];
 for(int l=0;l<14;l++)for(int s=0;s<343;s++)buckets[l][s].clear();
 for(auto &r:R) if(r.len<=13) buckets[r.len][scode(r.sum)].push_back(r.state);
 vector<int> zs; zs.reserve(2048);
 for(auto &l:L){
   V ns=negv(l.sum); int ss=scode(ns);
   for(int total=8;total<=13;total++){
     int rl=total-l.len; if(rl<0||rl>13)continue;
     for(int rs:buckets[rl][ss]) zs.push_back(l.state+rs);
   }
 }
 sort(zs.begin(),zs.end());zs.erase(unique(zs.begin(),zs.end()),zs.end());
 if(zero_count)*zero_count=zs.size();
 unordered_set<int> pairs; pairs.reserve(min<size_t>(823543,zs.size()*zs.size()/2+1));
 for(size_t i=0;i<zs.size();i++) for(size_t j=i;j<zs.size();j++){int s;if(add_states_leq(zs[i],zs[j],m,s))pairs.insert(s);} 
 if(pair_count)*pair_count=pairs.size();
 for(int s:pairs){int c=complement_state(s,m);if(pairs.find(c)!=pairs.end())return true;}
 return false;
}

int main(int argc,char**argv){
 init_short_patterns();
 if(argc<2){cerr<<"reps file\n";return 2;}
 ifstream in(argv[1]); string line; vector<array<V,7>> reps;
 while(getline(in,line)){ if(line.empty())continue; stringstream ss(line); array<V,7> q; string tok; for(int i=0;i<7;i++){ss>>tok; replace(tok.begin(),tok.end(),',',' '); stringstream tt(tok); tt>>q[i].x>>q[i].y>>q[i].z;} reps.push_back(q); }
 vector<array<int,7>> ws; array<int,7>w; genw_rec(0,12,w,ws);
 long long total=0,sf=0,pack4=0; vector<string> bad;
 auto t0=chrono::steady_clock::now();
 int startClass=(argc>=3?stoi(argv[2]):0), endClass=(argc>=4?stoi(argv[3]):(int)reps.size());
 for(int ri=startClass;ri<endClass;ri++){
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
   if(localSF!=EXPECTED_SF[ri]){cerr<<"shortfree count mismatch class "<<ri<<" got="<<localSF<<" expected="<<EXPECTED_SF[ri]<<"\n";return 3;}
   cerr<<"class "<<ri<<" shortfree="<<localSF<<" bad="<<localBad<<"\n";
 }
 double sec=chrono::duration<double>(chrono::steady_clock::now()-t0).count();
 cout<<"total="<<total<<" shortfree="<<sf<<" pack4="<<pack4<<" bad="<<bad.size()<<" seconds="<<sec<<"\n";
 for(auto&s:bad)cout<<s<<'\n';
 return bad.empty()?0:1;
}
