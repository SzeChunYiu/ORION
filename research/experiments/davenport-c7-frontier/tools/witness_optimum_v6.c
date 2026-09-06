/* witness_optimum_v6.c — maximise sum(m_A) over families of vectors in Z_p^r subject to
 * the witness-coordinate criterion, i.e. compute the best lower-bound construction
 *      S = prod_i e_i^{p-1} * prod_A v_A^{m_A},   |S| = r(p-1) + sum m_A,  z(S) = 1.
 * Criterion: every pair b,b' != 0 with b+b' <= m has a coordinate i with
 *      <(Mb)_i> != 0, <(Mb')_i> != 0, <(Mb)_i> + <(Mb')_i> <= p.
 * The criterion is downward closed in m, so DFS with immediate pruning explores
 * exactly the feasible families.  Bitmask per residue value => pair test is O(p^2).
 * Usage: witness_optimum p r [--all-vectors] */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define MAXR 12   /* coordinate-dimension bound: sizes anything indexed by a coordinate i<r */
#define MAXP 16   /* residue bound: msk's second index is a RESIDUE load%p, not a coordinate  */
static int p, r, NV, ALL=0, CAP=24, MINSZ=0;
static int (*vec)[MAXR];             /* sized to the actual vector count, not a fixed 2048 */
static int chosen[16], mult[16], nc, best, bestc[16], bestm[16], bestn;
#ifndef BOXCAP
#define BOXCAP 100000  /* max points in the multiplicity box; overflow is fatal, never silent */
#endif
static int boxb[BOXCAP][16], nbox;
static unsigned int msk[BOXCAP][MAXP];      /* msk[b][v] = coords whose load residue is v */

static void build_box(void){
    nbox=0;
    int b[16]; memset(b,0,sizeof b);
    while(1){
        int any=0; for(int i=0;i<nc;i++) if(b[i]) any=1;
        if(any){
            int load[MAXR]; for(int i=0;i<r;i++) load[i]=0;
            for(int a=0;a<nc;a++) if(b[a]) for(int i=0;i<r;i++) load[i]+=b[a]*vec[chosen[a]][i];
            for(int v=0;v<p;v++) msk[nbox][v]=0;
            for(int i=0;i<r;i++) msk[nbox][load[i]%p] |= 1u<<i;
            memcpy(boxb[nbox],b,sizeof(int)*nc);
            /* The box must fit entirely: a truncated box makes feasible() test only some
             * of the pairs, which can return a false FEASIBLE and silently OVERREPORT M*.
             * Never truncate quietly -- abort so the caller sees it. */
            if(++nbox>=BOXCAP){
                fprintf(stderr,"FATAL: box exceeded BOXCAP=%d at nc=%d (sum m too large for "
                        "this build); M* would be overreported.  Raise BOXCAP and rerun.\n",
                        BOXCAP, nc);
                exit(3);
            }
        }
        int i=0; while(i<nc){ if(++b[i]<=mult[i]) break; b[i]=0; i++; }
        if(i==nc) break;
    }
}
static int feasible(void){
    build_box();
    for(int x=0;x<nbox;x++) for(int y=x;y<nbox;y++){
        int ok=1;
        for(int a=0;a<nc;a++) if(boxb[x][a]+boxb[y][a]>mult[a]){ ok=0; break; }
        if(!ok) continue;
        int wit=0;
        for(int u=1;u<p && !wit;u++) for(int w=1;u+w<=p && !wit;w++)
            if(msk[x][u] & msk[y][w]) wit=1;
        if(!wit) return 0;
    }
    return 1;
}
static void dfs(int start,int tot){
    if(tot>best){ best=tot; bestn=nc; memcpy(bestc,chosen,sizeof chosen); memcpy(bestm,mult,sizeof mult); }
    if(nc>=16 || tot>=CAP) return;
    for(int v=start; v<NV; v++){
        chosen[nc]=v;
        for(int m=1;m<=p;m++){
            if(tot+m>CAP) break;
            mult[nc]=m; nc++;
            int ok=feasible();
            nc--;
            if(!ok) break;                       /* downward closed in m */
            nc++; dfs(v+1,tot+m); nc--;
        }
    }
}
int main(int argc,char**argv){
    p=atoi(argv[1]); r=atoi(argv[2]);
    for(int i=3;i<argc;i++){ if(!strcmp(argv[i],"--all-vectors")) ALL=1;
        else if(!strcmp(argv[i],"--minsize")) MINSZ=atoi(argv[i+1]); }
    if(r<1||r>MAXR){ fprintf(stderr,"r must be in 1..%d\n",MAXR); return 2; }
    if(p<2||p>MAXP){ fprintf(stderr,"p must be in 2..%d\n",MAXP); return 2; }
    long want=1; for(int i=0;i<r;i++){ want*= ALL?p:2; }   /* p^r or 2^r, minus the zero vector */
    vec=malloc(sizeof(*vec)*(size_t)want);
    if(!vec){ fprintf(stderr,"oom allocating %ld vectors\n",want); return 2; }
    NV=0;
    if(ALL){ int T=1; for(int i=0;i<r;i++) T*=p;
        for(int g=1;g<T;g++){ int t=g; for(int d=0;d<r;d++){ vec[NV][d]=t%p; t/=p; } NV++; } }
    else for(int s=1;s<(1<<r);s++){ int pc=0; for(int d=0;d<r;d++) pc+=(s>>d)&1;
        if(pc<MINSZ) continue;
        for(int d=0;d<r;d++) vec[NV][d]=(s>>d)&1; NV++; }
    best=0; nc=0;
    dfs(0,0);
    printf("p=%d r=%d %s minsize=%d: max sum m = %d  =>  |S| = r(p-1)+m = %d  =>  D_2(C_%d^%d) >= %d\n",
           p,r, ALL?"[all vectors]":"[0/1 indicators]", MINSZ, best, r*(p-1)+best, p, r, r*(p-1)+best+1);
    printf("   optimal family:");
    for(int i=0;i<bestn;i++){ printf(" ("); for(int d=0;d<r;d++) printf("%d",vec[bestc[i]][d]);
        printf(")^%d",bestm[i]); }
    printf("\n");
    return 0;
}
