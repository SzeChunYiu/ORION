/* enum2.c — exhaustive enumeration of multisets S over F_p^3 \ {0}:
 *   |S| = L, multiplicities <= cap, no zero-sum sub-multiset of size in [1,s],
 *   optional zero-sum requirement, plane-count cap, GL(3,p) symmetry breaking
 *   (e1,e2,e3 in supp(S); m(e1) = max mult; m(e2) = max mult off <e1>; m(e3) = max mult off <e1,e2>).
 *   Pruning: availability bound sum_{v>=i} c_v >= L - total, where c_v = max further copies of v
 *   addable without creating a zero-sum of size <= s.
 *   Leaf: exact zero-sum packing number via atom recursion (no box); print leaves with packing <= kmax.
 * Usage: enum2 p L cap s kmax [--zerosum] [--planecap C] [--count-only] [--progress]
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define MAXS 40
static int p, L, cap, s, kmax, need_zs=0, planecap=1000000, count_only=0, G, m1lo=1, m1hi=1000, zsfree=0, descending=0, reverse_order=0;
static int NP; static int PX[400][3]; static int enc[400]; static int cls[400];
static int negt[8][400];  /* code of -t*v */
static int addtab[343][343];
static int planes_of[400][16]; static int nplanes; static int planecnt[60];
static int mult[400];
static uint64_t Sig[MAXS+1][6], Uni[MAXS+1][6]; /* Sig[j]: sums of size-j subs; Uni[j] = union_{i<=j} Sig[i] */
static long long leaves=0, found=0, nodes=0; static int progress=0;
static inline void bs_set(uint64_t *b, int i){ b[i>>6] |= 1ULL<<(i&63); }
static inline int bs_get(const uint64_t *b, int i){ return (b[i>>6]>>(i&63))&1; }

