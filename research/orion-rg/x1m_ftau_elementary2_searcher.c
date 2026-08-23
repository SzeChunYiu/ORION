/* f_T(C_2^r), r<=6 : max-size subset of F_2^r\{0} with no zero-sum of size <= T.
   reach[j] = bitmask over 0..63 of values expressible as XOR of exactly j chosen elts.
   Adding v is legal iff v not in reach[0..T-1]. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef unsigned long long u64;
static u64 MLO[6],MHI[6];
static void initmask(void){
    for(int i=0;i<6;i++){ int b=1<<i; u64 lo=0;
        for(int x=0;x<64;x++) if(!((x>>i)&1)) lo|=1ULL<<x;
        MLO[i]=lo; MHI[i]=~lo; (void)b; }
}
/* permute bitmask by XOR with v */
static inline u64 xsh(u64 m,int v){
    for(int i=0;i<6;i++) if((v>>i)&1){ int s=1<<i; m=((m&MLO[i])<<s)|((m&MHI[i])>>s); }
    return m;
}
static int R,N,T,best,bestset[64],cur[64];
static void rec(int k,u64*reach,int*cand,int nc){
    if(k>best){ best=k; memcpy(bestset,cur,k*sizeof(int));
        printf("BEST %d :",k); for(int i=0;i<k;i++)printf(" %d",cur[i]); printf("\n"); fflush(stdout); }
    if(k+nc<=best) return;
    u64 nr[8]; int nx[64];
    for(int ci=0;ci<nc;ci++){
        if(k+(nc-ci)<=best) return;
        int v=cand[ci];
        /* extend reach */
        for(int j=T;j>=1;j--) nr[j]=reach[j]|xsh(reach[j-1],v);
        nr[0]=reach[0];
        /* filter remaining candidates */
        int m2=0;
        for(int cj=ci+1;cj<nc;cj++){ int c=cand[cj]; int ok=1;
            for(int j=0;j<T;j++) if((nr[j]>>c)&1){ ok=0;break; }
            if(ok) nx[m2++]=c; }
        cur[k]=v; rec(k+1,nr,nx,m2);
    }
}
int main(int argc,char**argv){
    initmask(); R=atoi(argv[1]); T=atoi(argv[2]); N=(1<<R)-1; best=0;
    u64 reach[8]; memset(reach,0,sizeof(reach)); reach[0]=1ULL; /* {0} */
    int cand[64],nc=0; for(int v=1;v<=N;v++) cand[nc++]=v;
    rec(0,reach,cand,nc);
    printf("f_%d(C_2^%d) = %d\n",T,R,best); return 0;
}
