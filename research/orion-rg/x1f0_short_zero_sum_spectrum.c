/* f_T(C_5^3) = max length of a multiset over C_5^3 with NO nonempty zero-sum
 * subsequence of length <= T.  EXHAUSTIVE over rank-3 supports.
 * Primitive mod-5 addition only.
 *
 * Exact multiplicity oracle: adding k copies of v keeps the property iff for
 * every j=1..k, (-j*v) is not a sum of <= T-j current elements.
 *
 * SOUND bound: partition the 124 nonzero vectors into the 31 projective lines
 * {g,2g,3g,4g}.  A line's own contribution (a1,a2,a3,a4) must itself be free of
 * zero-sums of length <= T, i.e. no (b_i)<=(a_i) with 1<=sum b_i<=T and
 * sum(i*b_i)=0 mod 5.  MAXLINE[u1][u2][u3][u4] tabulates the max attainable
 * line total under per-point caps u_i.  (The earlier "max over points" bound was
 * UNSOUND: g and 2g can coexist -- see PROTOCOL note.)
 */
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#define N 125
static unsigned char ADD[N][N]; static int NEGM[5][N];
static int T=7, MAXMULT=4, TARGET=0, found=0;
static int LINE[N], LPOS[N], NLINES=0, LPT[64][4];
static unsigned char MAXLINE[5][5][5][5];
typedef struct { unsigned char r[9][N]; unsigned char pre[9][N]; } Reach;

