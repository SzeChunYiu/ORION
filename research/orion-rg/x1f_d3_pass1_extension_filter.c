/* Pass 1 of the D_3 decision: for each complete length-19 no-two-disjoint
 * witness C, enumerate every 6-element extension keeping min zero-sum >= 6
 * (necessary for any length-25 sequence with no three disjoint zero-sums,
 * by Lemma A with D_2 = 20).  Cheap state only: the weight-<=5 reach board.
 * Survivors go to pass 2 for the exact three-disjoint test. */
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#define N 125
#define TZ 5
static unsigned char ADD[N][N]; static int NEG[N];
static long long surv=0, wit=0, bad=0;
static FILE *OUT;
typedef struct { unsigned char r[TZ+1][N], pre[N]; } R;
static int addel(const R*in,int v,R*out){
    memcpy(out->r,in->r,sizeof(in->r));
    for(int w=TZ;w>=1;w--){ const unsigned char*pv=in->r[w-1]; unsigned char*cu=out->r[w];
        for(int s=0;s<N;s++){ if(!pv[s])continue; int t=ADD[s][v];
            if(t==0) return 0; cu[t]=1; } }
    for(int i=0;i<N;i++){ unsigned char a=0; for(int w=0;w<=TZ-1;w++) a|=out->r[w][i]; out->pre[i]=a; }
    return 1;
}
static int base[19], ext6[6];
static int ASUM=0;   /* running sum of the added block */
static R BUF[8];
/* A must itself be a zero-sum of length exactly 6 (structure theorem), and it is
 * a multiset, so enumerate it in nondecreasing order and force the last element. */
static void rec(const R*st,int d,int minv){
    if(d==0){ surv++;
        if(OUT){ for(int i=0;i<19;i++) fprintf(OUT,"%s[%d,%d,%d]",i?",":"[",base[i]/25,(base[i]/5)%5,base[i]%5);
                 for(int i=0;i<6;i++) fprintf(OUT,",[%d,%d,%d]",ext6[i]/25,(ext6[i]/5)%5,ext6[i]%5);
                 fprintf(OUT,"]\n"); }
        return; }
    R*nx=&BUF[d];
    int lo=minv, hi=N-1;
    if(d==1){ lo=hi=NEG[ASUM]; if(lo<minv||lo==0) return; }   /* forced: sum(A)=0 */
    for(int v=lo;v<=hi;v++){
        if(st->pre[NEG[v]]) continue;             /* would create a zero-sum of length <= TZ */
        if(!addel(st,v,nx)) continue;
        ext6[6-d]=v; ASUM=ADD[ASUM][v];
        rec(nx,d-1,v);
        ASUM=ADD[ASUM][NEG[v]];
    }
}
int main(int argc,char**argv){
    for(int a=0;a<N;a++){ int ax=a/25,ay=(a/5)%5,az=a%5;
        for(int b=0;b<N;b++){ int bx=b/25,by=(b/5)%5,bz=b%5;
            ADD[a][b]=((ax+bx)%5)*25+((ay+by)%5)*5+((az+bz)%5); } }
    for(int v=0;v<N;v++){ int x=v/25,y=(v/5)%5,z=v%5;
        NEG[v]=((5-x)%5)*25+((5-y)%5)*5+((5-z)%5); }
    FILE*f=fopen(argv[1],"r"); OUT=fopen(argv[2],"w");
    char line[4096];
    while(fgets(line,sizeof(line),f)){
        int nv=0; char*p=line;
        while(*p){ if(*p=='['){ int a,b,c; if(sscanf(p,"[%d,%d,%d]",&a,&b,&c)==3&&nv<19) base[nv++]=a*25+b*5+c; } p++; }
        if(nv!=19) continue;
        R cur; memset(&cur,0,sizeof(R)); cur.r[0][0]=1;
        for(int i=0;i<N;i++) cur.pre[i]=cur.r[0][i];
        int ok=1; R t;
        for(int i=0;i<19&&ok;i++){ if(!addel(&cur,base[i],&t)){ ok=0; break; } memcpy(&cur,&t,sizeof(R)); }
        wit++;
        if(!ok){ bad++; continue; }   /* C already has a zero-sum of length <=5: cannot host M */
        ASUM=0; rec(&cur,6,1);
        if(wit%20000==0){ fprintf(stderr,"witnesses=%lld survivors=%lld skipped=%lld\n",wit,surv,bad); fflush(stderr); }
    }
    fclose(OUT);
    printf("{\"pass\":1,\"witnesses\":%lld,\"witnesses_with_short_zero_sum_skipped\":%lld,"
           "\"length25_candidates_min_zerosum_ge_6\":%lld}\n",wit,bad,surv);
    return 0;
}
