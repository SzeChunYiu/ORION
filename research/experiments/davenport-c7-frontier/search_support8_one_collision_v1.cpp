#include <bits/stdc++.h>
using namespace std;
struct V{int x,y,z;};
int inv7[7]={0,1,4,5,2,3,6};
inline V addv(V a,V b){return {(a.x+b.x)%7,(a.y+b.y)%7,(a.z+b.z)%7};}
inline V mulv(V a,int s){return {a.x*s%7,a.y*s%7,a.z*s%7};}
inline bool zero(V a){return a.x==0&&a.y==0&&a.z==0;}
const uint32_t POW7[9]={1,7,49,343,2401,16807,117649,823543,5764801};

bool shortrec(const array<V,8>&v,const array<int,8>&m,int idx,int rem,V sum,int used){
 if(used&&zero(sum))return false;
 if(idx==8||rem==0)return true;
 V cur=sum;int mx=min(m[idx],rem);
 for(int r=0;r<=mx;r++){if(r)cur=addv(cur,v[idx]);if(!shortrec(v,m,idx+1,rem-r,cur,used+r))return false;}
 return true;
}
inline bool shortfree(const array<V,8>&v,const array<int,8>&m){return shortrec(v,m,0,7,{0,0,0},0);}
inline bool leqstate(uint32_t a,uint32_t b){for(int i=0;i<8;i++){if(a%7>b%7)return false;a/=7;b/=7;}return true;}
inline uint32_t substate(uint32_t a,uint32_t b){uint32_t r=0,p=1;for(int i=0;i<8;i++){int x=a%7,y=b%7;a/=7;b/=7;r+=(x-y)*p;p*=7;}return r;}

bool has4pack(const array<V,8>&v,const array<int,8>&m){
 vector<uint32_t> bylen[14];
 function<void(int,int,V,uint32_t)> rec=[&](int idx,int len,V sum,uint32_t st){
  if(len>13)return;
  if(idx==8){if(len>=8&&zero(sum))bylen[len].push_back(st);return;}
  V cur=sum;uint32_t ss=st;int mx=min(m[idx],13-len);
  for(int r=0;r<=mx;r++){if(r){cur=addv(cur,v[idx]);ss+=POW7[idx];}rec(idx+1,len+r,cur,ss);}
 };
 rec(0,0,{0,0,0},0);
 uint32_t full=0;for(int i=0;i<8;i++)full+=m[i]*POW7[i];
 // In a four-partition of 37 into blocks of size >=8, the two successive
 // smallest blocks can be chosen with sizes 8 or 9; every block has size <=13.
 for(int la=8;la<=9;la++)for(uint32_t A:bylen[la]){
  uint32_t r1=substate(full,A);int rem1=37-la;
  for(int lb=8;lb<=9;lb++)for(uint32_t B:bylen[lb])if(leqstate(B,r1)){
   uint32_t r2=substate(r1,B);int rem2=rem1-lb;int maxc=min(13,rem2-8);
   for(int lc=8;lc<=maxc;lc++)for(uint32_t C:bylen[lc])if(leqstate(C,r2))return true;
  }
 }
 return false;
}

struct Local{int a,r,s,h;};
int main(int argc,char**argv){
 if(argc<2){cerr<<"reps [start end]\n";return 2;}
 ifstream in(argv[1]);string line;vector<array<V,7>>reps;
 while(getline(in,line)){if(line.empty())continue;stringstream ss(line);array<V,7>q;string tok;for(int i=0;i<7;i++){ss>>tok;replace(tok.begin(),tok.end(),',',' ');stringstream tt(tok);tt>>q[i].x>>q[i].y>>q[i].z;}reps.push_back(q);}
 int st=argc>=3?stoi(argv[2]):0,en=argc>=4?stoi(argv[3]):(int)reps.size();
 vector<Local>loc;
 for(int a=2;a<7;a++)for(int r=1;r<=6;r++)for(int s=1;r+s<=6;s++){
  bool bad=false;for(int u=0;u<=r&&!bad;u++)for(int w=0;w<=s;w++)if(u+w&&(u+a*w)%7==0){bad=true;break;}
  if(bad)continue;tuple<int,int,int>x={a,r,s},y={inv7[a],s,r};if(x>y)continue;
  int h=(r+a*s)%7;if(!h)return 3;loc.push_back({a,r,s,h});
 }
 if(loc.size()!=9)return 3;
 vector<array<int,7>>ds;array<int,7>d{};
 function<void(int,int)>gd=[&](int i,int left){if(i==6){d[6]=left;ds.push_back(d);return;}for(int x=0;x<=left;x++){d[i]=x;gd(i+1,left-x);}};gd(0,5);
 if(ds.size()!=462)return 3;
 long long total=0,sf=0,p4=0;auto t0=chrono::steady_clock::now();
 for(int ri=st;ri<en;ri++){
  auto q=reps[ri];vector<array<int,7>>kernels;
  for(int a=1;a<7;a++)for(int b=1;b<7;b++)for(int c=1;c<7;c++)for(int e=1;e<7;e++)for(int f=1;f<7;f++)for(int g=1;g<7;g++){
   array<int,7>C={1,a,b,c,e,f,g};V z{0,0,0};for(int i=0;i<7;i++)z=addv(z,mulv(q[i],C[i]));if(zero(z))kernels.push_back(C);
  }
  long long ltot=0,lsf=0,lbad=0;
  for(int j=0;j<7;j++)for(auto&dd:ds){int t[7];for(int i=0;i<7;i++)t[i]=6-dd[i];
   for(auto L:loc)if(L.r+L.s==t[j])for(auto&C:kernels){total++;ltot++;array<V,8>vv;array<int,8>mm;int k=0;
    for(int i=0;i<7;i++)if(i==j){int lam=C[i]*inv7[L.h]%7;vv[k]=mulv(q[i],lam);mm[k++]=L.r;vv[k]=mulv(q[i],lam*L.a%7);mm[k++]=L.s;}else{int lam=C[i]*inv7[t[i]]%7;vv[k]=mulv(q[i],lam);mm[k++]=t[i];}
    V z{0,0,0};int len=0;for(int i=0;i<8;i++){z=addv(z,mulv(vv[i],mm[i]));len+=mm[i];}if(!zero(z)||len!=37)return 5;
    if(!shortfree(vv,mm))continue;sf++;lsf++;if(has4pack(vv,mm))p4++;else lbad++;
   }
  }
  cerr<<"class "<<ri<<" kernels="<<kernels.size()<<" total="<<ltot<<" sf="<<lsf<<" bad="<<lbad<<"\n";
  if(lbad)return 1;
 }
 cout<<"classes="<<st<<".."<<en<<" total="<<total<<" shortfree="<<sf<<" pack4="<<p4<<" bad="<<(sf-p4)<<" seconds="<<chrono::duration<double>(chrono::steady_clock::now()-t0).count()<<"\n";
 return sf==p4?0:1;
}
