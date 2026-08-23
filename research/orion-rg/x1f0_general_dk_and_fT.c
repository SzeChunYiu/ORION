/* Exact D_k(G) and f_T(G) for G = C_p^r, by complete DFS over multisets.
 * D_k(G) = 1 + max length of a sequence with no k pairwise disjoint nonempty
 * zero-sum subsequences.   State: reachable tuples of k partial sums + flags.
 * Primitive mod-p coordinate addition only. */
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
static int P,R,NG,KK,MODE,TT;          /* MODE 0 = D_k, MODE 1 = f_T */
static int *ADDT;                       /* NG x NG */
#define A(a,b) ADDT[(a)*NG+(b)]
/* --- D_k state: bitset over (s_1..s_k) with s_i in [0,NG), plus "used" flags
   folded in by representing an unused slot as sum 0 with flag 0.  We store
   states as arrays of k slots each in [0,NG) and a k-bit flag mask.  For small
   groups we materialise the full state set as a hash-free bitset.        --- */
static unsigned char *ST, *ST2;  static long long NST;
static int POW[8];
static long long enc_state(const int*s,int fl){ long long e=fl; for(int i=0;i<KK;i++) e=e*NG+s[i]; return e; }
static void dec_state(long long e,int*s,int*fl){ for(int i=KK-1;i>=0;i--){ s[i]=e%NG; e/=NG; } *fl=e; }
/* --- f_T state: reach[w][sum] --- */
static unsigned char *RE, *PRE;
static int best=0; static long long nodes=0;
static int NEGM[8][512];
static int seqbuf[128], bestseq[128];

static int fT_add(const unsigned char*in,int v,unsigned char*out){
    memcpy(out,in,(TT+1)*NG);
    for(int w=TT;w>=1;w--){ const unsigned char*pv=in+(w-1)*NG; unsigned char*cu=out+w*NG;
        for(int s=0;s<NG;s++){ if(!pv[s])continue; int t=A(s,v); if(t==0) return 0; cu[t]=1; } }
    return 1;
}
static int dk_add(const unsigned char*in,int v,unsigned char*out,long long nst){
    memcpy(out,in,nst);
    int s[8];int fl;
    for(long long e=0;e<nst;e++){ if(!in[e])continue;
        dec_state(e,s,&fl);
        for(int i=0;i<KK;i++){ int t[8]; memcpy(t,s,sizeof(t)); t[i]=A(s[i],v);
            int nf=fl|(1<<i); long long e2=enc_state(t,nf);
            out[e2]=1;
            if(nf==(1<<KK)-1){ int allz=1; for(int j=0;j<KK;j++) if(t[j]) {allz=0;break;}
                if(allz) return 0; } } }
    return 1;
}
static void dfs(const unsigned char*st,int len,int startv){
    nodes++;
    if(len>best){ best=len; memcpy(bestseq,seqbuf,len*sizeof(int)); }
    long long nst = MODE? (long long)(TT+1)*NG : NST;
    unsigned char *nx = malloc(nst);
    for(int v=startv;v<NG;v++){
        int ok = MODE? fT_add(st,v,nx) : dk_add(st,v,nx,nst);
        if(!ok) continue;
        seqbuf[len]=v;
        dfs(nx,len+1,v);
    }
    free(nx);
}
int main(int argc,char**argv){
    /* usage: dk p r mode k_or_T   (mode: dk | fT) */
    P=atoi(argv[1]); R=atoi(argv[2]);
    MODE = strcmp(argv[3],"fT")==0;
    if(MODE) TT=atoi(argv[4]); else KK=atoi(argv[4]);
    NG=1; for(int i=0;i<R;i++) NG*=P;
    ADDT=malloc(sizeof(int)*NG*NG);
    for(int a=0;a<NG;a++)for(int b=0;b<NG;b++){
        int x=a,y=b,res=0,m=1;
        for(int i=0;i<R;i++){ int d=((x%P)+(y%P))%P; res+=d*m; m*=P; x/=P; y/=P; }
        A(a,b)=res; }
    long long nst;
    unsigned char*st0;
    if(MODE){ nst=(long long)(TT+1)*NG; st0=calloc(nst,1); st0[0*NG+0]=1; }
    else { NST=1; for(int i=0;i<KK;i++) NST*=NG; NST*=(1<<KK); nst=NST;
           st0=calloc(nst,1); int s[8]={0,0,0,0,0,0,0,0}; st0[enc_state(s,0)]=1; }
    dfs(st0,0,1);
    if(MODE) printf("{\"group\":\"C_%d^%d\",\"T\":%d,\"f_T\":%d,\"nodes\":%lld,\"witness\":[",P,R,TT,best,nodes);
    else     printf("{\"group\":\"C_%d^%d\",\"k\":%d,\"max_no_k_disjoint\":%d,\"D_k\":%d,\"nodes\":%lld,\"witness\":[",P,R,KK,best,best+1,nodes);
    for(int i=0;i<best;i++){ printf("%s%d",i?",":"",bestseq[i]); }
    printf("]}\n"); return 0;
}
