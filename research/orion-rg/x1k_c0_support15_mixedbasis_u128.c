/* X1-K support-15 hard row: multiplicity pattern 1 2^13 4.
 * If the multiplicity-4 point together with the thirteen multiplicity-2 points
 * had rank <=2, those 30 terms would already contain a <=5 zero sum because
 * eta(C_5^2)=13.  Hence some two multiplicity-2 points extend the multiplicity-4
 * point to a basis.  Normalize multiplicities (4,2,2) at e1,e2,e3, enumerate
 * the remaining eleven multiplicity-2 support points, and force the singleton
 * from total sum.  Exact u128 subset-sum masks reject all <=5 zero sums.
 */
#include <stdio.h>
#include <stdint.h>
#include <string.h>
typedef unsigned __int128 u128;
#define N 125
#define T 5
static u128 MA[3][5],MB[3][5],ONE=(u128)1;static unsigned char ADD[N][N],LINE[N];typedef struct{u128 r[T+1];}Reach;static int sel[30],mul[30],ns;static long long nodes,leaves,sol;
static int scal(int c,int v){int x=v/25,y=(v/5)%5,z=v%5;return ((c*x)%5)*25+((c*y)%5)*5+((c*z)%5);}static int neg(int v){return scal(4,v);}static u128 sh(u128 m,int e){int dx=e/25,dy=(e/5)%5,dz=e%5;if(dz)m=((m&MA[0][dz])<<dz)|((m&MB[0][dz])>>(5-dz));if(dy)m=((m&MA[1][dy])<<(5*dy))|((m&MB[1][dy])>>(5*(5-dy)));if(dx)m=((m&MA[2][dx])<<(25*dx))|((m&MB[2][dx])>>(25*(5-dx)));return m;}static int add1(const Reach*i,int v,Reach*o){*o=*i;for(int w=T;w>=1;w--){u128 z=sh(i->r[w-1],v);if(z&ONE)return 0;o->r[w]|=z;}return 1;}static int addm(const Reach*i,int v,int m,Reach*o){Reach a,b;const Reach*c=i;Reach*n=&a;for(int k=0;k<m;k++){if(!add1(c,v,n))return 0;c=n;n=n==&a?&b:&a;}*o=*c;return 1;}static int used(int v){for(int i=0;i<ns;i++)if(sel[i]==v)return 1;return 0;}static int lconf(int v){return LINE[v]==LINE[25];}static int addsum(int s,int v,int m){return ADD[s][scal(m%5,v)];}
static void dfs(int got,int start,const Reach*R,int sum){nodes++;if(got==11){int q=neg(sum);leaves++;if(!q||used(q)||lconf(q))return;Reach z;if(!addm(R,q,1,&z))return;sol++;return;}for(int v=start;v<N;v++){if(!v||used(v)||lconf(v))continue;Reach z;if(!addm(R,v,2,&z))continue;sel[ns]=v;mul[ns]=2;ns++;dfs(got+1,v+1,&z,addsum(sum,v,2));ns--;if(sol)return;}}
int main(){for(int a=0;a<N;a++)for(int b=0;b<N;b++){int ax=a/25,ay=(a/5)%5,az=a%5,bx=b/25,by=(b/5)%5,bz=b%5;ADD[a][b]=((ax+bx)%5)*25+((ay+by)%5)*5+((az+bz)%5);}for(int d=0;d<5;d++){MA[0][d]=MB[0][d]=MA[1][d]=MB[1][d]=MA[2][d]=MB[2][d]=0;for(int i=0;i<N;i++){int x=i/25,y=(i/5)%5,z=i%5;u128 bb=ONE<<i;if(z+d<5)MA[0][d]|=bb;else MB[0][d]|=bb;if(y+d<5)MA[1][d]|=bb;else MB[1][d]|=bb;if(x+d<5)MA[2][d]|=bb;else MB[2][d]|=bb;}}memset(LINE,255,sizeof(LINE));int nl=0;for(int v=1;v<N;v++)if(LINE[v]==255){for(int c=1;c<5;c++)LINE[scal(c,v)]=nl;nl++;}Reach R;memset(&R,0,sizeof(R));R.r[0]=ONE;int sum=0,base[3]={25,5,1},ms[3]={4,2,2};for(int i=0;i<3;i++){Reach z;if(!addm(&R,base[i],ms[i],&z))return 3;R=z;sel[ns]=base[i];mul[ns]=ms[i];ns++;sum=addsum(sum,base[i],ms[i]);}dfs(0,2,&R,sum);printf("nodes=%lld leaves=%lld solutions=%lld\n",nodes,leaves,sol);return sol?1:0;}
