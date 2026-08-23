/* Independent byte-array replay of x1k_c0_support13_rank2_u128.c.
 * Same normalized rank-2 multiplicity-4 branch, but explicit reach[weight][sum]
 * state instead of u128 translation masks.  Bounded computation only.
 */
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#define N 125
#define T 5
static unsigned char ADD[N][N],LINE[N];typedef struct{unsigned char r[T+1][N];}Reach;static int sel[20],mul[20],ns;static long long nodes,leaves,sol;static int third;
static int scal(int c,int v){int x=v/25,y=(v/5)%5,z=v%5;return ((c*x)%5)*25+((c*y)%5)*5+((c*z)%5);}static int neg(int v){return scal(4,v);}static int add1(const Reach*i,int v,Reach*o){memcpy(o,i,sizeof(*o));for(int w=T;w>=1;w--)for(int s=0;s<N;s++)if(i->r[w-1][s]){int q=ADD[s][v];if(!q)return 0;o->r[w][q]=1;}return 1;}static int addm(const Reach*i,int v,int m,Reach*o){Reach a,b;const Reach*c=i;Reach*n=&a;for(int k=0;k<m;k++){if(!add1(c,v,n))return 0;c=n;n=n==&a?&b:&a;}*o=*c;return 1;}static int used(int v){for(int i=0;i<ns;i++)if(sel[i]==v)return 1;return 0;}static int lconf(int v){for(int i=0;i<ns;i++)if(mul[i]==4&&LINE[sel[i]]==LINE[v])return 1;return 0;}static int addsum(int s,int v,int m){return ADD[s][scal(m%5,v)];}
static void dfs(int got,int start,const Reach*R,int sum){nodes++;if(got==9){int q=neg(sum);leaves++;if(!q||used(q)||lconf(q))return;Reach z;if(!addm(R,q,1,&z))return;sol++;return;}for(int v=start;v<N;v++){if(!v||used(v)||lconf(v))continue;Reach z;if(!addm(R,v,2,&z))continue;sel[ns]=v;mul[ns]=2;ns++;dfs(got+1,v+1,&z,addsum(sum,v,2));ns--;if(sol)return;}}
int main(){for(int a=0;a<N;a++)for(int b=0;b<N;b++){int ax=a/25,ay=(a/5)%5,az=a%5,bx=b/25,by=(b/5)%5,bz=b%5;ADD[a][b]=((ax+bx)%5)*25+((ay+by)%5)*5+((az+bz)%5);}memset(LINE,255,sizeof(LINE));int nl=0;for(int v=1;v<N;v++)if(LINE[v]==255){for(int c=1;c<5;c++)LINE[scal(c,v)]=nl;nl++;}long long tn=0,tl=0;for(int a=1;a<5&&!sol;a++)for(int b=1;b<5&&!sol;b++){third=25*a+5*b;Reach R;memset(&R,0,sizeof(R));R.r[0][0]=1;ns=0;int sum=0,base[3]={25,5,third},ok=1;for(int i=0;i<3;i++){Reach z;if(!addm(&R,base[i],4,&z)){ok=0;break;}R=z;sel[ns]=base[i];mul[ns]=4;ns++;sum=addsum(sum,base[i],4);}if(!ok)continue;nodes=leaves=0;dfs(0,1,&R,sum);printf("third=%d nodes=%lld leaves=%lld sol=%lld\n",third,nodes,leaves,sol);tn+=nodes;tl+=leaves;}printf("TOTAL nodes=%lld leaves=%lld solutions=%lld\n",tn,tl,sol);return sol?1:0;}
