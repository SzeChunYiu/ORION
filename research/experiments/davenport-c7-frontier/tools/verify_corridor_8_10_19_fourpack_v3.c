/* corridor.c - close the p=7 (8,10,19) corridor.
 *
 * Stage 1: for each canonical support-4 19-atom W (type a) and each 10-atom companion V
 *          (the pairs counted in pair.c), enumerate every 8-atom U such that T = U.V.W has
 *          no nonempty zero-sum subsequence of length <= 7.
 * Stage 2: test the four-pack predicate on each T.
 *
 * Key structural reduction used in stage 2: any four pairwise disjoint blocks of T have
 * length >= 8 each (T is 7-short-free), so they use >= 32 of the 37 terms; the unused part
 * C is zero-sum (sigma(T)=0) of size <= 5, and T being 7-short-free forces C empty.
 * Hence FOUR DISJOINT BLOCKS MUST PARTITION T, with length profile one of
 *   (8,8,8,13) (8,8,9,12) (8,8,10,11) (8,9,9,11) (8,9,10,10) (9,9,9,10).
 * So stage 2 is an exact partition search, not a packing search.
 *
 * Usage: corridor a [--quiet]
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define P 7
#define N 343
static int addt[N][N], neg[N];
static int idx3(int x,int y,int z){ return x+P*y+P*P*z; }
static void build(void){
    for(int a=0;a<N;a++){ int ax=a%P,ay=(a/P)%P,az=a/(P*P);
        neg[a]=idx3((P-ax)%P,(P-ay)%P,(P-az)%P);
        for(int b=0;b<N;b++){ int bx=b%P,by=(b/P)%P,bz=b/(P*P);
            addt[a][b]=idx3((ax+bx)%P,(ay+by)%P,(az+bz)%P); } }
}
/* ---------- multiset of T ---------- */
static int sup[64], mul[64], ns;
static void add_elem(int g){ for(int i=0;i<ns;i++) if(sup[i]==g){ mul[i]++; return; } sup[ns]=g; mul[ns]=1; ns++; }

/* partition remaining multiset into k zero-sum blocks, each of length >= 8 */
static int rem[64], total;
static int part(int k){
    if(k==0) return total==0;
    if(total < 8*k) return 0;
    /* first occupied support index must be covered by the next block */
    int f=-1; for(int i=0;i<ns;i++) if(rem[i]){ f=i; break; }
    if(f<0) return 0;
    int maxlen = total - 8*(k-1);
    /* enumerate sub-multisets containing at least one copy of sup[f], size in [8,maxlen], zero-sum */
    int c[64]; memset(c,0,sizeof(c));
    int idx[64], ni=0; for(int i=0;i<ns;i++) if(rem[i]) idx[ni++]=i;
    /* iterative odometer over counts */
    int pos=0; c[0]=1;                    /* force >=1 copy of sup[f] (idx[0]==f) */
    while(pos>=0){
        int len=0,s=0;
        for(int t=0;t<ni;t++){ len+=c[t]; for(int q=0;q<c[t];q++) s=addt[s][sup[idx[t]]]; }
        if(len>=8 && len<=maxlen && s==0){
            for(int t=0;t<ni;t++) rem[idx[t]]-=c[t];
            total-=len;
            int ok=part(k-1);
            for(int t=0;t<ni;t++) rem[idx[t]]+=c[t];
            total+=len;
            if(ok) return 1;
        }
        /* advance odometer, pruning on length */
        int t=ni-1;
        while(t>=0){
            int lim=rem[idx[t]];
            if(t==0) { if(c[0]<lim){ c[0]++; break; } else { t--; continue; } }
            if(c[t]<lim){ c[t]++; break; }
            c[t]=0; t--;
        }
        if(t<0) break;
        int len2=0; for(int q=0;q<ni;q++) len2+=c[q];
        if(len2>maxlen){ /* skip ahead: zero out tail */
            for(int q=t+1;q<ni;q++) c[q]=0;
        }
        pos = t;
    }
    return 0;
}

