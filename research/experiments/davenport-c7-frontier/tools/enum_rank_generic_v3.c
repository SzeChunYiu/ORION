/* enumr2.c - rank-generic search: sequences over F_p^r of length L with no zero-sum of
 * length <= s and packing number <= 1.  Leaf test is an exact layered DP over pairs of
 * DISJOINT sub-multisets (sumA, sumB) with emptiness flags - no enumeration of blocks.
 * Usage: enumr2 p r L s [--progress] */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
static int p, r, L, s, N;
static int *addtab;
static int *negv;            /* negv[g] = -g, for the O(1) candidate test */
static unsigned char *reach;
static int *seq;
static long long nodes=0, leaves=0, found=0;
static int progress=0, SHARD=-1, NSHARD=1;
static inline unsigned char *R(int d,int l){ return reach + ((size_t)d*(s+1)+l)*N; }

/* layers: 00,10,01,11 over (sA,sB) in [N]x[N] */
static unsigned char *lay[4], *nl[4];
static int two_disjoint(void){
    size_t sz=(size_t)N*N;
    for(int i=0;i<4;i++){ memset(lay[i],0,sz); }
    lay[0][0]=1;
    for(int t=0;t<L;t++){
        int g=seq[t];
        for(int i=0;i<4;i++) memcpy(nl[i],lay[i],sz);
        for(int a=0;a<N;a++) for(int b=0;b<N;b++){
            size_t ix=(size_t)a*N+b;
            if(lay[0][ix]){ nl[1][(size_t)addtab[a*N+g]*N+b]=1; nl[2][(size_t)a*N+addtab[b*N+g]]=1; }
            if(lay[1][ix]){ nl[1][(size_t)addtab[a*N+g]*N+b]=1; nl[3][(size_t)a*N+addtab[b*N+g]]=1; }
            if(lay[2][ix]){ nl[2][(size_t)a*N+addtab[b*N+g]]=1; nl[3][(size_t)addtab[a*N+g]*N+b]=1; }
            if(lay[3][ix]){ nl[3][(size_t)addtab[a*N+g]*N+b]=1; nl[3][(size_t)a*N+addtab[b*N+g]]=1; }
        }
        for(int i=0;i<4;i++) memcpy(lay[i],nl[i],sz);
        if(lay[3][0]) return 1;
    }
    return lay[3][0];
}
static void dfs(int d,int lo){
    nodes++;
    /* One pass per node: forb[y]=1 iff y is a subsum of <= s-1 chosen terms.  Then a candidate g
     * is rejected iff forb[-g] -- O(1) each, instead of a memcpy + O(s*N) update to find out. */
    unsigned char forb[4096];
    if(d<L){
        memcpy(forb,R(d,0),N);
        for(int l=1;l<=s-1;l++){ unsigned char *src=R(d,l);
            for(int x=0;x<N;x++) forb[x]|=src[x]; }
    }
    if(progress && (nodes&0xFFFFF)==0) fprintf(stderr,"progress nodes=%lld leaves=%lld found=%lld d=%d\n",nodes,leaves,found,d);
    if(d==L){ leaves++;
        if(!two_disjoint()){ found++; printf("packing<=1:"); for(int i=0;i<L;i++) printf(" %d",seq[i]); printf("\n"); fflush(stdout);} return; }
    for(int g=lo; g<N; g++){
        if(g==0) continue;
        if(SHARD>=0 && d==r && g%NSHARD!=SHARD) continue;   /* shard on 1st free term */
        if(forb[negv[g]]) continue;                        /* O(1) reject, was O(s*N) */
        unsigned char *dst=R(d+1,0); memcpy(dst,R(d,0),(size_t)(s+1)*N);
        int bad=0;
        for(int l=s;l>=1;l--){
            unsigned char *from=R(d,l-1), *to=R(d+1,l);
            for(int x=0;x<N;x++) if(from[x]) to[addtab[x*N+g]]=1;
        }
        seq[d]=g; dfs(d+1,g);
    }
}
int main(int argc,char**argv){
    p=atoi(argv[1]); r=atoi(argv[2]); L=atoi(argv[3]); s=atoi(argv[4]);
    for(int i=5;i<argc;i++){ if(!strcmp(argv[i],"--progress")) progress=1;
        else if(!strcmp(argv[i],"--shard")){ SHARD=atoi(argv[i+1]); NSHARD=atoi(argv[i+2]); } }
    N=1; for(int i=0;i<r;i++) N*=p;
    addtab=malloc(sizeof(int)*(size_t)N*N);
    for(int a=0;a<N;a++) for(int b=0;b<N;b++){ int x=0,pw=1,aa=a,bb=b;
        for(int i=0;i<r;i++){ x+=((aa%p+bb%p)%p)*pw; aa/=p; bb/=p; pw*=p; } addtab[a*N+b]=x; }
    negv=malloc(sizeof(int)*N);
    for(int g=0;g<N;g++){ int t=g,n=0,pw=1;
        for(int i=0;i<r;i++){ n+=((p-(t%p))%p)*pw; t/=p; pw*=p; } negv[g]=n; }
    reach=calloc((size_t)(L+1)*(s+1)*N,1); seq=malloc(sizeof(int)*L);
    for(int i=0;i<4;i++){ lay[i]=malloc((size_t)N*N); nl[i]=malloc((size_t)N*N); }
    R(0,0)[0]=1;
    int d=0,pw=1;
    for(int i=0;i<r;i++){ int g=pw; pw*=p;
        memcpy(R(d+1,0),R(d,0),(size_t)(s+1)*N);
        for(int l=s;l>=1;l--){ unsigned char*from=R(d,l-1),*to=R(d+1,l);
            for(int x=0;x<N;x++) if(from[x]) to[addtab[x*N+g]]=1; }
        seq[d]=g; d++; }
    fprintf(stderr,"p=%d r=%d L=%d s=%d N=%d\n",p,r,L,s,N);
    dfs(d,1);
    fprintf(stderr,"DONE nodes=%lld leaves=%lld found=%lld\n",nodes,leaves,found);
    printf("RESULT p=%d r=%d L=%d s=%d shard=%d/%d found=%lld leaves=%lld nodes=%lld\n",p,r,L,s,SHARD,NSHARD,found,leaves,nodes);
    return 0;
}
