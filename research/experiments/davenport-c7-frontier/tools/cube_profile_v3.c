/* cubeprofile.c — exact packing profile of the nonzero binary cube in C_n^3, for ANY odd n.
 * Mixed-radix DP over the whole box [0,n-1]^7 of multiplicity vectors on
 *   Q = (e1, e2, e3, e12, e13, e23, e123).
 * Reports, for each j:
 *   c_j(n) = max{ |m| : m in box, pk(m) <= j }        (unrestricted)
 *   z_j(n) = max{ |m| : m in box, m zero-sum, pk(m) <= j }
 * with a witness for each, plus the packing number of the full cube.
 * Usage: cubeprofile n [jmax]
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

int main(int argc, char **argv){
    int n = atoi(argv[1]); int jmax = atoi(argv[2]); int k = atoi(argv[3]);
    int V[12][3]; { int a=4; for(int i=0;i<k;i++){ V[i][0]=atoi(argv[a++]); V[i][1]=atoi(argv[a++]); V[i][2]=atoi(argv[a++]); } }
    int cap = n-1;
    uint64_t R[13]; R[0]=1; for(int i=0;i<k;i++) R[i+1]=R[i]*(cap+1);
    uint64_t NS = R[k];
    uint8_t *zs=malloc(NS), *H=malloc(NS), *P=malloc(NS); uint8_t *len=malloc(NS);
    if(!zs||!H||!P||!len){ fprintf(stderr,"alloc failed for %llu states\n",(unsigned long long)NS); return 1; }
    int r[12]; memset(r,0,sizeof(r));
    for(uint64_t idx=0; idx<NS; idx++){
        int s0=0,s1=0,s2=0,L=0;
        for(int i=0;i<k;i++){ s0+=r[i]*V[i][0]; s1+=r[i]*V[i][1]; s2+=r[i]*V[i][2]; L+=r[i]; }
        zs[idx] = (s0%n==0 && s1%n==0 && s2%n==0); len[idx]=L;
        for(int i=0;i<k;i++){ if(++r[i]<=cap) break; r[i]=0; }
    }
    zs[0]=0;
    memset(r,0,sizeof(r));
    for(uint64_t idx=0; idx<NS; idx++){
        uint8_t h=0; for(int i=0;i<k && !h;i++) if(r[i]>0){ uint64_t j=idx-R[i]; if(zs[j]||H[j]) h=1; }
        H[idx]=h;
        for(int i=0;i<k;i++){ if(++r[i]<=cap) break; r[i]=0; }
    }
    int na=0; for(uint64_t idx=1; idx<NS; idx++) if(zs[idx]&&!H[idx]) na++;
    uint64_t *atoms=malloc(sizeof(uint64_t)*(na?na:1)); uint8_t (*ad)[12]=malloc(sizeof(uint8_t[12])*(na?na:1)); int t=0;
    memset(r,0,sizeof(r));
    for(uint64_t idx=0; idx<NS; idx++){ if(idx&&zs[idx]&&!H[idx]){ atoms[t]=idx; for(int i=0;i<k;i++) ad[t][i]=r[i]; t++; }
        for(int i=0;i<k;i++){ if(++r[i]<=cap) break; r[i]=0; } }
    memset(P,0,NS); memset(r,0,sizeof(r));
    for(uint64_t idx=0; idx<NS; idx++){
        uint8_t best=0;
        for(int q=0;q<na;q++){ uint64_t b=atoms[q]; if(b>idx) break; int ok=1;
            for(int i=0;i<k;i++) if(ad[q][i]>r[i]){ok=0;break;}
            if(!ok) continue; uint8_t c=1+P[idx-b]; if(c>best) best=c; }
        P[idx]=best;
        for(int i=0;i<k;i++){ if(++r[i]<=cap) break; r[i]=0; }
    }
    int bc[16], bz[16]; uint64_t wc[16], wz[16];
    for(int j=0;j<16;j++){ bc[j]=-1; bz[j]=-1; wc[j]=0; wz[j]=0; }
    for(uint64_t idx=0; idx<NS; idx++){
        int j=P[idx]; if(j<16){ if(len[idx]>bc[j]){ bc[j]=len[idx]; wc[j]=idx; }
            if(zs[idx] && len[idx]>bz[j]){ bz[j]=len[idx]; wz[j]=idx; } }
    }
    printf("n=%d k=%d states=%llu atoms=%d pk(full)=%d\n", n, k, (unsigned long long)NS, na, P[NS-1]);
    int runc=-1, runz=-1;
    for(int j=0;j<=jmax;j++){
        int pc = bc[j]>runc ? bc[j] : runc; int pz = bz[j]>runz ? bz[j] : runz;
        printf("c_%d(%d) = %3d", j, n, pc);
        if(bc[j]==pc && bc[j]>=0){ uint64_t x=wc[j]; printf("  witness:"); for(int i=0;i<k;i++){ printf(" %d",(int)(x%(cap+1))); x/=(cap+1);} }
        printf("   |   z_%d(%d) = %3d", j, n, pz);
        if(bz[j]==pz && bz[j]>=0){ uint64_t x=wz[j]; printf("  witness:"); for(int i=0;i<k;i++){ printf(" %d",(int)(x%(cap+1))); x/=(cap+1);} }
        printf("\n");
        runc=pc; runz=pz;
    }
    return 0;
}
