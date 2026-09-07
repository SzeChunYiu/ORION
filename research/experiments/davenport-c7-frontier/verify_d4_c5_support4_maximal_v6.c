/* Checker for D4_C5_SUPPORT4_MAXIMAL_CLOSURE_V6.md.
 *
 * THEOREM.  No length-31 zero-sum 5-short-free sequence over C_5^3 contains a
 * maximal atom of support four.  Hence the (6,6,6,13) profile of the
 * D_4(C_5^3) = 31 corridor requires a 13-atom of support at least five.
 *
 * By the support-four maximal-atom classification, every such atom is, up to
 * GL(3,5), U = e1^4 e2^4 e3^a g4^(5-a) with a in {1,2}, g4 = e3 - a^{-1}(e1+e2).
 * "Contains a support-four maximal atom" is GL-invariant, so the two canonical
 * types suffice.
 *
 * Method: exhaustively enumerate every 5-short-free multiset of length 31
 * containing U, and report how many are zero-sum.  Controls printed: the total
 * number of length-31 extensions (must be > 0, else the test is vacuous) and
 * how many distinct total-sums they realise.
 *
 * Largest 5-short-free multiset over C_5^3 containing a canonical maximal atom U.
 * If that maximum is < 31, the (6,6,6,13) profile of the D_4(C_5^3) corridor is
 * eliminated for support-four maximal atoms.
 *
 * State: S_k = set of sums of k-element sub-multisets, k = 0..4, as 125-bit masks.
 * Adding v is legal iff -v is in none of S_0..S_4 (a zero-sum of length <= 5
 * through v would be exactly that).  Update S_k |= (S_{k-1} shifted by +v).
 */
#include <stdio.h>
#include <string.h>

#define P 5
#define NG 125
typedef struct { unsigned long long a[2]; } Msk;   /* 125 bits */

static int addtab[NG][NG];
static int negv[NG];
static int cand[NG], ncand;
static int best; static long long nsol, ntot; static long long sumhist[125]; static int sumv; static int chosen[64];
static int mult[NG];

static inline int get(Msk *m,int i){ return (m->a[i>>6]>>(i&63))&1ULL; }
static inline void set(Msk *m,int i){ m->a[i>>6] |= 1ULL<<(i&63); }

static void shift_or(Msk *dst, const Msk *src, int v){
    for(int i=0;i<NG;i++) if(get((Msk*)src,i)) set(dst, addtab[i][v]);
}

static int vecs[NG][3];
static void dfs(int start, int len, Msk S[5]){
    if(len>best){ best=len; }
    if(len>=31){
        ntot++;
        int s0=0,s1=0,s2=0;
        for(int q=0;q<len;q++){ s0+=vecs[chosen[q]][0]; s1+=vecs[chosen[q]][1]; s2+=vecs[chosen[q]][2]; }
        sumhist[(s0%P)*25+(s1%P)*5+(s2%P)]++;
        if(s0%P==0 && s1%P==0 && s2%P==0){
            nsol++;
            if(nsol<=3){
                printf("   zero-sum length-31 witness #%lld:", nsol);
                for(int q=13;q<len;q++) printf(" %d", chosen[q]);
                printf("\n");
            }
        }
        return;
    }
    /* optimistic bound: every remaining candidate usable, each at most 4 times */
    int room=0;
    for(int i=start;i<ncand;i++) room += 4-mult[cand[i]];
    if(len+room<=best) return;
    for(int i=start;i<ncand;i++){
        int v=cand[i];
        if(mult[v]>=4) continue;
        int nv=negv[v];
        int bad=0;
        for(int k=0;k<5 && !bad;k++) if(get(&S[k],nv)) bad=1;
        if(bad) continue;
        Msk T[5]; memcpy(T,S,sizeof T);
        for(int k=4;k>=1;k--) shift_or(&T[k],&S[k-1],v);
        mult[v]++; chosen[len]=v;
        dfs(i,len+1,T);
        mult[v]--;
    }
}

int main(void){
    int (*vec)[3]=vecs;
    for(int i=0;i<NG;i++){ vec[i][0]=i/25; vec[i][1]=(i/5)%5; vec[i][2]=i%5; }
    for(int i=0;i<NG;i++){
        int n[3]; for(int t=0;t<3;t++) n[t]=(P-vec[i][t])%P;
        negv[i]=n[0]*25+n[1]*5+n[2];
        for(int j=0;j<NG;j++){
            int s[3]; for(int t=0;t<3;t++) s[t]=(vec[i][t]+vec[j][t])%P;
            addtab[i][j]=s[0]*25+s[1]*5+s[2];
        }
    }
    int idx=(int[]){0}[0];
    for(int a=1;a<=2;a++){
        int ai = (a==1)?1:3;                    /* inverse of a mod 5 */
        int e1=1*25, e2=1*5, e3=1;
        int g4v[3]={(0-ai*(1+0))%P,(0-ai*(0+1))%P,1};
        for(int t=0;t<3;t++) g4v[t]=((g4v[t]%P)+P)%P;
        int g4=g4v[0]*25+g4v[1]*5+g4v[2];
        int U[13],n=0;
        for(int t=0;t<4;t++) U[n++]=e1;
        for(int t=0;t<4;t++) U[n++]=e2;
        for(int t=0;t<a;t++) U[n++]=e3;
        for(int t=0;t<P-a;t++) U[n++]=g4;
        Msk S[5]; memset(S,0,sizeof S); set(&S[0],0);
        memset(mult,0,sizeof mult);
        int okU=1;
        for(int q=0;q<13;q++){
            int v=U[q], nv=negv[v], bad=0;
            for(int k=0;k<5&&!bad;k++) if(get(&S[k],nv)) bad=1;
            if(bad){ okU=0; break; }
            Msk T[5]; memcpy(T,S,sizeof T);
            for(int k=4;k>=1;k--) shift_or(&T[k],&S[k-1],v);
            memcpy(S,T,sizeof S); mult[v]++;
        }
        /* candidates: everything still legal as a single addition */
        ncand=0;
        for(int v=1;v<NG;v++){
            int nv=negv[v], bad=0;
            for(int k=0;k<5&&!bad;k++) if(get(&S[k],nv)) bad=1;
            if(!bad) cand[ncand++]=v;
        }
        best=13; nsol=0; ntot=0; for(int q=0;q<125;q++) sumhist[q]=0;
        for(int q=0;q<13;q++) chosen[q]=U[q];
        dfs(0,13,S);
        { long long nz=0; int distinct=0;
          for(int q=0;q<125;q++) if(sumhist[q]){ distinct++; }
          printf("a=%d: candidates %d ; max length %d ; TOTAL length-31 5-short-free "
                 "extensions: %lld ; of these zero-sum: %lld ; distinct total-sums "
                 "realised: %d of 125\n", a, ncand, best, ntot, nsol, distinct);
          (void)nz; }
        (void)idx;
    }
    return 0;
}
