/* Enumerate extremal D_2 witnesses over C_2^r: length-L subsets of F_2^r\{0}
   with no two disjoint nonempty zero-sum subsequences.
   Prune with Lemma A: min zero-sum >= m, so no zero-sum of length <= m-1.
   Emit min-zero-sum histogram and (optionally) all witnesses. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef unsigned long long u64;
static int R,N,L,M;           /* M = m = D_2 - D */
static int cur[32]; static long long hist[16]; static long long total=0;
static FILE*out=NULL;
/* reach[j] over 0..N : sums of exactly j chosen elements, as bitmask (N<=32 -> u64 ok) */
static inline u64 xsh(u64 mask,int v,int n){ u64 r=0; while(mask){int x=__builtin_ctzll(mask);mask&=mask-1;r|=1ULL<<(x^v);} return r; }
/* full check: any two disjoint nonempty zero-sums among cur[0..L-1]? */
static int two_disjoint(void){
    int nz=0; unsigned zs[512];
    for(unsigned s=1;s<(1u<<L);s++){
        int x=0;
        for(int i=0;i<L;i++) if((s>>i)&1) x^=cur[i];
        if(x==0){ if(nz<512) zs[nz++]=s; }
    }
    for(int i=0;i<nz;i++) for(int j=i+1;j<nz;j++) if(!(zs[i]&zs[j])) return 1;
    return 0;
}
static int min_zs(void){
    for(int k=1;k<=L;k++)
        for(unsigned s=1;s<(1u<<L);s++){
            if(__builtin_popcount(s)!=k) continue;
            int x=0;
            for(int i=0;i<L;i++) if((s>>i)&1) x^=cur[i];
            if(x==0) return k;
        }
    return 0;
}
static void rec(int start,int k,u64*reach){
    if(k==L){
        if(!two_disjoint()){ total++; hist[min_zs()]++;
            if(out){ for(int i=0;i<L;i++) fprintf(out,"%s%d",i?" ":"",cur[i]); fputc('\n',out); } }
        return; }
    if(k+(N-start) < L) return;
    for(int v=start; v<N; v++){
        if(k+(N-v) < L) return;
        /* legal if v not reachable by <= M-2 chosen elements (would give zero-sum of len <= M-1) */
        int ok=1;
        for(int j=0;j<=M-2;j++) if((reach[j]>>v)&1){ ok=0;break; }
        if(!ok) continue;
        u64 nr[16]; memcpy(nr,reach,(L+1)*sizeof(u64));
        for(int j=L;j>=1;j--) nr[j]|=xsh(nr[j-1],v,N);
        cur[k]=v; rec(v+1,k+1,nr);
    }
}
int main(int argc,char**argv){
    R=atoi(argv[1]); L=atoi(argv[2]); M=atoi(argv[3]);
    if(argc>4) out=fopen(argv[4],"w");
    N=1<<R;
    u64 reach[16]; memset(reach,0,sizeof(reach)); reach[0]=1ULL;
    rec(1,0,reach);
    printf("C_2^%d L=%d m=%d : witnesses=%lld  hist:",R,L,M,total);
    for(int i=0;i<16;i++) if(hist[i]) printf(" {%d:%lld}",i,hist[i]);
    printf("\n"); if(out) fclose(out);
    return 0;
}
