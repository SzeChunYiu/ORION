/* f_T(C_p^r) for p^r <= 64 : max-length sequence (repeats allowed) over C_p^r\{0}
   with no nonempty zero-sum subsequence of length <= T.  Prints extremal witness. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef unsigned long long u64;
static int P,R,N,T,best,MAXM;
static int ADD[64][64];
static int curE[80],curM[80],nc;
static int bE[80],bM[80],bn;
static inline u64 tr(u64 m,int g){ u64 r=0; while(m){int x=__builtin_ctzll(m); m&=m-1; r|=1ULL<<ADD[x][g];} return r; }
static inline int multub(u64*reach,int g){
    u64 t[16]; memcpy(t,reach,(T+1)*sizeof(u64)); int k=0;
    for(int c=1;c<=MAXM;c++){
        for(int j=T;j>=1;j--) t[j]|=tr(t[j-1],g);
        int bad=0; for(int j=1;j<=T;j++) if(t[j]&1ULL){bad=1;break;}
        if(bad) break; k=c; }
    return k;
}
static void pr(int*E,int*M,int m){
    for(int i=0;i<m;i++){ int x=E[i]; printf(" (");
        for(int d=0;d<R;d++){ printf("%s%d",d?",":"",x%P); x/=P; } printf(")^%d",M[i]); }
}
static void rec(int ei,int k,u64*reach){
    if(k>best){ best=k; bn=nc; memcpy(bE,curE,nc*sizeof(int)); memcpy(bM,curM,nc*sizeof(int));
        printf("BEST %d :",k); pr(curE,curM,nc); printf("\n"); fflush(stdout); }
    int cap=0; for(int g=ei;g<=N-1;g++) cap+=multub(reach,g);
    if(k+cap<=best) return;
    for(int g=ei;g<=N-1;g++){
        int ub=multub(reach,g); if(!ub) continue;
        u64 nr[16]; memcpy(nr,reach,(T+1)*sizeof(u64));
        for(int c=1;c<=ub;c++){
            for(int j=T;j>=1;j--) nr[j]|=tr(nr[j-1],g);
            curE[nc]=g; curM[nc]=c; nc++;
            rec(g+1,k+c,nr); nc--; }
    }
}
int main(int argc,char**argv){
    P=atoi(argv[1]); R=atoi(argv[2]); T=atoi(argv[3]);
    MAXM=(argc>4)?atoi(argv[4]):(2*P-1);
    N=1; for(int i=0;i<R;i++) N*=P;
    if(N>64){ fprintf(stderr,"N=%d >64 unsupported\n",N); return 2; }
    for(int a=0;a<N;a++) for(int b=0;b<N;b++){
        int x=a,y=b,res=0,mm=1;
        for(int i=0;i<R;i++){ res+=(((x%P)+(y%P))%P)*mm; mm*=P; x/=P; y/=P; }
        ADD[a][b]=res; }
    best=0; nc=0;
    u64 reach[16]; memset(reach,0,sizeof(reach)); reach[0]=1ULL;
    rec(1,0,reach);
    printf("f_%d(C_%d^%d) = %d   witness:",T,P,R,best); pr(bE,bM,bn); printf("\n");
    return 0;
}
