/* Enumerate every length-L sequence over C_5^3 with NO two disjoint nonempty
 * zero-sum subsequences, and report the maximum such L (= D_2 - 1).
 * Two independent state machines run together:
 *   (a) exact 2-disjoint DP  -> the real predicate (hereditary)
 *   (b) "no zero-sum of length <= T" reach  -> prune, valid whenever the target
 *       length is >= T + D(C_5^3) = T + 13  (Lemma A)
 * Reductions R1 (GL(3,5): support contains e1,e2,e3) and R2 (S_3 ordering).  */
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
typedef unsigned __int128 u128;
#define N 125
static unsigned char ADD[N][N]; static int NEGM[5][N];
static u128 MA[3][5], MB[3][5], ONE=1;
static int T=6, MAXMULT=4, LMIN=19, found_count=0, best=0;
static int LINE[N], LPOS[N], NLINES=0; static unsigned char MAXLINE[5][5][5][5];
static long long nodes=0;
static int seqb[64], bestseq[64];
static FILE *OUT;

static inline u128 shft(u128 m,int e){
    int dx=e/25,dy=(e/5)%5,dz=e%5;
    if(dz) m=((m&MA[0][dz])<<dz)|((m&MB[0][dz])>>(5-dz));
    if(dy) m=((m&MA[1][dy])<<(5*dy))|((m&MB[1][dy])>>(5*(5-dy)));
    if(dx) m=((m&MA[2][dx])<<(25*dx))|((m&MB[2][dx])>>(25*(5-dx)));
    return m;
}
typedef struct {
    unsigned char r[8][N], pre[8][N];   /* no-ZS<=T reach */
    u128 R1;                            /* one nonempty part, its sum */
    u128 R2[N];                         /* both parts nonempty: row=s1, bit=s2 */
} St;
static void rebuild_pre(St*s){ memcpy(s->pre[0],s->r[0],N);
    for(int w=1;w<=T;w++) for(int i=0;i<N;i++) s->pre[w][i]=s->pre[w-1][i]|s->r[w][i]; }

static int add_elem(const St*in,int v,St*out){
    memcpy(out->r,in->r,sizeof(in->r));
    for(int w=T;w>=1;w--){ const unsigned char*pv=in->r[w-1]; unsigned char*cu=out->r[w];
        for(int s=0;s<N;s++){ if(!pv[s])continue; int t=ADD[s][v];
            if(t==0) return 0; cu[t]=1; } }
    rebuild_pre(out);
    /* 2-disjoint update, all reads from `in` */
    out->R1 = in->R1 | shft(in->R1,v) | (ONE<<v);
    for(int s=0;s<N;s++) out->R2[s]=in->R2[s];
    for(int s=0;s<N;s++){ u128 row=in->R2[s]; if(!row) continue;
        out->R2[ADD[s][v]] |= row;          /* v joins part 1 */
        out->R2[s] |= shft(row,v); }        /* v joins part 2 */
    for(int s=0;s<N;s++) if((in->R1>>s)&1) out->R2[s] |= (ONE<<v);  /* v starts part 2 */
    if(out->R2[0] & ONE) return 0;          /* (0,0) both nonempty -> two disjoint */
    return 1;
}
static inline int mult_ub(const St*s,int v){ int k=0;
    for(int j=1;j<=MAXMULT;j++){ int lim=T-j; if(lim<0)break;
        if(s->pre[lim][NEGM[j][v]]) break; k=j; } return k; }

static void dfs(const St*st,int len,const int*cand,int nc){
    nodes++;
    if(len>best){ best=len; memcpy(bestseq,seqb,len*sizeof(int));
        fprintf(stderr,"NEW BEST %d nodes=%lld\n",len,nodes); fflush(stderr); }
    if(len>=LMIN){ found_count++;
        if(OUT){ fprintf(OUT,"["); for(int i=0;i<len;i++) fprintf(OUT,"%s[%d,%d,%d]",i?",":"",
            seqb[i]/25,(seqb[i]/5)%5,seqb[i]%5); fprintf(OUT,"]\n"); } }
    int fc[N],fm[N],nf=0; unsigned char ub[64][4]; memset(ub,0,sizeof(ub));
    for(int i=0;i<nc;i++){ int m=mult_ub(st,cand[i]);
        if(m){ fc[nf]=cand[i]; fm[nf]=m; nf++; ub[LINE[cand[i]]][LPOS[cand[i]]]=m; } }
    int bound=len; for(int L=0;L<NLINES;L++) bound+=MAXLINE[ub[L][0]][ub[L][1]][ub[L][2]][ub[L][3]];
    if(bound<LMIN && bound<=best) return;
    St *buf=malloc(5*sizeof(St));
    for(int i=0;i<nf;i++){
        memset(ub,0,sizeof(ub));
        for(int j=i;j<nf;j++) ub[LINE[fc[j]]][LPOS[fc[j]]]=fm[j];
        int b=len; for(int L=0;L<NLINES;L++) b+=MAXLINE[ub[L][0]][ub[L][1]][ub[L][2]][ub[L][3]];
        if(b<LMIN && b<=best) break;
        const St*cur=st; int bi=0;
        for(int k=1;k<=fm[i];k++){
            if(!add_elem(cur,fc[i],&buf[bi])) break;
            cur=&buf[bi]; bi++; seqb[len+k-1]=fc[i];
            dfs(cur,len+k,fc+i+1,nf-i-1); } }
    free(buf);
}
static int line_ok(int a,int b,int c,int d){
    for(int x=0;x<=a;x++)for(int y=0;y<=b;y++)for(int z=0;z<=c;z++)for(int w=0;w<=d;w++){
        int s=x+y+z+w; if(s>=1&&s<=T&&((x+2*y+3*z+4*w)%5)==0) return 0; } return 1; }
