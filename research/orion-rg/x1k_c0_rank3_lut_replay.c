/* Independent rank-3-high-multiplicity replay for X1-K C0(31) support rows.
 * Usage: program a1 b2 c4, a1+2*b2+4*c4=31, c4>=3.
 *
 * Unlike x1k_c0_support10_13_rank3_u128.c, translation of a subset-sum mask is
 * not performed by coordinate-mask cyclic shifts.  A lookup table is generated
 * entirely from primitive ADD[src][v] and maps each 8-bit chunk of a u128 mask
 * to its translated u128 image.  This gives an independent translation primitive
 * while remaining fast enough for >10M-state rows.
 */
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>
typedef unsigned __int128 u128;
#define N 125
#define T 5
static unsigned char ADD[N][N],LINE[N];
static u128 *LUT;
#define L(v,j,b) LUT[(((v)*16+(j))*256)+(b)]
typedef struct{u128 r[T+1];}Reach;static long long nodes,leaves,sol;static int sel[40],mul[40],ns,A1,B2,C4,cnt4,cnt2,cnt1;
static int scal(int c,int v){int x=v/25,y=(v/5)%5,z=v%5;return ((c*x)%5)*25+((c*y)%5)*5+((c*z)%5);}static int neg(int v){return scal(4,v);}static int used(int v){for(int i=0;i<ns;i++)if(sel[i]==v)return 1;return 0;}static int lconf(int v){for(int i=0;i<ns;i++)if(mul[i]==4&&LINE[sel[i]]==LINE[v])return 1;return 0;}static int addsum(int s,int v,int m){return ADD[s][scal(m%5,v)];}
static inline u128 tr(u128 m,int v){u128 out=0;for(int j=0;j<16;j++){unsigned b=(unsigned)(m&255);if(b)out|=L(v,j,b);m>>=8;}return out;}
static inline int add1(const Reach*i,int v,Reach*o){*o=*i;for(int w=T;w>=1;w--){u128 z=tr(i->r[w-1],v);if(z&1)return 0;o->r[w]|=z;}return 1;}static inline int addm(const Reach*i,int v,int m,Reach*o){Reach a,b;const Reach*c=i;Reach*n=&a;for(int k=0;k<m;k++){if(!add1(c,v,n))return 0;c=n;n=n==&a?&b:&a;}*o=*c;return 1;}
static void dfs(int stage,int got,int start,const Reach*R,int sum){nodes++;if(stage==3){int q=neg(sum);leaves++;if(!q||used(q)||lconf(q))return;if(A1>1&&q<=sel[ns-1])return;Reach z;if(!addm(R,q,1,&z))return;sol++;return;}int need=stage==0?cnt4:(stage==1?cnt2:cnt1),m=stage==0?4:(stage==1?2:1);if(got==need){dfs(stage+1,0,1,R,sum);return;}for(int v=start;v<N;v++){if(!v||used(v)||lconf(v))continue;Reach z;if(!addm(R,v,m,&z))continue;sel[ns]=v;mul[ns]=m;ns++;dfs(stage,got+1,v+1,&z,addsum(sum,v,m));ns--;if(sol)return;}}
int main(int ac,char**av){if(ac!=4)return 2;A1=atoi(av[1]);B2=atoi(av[2]);C4=atoi(av[3]);if(A1+2*B2+4*C4!=31||C4<3||A1<1)return 2;for(int a=0;a<N;a++)for(int b=0;b<N;b++){int ax=a/25,ay=(a/5)%5,az=a%5,bx=b/25,by=(b/5)%5,bz=b%5;ADD[a][b]=((ax+bx)%5)*25+((ay+by)%5)*5+((az+bz)%5);}memset(LINE,255,sizeof(LINE));int nl=0;for(int v=1;v<N;v++)if(LINE[v]==255){for(int c=1;c<5;c++)LINE[scal(c,v)]=nl;nl++;}LUT=calloc((size_t)N*16*256,sizeof(u128));if(!LUT)return 3;for(int v=0;v<N;v++)for(int j=0;j<16;j++)for(int b=1;b<256;b++){int lb=__builtin_ctz(b);int rest=b&(b-1);u128 z=L(v,j,rest);int src=j*8+lb;if(src<N){int q=ADD[src][v];z|=((u128)1)<<q;}L(v,j,b)=z;}Reach R;memset(&R,0,sizeof(R));R.r[0]=1;int sum=0,bas[3]={25,5,1};for(int i=0;i<3;i++){Reach z;if(!addm(&R,bas[i],4,&z))return 3;R=z;sel[ns]=bas[i];mul[ns]=4;ns++;sum=addsum(sum,bas[i],4);}cnt4=C4-3;cnt2=B2;cnt1=A1-1;dfs(0,0,1,&R,sum);printf("a1=%d b2=%d c4=%d support=%d nodes=%lld leaves=%lld solutions=%lld\n",A1,B2,C4,A1+B2+C4,nodes,leaves,sol);return sol?1:0;}
