/* pair.c - independent count of 10-atom companions V to a canonical support-4 19-atom W
 * over C_7^3, subject to: W.V has no nonempty zero-sum subsequence of length <= 9.
 *
 * W has support {e1,e2,e3,g4} with multiplicities (a, 7-a, 6, 6) and g4 = (a, 7-a, 6),
 * the three canonical types of SUPPORT4_MAXIMAL_ATOM_WEIGHTS_V1 at p=7 (a = 1,2,3).
 *
 * Condition, spelled out: for every pair of sub-multisets A_V <= V, A_W <= W with
 * |A_V|+|A_W| <= 9 and not both empty, sigma(A_V)+sigma(A_W) != 0.  Equivalently, for each
 * i, the i-element subsums of V must avoid  F[i] = union_{j<=9-i} ( -sigma_j(W) ).
 * Usage: pair a   (a = 1, 2, 3)
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define P 7
#define N 343
#ifndef K
#define K 10          /* |V|; override with -DK= for other corridors */
#endif
#ifndef S
#define S 9           /* short-free bound on the pair = |VW| - D - 1; -DS= to override */
#endif

static int addt[N][N], neg[N];
static unsigned char SW[S+1][N];   /* SW[j][x] : x is a sum of some j-element sub-multiset of W */
static unsigned char F[S+1][N];    /* forbidden sums for i-element subsums of V */
static int Wel[4], Wm[4];
static long long count = 0, nodes = 0;
static int V[K];
static unsigned char reach[K+1][S+1][N];

static int idx3(int x,int y,int z){ return x + P*y + P*P*z; }

static void build_tables(void){
    for (int a=0;a<N;a++){
        int ax=a%P, ay=(a/P)%P, az=a/(P*P);
        neg[a]=idx3((P-ax)%P,(P-ay)%P,(P-az)%P);
        for (int b=0;b<N;b++){
            int bx=b%P, by=(b/P)%P, bz=b/(P*P);
            addt[a][b]=idx3((ax+bx)%P,(ay+by)%P,(az+bz)%P);
        }
    }
}

int main(int argc,char**argv){
    int a=atoi(argv[1]);
    build_tables();
    /* W: e1^a e2^(7-a) e3^6 g4^6 with g4=(a,7-a,6) */
    Wel[0]=idx3(1,0,0); Wm[0]=a;
    Wel[1]=idx3(0,1,0); Wm[1]=P-a;
    Wel[2]=idx3(0,0,1); Wm[2]=P-1;
    Wel[3]=idx3(a%P,(P-a)%P,(P-1)%P); Wm[3]=P-1;
    int tot=0; for(int i=0;i<4;i++) tot+=Wm[i];
    /* sanity: W is zero-sum of length 3p-2 = 19 */
    int sw=0; for(int i=0;i<4;i++) for(int c=0;c<Wm[i];c++) sw=addt[sw][Wel[i]];
    fprintf(stderr,"a=%d: W = %d^%d %d^%d %d^%d %d^%d, |W|=%d, sigma(W)=%d\n",
            a,Wel[0],Wm[0],Wel[1],Wm[1],Wel[2],Wm[2],Wel[3],Wm[3],tot,sw);
    if(tot!=3*P-2 || sw!=0){ fprintf(stderr,"BAD W\n"); return 2; }

    /* SW[j] */
    for(int c0=0;c0<=Wm[0];c0++)for(int c1=0;c1<=Wm[1];c1++)for(int c2=0;c2<=Wm[2];c2++)for(int c3=0;c3<=Wm[3];c3++){
        int j=c0+c1+c2+c3; if(j>S) continue;
        int s=0;
        for(int t=0;t<c0;t++) s=addt[s][Wel[0]];
        for(int t=0;t<c1;t++) s=addt[s][Wel[1]];
        for(int t=0;t<c2;t++) s=addt[s][Wel[2]];
        for(int t=0;t<c3;t++) s=addt[s][Wel[3]];
        SW[j][s]=1;
    }
    /* F[i] = union_{j=0..9-i} -SW[j] */
    for(int i=0;i<=S;i++) for(int j=0;j+i<=S;j++) for(int x=0;x<N;x++) if(SW[j][x]) F[i][neg[x]]=1;

    /* DFS over V: 10 elements in nondecreasing index order, elements 1..N-1 */
    memset(reach,0,sizeof(reach));
    reach[0][0][0]=1;
    int stack_lo[K+1]; stack_lo[0]=1;
    /* iterative-free: simple recursion via explicit function */
    /* (recursive lambda not available in C; use a nested function-free approach) */
    int d=0; int g=1; int path[K+1]; path[0]=1;
    /* explicit stack DFS */
    struct { int g; } st[K+1];
    st[0].g=1;
    while(d>=0){
        if(d==K){
            /* full: require zero sum */
            int s=0; for(int i=0;i<K;i++) s=addt[s][V[i]];
            if(s==0) count++;
            d--; if(d>=0) st[d].g++;
            continue;
        }
        int gg=st[d].g;
        if(gg>=N){ d--; if(d>=0) st[d].g++; continue; }
        nodes++;
        /* try element gg */
        int ok=1;
        for(int i=0;i<=S;i++) memcpy(reach[d+1][i],reach[d][i],N);
        for(int i=S;i>=1 && ok;i--){
            for(int x=0;x<N;x++) if(reach[d][i-1][x]){
                int y=addt[x][gg];
                if(!reach[d+1][i][y]){ reach[d+1][i][y]=1; if(F[i][y]) ok=0; }
                else if(F[i][y]) ok=0;
            }
        }
        if(ok){
            V[d]=gg;
            d++;
            st[d].g=gg;      /* nondecreasing */
        } else {
            st[d].g++;
        }
    }
    printf("a=%d companions=%lld nodes=%lld\n",a,count,nodes);
    return 0;
}
