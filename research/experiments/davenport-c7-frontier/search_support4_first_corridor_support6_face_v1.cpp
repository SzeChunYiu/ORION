#include <bits/stdc++.h>
using namespace std;

// Exact bounded sweep of the support-six equality face in the first
// prime-uniform maximal corridor.  This enumerates only the two branches
// proved by SUPPORT4_MAXIMAL_PAIR_SUPPORT6_NORMAL_FORM_V1.md and tests them
// with the exact support-four representation-depth oracle.

struct V3{int x,y,z;};
struct Engine{
 int p,a,u,N,j=1,b,m,H; vector<int> rho; vector<V3> all; vector<V3> Us;
 Engine(int P,int A):p(P),a(A){
  u=1; while(u*a%p!=1)u++; N=p*p*p; b=(p+1)/2-j; m=p+b; H=m-1;
  for(int x=0;x<p;x++)for(int y=0;y<p;y++)for(int z=0;z<p;z++)all.push_back({x,y,z});
  Us={{1,0,0},{0,1,0},{0,0,1},{(p-u)%p,(p-u)%p,1}};
  rho.assign(N,1000000000); rho[0]=0;
  for(auto x:all){
   int id=enc(x); if(id==0)continue; int best=1000000000;
   for(int t=0;t<=p-a;t++){
    int c1=(x.x+u*t)%p,c2=(x.y+u*t)%p,c3=(x.z-t)%p;
    if(c3<0)c3+=p;
    if(c3<=a)best=min(best,c1+c2+c3+t);
   }
   rho[id]=best;
  }
 }
 int enc(V3 v)const{return (v.x*p+v.y)*p+v.z;}
 V3 add(V3 x,V3 y)const{return {(x.x+y.x)%p,(x.y+y.y)%p,(x.z+y.z)%p};}
 V3 mul(int c,V3 x)const{return {c*x.x%p,c*x.y%p,c*x.z%p};}
 V3 neg(V3 x)const{return {(p-x.x)%p,(p-x.y)%p,(p-x.z)%p};}
 bool eq(V3 x,V3 y)const{return x.x==y.x&&x.y==y.y&&x.z==y.z;}
 bool zero(V3 x)const{return x.x==0&&x.y==0&&x.z==0;}
 int det(V3 A,V3 B,V3 C)const{
  long long d=1LL*A.x*(B.y*C.z-B.z*C.y)-1LL*A.y*(B.x*C.z-B.z*C.x)+1LL*A.z*(B.x*C.y-B.y*C.x);
  d%=p;if(d<0)d+=p;return (int)d;
 }
 bool inU(V3 x)const{for(auto q:Us)if(eq(x,q))return true;return false;}
 bool scalar(V3 x,V3 s)const{
  int idx=s.x?0:(s.y?1:2);
  int sv=idx==0?s.x:idx==1?s.y:s.z;
  int xv=idx==0?x.x:idx==1?x.y:x.z;
  int iv=1;while(iv*sv%p!=1)iv++;
  int lam=xv*iv%p;return eq(x,mul(lam,s));
 }
 bool atom_coeff3(int c,int r,int t)const{
  for(int q=2;q<p;q++){
   int C=q*c%p,R=q*r%p,T=q*t%p;
   if(C<=c&&R<=r&&T<=t)return false;
  }
  return true;
 }
 bool atom_coeff4(int c,int d,int r,int t)const{
  for(int q=2;q<p;q++){
   int C=q*c%p,D=q*d%p,R=q*r%p,T=q*t%p;
   if(C<=c&&D<=d&&R<=r&&T<=t)return false;
  }
  return true;
 }
 bool depth3(int c,int r,int t,V3 s,V3 x,V3 y)const{
  for(int i=0;i<=c;i++)for(int k=0;k<=r;k++)for(int l=0;l<=t;l++){
   int L=i+k+l;if(L==0||L==m)continue;
   V3 q=add(add(mul(i,s),mul(k,x)),mul(l,y));
   if(L+rho[enc(neg(q))]<m)return false;
  }
  return true;
 }
 bool depth4(int c,int d,int r,int t,V3 s,V3 h,V3 x,V3 y)const{
  for(int i=0;i<=c;i++)for(int j0=0;j0<=d;j0++)for(int k=0;k<=r;k++)for(int l=0;l<=t;l++){
   int L=i+j0+k+l;if(L==0||L==m)continue;
   V3 q=add(add(mul(i,s),mul(j0,h)),add(mul(k,x),mul(l,y)));
   if(L+rho[enc(neg(q))]<m)return false;
  }
  return true;
 }
 pair<long long,long long> run(){
  long long surv3=0,surv4=0; V3 e3=Us[2],g4=Us[3];

  // Branch 1: support-three/rank-two companion sharing exactly one
  // unsaturated maximal-atom support value.
  for(int kind=0;kind<2;kind++){
   V3 s=kind?g4:e3;
   int cap=kind?(a-1):(p-1-a);
   if(cap<=0)continue;
   vector<V3> other;for(auto q:Us)if(!eq(q,s))other.push_back(q);
   for(int c=1;c<=cap;c++)for(int r=1;r<p;r++){
    int t=m-c-r;
    if(t<1||t>=p)continue;
    if(!atom_coeff3(c,r,t))continue;
    for(auto x:all){
     if(zero(x)||inU(x)||scalar(x,s))continue;
     bool planeok=true;
     for(auto q:other)if(det(s,x,q)==0){planeok=false;break;}
     if(!planeok)continue;
     int it=1;while(it*t%p!=1)it++;
     V3 rhs=add(mul(c,s),mul(r,x));
     V3 y=mul((p-it)%p,rhs);
     if(zero(y)||inU(y)||eq(y,x)||eq(y,s))continue;
     if(1+rho[enc(neg(x))]<m||1+rho[enc(neg(y))]<m)continue;
     if(depth3(c,r,t,s,x,y))surv3++;
    }
   }
  }

  // Branch 2: support-four/rank-three companion sharing both unsaturated
  // maximal-atom values and two genuinely new values.
  int capc=p-1-a,capd=a-1;
  if(capc>0&&capd>0){
   for(int c=1;c<=capc;c++)for(int d=1;d<=capd;d++)for(int r=1;r<p;r++){
    int t=m-c-d-r;
    if(t<1||t>=p)continue;
    if(!atom_coeff4(c,d,r,t))continue;
    bool shok=true;
    for(int i=0;i<=c&&shok;i++)for(int jj=0;jj<=d;jj++){
     int L=i+jj;if(!L)continue;
     V3 q=add(mul(i,e3),mul(jj,g4));
     if(L+rho[enc(neg(q))]<m){shok=false;break;}
    }
    if(!shok)continue;
    int it=1;while(it*t%p!=1)it++;
    for(auto x:all){
     if(zero(x)||inU(x))continue;
     if(det(e3,g4,x)==0)continue;
     if(1+rho[enc(neg(x))]<m)continue;
     V3 rhs=add(add(mul(c,e3),mul(d,g4)),mul(r,x));
     V3 y=mul((p-it)%p,rhs);
     if(zero(y)||inU(y)||eq(y,x))continue;
     if(1+rho[enc(neg(y))]<m)continue;
     if(depth4(c,d,r,t,e3,g4,x,y))surv4++;
    }
   }
  }
  return {surv3,surv4};
 }
};

int main(){
 map<int,vector<pair<long long,long long>>> frozen;
 for(int p: {5,7,11,13,17,19,23,29}){
  for(int a=1;a<=(p-1)/2;a++){
   Engine E(p,a);
   frozen[p].push_back(E.run());
  }
 }

 // p=5 is the sharp mutation/control boundary: type a=2 has four ordered
 // support-three equality-face survivors.  No support-four survivor occurs.
 assert(frozen[5].size()==2);
 assert(frozen[5][0]==make_pair(0LL,0LL));
 assert(frozen[5][1]==make_pair(4LL,0LL));

 // Every exact support-six equality-face candidate is eliminated for every
 // support-four maximal-atom type at these independently bounded prime rows.
 for(int p: {7,11,13,17,19,23,29})
  for(auto z:frozen[p])assert(z==make_pair(0LL,0LL));

 cout<<"{\"status\":\"SUPPORT4_FIRST_CORRIDOR_SUPPORT6_FACE_SWEEP_GREEN\","
     <<"\"p5\":[[0,0],[4,0]],"
     <<"\"zero_primes\":[7,11,13,17,19,23,29]}\n";
}
