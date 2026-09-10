/* enum_rank_sym_v2.c - enum_rank_generic_v3 plus orderly generation and row-major sums against the basis stabiliser.
 *
 * WHAT IS ADDED, AND WHY IT IS SOUND
 *
 * The parent search fixes seq[0..r-1] = e_1..e_r and enumerates the tail seq[r..L-1] in
 * nondecreasing index order.  The subgroup of GL(r,p) fixing the multiset {e_1,...,e_r} is the
 * symmetric group S_r acting by permuting coordinates: a monomial matrix with a diagonal entry
 * other than 1 sends e_i outside the basis, so only permutations survive.  The parent search does
 * not quotient by S_r at all, and therefore walks up to r! isomorphic copies of every tail --
 * 720 of them at rank 6 and 5040 at rank 7.
 *
 * This build prunes a node whose tail is not lexicographically minimal in its S_r orbit, tested
 * against the C(r,2) transpositions rather than all r! permutations.  Testing a SUBSET of the
 * group is still sound (each test is an independent necessary condition) and costs O(r^2 * m)
 * per node instead of O(r! * m).
 *
 * Soundness.  Write T_d for the sorted tail at depth d and T_L for a complete tail.  If some
 * permutation b has sort(b(T_d)) <lex T_d, then sort(b(T_L)) <lex T_L.  Reason: the first d
 * entries of sort(b(T_L)) are the d smallest of a superset of b(T_d), so they are entrywise <=
 * sort(b(T_d)); at the first index j where sort(b(T_d))[j] < T_d[j] = T_L[j], either an earlier
 * index already differs downward or index j does.  Contrapositive: if T_L is the lex-least
 * element of its orbit, no prefix of it is ever pruned.  So every orbit still reaches a leaf
 * through its lex-least representative, and `found = 0` here means `found = 0` in the parent
 * search -- which is the only direction the upper-bound proof uses.
 *
 * WHAT THIS CHANGES IN THE OUTPUT.  Node, leaf and found counts are all SMALLER than the parent
 * search's, because isomorphic copies are no longer walked.  They are therefore NOT comparable to
 * the recorded counts, and calibration must compare the decision (found = 0 or found > 0) rather
 * than the tallies.  A build of this file that fails to reproduce D_2(C_3^3) = 11,
 * D_2(C_3^4) = 14 and D_2(C_3^5) = 17 from BOTH sides must not be used for anything.
 *
 * Usage: enum_rank_sym p r L s [--progress] [--shard i n] [--nosym] [--colmajor]
 *                             [--maxnodes N] [--maxsecs S]
 *
 *   --maxnodes caps NODES.  It does not bound runtime: at rank 7 a single leaf costs
 *   O(L*N^2) ~ 1e9 byte-ops, so a 5000-node cap can still run for minutes.  Use
 *   --maxsecs to bound a timing sample by the clock.  Either cap marks the RESULT line
 *   TRUNCATED, and collect.py refuses a verdict from a truncated run.
 *   --nosym disables the orbit prune, recovering the parent search exactly.  Keep it: it is how
 *   the speedup is measured and how a suspected soundness bug is bisected.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>
#define USAGE "usage: %s p r L s [--progress] [--shard i n] [--nosym] [--colmajor]" \
              " [--maxnodes N] [--maxsecs S]\n"
static int p, r, L, s, N;
static int *addtab;
static int *negv;
static unsigned char *forbbuf;
static unsigned char *reach;
static int *seq;
static long long nodes=0, leaves=0, found=0, pruned_sym=0;
static int progress=0, SHARD=-1, NSHARD=1, nosym=0, colmajor=0;
static long long maxnodes=0;   /* 0 = unlimited; otherwise stop and mark the run truncated */
static double maxsecs=0;       /* 0 = unlimited; a WALL-CLOCK cap, which --maxnodes is not */
static int truncated=0;
static const char *trunc_why="";
static struct timespec t_start;
static inline double elapsed(void){
    struct timespec now; clock_gettime(CLOCK_MONOTONIC,&now);
    return (double)(now.tv_sec-t_start.tv_sec) + 1e-9*(double)(now.tv_nsec-t_start.tv_nsec);
}
static inline unsigned char *R(int d,int l){ return reach + ((size_t)d*(s+1)+l)*N; }

/* ---- basis stabiliser: the C(r,2) coordinate transpositions, as tables on element indices ---- */
static int NTR=0;
static int **tr;                 /* tr[k][g] = image of element g under the k-th transposition */
static int tailbuf[64];

