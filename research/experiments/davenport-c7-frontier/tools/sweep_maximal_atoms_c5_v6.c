/* Time the per-atom extension test, to decide whether sweeping all maximal
 * atoms is feasible.  For each atom we only need a cheap NECESSARY condition
 * first: how many elements are compatible at all (13 + slack >= 31?). */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#define P 5
#define NG 125
typedef struct { unsigned long long a[2]; } Msk;
static int addtab[NG][NG], negv[NG], vecs[NG][3];
static int mult[NG], chosen[16];
static long long natom, nodes, cheappass, NODECAP, SAMPLE, extnodes, nzs, maxext;
static int aborted;
static inline int get(Msk*m,int i){return (m->a[i>>6]>>(i&63))&1ULL;}
static inline void st(Msk*m,int i){m->a[i>>6]|=1ULL<<(i&63);}

/* full extension search from a fixed 13-atom, to length 31, counting zero-sum */
static int ecand[NG], nec, emult[NG], echosen[64];
static void edfs(int start,int len,Msk S[5]){
    extnodes++;
    if(extnodes>maxext) return;
    if(len>=31){
        int s0=0,s1=0,s2=0;
        for(int q=0;q<len;q++){s0+=vecs[echosen[q]][0];s1+=vecs[echosen[q]][1];s2+=vecs[echosen[q]][2];}
        if(s0%P==0&&s1%P==0&&s2%P==0) nzs++;
        return;
    }
    int room=0; for(int i=start;i<nec;i++) room+=4-emult[ecand[i]];
    if(len+room<31) return;
    for(int i=start;i<nec;i++){
        int v=ecand[i]; if(emult[v]>=4) continue;
        int nv=negv[v],bad=0;
        for(int k=0;k<5&&!bad;k++) if(get(&S[k],nv)) bad=1;
        if(bad) continue;
        Msk T[5]; memcpy(T,S,sizeof T);
        for(int k=4;k>=1;k--)
            for(int j=0;j<NG;j++) if(get(&S[k-1],j)) st(&T[k],addtab[j][v]);
        emult[v]++; echosen[len]=v; edfs(i,len+1,T); emult[v]--;
        if(extnodes>maxext) return;
    }
}
static void full_ext(int *U){
    Msk S[5]; memset(S,0,sizeof S); st(&S[0],0);
    memset(emult,0,sizeof emult);
    for(int q=0;q<13;q++){
        int v=U[q]; Msk T[5]; memcpy(T,S,sizeof T);
        for(int k=4;k>=1;k--)
            for(int j=0;j<NG;j++) if(get(&S[k-1],j)) st(&T[k],addtab[j][v]);
        memcpy(S,T,sizeof S); emult[v]++; echosen[q]=v;
    }
    nec=0;
    for(int v=1;v<NG;v++){int nv=negv[v],bad=0;
        for(int k=0;k<5&&!bad;k++) if(get(&S[k],nv)) bad=1;
        if(!bad) ecand[nec++]=v;}
    edfs(0,13,S);
}

/* cheap filter: with U fixed, how many elements v keep U*v 5-short-free, and
   what is the total multiplicity budget?  Need >= 18 more slots. */
static int cheap_ok(int *U){
    Msk S[5]; memset(S,0,sizeof S); st(&S[0],0);
    int m2[NG]; memset(m2,0,sizeof m2);
    for(int q=0;q<13;q++){
        int v=U[q]; Msk T[5]; memcpy(T,S,sizeof T);
        for(int k=4;k>=1;k--)
            for(int j=0;j<NG;j++) if(get(&S[k-1],j)) st(&T[k],addtab[j][v]);
        memcpy(S,T,sizeof S); m2[v]++;
    }
    int slack=0;
    for(int v=1;v<NG;v++){
        int nv=negv[v],bad=0;
        for(int k=0;k<5&&!bad;k++) if(get(&S[k],nv)) bad=1;
        if(!bad) slack += 4-m2[v];
    }
    return slack>=18;
}

static void dfs(int start,int len,Msk S){
    if(aborted) return;
    if(++nodes>NODECAP){aborted=1;return;}
    if(len==12){
        int s0=0,s1=0,s2=0;
        for(int q=0;q<12;q++){s0+=vecs[chosen[q]][0];s1+=vecs[chosen[q]][1];s2+=vecs[chosen[q]][2];}
        int w=((P-s0%P)%P)*25+((P-s1%P)%P)*5+((P-s2%P)%P);
        if(!w) return;
        natom++;
        int U[13]; for(int q=0;q<12;q++) U[q]=chosen[q]; U[12]=w;
        if(natom<=SAMPLE){ full_ext(U); }
        else { aborted=1; }
        return;
    }
    for(int i=start;i<NG;i++){
        if(mult[i]>=4) continue;
        if(get(&S,negv[i])) continue;
        Msk T=S;
        for(int q=0;q<NG;q++) if(get(&S,q)) st(&T,addtab[q][i]);
        mult[i]++; chosen[len]=i; dfs(i,len+1,T); mult[i]--;
        if(aborted) return;
    }
}
int main(int argc,char**argv){
    NODECAP = argc>1 ? atoll(argv[1]) : 30000000LL;
    for(int i=0;i<NG;i++){vecs[i][0]=i/25;vecs[i][1]=(i/5)%5;vecs[i][2]=i%5;}
    for(int i=0;i<NG;i++){int n[3];for(int t=0;t<3;t++)n[t]=(P-vecs[i][t])%P;
        negv[i]=n[0]*25+n[1]*5+n[2];
        for(int j=0;j<NG;j++){int s[3];for(int t=0;t<3;t++)s[t]=(vecs[i][t]+vecs[j][t])%P;
            addtab[i][j]=s[0]*25+s[1]*5+s[2];}}
    Msk S; memset(&S,0,sizeof S); st(&S,0); memset(mult,0,sizeof mult);
    int init[3]={25,5,1};
    for(int q=0;q<3;q++){int v=init[q]; Msk T=S;
        for(int j=0;j<NG;j++) if(get(&S,j)) st(&T,addtab[j][v]);
        S=T; mult[v]++; chosen[q]=v;}
    SAMPLE = argc>2 ? atoll(argv[2]) : 2000; maxext=200000000LL;
    clock_t t0=clock(); natom=0; nodes=0; cheappass=0; aborted=0; extnodes=0; nzs=0;
    dfs(0,3,S);
    double el=(double)(clock()-t0)/CLOCKS_PER_SEC;
    long long done = natom<SAMPLE?natom:SAMPLE;
    printf("FULL extension search on %lld sampled maximal atoms in %.1fs\n", done, el);
    printf("  extension nodes total %lld ; zero-sum length-31 completions found: %lld\n", extnodes, nzs);
    printf("  per-atom cost: %.2f ms\n", done? 1000.0*el/done : 0.0);
    printf("  => full sweep of 6,315,607 atoms: %.1f hours\n",
           done? 6315607.0*(el/done)/3600.0 : 0.0);
    return 0;
}
