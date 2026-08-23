/* Direct test on C_3^3: enumerate every length-10 multiset with no two disjoint
 * nonempty zero-sums, and record its minimum zero-sum length.
 * D(C_3^3)=7, D_2=11 (Freeze-Schmid), m = 4.  Criterion predicts min ZS == 4.
 * 27 group elements, so every reachability set fits in a uint32 bitmask. */
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
static int N;
static int ADD[64][64];
static int L, M, P, R;
static long long nodes=0, nwit=0, hist[16];

typedef struct { unsigned R1; unsigned R2[64]; unsigned reach[12]; } St;

/* returns 0 if two disjoint zero-sums appear (prune) */
static int step(const St*in, int v, St*out){
    out->R1 = in->R1 | (1u<<v);
    for(int s=0;s<N;s++) if((in->R1>>s)&1) out->R1 |= 1u<<ADD[s][v];
    for(int s=0;s<N;s++) out->R2[s]=in->R2[s];
    for(int a=0;a<N;a++){ unsigned row=in->R2[a]; if(!row) continue;
        out->R2[ADD[a][v]] |= row;
        unsigned nb=0;
        for(int b=0;b<N;b++) if((row>>b)&1) nb |= 1u<<ADD[b][v];
        out->R2[a] |= nb; }
    for(int s=0;s<N;s++) if((in->R1>>s)&1) out->R2[s] |= 1u<<v;
    if(out->R2[0] & 1u) return 0;                 /* (0,0) both nonempty */
    /* zero-sum reach by weight, for the min-zero-sum readout */
    for(int w=0;w<=L;w++) out->reach[w]=in->reach[w];
    for(int w=L-1;w>=0;w--){ unsigned r=in->reach[w]; if(!r) continue;
        unsigned nr=0;
        for(int s=0;s<N;s++) if((r>>s)&1) nr |= 1u<<ADD[s][v];
        out->reach[w+1] |= nr; }
    return 1;
}
static St buf[16];
static void dfs(const St*st, int len, int start){
    nodes++;
    if(len==L){
        nwit++;
        for(int w=1;w<=L;w++) if(st->reach[w]&1u){ hist[w<15?w:15]++; break; }
        return; }
    for(int v=start; v<N; v++){
        if(v==0) continue;                         /* skip the identity */
        if(!step(st,v,&buf[len])) continue;
        dfs(&buf[len], len+1, v); }
}
int main(int argc,char**argv){
    P=atoi(argv[1]); R=atoi(argv[2]); L=atoi(argv[3]); M=atoi(argv[4]);
    N=1; for(int i=0;i<R;i++) N*=P;
    for(int a=0;a<N;a++) for(int b=0;b<N;b++){
        int x=a,y=b,res=0,mm=1;
        for(int i=0;i<R;i++){ res += (((x%P)+(y%P))%P)*mm; mm*=P; x/=P; y/=P; }
        ADD[a][b]=res; }
    St z; memset(&z,0,sizeof(z)); z.reach[0]=1u;   /* sum 0 with 0 elements */
    dfs(&z,0,1);
    printf("{\"group\":\"C_%d^%d\",\"m\":%d,\"witness_length\":%d,"
           "\"nodes\":%lld,\"extremal_witnesses\":%lld,\"min_zerosum_histogram\":{",P,R,M,L,nodes,nwit);
    int first=1;
    for(int w=1;w<16;w++) if(hist[w]){ printf("%s\"%d\":%lld",first?"":",",w,hist[w]); first=0; }
    printf("}}\n");
    return 0;
}
