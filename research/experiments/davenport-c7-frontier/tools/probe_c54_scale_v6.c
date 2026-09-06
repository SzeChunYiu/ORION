/* Scale probe for D_2(C_5^4) in {26,27}.
 * A length-26 S with z(S) <= 1 splits as S = A.B with A an atom and
 * B = S\A zero-sum-free, |B| <= D(C_5^4)-1 = 16, so |A| >= 10.
 * The binding sub-problem is: how many zero-sum-free sequences of length 16
 * are there over C_5^4?  Measure the rate rather than guess. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#define P 5
#define NG 625
#define W 10               /* 625 bits in 10 uint64 */
typedef struct { unsigned long long a[W]; } Msk;
static int addtab[NG][NG], negv[NG], vecs[NG][4];
static int mult[NG], chosen[24];
static long long cnt, nodes, CAP;
static int TARGET=16, aborted;
static inline int g(Msk*m,int i){return (m->a[i>>6]>>(i&63))&1ULL;}
static inline void s(Msk*m,int i){m->a[i>>6]|=1ULL<<(i&63);}
static void dfs(int start,int len,Msk *S){
    if(++nodes>CAP){aborted=1;return;}
    if(len==TARGET){ cnt++; return; }
    for(int i=start;i<NG;i++){
        if(mult[i]>=4) continue;
        if(g(S,negv[i])) continue;          /* would create a zero-sum */
        Msk T=*S;
        for(int q=0;q<NG;q++) if(g(S,q)) s(&T,addtab[q][i]);
        mult[i]++; chosen[len]=i;
        dfs(i,len+1,&T);
        mult[i]--;
        if(aborted) return;
    }
}
int main(int argc,char**argv){
    CAP = argc>1? atoll(argv[1]) : 300000000LL;
    if(argc>2) TARGET=atoi(argv[2]);
    for(int i=0;i<NG;i++){int t=i;for(int d=3;d>=0;d--){vecs[i][d]=t%5;t/=5;}}
    for(int i=0;i<NG;i++){
        int n=0; for(int d=0;d<4;d++) n=n*5+((P-vecs[i][d])%P);
        negv[i]=n;
        for(int j=0;j<NG;j++){int a=0;
            for(int d=0;d<4;d++) a=a*5+((vecs[i][d]+vecs[j][d])%P);
            addtab[i][j]=a;}
    }
    /* normalise: a zero-sum-free sequence of length 16 spans rank 4
       (in a hyperplane C_5^3 the max zero-sum-free length is D-1 = 12 < 16) */
    Msk S; memset(&S,0,sizeof S); s(&S,0);
    int e[4]; for(int d=0;d<4;d++){int idx=0; for(int q=0;q<4;q++) idx=idx*5+(q==d?1:0); e[d]=idx;}
    for(int q=0;q<4;q++){int v=e[q]; Msk T=S;
        for(int j=0;j<NG;j++) if(g(&S,j)) s(&T,addtab[j][v]);
        S=T; mult[v]++; chosen[q]=v;}
    clock_t t0=clock(); cnt=0; nodes=0; aborted=0;
    dfs(0,4,&S);
    double el=(double)(clock()-t0)/CLOCKS_PER_SEC;
    printf("C_5^4, zero-sum-free length %d containing e1..e4: counted %lld in %.1fs "
           "(%lld nodes, aborted=%d)\n", TARGET, cnt, el, nodes, aborted);
    if(aborted) printf("  -> NOT exhaustive; rate %.0f leaves/s at cap %lld\n", cnt/el, CAP);
    return 0;
}
