/* Enumerate maximal atoms (length 13 = D) over C_5^3, up to the normalisation
 * that the first independent triple is e1,e2,e3.
 *
 * A length-13 atom is an extremal zero-sum-free sequence of length 12 plus the
 * completing element -(sum).  Zero-sum-freeness prunes far harder than
 * 5-short-freeness: maintain SIGMA = set of ALL subsums as one 125-bit mask;
 * adding v is legal iff -v is not in SIGMA. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#define P 5
#define NG 125
typedef struct { unsigned long long a[2]; } Msk;
static int addtab[NG][NG], negv[NG], vecs[NG][3];
static long long nodes, natom, NODECAP; static int aborted;
static int chosen[16], mult[NG];
static inline int get(Msk*m,int i){return (m->a[i>>6]>>(i&63))&1ULL;}
static inline void st(Msk*m,int i){m->a[i>>6]|=1ULL<<(i&63);}
static int supp_hist[9];

static void dfs(int start,int len,Msk S){
    if(aborted) return;
    if(++nodes>NODECAP){aborted=1;return;}
    if(len==12){
        /* completing element */
        int s0=0,s1=0,s2=0;
        for(int q=0;q<12;q++){s0+=vecs[chosen[q]][0];s1+=vecs[chosen[q]][1];s2+=vecs[chosen[q]][2];}
        int t0=(P-s0%P)%P,t1=(P-s1%P)%P,t2=(P-s2%P)%P;
        int w=t0*25+t1*5+t2;
        if(w==0) return;                     /* the 12 already sum to zero: not zero-sum-free */
        natom++;
        if(natom<=3){
            int seen[NG]; memset(seen,0,sizeof seen); int sup=0;
            for(int q=0;q<12;q++) if(!seen[chosen[q]]++) sup++;
            if(!seen[w]) sup++;
            printf("   atom #%lld support %d\n", natom, sup);
        }
        return;
    }
    for(int i=start;i<NG;i++){
        if(mult[i]>=4) continue;
        int nv=negv[i];
        if(get(&S,nv)) continue;             /* would create a zero-sum */
        Msk T=S;
        for(int q=0;q<NG;q++) if(get(&S,q)) st(&T,addtab[q][i]);
        mult[i]++; chosen[len]=i;
        dfs(i,len+1,T);
        mult[i]--;
        if(aborted) return;
    }
}

int main(int argc,char**argv){
    NODECAP = argc>1 ? atoll(argv[1]) : 400000000LL;
    for(int i=0;i<NG;i++){vecs[i][0]=i/25;vecs[i][1]=(i/5)%5;vecs[i][2]=i%5;}
    for(int i=0;i<NG;i++){int n[3];for(int t=0;t<3;t++)n[t]=(P-vecs[i][t])%P;
        negv[i]=n[0]*25+n[1]*5+n[2];
        for(int j=0;j<NG;j++){int s[3];for(int t=0;t<3;t++)s[t]=(vecs[i][t]+vecs[j][t])%P;
            addtab[i][j]=s[0]*25+s[1]*5+s[2];}}
    /* normalise: e1,e2,e3 are the first three (an atom of length 13 spans rank 3) */
    int e1=25,e2=5,e3=1;
    Msk S; memset(&S,0,sizeof S); st(&S,0);
    memset(mult,0,sizeof mult);
    int init[3]={e1,e2,e3};
    for(int q=0;q<3;q++){
        int v=init[q]; Msk T=S;
        for(int j=0;j<NG;j++) if(get(&S,j)) st(&T,addtab[j][v]);
        S=T; mult[v]++; chosen[q]=v;
    }
    clock_t t0=clock(); nodes=0; natom=0; aborted=0;
    dfs(0,3,S);
    double el=(double)(clock()-t0)/CLOCKS_PER_SEC;
    printf("maximal atoms (length 13) with e1,e2,e3 normalised: %lld ; nodes %lld ; "
           "%.1fs ; aborted=%d\n", natom, nodes, el, aborted);
    return 0;
}
