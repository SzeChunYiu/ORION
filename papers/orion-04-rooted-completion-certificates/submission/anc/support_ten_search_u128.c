/* Finite support-ten discriminator for hypothetical length-31 total-zero short-free
 * sequences over C_5^3.  Usage: program a1 b2 c4, where a1+2*b2+4*c4=31.
 *
 * This engine is valid when three multiplicity-4 support points span rank 3;
 * they are normalized to e1,e2,e3.  For c4>=4 this rank-3 condition is forced:
 * four multiplicity-4 points cannot lie in a rank-2 subgroup because their
 * 16 terms would exceed eta(C_5^2)=13 and create a zero-sum of length <=5.
 * The c4=3 row is therefore only the rank-3 branch and is paired with the
 * separate rank-2 analysis.
 *
 * Exact state: u128 exact-weight subset-sum masks for weights 0..5.
 * The final singleton is forced by the total-sum equation.  Every candidate
 * sharing a projective line with a multiplicity-4 point is rejected; that prune
 * is symbolic because x^4 plus any distinct scalar mate contains a <=5 zero sum.
 *
 * Interpretation: bounded exact computation only.  This program does not
 * establish an exact generalized Davenport constant.
 */
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>

typedef unsigned __int128 u128;
#define N 125
#define T 5
static u128 MA[3][5],MB[3][5],ONE=(u128)1;
static unsigned char ADD[N][N],LINE[N];
typedef struct{u128 r[T+1];} Reach;
static long long nodes=0,leaves=0,sol=0;
static int sel[40],mul[40],ns=0;
static int A1,B2,C4;
static int cnt4,cnt2,cnt1;

static inline int scal(int c,int v){int x=v/25,y=(v/5)%5,z=v%5;return ((c*x)%5)*25+((c*y)%5)*5+((c*z)%5);}
static inline int neg(int v){return scal(4,v);}
static inline u128 shft(u128 m,int e){int dx=e/25,dy=(e/5)%5,dz=e%5;if(dz)m=((m&MA[0][dz])<<dz)|((m&MB[0][dz])>>(5-dz));if(dy)m=((m&MA[1][dy])<<(5*dy))|((m&MB[1][dy])>>(5*(5-dy)));if(dx)m=((m&MA[2][dx])<<(25*dx))|((m&MB[2][dx])>>(25*(5-dx)));return m;}
static inline int add1(const Reach*in,int v,Reach*out){*out=*in;for(int w=T;w>=1;--w){u128 z=shft(in->r[w-1],v);if(z&ONE)return 0;out->r[w]|=z;}return 1;}
static inline int addm(const Reach*in,int v,int m,Reach*out){Reach a,b;const Reach*c=in;Reach*n=&a;for(int i=0;i<m;i++){if(!add1(c,v,n))return 0;c=n;n=(n==&a)?&b:&a;}*out=*c;return 1;}
static inline int used(int v){for(int i=0;i<ns;i++)if(sel[i]==v)return 1;return 0;}
static inline int line_conflict(int v){for(int i=0;i<ns;i++)if(mul[i]==4&&LINE[sel[i]]==LINE[v])return 1;return 0;}
static inline int addsum(int s,int v,int m){return ADD[s][scal(m%5,v)];}

static void dfs1(int stage,int got,int start,const Reach*R,int sum){
  nodes++;
  if(stage==3){
    int q=neg(sum); leaves++;
    if(q==0||used(q)||line_conflict(q))return;
    if(A1>1 && q<=sel[ns-1]) return;
    Reach z;if(!addm(R,q,1,&z))return;sol++;return;
  }
  int need=(stage==0?cnt4:(stage==1?cnt2:cnt1));
  int m=(stage==0?4:(stage==1?2:1));
  if(got==need){dfs1(stage+1,0,1,R,sum);return;}
  for(int v=start;v<N;v++){
    if(v==0||used(v)||line_conflict(v))continue;
    Reach z;if(!addm(R,v,m,&z))continue;
    sel[ns]=v;mul[ns]=m;ns++;
    dfs1(stage,got+1,v+1,&z,addsum(sum,v,m));
    ns--; if(sol)return;
  }
}
static void init(){
 for(int a=0;a<N;a++)for(int b=0;b<N;b++){int ax=a/25,ay=(a/5)%5,az=a%5,bx=b/25,by=(b/5)%5,bz=b%5;ADD[a][b]=((ax+bx)%5)*25+((ay+by)%5)*5+((az+bz)%5);}
 for(int d=0;d<5;d++){MA[0][d]=MB[0][d]=MA[1][d]=MB[1][d]=MA[2][d]=MB[2][d]=0;for(int i=0;i<N;i++){int x=i/25,y=(i/5)%5,z=i%5;u128 bb=ONE<<i;if(z+d<5)MA[0][d]|=bb;else MB[0][d]|=bb;if(y+d<5)MA[1][d]|=bb;else MB[1][d]|=bb;if(x+d<5)MA[2][d]|=bb;else MB[2][d]|=bb;}}
 memset(LINE,255,sizeof(LINE));int nl=0;for(int v=1;v<N;v++)if(LINE[v]==255){for(int c=1;c<5;c++)LINE[scal(c,v)]=nl;nl++;}
}
int main(int ac,char**av){
 if(ac!=4){fprintf(stderr,"usage: %s a1 b2 c4\n",av[0]);return 2;}A1=atoi(av[1]);B2=atoi(av[2]);C4=atoi(av[3]);if(A1+2*B2+4*C4!=31){fprintf(stderr,"bad length\n");return 2;}if(C4<3){fprintf(stderr,"requires c4>=3\n");return 2;}if(A1<1)return 2;
 init();Reach R;memset(&R,0,sizeof(R));R.r[0]=ONE;int sum=0;int bas[3]={25,5,1};
 for(int i=0;i<3;i++){Reach z;if(!addm(&R,bas[i],4,&z)){printf("seed fail\n");return 3;}R=z;sel[ns]=bas[i];mul[ns]=4;ns++;sum=addsum(sum,bas[i],4);}
 cnt4=C4-3;cnt2=B2;cnt1=A1-1;
 dfs1(0,0,1,&R,sum);
 printf("{\"a1\":%d,\"b2\":%d,\"c4\":%d,\"support\":%d,\"nodes\":%lld,\"leaves\":%lld,\"solutions\":%lld}\n",A1,B2,C4,A1+B2+C4,nodes,leaves,sol);
 return sol?1:0;
}
