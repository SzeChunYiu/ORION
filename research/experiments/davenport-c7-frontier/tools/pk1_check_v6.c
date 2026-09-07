/* pk1_check_v6.c — decide whether an explicit sequence over C_p^r has two disjoint
 * nonempty zero-sum subsequences (i.e. whether its packing number is >= 2).
 * Exact layered DP over pairs of disjoint sub-multisets (sumA,sumB) with
 * emptiness flags; no enumeration of blocks, so it is polynomial in p^r and |S|.
 * Usage: pk1_check p r      (vector indices, whitespace-separated, on stdin)
 * Prints "pk<=1" or "pk>=2". */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static int p,r,N,L;
static int *addtab, seq[512];
static unsigned char *lay[4], *nl[4];
int main(int argc,char**argv){
    if(argc<3){ fprintf(stderr,"usage: pk1_check p r  < indices\n"); return 2; }
    p=atoi(argv[1]); r=atoi(argv[2]);
    N=1; for(int i=0;i<r;i++) N*=p;
    addtab=malloc(sizeof(int)*(size_t)N*N);
    int dg[16];
    for(int g=0; g<N; g++){
        int t=g; for(int d=0; d<r; d++){ dg[d]=t%p; t/=p; }
        for(int v=0; v<N; v++){
            int u=v,a=0,pw=1;
            for(int d=0; d<r; d++){ int e=u%p; u/=p; a += ((dg[d]+e)%p)*pw; pw*=p; }
            addtab[(size_t)g*N+v]=a;
        }
    }
    L=0; while(L<512 && scanf("%d",&seq[L])==1) L++;
    size_t sz=(size_t)N*N;
    for(int i=0;i<4;i++){ lay[i]=calloc(sz,1); nl[i]=calloc(sz,1); }
    lay[0][0]=1;
    int found=0;
    for(int t=0;t<L && !found;t++){
        int g=seq[t];
        for(int i=0;i<4;i++) memcpy(nl[i],lay[i],sz);
        for(int a=0;a<N;a++) for(int b=0;b<N;b++){
            size_t ix=(size_t)a*N+b;
            int ag=addtab[(size_t)a*N+g], bg=addtab[(size_t)b*N+g];
            if(lay[0][ix]){ nl[1][(size_t)ag*N+b]=1; nl[2][ix-b+bg]=1; }
            if(lay[1][ix]){ nl[1][(size_t)ag*N+b]=1; nl[3][ix-b+bg]=1; }
            if(lay[2][ix]){ nl[2][ix-b+bg]=1;        nl[3][(size_t)ag*N+b]=1; }
            if(lay[3][ix]){ nl[3][(size_t)ag*N+b]=1; nl[3][ix-b+bg]=1; }
        }
        for(int i=0;i<4;i++) memcpy(lay[i],nl[i],sz);
        if(lay[3][0]) found=1;
    }
    printf("%s  (p=%d r=%d |S|=%d)\n", found?"pk>=2":"pk<=1", p, r, L);
    return found;
}
