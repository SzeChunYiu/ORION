/* f_T(C_n^2) for n^2<=64 : max length sequence (repeats allowed) over C_n^2\{0}
   with no nonempty zero-sum subsequence of length <= T.
   reach[j] = 64-bit mask over Z_n^2 (index n*a+b) of sums of EXACTLY j chosen elts. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef unsigned long long u64;
static int n,NV,T,best,MAXM;
static int ADD[64][64];            /* ADD[x][g] = index of x+g */
static int NEG[64];
static int curE[64],curM[64],nc_cur;
static int bestE[64],bestM[64],bestn;
static inline u64 tr(u64 m,int g){ /* translate mask by +g */
    u64 r=0; while(m){ int x=__builtin_ctzll(m); m&=m-1; r|=1ULL<<ADD[x][g]; } return r; }
/* max copies of g addable to state reach[] */
static inline int multub(u64*reach,int g){
    u64 tmp[16]; memcpy(tmp,reach,(T+1)*sizeof(u64));
    int k=0;
    for(int c=1;c<=MAXM;c++){
        for(int j=T;j>=1;j--) tmp[j]|=tr(tmp[j-1],g);
        int bad=0;
        for(int j=1;j<=T;j++) if(tmp[j]&1ULL){ bad=1;break; }   /* 0 reachable */
        if(bad) break;
        k=c;
    }
    return k;
}
static void rec(int ei,int k,u64*reach){
    if(k>best){ best=k; bestn=nc_cur;
        memcpy(bestE,curE,nc_cur*sizeof(int)); memcpy(bestM,curM,nc_cur*sizeof(int));
        printf("BEST %d :",k);
        for(int i=0;i<nc_cur;i++) printf(" (%d,%d)^%d",curE[i]/n,curE[i]%n,curM[i]);
        printf("\n"); fflush(stdout); }
    /* capacity bound over remaining elements */
    int cap=0; for(int g=ei; g<=NV; g++) cap+=multub(reach,g);
    if(k+cap<=best) return;
    for(int g=ei; g<=NV; g++){
        int ub=multub(reach,g);
        if(ub==0) continue;
        u64 nr[16]; memcpy(nr,reach,(T+1)*sizeof(u64));
        for(int c=1;c<=ub;c++){
            for(int j=T;j>=1;j--) nr[j]|=tr(nr[j-1],g);
            curE[nc_cur]=g; curM[nc_cur]=c; nc_cur++;
            rec(g+1,k+c,nr);
            nc_cur--;
        }
    }
}
int main(int argc,char**argv){
    n=atoi(argv[1]); T=atoi(argv[2]); int fixfirst=(argc>3)?atoi(argv[3]):0;
    NV=n*n-1; MAXM=n-1;
    for(int x=0;x<n*n;x++){ int a=x/n,b=x%n;
        for(int g=0;g<n*n;g++){ int c=g/n,d=g%n; ADD[x][g]=((a+c)%n)*n+((b+d)%n); }
        NEG[x]=((n-a)%n)*n+((n-b)%n); }
    (void)NEG;
    best=0; nc_cur=0;
    u64 reach[16]; memset(reach,0,sizeof(reach)); reach[0]=1ULL;
    if(fixfirst){
        /* WLOG (by GL(2,n) transitivity on nonzero vectors) the least element is e1=(0,1) idx 1 */
        int g=1; int ub=multub(reach,g);
        u64 nr[16]; memcpy(nr,reach,(T+1)*sizeof(u64));
        for(int c=1;c<=ub;c++){
            for(int j=T;j>=1;j--) nr[j]|=tr(nr[j-1],g);
            curE[nc_cur]=g; curM[nc_cur]=c; nc_cur++;
            rec(g+1,c,nr); nc_cur--;
        }
    } else rec(1,0,reach);
    printf("f_%d(C_%d^2) = %d\n",T,n,best); return 0;
}
