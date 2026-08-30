/* Independent AVX2 five-plane replay of universal C_5^3 discriminator. */
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>
#define N 125
#define T 5
typedef uint32_t V8 __attribute__((vector_size(32)));
typedef struct{V8 r[T+1];}Reach;
static V8 ZA[5],ZB[5],YA[5],YB[5];
static unsigned char ADD[N][N],LINE[N];
static int sel[40],mul[40],ns;static long long nodes,leaves,sol;static int A1,B2,C4;
static int scal(int c,int v){int x=v/25,y=(v/5)%5,z=v%5;return ((c*x)%5)*25+((c*y)%5)*5+((c*z)%5);}
static int neg(int v){return scal(4,v);}
static inline V8 rotx(V8 q,int d){switch(d){case 0:return q;case 1:return __builtin_shufflevector(q,q,4,0,1,2,3,5,6,7);case 2:return __builtin_shufflevector(q,q,3,4,0,1,2,5,6,7);case 3:return __builtin_shufflevector(q,q,2,3,4,0,1,5,6,7);default:return __builtin_shufflevector(q,q,1,2,3,4,0,5,6,7);}}
static inline V8 sh(V8 m,int e){int dx=e/25,dy=(e/5)%5,dz=e%5;V8 q=m;if(dz)q=((q&ZA[dz])<<dz)|((q&ZB[dz])>>(5-dz));if(dy)q=((q&YA[dy])<<(5*dy))|((q&YB[dy])>>(5*(5-dy)));return rotx(q,dx);}
static inline int add1(const Reach*i,int v,Reach*o){*o=*i;for(int w=T;w>=1;--w){V8 z=sh(i->r[w-1],v);if(z[0]&1U)return 0;o->r[w]|=z;}return 1;}
static inline int addm(const Reach*i,int v,int m,Reach*o){Reach a,b;const Reach*c=i;Reach*n=&a;for(int k=0;k<m;k++){if(!add1(c,v,n))return 0;c=n;n=n==&a?&b:&a;}*o=*c;return 1;}
static inline int used(int v){for(int i=0;i<ns;i++)if(sel[i]==v)return 1;return 0;}
static inline int lconf(int v){for(int i=0;i<ns;i++)if(mul[i]==4&&LINE[sel[i]]==LINE[v])return 1;return 0;}
static inline int addsum(int s,int v,int m){return ADD[s][scal(m%5,v)];}
static void dfs(int stage,int got,int start,const Reach*R,int sum){nodes++;if(stage==3){int q=neg(sum);leaves++;if(!q||used(q)||lconf(q))return;if(A1>1&&q<=sel[ns-1])return;Reach z;if(!addm(R,q,1,&z))return;sol++;return;}int need=stage==0?C4-3:(stage==1?B2:A1-1),m=stage==0?4:(stage==1?2:1);if(got==need){dfs(stage+1,0,1,R,sum);return;}for(int v=start;v<N;v++){if(!v||used(v)||lconf(v))continue;Reach z;if(!addm(R,v,m,&z))continue;sel[ns]=v;mul[ns]=m;ns++;dfs(stage,got+1,v+1,&z,addsum(sum,v,m));ns--;if(sol)return;}}
static void init(void){uint32_t za[5]={0},zb[5]={0},ya[5]={0},yb[5]={0};for(int d=0;d<5;d++){for(int y=0;y<5;y++)for(int z=0;z<5;z++){uint32_t b=1U<<(5*y+z);if(z+d<5)za[d]|=b;else zb[d]|=b;if(y+d<5)ya[d]|=b;else yb[d]|=b;}ZA[d]=(V8){za[d],za[d],za[d],za[d],za[d],0,0,0};ZB[d]=(V8){zb[d],zb[d],zb[d],zb[d],zb[d],0,0,0};YA[d]=(V8){ya[d],ya[d],ya[d],ya[d],ya[d],0,0,0};YB[d]=(V8){yb[d],yb[d],yb[d],yb[d],yb[d],0,0,0};}for(int a=0;a<N;a++)for(int b=0;b<N;b++){int ax=a/25,ay=(a/5)%5,az=a%5,bx=b/25,by=(b/5)%5,bz=b%5;ADD[a][b]=((ax+bx)%5)*25+((ay+by)%5)*5+((az+bz)%5);}memset(LINE,255,sizeof(LINE));int nl=0;for(int v=1;v<N;v++)if(LINE[v]==255){for(int c=1;c<5;c++)LINE[scal(c,v)]=(unsigned char)nl;nl++;}}
int main(int ac,char**av){if(ac!=4)return 2;A1=atoi(av[1]);B2=atoi(av[2]);C4=atoi(av[3]);if(A1+2*B2+4*C4!=31||A1<1||C4<3)return 2;init();Reach R;memset(&R,0,sizeof(R));R.r[0][0]=1U;int sum=0,b[3]={25,5,1};for(int i=0;i<3;i++){Reach z;if(!addm(&R,b[i],4,&z))return 3;R=z;sel[ns]=b[i];mul[ns]=4;ns++;sum=addsum(sum,b[i],4);}dfs(0,0,1,&R,sum);printf("a1=%d b2=%d c4=%d support=%d nodes=%lld leaves=%lld solutions=%lld\n",A1,B2,C4,A1+B2+C4,nodes,leaves,sol);return sol?1:0;}