int main(int argc,char**argv){
    int a=atoi(argv[1]);
    build();
    int Wel[4],Wm[4];
    Wel[0]=idx3(1,0,0); Wm[0]=a;
    Wel[1]=idx3(0,1,0); Wm[1]=P-a;
    Wel[2]=idx3(0,0,1); Wm[2]=P-1;
    Wel[3]=idx3(a%P,(P-a)%P,(P-1)%P); Wm[3]=P-1;

    /* ---- stage 1a: recompute the V companions (independent of pair.c, same predicate) ---- */
    static unsigned char SW[10][N], F[10][N];
    memset(SW,0,sizeof(SW)); memset(F,0,sizeof(F));
    for(int c0=0;c0<=Wm[0];c0++)for(int c1=0;c1<=Wm[1];c1++)for(int c2=0;c2<=Wm[2];c2++)for(int c3=0;c3<=Wm[3];c3++){
        int j=c0+c1+c2+c3; if(j>9) continue; int s=0;
        for(int t=0;t<c0;t++) s=addt[s][Wel[0]];
        for(int t=0;t<c1;t++) s=addt[s][Wel[1]];
        for(int t=0;t<c2;t++) s=addt[s][Wel[2]];
        for(int t=0;t<c3;t++) s=addt[s][Wel[3]];
        SW[j][s]=1; }
    for(int i=0;i<=9;i++) for(int j=0;j+i<=9;j++) for(int x=0;x<N;x++) if(SW[j][x]) F[i][neg[x]]=1;

    long long npairs=0, nT=0, four=0, notfour=0;
    static unsigned char reach[11][10][N];
    memset(reach,0,sizeof(reach)); reach[0][0][0]=1;
    int V[10]; int st[11]; int d=0; st[0]=1;
    while(d>=0){
        if(d==10){
            int s=0; for(int i=0;i<10;i++) s=addt[s][V[i]];
            if(s==0){
                npairs++;
                /* ---- stage 1b: enumerate 8-atoms U with T = U.V.W 7-short-free ---- */
                static unsigned char SVW[8][N], FU[8][N];
                memset(SVW,0,sizeof(SVW)); memset(FU,0,sizeof(FU));
                /* sums by size <=7 of the multiset V.W */
                static unsigned char cur[8][N], nxt[8][N];
                memset(cur,0,sizeof(cur)); cur[0][0]=1;
                int items[64], ni=0;
                for(int i=0;i<4;i++) for(int q=0;q<Wm[i];q++) items[ni++]=Wel[i];
                for(int i=0;i<10;i++) items[ni++]=V[i];
                for(int t=0;t<ni;t++){
                    memcpy(nxt,cur,sizeof(cur));
                    for(int i=7;i>=1;i--) for(int x=0;x<N;x++) if(cur[i-1][x]) nxt[i][addt[x][items[t]]]=1;
                    memcpy(cur,nxt,sizeof(cur));
                }
                memcpy(SVW,cur,sizeof(cur));
                for(int i=0;i<=7;i++) for(int j=0;j+i<=7;j++) for(int x=0;x<N;x++) if(SVW[j][x]) FU[i][neg[x]]=1;
                /* DFS over U */
                static unsigned char ur[9][8][N];
                memset(ur,0,sizeof(ur)); ur[0][0][0]=1;
                int U[8], ust[9], e=0; ust[0]=1;
                while(e>=0){
                    if(e==8){
                        int su=0; for(int i=0;i<8;i++) su=addt[su][U[i]];
                        if(su==0){
                            nT++;
                            ns=0; total=0;
                            for(int i=0;i<ni;i++){ add_elem(items[i]); total++; }
                            for(int i=0;i<8;i++){ add_elem(U[i]); total++; }
                            for(int i=0;i<ns;i++) rem[i]=mul[i];
                            if(part(4)) four++; else { notfour++;
                                printf("NO-FOUR-PACK a=%d T:",a);
                                for(int i=0;i<ns;i++) printf(" %d^%d",sup[i],mul[i]);
                                printf("\n"); fflush(stdout); }
                        }
                        e--; if(e>=0) ust[e]++; continue;
                    }
                    int gg=ust[e];
                    if(gg>=N){ e--; if(e>=0) ust[e]++; continue; }
                    int ok=1;
                    for(int i=0;i<=7;i++) memcpy(ur[e+1][i],ur[e][i],N);
                    for(int i=7;i>=1&&ok;i--)
                        for(int x=0;x<N;x++) if(ur[e][i-1][x]){ int y=addt[x][gg];
                            ur[e+1][i][y]=1; if(FU[i][y]) ok=0; }
                    if(ok){ U[e]=gg; e++; ust[e]=gg; } else ust[e]++;
                }
            }
            d--; if(d>=0) st[d]++; continue;
        }
        int gg=st[d];
        if(gg>=N){ d--; if(d>=0) st[d]++; continue; }
        int ok=1;
        for(int i=0;i<=9;i++) memcpy(reach[d+1][i],reach[d][i],N);
        for(int i=9;i>=1&&ok;i--)
            for(int x=0;x<N;x++) if(reach[d][i-1][x]){ int y=addt[x][gg];
                reach[d+1][i][y]=1; if(F[i][y]) ok=0; }
        if(ok){ V[d]=gg; d++; st[d]=gg; } else st[d]++;
    }
    printf("RESULT a=%d pairs=%lld T_candidates=%lld four_pack=%lld NO_four_pack=%lld\n",a,npairs,nT,four,notfour);
    return 0;
}
