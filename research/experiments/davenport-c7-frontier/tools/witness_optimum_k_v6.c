/* witness_optimum_k_v6.c — the witness criterion for general packing number.
 *
 * THEOREM W_t.  For S = prod_i e_i^{p-1} * prod_A v_A^{m_A},
 *      z(S) >= t  <=>  there are b^(1..t) != 0 with sum_j b^(j) <= m and
 *                      sum_j <-(M b^(j))_i>  <=  p-1   for every coordinate i.
 * (t = 2 is Theorem W: two blocks are disjoint iff their e-parts add with no carry.)
 * So  D_k(C_p^r) >= r(p-1) + M*_k(r,p) + 1,  where M*_k maximises sum m_A subject to
 * there being no t = k such tuple.
 * Usage: witness_optimum_k p r k [--minsize s] [--cap c] */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static int p,r,K,NV,MINSZ=0,CAP=24;
static int vec[4096][10];
static int chosen[20],mult[20],nc,best,bestc[20],bestm[20],bestn;
/* box of b-vectors */
static int nbox; static int (*boxb)[20]; static unsigned char (*A)[10];
static void build_box(void){
    nbox=0; int b[20]; memset(b,0,sizeof b);
    while(1){
        int any=0; for(int i=0;i<nc;i++) if(b[i]) any=1;
        if(any){
            memcpy(boxb[nbox],b,sizeof(int)*nc);
            for(int i=0;i<r;i++){
                int c=0; for(int a=0;a<nc;a++) c+=b[a]*vec[chosen[a]][i];
                c%=p; A[nbox][i] = c? (p-c) : 0;      /* <-c_i> */
            }
            nbox++;
        }
        int i=0; while(i<nc){ if(++b[i]<=mult[i]) break; b[i]=0; i++; }
        if(i==nc) break;
    }
}
static int rem[20], acc[10];
static int find_tuple(int depth,int start){
    if(depth==K) return 1;                       /* K disjoint blocks, no carry */
    for(int x=start;x<nbox;x++){
        int ok=1;
        for(int a=0;a<nc && ok;a++) if(boxb[x][a]>rem[a]) ok=0;
        if(!ok) continue;
        for(int i=0;i<r && ok;i++) if(acc[i]+A[x][i] > p-1) ok=0;
        if(!ok) continue;
        for(int a=0;a<nc;a++) rem[a]-=boxb[x][a];
        for(int i=0;i<r;i++) acc[i]+=A[x][i];
        int got=find_tuple(depth+1,x);           /* x reusable: blocks may repeat as vectors */
        for(int a=0;a<nc;a++) rem[a]+=boxb[x][a];
        for(int i=0;i<r;i++) acc[i]-=A[x][i];
        if(got) return 1;
    }
    return 0;
}
static int feasible(void){
    build_box();
    for(int a=0;a<nc;a++) rem[a]=mult[a];
    memset(acc,0,sizeof acc);
    return !find_tuple(0,0);
}
static void dfs(int start,int tot){
    if(tot>best){ best=tot; bestn=nc; memcpy(bestc,chosen,sizeof chosen); memcpy(bestm,mult,sizeof mult); }
    if(nc>=20 || tot>=CAP) return;
    for(int v=start;v<NV;v++){
        chosen[nc]=v;
        for(int m=1;m<=p;m++){
            if(tot+m>CAP) break;
            mult[nc]=m; nc++;
            int ok=feasible(); nc--;
            if(!ok) break;
            nc++; dfs(v+1,tot+m); nc--;
        }
    }
}
int main(int argc,char**argv){
    p=atoi(argv[1]); r=atoi(argv[2]); K=atoi(argv[3]);
    for(int i=4;i<argc;i++){ if(!strcmp(argv[i],"--minsize")) MINSZ=atoi(argv[i+1]);
                             else if(!strcmp(argv[i],"--cap")) CAP=atoi(argv[i+1]); }
    for(int s=1;s<(1<<r);s++){ int pc=0; for(int d=0;d<r;d++) pc+=(s>>d)&1;
        if(pc<MINSZ) continue;
        for(int d=0;d<r;d++) vec[NV][d]=(s>>d)&1; NV++; }
    long cap=1; for(int i=0;i<20;i++){ cap*= (p+1); if(cap>4000000) break; }
    boxb=malloc(sizeof(int)*20*4000000L); A=malloc(10L*4000000L);
    if(!boxb||!A){ fprintf(stderr,"oom\n"); return 2; }
    best=0; nc=0; dfs(0,0);
    printf("p=%d r=%d k=%d: M*_k = %d  =>  |S| = %d  =>  D_%d(C_%d^%d) >= %d\n",
           p,r,K,best, r*(p-1)+best, K,p,r, r*(p-1)+best+1);
    printf("   family:");
    for(int i=0;i<bestn;i++){ printf(" ("); for(int d=0;d<r;d++) printf("%d",vec[bestc[i]][d]); printf(")^%d",bestm[i]); }
    printf("\n");
    return 0;
}
