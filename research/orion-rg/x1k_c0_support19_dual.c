/* X1-K exact support-19 discriminator for a hypothetical length-31 total-zero
 * sequence over C_5^3 with no nonempty zero-sum subsequence of length <=5.
 *
 * Saturation/no-multiplicity-3 leaves five patterns:
 *   (a1,b2,c4) = (7,12,0),(9,9,1),(11,6,2),(13,3,3),(15,0,4).
 *
 * Normalizations are proved before search:
 *  c4=0: the multiplicity-2 support spans rank 3 -> seed (2,2,2) on a basis;
 *  c4=1: the 4-point plus multiplicity-2 support spans rank 3 -> (4,2,2);
 *  c4=2: the two 4-points plus multiplicity-2 support spans rank 3 -> (4,4,2);
 *  c4=3: split high-4 rank 3 versus rank 2; in rank 2, one multiplicity-2
 *        point must leave the high-4 plane and is normalized to e3;
 *  c4=4: four multiplicity-4 points cannot lie in rank <=2, so high-4 rank 3.
 *
 * Two exact translation primitives are run on the identical frozen grammar:
 *  A) coordinate-mask u128 shift;
 *  B) lookup translation generated solely from primitive ADD[src][v].
 * Both maintain exact subset-sum masks for weights 0..5 and force the final
 * singleton from the total-sum equation.  Authority: bounded exact computation;
 * novelty/theorem authority false.
 */
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
typedef unsigned __int128 u128;
#define N 125
#define T 5
static unsigned char ADD[N][N],LINE[N];
static u128 MA[3][5],MB[3][5],ONE=(u128)1,*LUT;
#define L(v,j,b) LUT[(((v)*16+(j))*256)+(b)]
typedef struct{u128 r[T+1];} Reach;
typedef struct{long long nodes,leaves,solutions;} Counts;
static int sel[40],mul[40],ns,R1,R2,R4,translator;
static long long nodes,leaves,sol;
static int scal(int c,int v){int x=v/25,y=(v/5)%5,z=v%5;return ((c*x)%5)*25+((c*y)%5)*5+((c*z)%5);}
static int neg(int v){return scal(4,v);}
static u128 tr_shift(u128 m,int e){int dx=e/25,dy=(e/5)%5,dz=e%5;if(dz)m=((m&MA[0][dz])<<dz)|((m&MB[0][dz])>>(5-dz));if(dy)m=((m&MA[1][dy])<<(5*dy))|((m&MB[1][dy])>>(5*(5-dy)));if(dx)m=((m&MA[2][dx])<<(25*dx))|((m&MB[2][dx])>>(25*(5-dx)));return m;}
static u128 tr_lut(u128 m,int v){u128 o=0;for(int j=0;j<16;j++){unsigned b=(unsigned)(m&255);if(b)o|=L(v,j,b);m>>=8;}return o;}
static int add1(const Reach*i,int v,Reach*o){*o=*i;for(int w=T;w>=1;w--){u128 z=translator?tr_lut(i->r[w-1],v):tr_shift(i->r[w-1],v);if(z&ONE)return 0;o->r[w]|=z;}return 1;}
static int addm(const Reach*i,int v,int m,Reach*o){Reach a,b;const Reach*c=i;Reach*n=&a;for(int k=0;k<m;k++){if(!add1(c,v,n))return 0;c=n;n=n==&a?&b:&a;}*o=*c;return 1;}
static int used(int v){for(int i=0;i<ns;i++)if(sel[i]==v)return 1;return 0;}
static int lconf(int v){for(int i=0;i<ns;i++)if(mul[i]==4&&LINE[sel[i]]==LINE[v])return 1;return 0;}
static int addsum(int s,int v,int m){return ADD[s][scal(m%5,v)];}
static void dfs(int stage,int got,int start,const Reach*R,int sum){nodes++;if(stage==3){int q=neg(sum);leaves++;if(!q||used(q)||lconf(q))return;if(R1>1&&q<=sel[ns-1])return;Reach z;if(!addm(R,q,1,&z))return;sol++;return;}int need=stage==0?R4:(stage==1?R2:R1-1),m=stage==0?4:(stage==1?2:1);if(got==need){dfs(stage+1,0,1,R,sum);return;}for(int v=start;v<N;v++){if(!v||used(v)||lconf(v))continue;Reach z;if(!addm(R,v,m,&z))continue;sel[ns]=v;mul[ns]=m;ns++;dfs(stage,got+1,v+1,&z,addsum(sum,v,m));ns--;if(sol)return;}}
static Counts seedrun(const int*base,const int*ms,int nseed,int a1,int b2,int c4){Reach R;memset(&R,0,sizeof(R));R.r[0]=ONE;ns=0;int sum=0,s1=0,s2=0,s4=0;for(int i=0;i<nseed;i++){Reach z;if(!addm(&R,base[i],ms[i],&z))return(Counts){0,0,0};R=z;sel[ns]=base[i];mul[ns]=ms[i];ns++;sum=addsum(sum,base[i],ms[i]);if(ms[i]==1)s1++;else if(ms[i]==2)s2++;else s4++;}R1=a1-s1;R2=b2-s2;R4=c4-s4;nodes=leaves=sol=0;dfs(0,0,1,&R,sum);return(Counts){nodes,leaves,sol};}
static Counts run_pattern(int idx){int a1,b2,c4;base:;Counts t={0,0,0};if(idx==0){a1=7;b2=12;c4=0;int b[]={25,5,1},m[]={2,2,2};return seedrun(b,m,3,a1,b2,c4);}if(idx==1){a1=9;b2=9;c4=1;int b[]={25,5,1},m[]={4,2,2};return seedrun(b,m,3,a1,b2,c4);}if(idx==2){a1=11;b2=6;c4=2;int b[]={25,5,1},m[]={4,4,2};return seedrun(b,m,3,a1,b2,c4);}if(idx==3){a1=13;b2=3;c4=3;int b[]={25,5,1},m[]={4,4,4};return seedrun(b,m,3,a1,b2,c4);}if(idx==4){a1=13;b2=3;c4=3;for(int x=1;x<5;x++)for(int y=1;y<5;y++){int q=25*x+5*y,b[]={25,5,q,1},m[]={4,4,4,2};Counts c=seedrun(b,m,4,a1,b2,c4);t.nodes+=c.nodes;t.leaves+=c.leaves;t.solutions+=c.solutions;if(t.solutions)return t;}return t;}a1=15;b2=0;c4=4;int b[]={25,5,1},m[]={4,4,4};return seedrun(b,m,3,a1,b2,c4);}
static void init(void){for(int a=0;a<N;a++)for(int b=0;b<N;b++){int ax=a/25,ay=(a/5)%5,az=a%5,bx=b/25,by=(b/5)%5,bz=b%5;ADD[a][b]=((ax+bx)%5)*25+((ay+by)%5)*5+((az+bz)%5);}for(int d=0;d<5;d++){MA[0][d]=MB[0][d]=MA[1][d]=MB[1][d]=MA[2][d]=MB[2][d]=0;for(int i=0;i<N;i++){int x=i/25,y=(i/5)%5,z=i%5;u128 bb=ONE<<i;if(z+d<5)MA[0][d]|=bb;else MB[0][d]|=bb;if(y+d<5)MA[1][d]|=bb;else MB[1][d]|=bb;if(x+d<5)MA[2][d]|=bb;else MB[2][d]|=bb;}}memset(LINE,255,sizeof(LINE));int nl=0;for(int v=1;v<N;v++)if(LINE[v]==255){for(int c=1;c<5;c++)LINE[scal(c,v)]=nl;nl++;}LUT=calloc((size_t)N*16*256,sizeof(u128));if(!LUT)exit(3);for(int v=0;v<N;v++)for(int j=0;j<16;j++)for(int b=1;b<256;b++){int lb=__builtin_ctz(b),rest=b&(b-1),src=j*8+lb;u128 z=L(v,j,rest);if(src<N)z|=((u128)1)<<ADD[src][v];L(v,j,b)=z;}}
int main(void){init();static const char*name[]={"1^7 2^12","1^9 2^9 4","1^11 2^6 4^2","1^13 2^3 4^3 rank3","1^13 2^3 4^3 rank2","1^15 4^4"};int ok=1;for(int i=0;i<6;i++){translator=0;Counts a=run_pattern(i);translator=1;Counts b=run_pattern(i);printf("%s A=(%lld,%lld,%lld) B=(%lld,%lld,%lld)\n",name[i],a.nodes,a.leaves,a.solutions,b.nodes,b.leaves,b.solutions);if(memcmp(&a,&b,sizeof(a))||a.solutions)ok=0;}return ok?0:1;}