int main(int argc,char**argv){
    if(argc>1) LMIN=atoi(argv[1]);
    if(argc>2) T=atoi(argv[2]);
    if(argc>3) OUT=fopen(argv[3],"w");
    for(int d=0;d<5;d++){ MA[0][d]=MB[0][d]=MA[1][d]=MB[1][d]=MA[2][d]=MB[2][d]=0;
        for(int i=0;i<125;i++){ int x=i/25,y=(i/5)%5,z=i%5; u128 bb=ONE<<i;
            if(z+d<5)MA[0][d]|=bb; else MB[0][d]|=bb;
            if(y+d<5)MA[1][d]|=bb; else MB[1][d]|=bb;
            if(x+d<5)MA[2][d]|=bb; else MB[2][d]|=bb; } }
    for(int a=0;a<N;a++){ int ax=a/25,ay=(a/5)%5,az=a%5;
        for(int b=0;b<N;b++){ int bx=b/25,by=(b/5)%5,bz=b%5;
            ADD[a][b]=((ax+bx)%5)*25+((ay+by)%5)*5+((az+bz)%5); } }
    for(int j=0;j<5;j++) for(int v=0;v<N;v++){ int x=v/25,y=(v/5)%5,z=v%5;
        NEGM[j][v]=(((-j*x)%5+5)%5)*25+(((-j*y)%5+5)%5)*5+(((-j*z)%5+5)%5); }
    for(int v=0;v<N;v++) LINE[v]=-1;
    for(int v=1;v<N;v++){ if(LINE[v]>=0)continue; int id=NLINES++;
        for(int c=1;c<5;c++){ int u=((c*(v/25))%5)*25+((c*((v/5)%5))%5)*5+((c*(v%5))%5);
            LINE[u]=id; LPOS[u]=c-1; } }
    for(int u1=0;u1<5;u1++)for(int u2=0;u2<5;u2++)for(int u3=0;u3<5;u3++)for(int u4=0;u4<5;u4++){
        int mx=0; for(int a=0;a<=u1;a++)for(int b=0;b<=u2;b++)for(int c=0;c<=u3;c++)for(int d=0;d<=u4;d++)
            if(a+b+c+d>mx&&line_ok(a,b,c,d)) mx=a+b+c+d;
        MAXLINE[u1][u2][u3][u4]=mx; }
    int E1=25,E2=5,E3=1,cand0[N],nc0=0;
    for(int v=1;v<N;v++) if(v!=E1&&v!=E2&&v!=E3) cand0[nc0++]=v;
    St z; memset(&z,0,sizeof(z)); z.r[0][0]=1; rebuild_pre(&z); z.R1=0; memset(z.R2,0,sizeof(z.R2));
    for(int m1=1;m1<=MAXMULT;m1++) for(int m2=m1;m2<=MAXMULT;m2++) for(int m3=m2;m3<=MAXMULT;m3++){
        St a,b; const St*cur=&z; St*nx=&a; int ok=1,len=0;
        for(int i=0;i<m1&&ok;i++){ok=add_elem(cur,E1,nx);cur=nx;nx=(nx==&a)?&b:&a;seqb[len++]=E1;}
        for(int i=0;i<m2&&ok;i++){ok=add_elem(cur,E2,nx);cur=nx;nx=(nx==&a)?&b:&a;seqb[len++]=E2;}
        for(int i=0;i<m3&&ok;i++){ok=add_elem(cur,E3,nx);cur=nx;nx=(nx==&a)?&b:&a;seqb[len++]=E3;}
        if(!ok) continue;
        St hold; memcpy(&hold,cur,sizeof(St));
        fprintf(stderr,"[m=%d,%d,%d] nodes=%lld best=%d found=%d\n",m1,m2,m3,nodes,best,found_count);
        fflush(stderr);
        dfs(&hold,len,cand0,nc0); }
    if(OUT) fclose(OUT);
    printf("{\"group\":\"C_5^3\",\"predicate\":\"no_two_disjoint_zero_sums\",\"T_prune\":%d,"
           "\"max_length\":%d,\"D_2_from_this_route\":%d,\"witnesses_at_length_ge_%d\":%d,"
           "\"nodes\":%lld,\"extremal_witness\":[",T,best,best+1,LMIN,found_count,nodes);
    for(int i=0;i<best;i++) printf("%s[%d,%d,%d]",i?",":"",bestseq[i]/25,(bestseq[i]/5)%5,bestseq[i]%5);
    printf("]}\n"); return 0;
}