static void rebuild_pre(Reach*R){
    memcpy(R->pre[0],R->r[0],N);
    for(int w=1;w<=T;w++) for(int s=0;s<N;s++) R->pre[w][s]=R->pre[w-1][s]|R->r[w][s];
}
static int add_elem(const Reach*in,int v,Reach*out){
    memcpy(out,in,sizeof(Reach));
    for(int w=T;w>=1;w--){
        const unsigned char*prev=in->r[w-1]; unsigned char*cur=out->r[w];
        for(int s=0;s<N;s++){ if(!prev[s])continue; int t=ADD[s][v];
            if(t==0) return 0; cur[t]=1; } }
    rebuild_pre(out); return 1;
}
static inline int mult_ub(const Reach*R,int v){
    int k=0;
    for(int j=1;j<=MAXMULT;j++){ int lim=T-j; if(lim<0)break;
        if(R->pre[lim][NEGM[j][v]]) break; k=j; }
    return k;
}
static int best=0,best_seq[64]; static long long nodes=0;
static void dfs(const Reach*reach,int*seq,int len,const int*cand,int nc){
    nodes++;
    if(len>best){ best=len; memcpy(best_seq,seq,len*sizeof(int));
        fprintf(stderr,"NEW BEST %d nodes=%lld\n",len,nodes); fflush(stderr);
        if(TARGET&&len>=TARGET){found=1;return;} }
    int fc[N],fm[N],nf=0;
    unsigned char ub[64][4]; memset(ub,0,sizeof(ub));
    for(int i=0;i<nc;i++){ int m=mult_ub(reach,cand[i]);
        if(m){ fc[nf]=cand[i]; fm[nf]=m; nf++; ub[LINE[cand[i]]][LPOS[cand[i]]]=m; } }
    int bound=len;
    for(int L=0;L<NLINES;L++) bound+=MAXLINE[ub[L][0]][ub[L][1]][ub[L][2]][ub[L][3]];
    if(bound<=best) return;
    if(TARGET&&bound<TARGET) return;
    Reach buf[5];
    for(int i=0;i<nf;i++){
        memset(ub,0,sizeof(ub));
        for(int j=i;j<nf;j++) ub[LINE[fc[j]]][LPOS[fc[j]]]=fm[j];
        int b=len; for(int L=0;L<NLINES;L++) b+=MAXLINE[ub[L][0]][ub[L][1]][ub[L][2]][ub[L][3]];
        if(b<=best) return;
        if(TARGET&&b<TARGET) return;
        const Reach*cur=reach; int bi=0;
        for(int k=1;k<=fm[i];k++){
            if(!add_elem(cur,fc[i],&buf[bi])) break;
            cur=&buf[bi]; bi++; seq[len+k-1]=fc[i];
            dfs(cur,seq,len+k,fc+i+1,nf-i-1);
            if(found) return; } }
}
static int line_ok(int a,int b,int c,int d){
    for(int x=0;x<=a;x++)for(int y=0;y<=b;y++)for(int z=0;z<=c;z++)for(int w=0;w<=d;w++){
        int s=x+y+z+w; if(s>=1&&s<=T&&((x+2*y+3*z+4*w)%5)==0) return 0; }
    return 1;
}
int main(int argc,char**argv){
    if(argc>1) T=atoi(argv[1]);
    if(argc>2) TARGET=atoi(argv[2]);
    for(int a=0;a<N;a++){ int ax=a/25,ay=(a/5)%5,az=a%5;
        for(int b=0;b<N;b++){ int bx=b/25,by=(b/5)%5,bz=b%5;
            ADD[a][b]=((ax+bx)%5)*25+((ay+by)%5)*5+((az+bz)%5); } }
    for(int j=0;j<5;j++) for(int v=0;v<N;v++){ int x=v/25,y=(v/5)%5,z=v%5;
        NEGM[j][v]=(((-j*x)%5+5)%5)*25+(((-j*y)%5+5)%5)*5+(((-j*z)%5+5)%5); }
    for(int v=0;v<N;v++) LINE[v]=-1;
    for(int v=1;v<N;v++){ if(LINE[v]>=0)continue; int id=NLINES++;
        for(int c=1;c<5;c++){ int u=((c*(v/25))%5)*25+((c*((v/5)%5))%5)*5+((c*(v%5))%5);
            LINE[u]=id; LPOS[u]=c-1; LPT[id][c-1]=u; } }
    for(int u1=0;u1<5;u1++)for(int u2=0;u2<5;u2++)for(int u3=0;u3<5;u3++)for(int u4=0;u4<5;u4++){
        int mx=0;
        for(int a=0;a<=u1;a++)for(int b=0;b<=u2;b++)for(int c=0;c<=u3;c++)for(int d=0;d<=u4;d++)
            if(a+b+c+d>mx && line_ok(a,b,c,d)) mx=a+b+c+d;
        MAXLINE[u1][u2][u3][u4]=mx; }
    fprintf(stderr,"MAXLINE[4][4][4][4]=%d  MAXLINE[1][1][0][0]=%d\n",
            MAXLINE[4][4][4][4],MAXLINE[1][1][0][0]);
    int E1=25,E2=5,E3=1,cand0[N],nc0=0;
    for(int v=1;v<N;v++) if(v!=E1&&v!=E2&&v!=E3) cand0[nc0++]=v;
    Reach R0; memset(&R0,0,sizeof(R0)); R0.r[0][0]=1; rebuild_pre(&R0);
    int seq[64];
    for(int m1=1;m1<=MAXMULT&&!found;m1++)
    for(int m2=m1;m2<=MAXMULT&&!found;m2++)
    for(int m3=m2;m3<=MAXMULT&&!found;m3++){
        Reach a,b; const Reach*cur=&R0; Reach*nx=&a; int ok=1,len=0;
        for(int i=0;i<m1&&ok;i++){ok=add_elem(cur,E1,nx);cur=nx;nx=(nx==&a)?&b:&a;seq[len++]=E1;}
        for(int i=0;i<m2&&ok;i++){ok=add_elem(cur,E2,nx);cur=nx;nx=(nx==&a)?&b:&a;seq[len++]=E2;}
        for(int i=0;i<m3&&ok;i++){ok=add_elem(cur,E3,nx);cur=nx;nx=(nx==&a)?&b:&a;seq[len++]=E3;}
        if(!ok) continue;
        Reach hold; memcpy(&hold,cur,sizeof(Reach));
        fprintf(stderr,"[m=%d,%d,%d] nodes=%lld best=%d\n",m1,m2,m3,nodes,best); fflush(stderr);
        dfs(&hold,seq,len,cand0,nc0); }
    printf("{\"group\":\"C_5^3\",\"T\":%d,\"f_T_rank3\":%d,\"nodes\":%lld,\"complete_search\":%s,\"witness\":[",
           T,best,nodes,found?"false":"true");
    for(int i=0;i<best;i++) printf("%s[%d,%d,%d]",i?",":"",best_seq[i]/25,(best_seq[i]/5)%5,best_seq[i]%5);
    printf("]}\n"); return 0;
}
