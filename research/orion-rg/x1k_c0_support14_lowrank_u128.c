/* X1-K support-14 low-rank branches for the length-31 total-zero short-free gate.
 * Handles multiplicity patterns 1 2^11 4^2 and 1^3 2^8 4^3 when the three
 * multiplicity-4 points (if present) span rank 2.  Two multiplicity-4 points are
 * independent because projective-line sharing is forbidden, so normalize them
 * to e1,e2.  In the c4=3 branch enumerate the third as a e1+b e2, a,b !=0.
 * Then enumerate multiplicity-2/singleton support canonically and force the last
 * singleton from total sum.  Exact u128 subset-sum masks reject all <=5 zero sums.
 */
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>
typedef unsigned __int128 u128;
#define N 125
#define T 5
static u128 MA[3][5],MB[3][5],ONE=(u128)1;static unsigned char ADD[N][N],LINE[N];typedef struct{u128 r[T+1];}Reach;static int sel[30],mul[30],ns;static long long nodes,leaves,sol;static int A1,B2,C4,third;
static int scal(int c,int v){int x=v/25,y=(v/5)%5,z=v%5;return ((c*x)%5)*25+((c*y)%5)*5+((c*z)%5);}static int neg(int v){return scal(4,v);}static u128 sh(u128 m,int e){int dx=e/25,dy=(e/5)%5,dz=e%5;if(dz)m=((m&MA[0][dz])<<dz)|((m&MB[0][dz])>>(5-dz));if(dy)m=((m&MA[1][dy])<<(5*dy))|((m&MB[1][dy])>>(5*(5-dy)));if(dx)m=((m&MA[2][dx])<<(25*dx))|((m&MB[2][dx])>>(25*(5-dx)));return m;}static int add1(const Reach*i,int v,Reach*o){*o=*i;for(int w=T;w>=1;w--){u128 z=sh(i->r[w-1],v);if(z&ONE)return 0;o->r[w]|=z;}return 1;}static int addm(const Reach*i,int v,int m,Reach*o){Reach a,b;const Reach*c=i;Reach*n=&a;for(int k=0;k<m;k++){if(!add1(c,v,n))return 0;c=n;n=n==&a?&b:&a;}*o=*c;return 1;}static int used(int v){for(int i=0;i<ns;i++)if(sel[i]==v)return 1;return 0;}static int lconf(int v){for(int i=0;i<ns;i++)if(mul[i]==4&&LINE[sel[i]]==LINE[v])return 1;return 0;}static int addsum(int s,int v,int m){return ADD[s][scal(m%5,v)];}
static void dfs1(int stage,int got,int start,const Reach*R,int sum){nodes++;if(stage==2){int q=neg(sum);leaves++;if(!q||used(q)||lconf(q))return;if(A1>1&&q<=sel[ns-1])return;Reach z;if(!addm(R,q,1,&z))return;sol++;return;}int need=stage==0?B2:A1-1,m=stage==0?2:1;if(got==need){dfs1(stage+1,0,1,R,sum);return;}for(int v=start;v<N;v++){if(!v||used(v)||lconf(v))continue;Reach z;if(!addm(R,v,m,&z))continue;sel[ns]=v;mul[ns]=m;ns++;dfs1(stage,got+1,v+1,&z,addsum(sum,v,m));ns--;if(sol)return;}}
static void init(){for(int a=0;a<N;a++)for(int b=0;b<N;b++){int ax=a/25,ay=(a/5)%5,az=a%5,bx=b/25,by=(b/5)%5,bz=b%5;ADD[a][b]=((ax+bx)%5)*25+((ay+by)%5)*5+((az+bz)%5);}for(int d=0;d<5;d++){MA[0][d]=MB[0][d]=MA[1][d]=MB[1][d]=MA[2][d]=MB[2][d]=0;for(int i=0;i<N;i++){int x=i/25,y=(i/5)%5,z=i%5;u128 bb=ONE<<i;if(z+d<5)MA[0][d]|=bb;else MB[0][d]|=bb;if(y+d<5)MA[1][d]|=bb;else MB[1][d]|=bb;if(x+d<5)MA[2][d]|=bb;else MB[2][d]|=bb;}}memset(LINE,255,sizeof(LINE));int nl=0;for(int v=1;v<N;v++)if(LINE[v]==255){for(int c=1;c<5;c++)LINE[scal(c,v)]=nl;nl++;}}
static void runseed(int tv,long long*tn,long long*tl){Reach R;memset(&R,0,sizeof(R));R.r[0]=ONE;ns=0;int sum=0,base[3]={25,5,tv};for(int i=0;i<C4;i++){Reach z;if(!addm(&R,base[i],4,&z))return;R=z;sel[ns]=base[i];mul[ns]=4;ns++;sum=addsum(sum,base[i],4);}nodes=leaves=0;dfs1(0,0,1,&R,sum);*tn+=nodes;*tl+=leaves;printf("seed=%d nodes=%lld leaves=%lld sol=%lld\n",tv,nodes,leaves,sol);}
int main(int ac,char**av){if(ac!=4)return 2;A1=atoi(av[1]);B2=atoi(av[2]);C4=atoi(av[3]);if(A1+2*B2+4*C4!=31||!(C4==2||C4==3))return 2;init();long long tn=0,tl=0;if(C4==2)runseed(0,&tn,&tl);else for(int a=1;a<5&&!sol;a++)for(int b=1;b<5&&!sol;b++){third=25*a+5*b;runseed(third,&tn,&tl);}printf("TOTAL a1=%d b2=%d c4=%d nodes=%lld leaves=%lld solutions=%lld\n",A1,B2,C4,tn,tl,sol);return sol?1:0;}