/* ---------- leaf packing via atoms recursion ---------- */
static int sp[64], sm[64], ns;
static int leaf_zs_count;
/* enumerate zero-sum subvectors of current leaf (restricted to b <= r) and test packing recursively */
static int has_zero_sum(const int *r){ /* does multiset r have a nonempty zero-sum sub? bitset subset-sum DP */
    uint64_t reach[6]; memset(reach,0,sizeof(reach)); bs_set(reach,0);
    for(int i=0;i<ns;i++) for(int t=0;t<r[i];t++){ uint64_t nr[6]; memcpy(nr,reach,sizeof(nr));
        for(int w=0;w<6;w++){ uint64_t bits=reach[w]; while(bits){ int b=__builtin_ctzll(bits); bits&=bits-1; int x=w*64+b; bs_set(nr, addtab[x][enc[sp[i]]]); } }
        memcpy(reach,nr,sizeof(nr)); }
    /* 0 is trivially reachable (empty); need nonempty: check whether some element v with -v reachable using others... simpler: DP counting sizes */
    /* redo: track reach without the empty set: reachN = sums of nonempty subs */
    uint64_t rn[6]; memset(rn,0,sizeof(rn));
    for(int i=0;i<ns;i++) for(int t=0;t<r[i];t++){ uint64_t nr[6]; memcpy(nr,rn,sizeof(nr));
        for(int w=0;w<6;w++){ uint64_t bits=rn[w]; while(bits){ int b=__builtin_ctzll(bits); bits&=bits-1; int x=w*64+b; bs_set(nr, addtab[x][enc[sp[i]]]); } }
        bs_set(nr, enc[sp[i]]); memcpy(rn,nr,sizeof(nr)); }
    return bs_get(rn,0);
}
static int pack_rec(int *r, int t, int minlen);
static int bvec[64];
static int dfs_block(int *r, int i, int cnt, int code, int t, int minlen, int maxlen){
    /* choose bvec[i..] <= r[i..], nonempty, sum zero, size in [minlen,maxlen]; then recurse pack on r-b */
    if(i==ns){
        if(cnt<minlen || code!=0) return 0;
        int rr[64]; for(int q=0;q<ns;q++) rr[q]=r[q]-bvec[q];
        return pack_rec(rr, t-1, cnt);
    }
    int rem=0; for(int q=i;q<ns;q++) rem+=r[q]; if(cnt+rem<minlen) return 0;
    for(int c=0;c<=r[i] && cnt+c<=maxlen;c++){ bvec[i]=c; int nc=code; for(int q=0;q<c;q++) nc=addtab[nc][enc[sp[i]]]; if(dfs_block(r,i+1,cnt+c,nc,t,minlen,maxlen)) { bvec[i]=0; return 1; } }
    bvec[i]=0; return 0;
}
static int pack_rec(int *r, int t, int minlen){
    /* does multiset r contain t pairwise disjoint nonempty zero-sum subs, with blocks of size >= minlen (blocks chosen in nondecreasing size WLOG) */
    if(t==0) return 1;
    int tot=0; for(int q=0;q<ns;q++) tot+=r[q];
    if(tot < t*minlen) return 0;
    if(t==1){ return has_zero_sum(r); }
    int maxlen = tot / t; /* smallest block has size <= tot/t */
    int save[64]; memcpy(save,bvec,sizeof(int)*ns); memset(bvec,0,sizeof(int)*ns);
    int res=dfs_block(r,0,0,0,t,minlen,maxlen);
    memcpy(bvec,save,sizeof(int)*ns);
    return res;
}
static int packing_number(void){
    ns=0; for(int i=0;i<NP;i++) if(mult[i]){ sp[ns]=i; sm[ns]=mult[i]; ns++; }
    int r[64]; memcpy(r,sm,sizeof(int)*ns);
    int k=0; while(k<=kmax && pack_rec(r,k+1,1)) k++;  /* returns kmax+1 if packing > kmax */
    return k;
}
static void print_leaf(int pk){
    printf("packing=%d len=%d supp=%d :", pk, L, ns);
    for(int i=0;i<NP;i++) if(mult[i]) printf(" (%d,%d,%d)^%d", PX[i][0],PX[i][1],PX[i][2],mult[i]);
    printf("\n"); fflush(stdout);
}
/* ---------- DFS ---------- */
static int total=0;
static int cur_i=0; /* current DFS index: mults of points >= cur_i are unassigned */
static int capfor(int i){
    int cmax=cap;
    if(i==1){ if(cur_i>0 && mult[0]<cmax) cmax=mult[0]; }
    else if(i==2){ if(cur_i>1 && mult[1]<cmax) cmax=mult[1]; }
    else if(i>2){ int c=cls[i]; int ref=(c==0)?0:(c==1)?1:2; if(cur_i>ref && mult[ref]<cmax) cmax=mult[ref]; }
    return cmax;
}
static int avail_copies(int v, int cmax){
    /* max t<=cmax such that for all t'<=t: -t'v not in Uni[s-t'] (for s-t'>=0) */
    int t=0;
    while(t<cmax){ int tp=t+1; int j=s-tp; if(j>=0 && bs_get(Uni[j], negt[tp][v])) break; t=tp; }
    return t;
}
static void dfs(int i){
    nodes++; if(progress && (nodes&((1LL<<26)-1))==0){ fprintf(stderr,"progress nodes=%lld leaves=%lld found=%lld m123=%d,%d,%d\n",nodes,leaves,found,mult[0],mult[1],mult[2]); }
    if(total==L){
        leaves++;
        if(need_zs){ int c=0; for(int j=0;j<NP;j++) for(int t=0;t<mult[j];t++) c=addtab[c][enc[j]]; if(c!=0) return; }
        if(count_only){ found++; return; }
        if(zsfree){ found++; ns=0; for(int i=0;i<NP;i++) if(mult[i]) ns++; print_leaf(0); return; }
        int pk=packing_number();
        if(pk<=kmax){ found++; print_leaf(pk); }
        return;
    }
    if(i==NP) return;
    cur_i=i;
    /* availability bound */
    { long need=L-total, have=0; for(int v=i; v<NP && have<need; v++){ int c=capfor(v); if(c>0) have+=avail_copies(v,c); } if(have<need) return; }
    int cmax=capfor(i);
    if(cmax > L-total) cmax=L-total;
    if(i<3 && cmax<1) return;
    int mlo=1; if(i==0){ if(cmax>m1hi) cmax=m1hi; mlo=m1lo; }
    uint64_t saveS[MAXS+1][6], saveU[MAXS+1][6]; memcpy(saveS,Sig,sizeof(Sig)); memcpy(saveU,Uni,sizeof(Uni));
    if(i>=3 && !descending){ mult[i]=0; dfs(i+1); cur_i=i; }
    /* precompute Sig/Uni states for m=1..cmax (stop at first bad) */
    static uint64_t stS[400][7][MAXS+1][6], stU[400][7][MAXS+1][6]; int mmax=0;
    for(int m=1;m<=cmax;m++){
        int bad=0;
        for(int j=s;j>=1;j--){
            for(int w=0;w<6;w++){ uint64_t bits=Sig[j-1][w]; while(bits){ int b=__builtin_ctzll(bits); bits&=bits-1; int x=w*64+b; bs_set(Sig[j], addtab[x][enc[i]]); } }
            if(bs_get(Sig[j],0)) { bad=1; break; }
        }
        if(bad) break;
        for(int j=1;j<=s;j++) for(int w=0;w<6;w++) Uni[j][w]=Uni[j-1][w]|Sig[j][w];
        memcpy(stS[i][m],Sig,sizeof(Sig)); memcpy(stU[i][m],Uni,sizeof(Uni)); mmax=m;
    }
    for(int q=0;q<mmax;q++){
        int m = descending ? (mmax-q) : (q+1);
        if(m<mlo) continue;
        memcpy(Sig,stS[i][m],sizeof(Sig)); memcpy(Uni,stU[i][m],sizeof(Uni));
        mult[i]=m; total+=m;
        int planebad=0; for(int t=0;t<m;t++) for(int qq=0;planes_of[i][qq]>=0;qq++){ planecnt[planes_of[i][qq]]++; if(planecnt[planes_of[i][qq]]>planecap) planebad=1; }
        if(!planebad) dfs(i+1);
        cur_i=i;
        for(int t=0;t<m;t++) for(int qq=0;planes_of[i][qq]>=0;qq++) planecnt[planes_of[i][qq]]--;
        total-=m; mult[i]=0;
        if(planebad && !descending) break;
    }
    memcpy(Sig,saveS,sizeof(Sig)); memcpy(Uni,saveU,sizeof(Uni));
    if(i>=3 && descending){ mult[i]=0; dfs(i+1); cur_i=i; }
}
int main(int argc,char**argv){
    if(argc<6){fprintf(stderr,"usage: enum2 p L cap s kmax [--zerosum] [--planecap C] [--count-only] [--progress]\n");return 2;}
    p=atoi(argv[1]); L=atoi(argv[2]); cap=atoi(argv[3]); s=atoi(argv[4]); kmax=atoi(argv[5]);
    for(int a=6;a<argc;a++){ if(!strcmp(argv[a],"--zerosum")) need_zs=1; else if(!strcmp(argv[a],"--planecap")) planecap=atoi(argv[++a]); else if(!strcmp(argv[a],"--count-only")) count_only=1; else if(!strcmp(argv[a],"--progress")) progress=1; else if(!strcmp(argv[a],"--m1")){ m1lo=atoi(argv[++a]); m1hi=atoi(argv[++a]); } else if(!strcmp(argv[a],"--zsfree")) zsfree=1; else if(!strcmp(argv[a],"--descending")) descending=1; else if(!strcmp(argv[a],"--reverse")) reverse_order=1; }
    if(s>MAXS-1){fprintf(stderr,"s too large\n");return 2;}
    NP=0; int e[3][3]={{1,0,0},{0,1,0},{0,0,1}};
    for(int k=0;k<3;k++){ PX[NP][0]=e[k][0];PX[NP][1]=e[k][1];PX[NP][2]=e[k][2]; NP++; }
    for(int x=0;x<p;x++)for(int y=0;y<p;y++)for(int z=0;z<p;z++){ if(!x&&!y&&!z) continue; if((x==1&&!y&&!z)||(!x&&y==1&&!z)||(!x&&!y&&z==1)) continue; PX[NP][0]=x;PX[NP][1]=y;PX[NP][2]=z; NP++; }
    if(reverse_order){ for(int i=3,j=NP-1;i<j;i++,j--){ int t0=PX[i][0],t1=PX[i][1],t2=PX[i][2]; PX[i][0]=PX[j][0];PX[i][1]=PX[j][1];PX[i][2]=PX[j][2]; PX[j][0]=t0;PX[j][1]=t1;PX[j][2]=t2; } }
    G=p*p*p;
    for(int i=0;i<NP;i++){ enc[i]=PX[i][0]*p*p+PX[i][1]*p+PX[i][2]; cls[i]=(PX[i][1]==0&&PX[i][2]==0)?0:(PX[i][2]==0)?1:2; }
    for(int a=0;a<G;a++)for(int b=0;b<G;b++){ int ax=a/(p*p),ay=(a/p)%p,az=a%p, bx=b/(p*p),by=(b/p)%p,bz=b%p; addtab[a][b]=((ax+bx)%p)*p*p+((ay+by)%p)*p+((az+bz)%p); }
    for(int t=0;t<8;t++)for(int i=0;i<NP;i++){ int x=((p-(t*PX[i][0])%p)%p), y=((p-(t*PX[i][1])%p)%p), z=((p-(t*PX[i][2])%p)%p); negt[t][i]=x*p*p+y*p+z; }
    nplanes=0; int normals[60][3];
    for(int x=0;x<p;x++)for(int y=0;y<p;y++)for(int z=0;z<p;z++){ if(!x&&!y&&!z)continue; int first=x?x:(y?y:z); if(first!=1) continue; normals[nplanes][0]=x;normals[nplanes][1]=y;normals[nplanes][2]=z;nplanes++; }
    for(int i=0;i<NP;i++){ int q=0; for(int h=0;h<nplanes;h++){ if((normals[h][0]*PX[i][0]+normals[h][1]*PX[i][1]+normals[h][2]*PX[i][2])%p==0) planes_of[i][q++]=h; } planes_of[i][q]=-1; }
    memset(Sig,0,sizeof(Sig)); memset(Uni,0,sizeof(Uni)); bs_set(Sig[0],0); for(int j=0;j<=s;j++) bs_set(Uni[j],0);
    dfs(0);
    fprintf(stderr,"nodes=%lld leaves=%lld found=%lld\n",nodes,leaves,found);
    return 0;
}
