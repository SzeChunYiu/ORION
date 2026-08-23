/* Enumerate ALL length-L sequences over C_p^r with no zero-sum of length <= T.
   Report the histogram of multiplicity profiles. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef unsigned long long u64;
static int P,R,N,T,L,MAXM; static long long total=0;
static int ADD[64][64];
static int curM[80],nc,curE[80];
#define MAXPROF 4096
static char profkey[MAXPROF][64]; static long long profcnt[MAXPROF]; static int nprof=0;
static inline u64 tr(u64 m,int g){u64 r=0;while(m){int x=__builtin_ctzll(m);m&=m-1;r|=1ULL<<ADD[x][g];}return r;}
static inline int multub(u64*reach,int g){
    u64 t[16];memcpy(t,reach,(T+1)*sizeof(u64));int k=0;
    for(int c=1;c<=MAXM;c++){for(int j=T;j>=1;j--)t[j]|=tr(t[j-1],g);
        int bad=0;for(int j=1;j<=T;j++)if(t[j]&1ULL){bad=1;break;} if(bad)break;k=c;}
    return k;}
static int cmpi(const void*a,const void*b){return *(int*)a-*(int*)b;}
static void record(void){
    int tmp[80]; memcpy(tmp,curM,nc*sizeof(int)); qsort(tmp,nc,sizeof(int),cmpi);
    char key[64]; int o=0; for(int i=0;i<nc;i++) o+=snprintf(key+o,64-o,"%d",tmp[i]);
    for(int i=0;i<nprof;i++) if(!strcmp(profkey[i],key)){profcnt[i]++;return;}
    if(nprof<MAXPROF){strcpy(profkey[nprof],key);profcnt[nprof]=1;nprof++;}
}
static void rec(int ei,int k,u64*reach){
    if(k==L){ total++; record(); return; }
    int cap=0; for(int g=ei;g<N;g++) cap+=multub(reach,g);
    if(k+cap<L) return;
    for(int g=ei;g<N;g++){
        int ub=multub(reach,g); if(!ub) continue;
        if(ub>L-k) ub=L-k;
        u64 nr[16]; memcpy(nr,reach,(T+1)*sizeof(u64));
        for(int c=1;c<=ub;c++){
            for(int j=T;j>=1;j--) nr[j]|=tr(nr[j-1],g);
            curE[nc]=g;curM[nc]=c;nc++; rec(g+1,k+c,nr); nc--; }
    }
}
int main(int argc,char**argv){
    P=atoi(argv[1]);R=atoi(argv[2]);T=atoi(argv[3]);L=atoi(argv[4]);
    MAXM=(argc>5)?atoi(argv[5]):(2*P-1);
    N=1;for(int i=0;i<R;i++)N*=P;
    for(int a=0;a<N;a++)for(int b=0;b<N;b++){int x=a,y=b,res=0,mm=1;
        for(int i=0;i<R;i++){res+=(((x%P)+(y%P))%P)*mm;mm*=P;x/=P;y/=P;} ADD[a][b]=res;}
    u64 reach[16];memset(reach,0,sizeof(reach));reach[0]=1ULL;nc=0;
    rec(1,0,reach);
    printf("C_%d^%d  T=%d  L=%d   total_extremal=%lld   distinct_profiles=%d\n",P,R,T,L,total,nprof);
    for(int i=0;i<nprof;i++) printf("  profile %-20s count %lld\n",profkey[i],profcnt[i]);
    return 0;
}