static void build_transpositions(void){
    NTR = r*(r-1)/2;
    tr = malloc(sizeof(int*)*(size_t)NTR);
    int k=0;
    for(int i=0;i<r;i++) for(int j=i+1;j<r;j++,k++){
        tr[k]=malloc(sizeof(int)*(size_t)N);
        for(int g=0; g<N; g++){
            int dig[16], t=g;
            for(int c=0;c<r;c++){ dig[c]=t%p; t/=p; }
            int tmp=dig[i]; dig[i]=dig[j]; dig[j]=tmp;
            int x=0,pw=1;
            for(int c=0;c<r;c++){ x+=dig[c]*pw; pw*=p; }
            tr[k][g]=x;
        }
    }
}

/* True when some transposition maps the tail to a lexicographically smaller sorted tail, i.e.
 * when this node cannot be a prefix of the lex-least representative of its orbit. */
static int not_canonical(int d){
    int m = d - r;
    if(m < 2) return 0;                       /* a single term is fixed by sorting */
    for(int k=0;k<NTR;k++){
        const int *T = tr[k];
        /* insertion sort of the image, aborting as soon as the comparison is decided */
        for(int a=0;a<m;a++){
            int v = T[seq[r+a]], b = a;
            while(b>0 && tailbuf[b-1]>v){ tailbuf[b]=tailbuf[b-1]; b--; }
            tailbuf[b]=v;
        }
        for(int a=0;a<m;a++){
            if(tailbuf[a] < seq[r+a]) return 1;
            if(tailbuf[a] > seq[r+a]) break;
        }
    }
    return 0;
}

static unsigned char *lay[4], *nl[4];
static int two_disjoint(void){
    size_t sz=(size_t)N*N;
    for(int i=0;i<4;i++){ memset(lay[i],0,sz); }
    lay[0][0]=1;
    for(int t=0;t<L;t++){
        int g=seq[t];
        for(int i=0;i<4;i++) memcpy(nl[i],lay[i],sz);
        const int *rg = addtab + (size_t)g*N;    /* symmetric: row g == column g */
        for(int a=0;a<N;a++){ const size_t ag=(size_t)rg[a]*N;
          for(int b=0;b<N;b++){
            size_t ix=(size_t)a*N+b;
            if(lay[0][ix]){ nl[1][ag+b]=1; nl[2][(size_t)a*N+rg[b]]=1; }
            if(lay[1][ix]){ nl[1][ag+b]=1; nl[3][(size_t)a*N+rg[b]]=1; }
            if(lay[2][ix]){ nl[2][(size_t)a*N+rg[b]]=1; nl[3][ag+b]=1; }
            if(lay[3][ix]){ nl[3][ag+b]=1; nl[3][(size_t)a*N+rg[b]]=1; }
          }
        }
        for(int i=0;i<4;i++) memcpy(lay[i],nl[i],sz);
        if(lay[3][0]) return 1;
    }
    return lay[3][0];
}

static void dfs(int d,int lo){
    if(truncated) return;
    nodes++;
    if(maxnodes && nodes>=maxnodes){ truncated=1; trunc_why="--maxnodes"; return; }
    /* A node cap does NOT bound runtime: cost is dominated by two_disjoint() at the
     * leaves, which is O(L*N^2) each.  Check the clock every 256 nodes as well. */
    if(maxsecs && (nodes & 0x3F)==0 && elapsed() >= maxsecs){
        truncated=1; trunc_why="--maxsecs"; return; }
    if(!nosym && d>r && not_canonical(d)){ pruned_sym++; return; }
    unsigned char *forb = forbbuf + (size_t)d*N;
    if(d<L){
        memcpy(forb,R(d,0),N);
        for(int l=1;l<=s-1;l++){ unsigned char *src=R(d,l);
            for(int x=0;x<N;x++) forb[x]|=src[x]; }
    }
    if(progress && (nodes&0xFFFFF)==0)
        fprintf(stderr,"progress nodes=%lld leaves=%lld found=%lld sympruned=%lld d=%d\n",
                nodes,leaves,found,pruned_sym,d);
    if(d==L){
        if(maxsecs && elapsed() >= maxsecs){ truncated=1; trunc_why="--maxsecs"; return; }
        leaves++;
        if(!two_disjoint()){ found++; printf("packing<=1:");
            for(int i=0;i<L;i++) printf(" %d",seq[i]); printf("\n"); fflush(stdout); }
        return; }
    for(int g=lo; g<N; g++){
        if(g==0) continue;
        if(SHARD>=0 && d==r && g%NSHARD!=SHARD) continue;
        if(forb[negv[g]]) continue;
        unsigned char *dst=R(d+1,0); memcpy(dst,R(d,0),(size_t)(s+1)*N);
        const int *rowg = addtab + (size_t)g*N;   /* addtab is symmetric: row g == column g */
        for(int l=s;l>=1;l--){
            unsigned char *from=R(d,l-1), *to=R(d+1,l);
            if(colmajor){ for(int x=0;x<N;x++) if(from[x]) to[addtab[(size_t)x*N+g]]=1; }
            else        { for(int x=0;x<N;x++) if(from[x]) to[rowg[x]]=1; }
        }
        seq[d]=g; dfs(d+1,g);
    }
}

