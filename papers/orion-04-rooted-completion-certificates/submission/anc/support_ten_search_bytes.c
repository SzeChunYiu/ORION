/* Second support-ten replay engine.
 * It uses the same mathematical search domain as support_ten_search_u128.c but
 * a different subset-sum representation: explicit
 * byte reachability r[weight][sum] instead of u128 translation masks.
 * Usage: program a1 b2 c4.  For c4=3 this is only the branch where the three
 * multiplicity-4 support points span rank 3; the rank-2 branch has a separate
 * check.  Interpretation: bounded exact computation only.
 */
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>
#define N 125
#define T 5
static unsigned char ADD[N][N],LINE[N];
typedef struct{unsigned char r[T+1][N];}Reach;
static long long nodes=0,leaves=0,sol=0; static int sel[40],mul[40],ns=0,A1,B2,C4,cnt4,cnt2,cnt1;
static int scal(int c,int v){int x=v/25,y=(v/5)%5,z=v%5;return ((c*x)%5)*25+((c*y)%5)*5+((c*z)%5);}
static int neg(int v){return scal(4,v);} static int used(int v){for(int i=0;i<ns;i++)if(sel[i]==v)return 1;return 0;} static int lconf(int v){for(int i=0;i<ns;i++)if(mul[i]==4&&LINE[sel[i]]==LINE[v])return 1;return 0;} static int addsum(int s,int v,int m){return ADD[s][scal(m%5,v)];}
static int add1(const Reach*in,int v,Reach*out){memcpy(out,in,sizeof(*out));for(int w=T;w>=1;w--)for(int s=0;s<N;s++)if(in->r[w-1][s]){int q=ADD[s][v];if(!q)return 0;out->r[w][q]=1;}return 1;} static int addm(const Reach*in,int v,int m,Reach*out){Reach a,b;const Reach*c=in;Reach*n=&a;for(int i=0;i<m;i++){if(!add1(c,v,n))return 0;c=n;n=(n==&a)?&b:&a;}*out=*c;return 1;}
static void dfs(int stage,int got,int start,const Reach*R,int sum){nodes++;if(stage==3){int q=neg(sum);leaves++;if(!q||used(q)||lconf(q))return;if(A1>1&&q<=sel[ns-1])return;Reach z;if(!addm(R,q,1,&z))return;sol++;return;}int need=stage==0?cnt4:(stage==1?cnt2:cnt1),m=stage==0?4:(stage==1?2:1);if(got==need){dfs(stage+1,0,1,R,sum);return;}for(int v=start;v<N;v++){if(!v||used(v)||lconf(v))continue;Reach z;if(!addm(R,v,m,&z))continue;sel[ns]=v;mul[ns]=m;ns++;dfs(stage,got+1,v+1,&z,addsum(sum,v,m));ns--;if(sol)return;}}
int main(int ac,char**av){if(ac!=4)return 2;A1=atoi(av[1]);B2=atoi(av[2]);C4=atoi(av[3]);if(A1+2*B2+4*C4!=31||C4<3||A1<1)return 2;for(int a=0;a<N;a++)for(int b=0;b<N;b++){int ax=a/25,ay=(a/5)%5,az=a%5,bx=b/25,by=(b/5)%5,bz=b%5;ADD[a][b]=((ax+bx)%5)*25+((ay+by)%5)*5+((az+bz)%5);}memset(LINE,255,sizeof(LINE));int nl=0;for(int v=1;v<N;v++)if(LINE[v]==255){for(int c=1;c<5;c++)LINE[scal(c,v)]=nl;nl++;}Reach R;memset(&R,0,sizeof(R));R.r[0][0]=1;int sum=0,bas[3]={25,5,1};for(int i=0;i<3;i++){Reach z;if(!addm(&R,bas[i],4,&z))return 3;R=z;sel[ns]=bas[i];mul[ns]=4;ns++;sum=addsum(sum,bas[i],4);}cnt4=C4-3;cnt2=B2;cnt1=A1-1;dfs(0,0,1,&R,sum);printf("{\"a1\":%d,\"b2\":%d,\"c4\":%d,\"support\":%d,\"nodes\":%lld,\"leaves\":%lld,\"solutions\":%lld}\n",A1,B2,C4,A1+B2+C4,nodes,leaves,sol);return sol?1:0;}
