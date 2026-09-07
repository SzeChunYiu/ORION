/* boxmax.c — for a fixed support {v_1..v_k} in F_p^3 and caps M_i, run the zero-sum packing DP
 * over the whole box and report, for each j, the maximum total length |m| with packing(m) <= j,
 * plus a witness. Usage: boxmax p k  v1x v1y v1z ... vkx vky vkz  M1 ... Mk [--jmax J] [--list j L]
 * --list j L : print every m with |m| = L and packing(m) <= j.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#define MAXK 14
int main(int argc,char**argv){
    int p=atoi(argv[1]), k=atoi(argv[2]); int a=3; int V[MAXK][3], M[MAXK];
    for(int i=0;i<k;i++){V[i][0]=atoi(argv[a++]);V[i][1]=atoi(argv[a++]);V[i][2]=atoi(argv[a++]);}
    for(int i=0;i<k;i++) M[i]=atoi(argv[a++]);
    int jmax=6, listj=-1, listL=-1;
    for(;a<argc;a++){ if(!strcmp(argv[a],"--jmax")) jmax=atoi(argv[++a]); else if(!strcmp(argv[a],"--list")){ listj=atoi(argv[++a]); listL=atoi(argv[++a]); } }
    uint64_t R[MAXK+1]; R[0]=1; for(int i=0;i<k;i++) R[i+1]=R[i]*(M[i]+1); uint64_t NS=R[k];
    uint8_t *zs=malloc(NS), *H=malloc(NS), *P=malloc(NS), *len=malloc(NS);
    /* digits via incremental counter */
    int r[MAXK]; memset(r,0,sizeof(r));
    for(uint64_t idx=0; idx<NS; idx++){
        int s0=0,s1=0,s2=0,L=0; for(int i=0;i<k;i++){ s0+=r[i]*V[i][0]; s1+=r[i]*V[i][1]; s2+=r[i]*V[i][2]; L+=r[i]; }
        zs[idx]=(s0%p==0&&s1%p==0&&s2%p==0); len[idx]=L;
        /* increment mixed radix */
        for(int i=0;i<k;i++){ if(++r[i]<=M[i]) break; r[i]=0; }
    }
    zs[0]=0;
    memset(r,0,sizeof(r));
    for(uint64_t idx=0; idx<NS; idx++){
        uint8_t h=0; for(int i=0;i<k&&!h;i++) if(r[i]>0){ uint64_t j=idx-R[i]; if(zs[j]||H[j]) h=1; }
        H[idx]=h;
        for(int i=0;i<k;i++){ if(++r[i]<=M[i]) break; r[i]=0; }
    }
    int na=0; for(uint64_t idx=1; idx<NS; idx++) if(zs[idx]&&!H[idx]) na++;
    uint64_t *atoms=malloc(sizeof(uint64_t)*na); uint8_t (*ad)[MAXK]=malloc(sizeof(uint8_t[MAXK])*na); int t=0;
    memset(r,0,sizeof(r));
    for(uint64_t idx=0; idx<NS; idx++){ if(idx&&zs[idx]&&!H[idx]){ atoms[t]=idx; for(int i=0;i<k;i++) ad[t][i]=r[i]; t++; } for(int i=0;i<k;i++){ if(++r[i]<=M[i]) break; r[i]=0; } }
    memset(P,0,NS); memset(r,0,sizeof(r));
    for(uint64_t idx=0; idx<NS; idx++){
        uint8_t best=0;
        for(int q=0;q<na;q++){ uint64_t b=atoms[q]; if(b>idx) break; int ok=1; for(int i=0;i<k;i++) if(ad[q][i]>r[i]){ok=0;break;} if(!ok) continue; uint8_t c=1+P[idx-b]; if(c>best) best=c; }
        P[idx]=best;
        for(int i=0;i<k;i++){ if(++r[i]<=M[i]) break; r[i]=0; }
    }
    /* report */
    int bestL[16]; uint64_t bestIdx[16]; for(int j=0;j<16;j++){bestL[j]=-1;bestIdx[j]=0;}
    memset(r,0,sizeof(r));
    for(uint64_t idx=0; idx<NS; idx++){
        int j=P[idx]; if(j<16 && len[idx]>bestL[j]){ bestL[j]=len[idx]; bestIdx[j]=idx; }
        if(listj>=0 && P[idx]<=listj && len[idx]==listL){ printf("list packing=%d len=%d m=",P[idx],listL); for(int i=0;i<k;i++) printf(" %d",r[i]); printf("\n"); }
        for(int i=0;i<k;i++){ if(++r[i]<=M[i]) break; r[i]=0; }
    }
    printf("support:"); for(int i=0;i<k;i++) printf(" (%d,%d,%d)",V[i][0],V[i][1],V[i][2]); printf("  caps:"); for(int i=0;i<k;i++) printf(" %d",M[i]); printf("  states=%llu atoms=%d\n",(unsigned long long)NS,na);
    /* max length with packing <= j is max over j'<=j */
    int run=-1;
    for(int j=0;j<=jmax;j++){ if(bestL[j]>run) run=bestL[j]; uint64_t idx=bestIdx[j]; 
        printf("maxlen(packing<=%d) = %d", j, run);
        if(bestL[j]==run && bestL[j]>=0){ printf("  witness(packing=%d):",j); uint64_t tt=idx; for(int i=0;i<k;i++){ printf(" %d", (int)(tt%(M[i]+1))); tt/=(M[i]+1);} }
        printf("\n"); }
    return 0;
}
