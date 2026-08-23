/* D_2(C_2^r) frontier hunt: search for a length-(r+k) sequence over C_2^r with
   no two disjoint nonempty zero-sum subsequences (a "witness").
   Completeness: such W is squarefree (repeat => 2-ZS + remaining r+k-2 >= D
   contains a ZS) and has rank r (rank <= r-1 embeds it in C_2^{r-1}, where
   length >= D_2(C_2^{r-1}) forces two disjoint ZS). So W contains a basis;
   mod GL fix it standard. Lemma A: min-ZS >= k (a ZS of length <= k-1 leaves
   >= r+1 = D elements containing a disjoint ZS). Hence the k extra elements
   have weight >= k-1, pair-XORs weight >= k-2, triple-XORs >= k-3, 4-XORs >= k-4. */
#include <stdio.h>
#include <stdlib.h>
static int R,K,N,MINZS,np;
static int pool[256], cur[8];
static long long leaves=0, found=0;
static FILE*wf=NULL;
static int wt(int x){ return __builtin_popcount(x); }
static int fullcheck(void){
    int n=R+K, W[16];
    for(int i=0;i<R;i++) W[i]=1<<i;
    for(int i=0;i<K;i++) W[R+i]=cur[i];
    static unsigned char x[1<<15];
    int total=1<<n, zs[1<<15], nz=0, mn=99;
    x[0]=0;
    for(int s=1;s<total;s++){
        int low=s&-s;
        x[s]=x[s^low]^W[__builtin_ctz(s)];
        if(!x[s]) zs[nz++]=s;
    }
    for(int i=0;i<nz;i++){ int p=__builtin_popcount(zs[i]); if(p<mn)mn=p; }
    for(int i=0;i<nz;i++) for(int j=i+1;j<nz;j++)
        if(!(zs[i]&zs[j])) return 0;
    if(mn<MINZS) printf("THEORY-VIOLATION minzs=%d\n",mn);
    return 1;
}
static void rec(int start,int k){
    if(k==K){
        leaves++;
        if(fullcheck()){
            found++;
            if(wf && found<=10){ for(int i=0;i<K;i++) fprintf(wf,"%s%d",i?" ":"",cur[i]); fputc('\n',wf); fflush(wf);} }
        return;
    }
    for(int pi=start; pi<np; pi++){
        int a=pool[pi], ok=1;
        for(int i=0;i<k&&ok;i++){
            if(wt(cur[i]^a)<MINZS-2){ ok=0; break; }
            for(int j=i+1;j<k&&ok;j++){
                if(wt(cur[i]^cur[j]^a)<MINZS-3){ ok=0; break; }
                for(int l=j+1;l<k&&ok;l++){
                    if(wt(cur[i]^cur[j]^cur[l]^a)<MINZS-4){ ok=0; break; }
                    for(int mI=l+1;mI<k&&ok;mI++)
                        if(wt(cur[i]^cur[j]^cur[l]^cur[mI]^a)<MINZS-5) ok=0;
                }
            }
        }
        if(!ok) continue;
        cur[k]=a; rec(pi+1,k+1);
    }
}
int main(int argc,char**argv){
    R=atoi(argv[1]); K=atoi(argv[2]); int MZOV=(argc>4)?atoi(argv[4]):0;
    if(argc>3 && argv[3][0]!=45) wf=fopen(argv[3],"w");
    N=1<<R; MINZS=MZOV?MZOV:K;
    for(int v=1;v<N;v++) if(wt(v)>=MINZS-1) pool[np++]=v;
    rec(0,0);
    printf("r=%d k=%d minzs=%d pool=%d leaves=%lld disjointfree=%lld\n",R,K,MINZS,np,leaves,found);
    if(found) printf("WITNESS EXISTS: length %d over C_2^%d => D_2(C_2^%d) >= %d\n",R+K,R,R,R+K+1);
    else printf("NO WITNESS of length %d over C_2^%d\n",R+K,R);
    return 0;
}
