/* Measure the cost of the Theorem-M extension search when the fixed atom is
#include <stdlib.h>
 * SHORT (length 6) instead of maximal (length 13). */
#include <stdio.h>
#include <string.h>
#include <time.h>
#define P 5
#define NG 125
typedef struct { unsigned long long a[2]; } Msk;
static int addtab[NG][NG], negv[NG], vecs[NG][3];
static int cand[NG], ncand, mult[NG], best, chosen[64];
static long long nodes, ntot, nsol, NODECAP;
static inline int get(Msk*m,int i){return (m->a[i>>6]>>(i&63))&1ULL;}
static inline void st(Msk*m,int i){m->a[i>>6]|=1ULL<<(i&63);}
static void sh(Msk*d,const Msk*s,int v){for(int i=0;i<NG;i++) if(get((Msk*)s,i)) st(d,addtab[i][v]);}
static int aborted;
static void dfs(int start,int len,Msk S[5]){
    if(aborted) return;
    if(++nodes>NODECAP){ aborted=1; return; }
    if(len>best) best=len;
    if(len>=31){
        ntot++;
        int s0=0,s1=0,s2=0;
        for(int q=0;q<len;q++){s0+=vecs[chosen[q]][0];s1+=vecs[chosen[q]][1];s2+=vecs[chosen[q]][2];}
        if(s0%P==0&&s1%P==0&&s2%P==0) nsol++;
        return;
    }
    int room=0; for(int i=start;i<ncand;i++) room+=4-mult[cand[i]];
    if(len+room<31) return;
    for(int i=start;i<ncand;i++){
        int v=cand[i]; if(mult[v]>=4) continue;
        int nv=negv[v],bad=0;
        for(int k=0;k<5&&!bad;k++) if(get(&S[k],nv)) bad=1;
        if(bad) continue;
        Msk T[5]; memcpy(T,S,sizeof T);
        for(int k=4;k>=1;k--) sh(&T[k],&S[k-1],v);
        mult[v]++; chosen[len]=v; dfs(i,len+1,T); mult[v]--;
        if(aborted) return;
    }
}
int main(int argc,char**argv){
    NODECAP = argc>1 ? atoll(argv[1]) : 200000000LL;
    for(int i=0;i<NG;i++){vecs[i][0]=i/25;vecs[i][1]=(i/5)%5;vecs[i][2]=i%5;}
    for(int i=0;i<NG;i++){int n[3];for(int t=0;t<3;t++)n[t]=(P-vecs[i][t])%P;
        negv[i]=n[0]*25+n[1]*5+n[2];
        for(int j=0;j<NG;j++){int s[3];for(int t=0;t<3;t++)s[t]=(vecs[i][t]+vecs[j][t])%P;
            addtab[i][j]=s[0]*25+s[1]*5+s[2];}}
    /* sample 6-atom: e1,e2,e3,e3,e3,(4,4,2)  -> from the probe */
    int A[6]={1*25,1*5,1,1,1,4*25+4*5+2};
    Msk S[5]; memset(S,0,sizeof S); st(&S[0],0); memset(mult,0,sizeof mult);
    for(int q=0;q<6;q++){int v=A[q];Msk T[5];memcpy(T,S,sizeof T);
        for(int k=4;k>=1;k--) sh(&T[k],&S[k-1],v);
        memcpy(S,T,sizeof S); mult[v]++; chosen[q]=v;}
    ncand=0; for(int v=1;v<NG;v++){int nv=negv[v],bad=0;
        for(int k=0;k<5&&!bad;k++) if(get(&S[k],nv)) bad=1;
        if(!bad) cand[ncand++]=v;}
    best=6; nodes=0; ntot=0; nsol=0; aborted=0;
    clock_t t0=clock();
    dfs(0,6,S);
    double el=(double)(clock()-t0)/CLOCKS_PER_SEC;
    printf("6-atom start: candidates %d ; nodes %lld ; %.1fs ; aborted=%d ; "
           "max length %d ; length-31 extensions %lld ; zero-sum %lld\n",
           ncand,nodes,el,aborted,best,ntot,nsol);
    return 0;
}