int main(int argc,char**argv){
    if(argc<5){ fprintf(stderr,USAGE,argv[0]); return 2; }
    p=atoi(argv[1]); r=atoi(argv[2]); L=atoi(argv[3]); s=atoi(argv[4]);
    /* An unrecognised flag is a hard error.  It used to fall through this chain unnoticed, so
     * `--maxnodes` against a build without it ran the FULL tree while looking capped. */
    for(int i=5;i<argc;i++){
        if(!strcmp(argv[i],"--progress")) progress=1;
        else if(!strcmp(argv[i],"--nosym")) nosym=1;
        else if(!strcmp(argv[i],"--colmajor")) colmajor=1;
        else if(!strcmp(argv[i],"--shard")){
            if(i+2>=argc){ fprintf(stderr,"FATAL: --shard needs two values: i n\n"); return 2; }
            SHARD=atoi(argv[i+1]); NSHARD=atoi(argv[i+2]); i+=2; }
        else if(!strcmp(argv[i],"--maxnodes")){
            if(i+1>=argc){ fprintf(stderr,"FATAL: --maxnodes needs a value\n"); return 2; }
            maxnodes=atoll(argv[++i]);
            if(maxnodes<=0){ fprintf(stderr,"FATAL: --maxnodes must be positive\n"); return 2; } }
        else if(!strcmp(argv[i],"--maxsecs")){
            if(i+1>=argc){ fprintf(stderr,"FATAL: --maxsecs needs a value\n"); return 2; }
            maxsecs=atof(argv[++i]);
            if(maxsecs<=0){ fprintf(stderr,"FATAL: --maxsecs must be positive\n"); return 2; } }
        else { fprintf(stderr,"FATAL: unrecognised argument \"%s\"\n",argv[i]);
               fprintf(stderr,USAGE,argv[0]); return 2; }
    }
    if(SHARD>=0 && (NSHARD<=0 || SHARD>=NSHARD)){
        fprintf(stderr,"FATAL: --shard %d %d is out of range\n",SHARD,NSHARD); return 2; }
    if(r>16){ fprintf(stderr,"FATAL: r>16 exceeds the digit buffer\n"); return 3; }
    if(L-r>64){ fprintf(stderr,"FATAL: tail longer than the canonicity buffer\n"); return 3; }
    N=1; for(int i=0;i<r;i++) N*=p;
    addtab=malloc(sizeof(int)*(size_t)N*N);
    for(int a=0;a<N;a++) for(int b=0;b<N;b++){ int x=0,pw=1,aa=a,bb=b;
        for(int i=0;i<r;i++){ x+=((aa%p+bb%p)%p)*pw; aa/=p; bb/=p; pw*=p; } addtab[a*N+b]=x; }
    forbbuf=malloc((size_t)(L+1)*N);
    negv=malloc(sizeof(int)*N);
    for(int g=0;g<N;g++){ int t=g,n=0,pw=1;
        for(int i=0;i<r;i++){ n+=((p-(t%p))%p)*pw; t/=p; pw*=p; } negv[g]=n; }
    reach=calloc((size_t)(L+1)*(s+1)*N,1); seq=malloc(sizeof(int)*L);
    for(int i=0;i<4;i++){ lay[i]=malloc((size_t)N*N); nl[i]=malloc((size_t)N*N); }
    build_transpositions();
    R(0,0)[0]=1;
    int d=0,pw=1;
    for(int i=0;i<r;i++){ int g=pw; pw*=p;
        memcpy(R(d+1,0),R(d,0),(size_t)(s+1)*N);
        const int *rowg = addtab + (size_t)g*N;
        for(int l=s;l>=1;l--){ unsigned char*from=R(d,l-1),*to=R(d+1,l);
            for(int x=0;x<N;x++) if(from[x]) to[rowg[x]]=1; }
        seq[d]=g; d++; }
    printf("p=%d r=%d L=%d s=%d N=%d sym=%s transpositions=%d\n",p,r,L,s,N,nosym?"off":"on",NTR);
    clock_gettime(CLOCK_MONOTONIC,&t_start);
    dfs(r,1);
    printf("DONE nodes=%lld leaves=%lld found=%lld sympruned=%lld\n",nodes,leaves,found,pruned_sym);
    printf("RESULT p=%d r=%d L=%d s=%d shard=%d/%d sym=%d found=%lld leaves=%lld nodes=%lld%s\n",
           p,r,L,s,SHARD,NSHARD,!nosym,found,leaves,nodes, truncated?" TRUNCATED":"");
    if(truncated) fprintf(stderr,"WARNING: stopped at the %s cap. This run proves NOTHING;\n"
                                 "it is a timing sample only, and collect.py rejects it.\n",trunc_why);
    return 0;
}
