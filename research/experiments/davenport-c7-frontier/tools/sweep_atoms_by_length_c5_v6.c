/* Reduce the 6,315,607 maximal atoms over C_5^3 to GL(3,5)-orbit representatives.
 *
 * Canonical form of an atom A: the lexicographic minimum, over every ordered
 * independent triple (x,y,z) drawn from the SUPPORT of A, of the sorted image of
 * A under the unique linear map sending (x,y,z) -> (e1,e2,e3).
 * Using the support rather than the 13 positions cuts the triples from <=1716 to
 * about |supp|^3. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#define P 5
static int ATOMLEN=13;
#define NG 125
static int addtab[NG][NG], negv[NG], vecs[NG][3];
static int mult[NG], chosen[16];
static long long natom, norbit;
static unsigned char reps[400000][16]; static int nreps;
static int ecand[NG], nec, emult[NG], echosen[64];
static long long nzs_total, sweep_nodes;
typedef struct { unsigned long long a[2]; } Msk5;
static inline int g5(Msk5*m,int i){return (m->a[i>>6]>>(i&63))&1ULL;}
static inline void s5(Msk5*m,int i){m->a[i>>6]|=1ULL<<(i&63);}
static void edfs(int start,int len,Msk5 S[5]){
    sweep_nodes++;
    if(len>=31){
        int s0=0,s1=0,s2=0;
        for(int q=0;q<len;q++){s0+=vecs[echosen[q]][0];s1+=vecs[echosen[q]][1];s2+=vecs[echosen[q]][2];}
        if(s0%P==0&&s1%P==0&&s2%P==0) nzs_total++;
        return;
    }
    int room=0; for(int i=start;i<nec;i++) room+=4-emult[ecand[i]];
    if(len+room<31) return;
    for(int i=start;i<nec;i++){
        int v=ecand[i]; if(emult[v]>=4) continue;
        int nv=negv[v],bad=0;
        for(int k=0;k<5&&!bad;k++) if(g5(&S[k],nv)) bad=1;
        if(bad) continue;
        Msk5 T[5]; memcpy(T,S,sizeof T);
        for(int k=4;k>=1;k--)
            for(int j=0;j<NG;j++) if(g5(&S[k-1],j)) s5(&T[k],addtab[j][v]);
        emult[v]++; echosen[len]=v; edfs(i,len+1,T); emult[v]--;
    }
}
static void sweep_one(unsigned char *U){
    Msk5 S[5]; memset(S,0,sizeof S); s5(&S[0],0);
    memset(emult,0,sizeof emult);
    for(int q=0;q<ATOMLEN;q++){
        int v=U[q]; Msk5 T[5]; memcpy(T,S,sizeof T);
        for(int k=4;k>=1;k--)
            for(int j=0;j<NG;j++) if(g5(&S[k-1],j)) s5(&T[k],addtab[j][v]);
        memcpy(S,T,sizeof S); emult[v]++; echosen[q]=v;
    }
    nec=0;
    for(int v=1;v<NG;v++){int nv=negv[v],bad=0;
        for(int k=0;k<5&&!bad;k++) if(g5(&S[k],nv)) bad=1;
        if(!bad) ecand[nec++]=v;}
    edfs(0,ATOMLEN,S);
}
/* hash set of canonical forms (13 bytes each) */
#define HB 22
#define HS (1<<HB)
static unsigned char *tab; static int used[HS]; static long long hcount;

static int inv5(int a){ static const int I[5]={0,1,3,2,4}; return I[a]; }

static int matinv(int m[3][3], int out[3][3]){
    int a=m[0][0],b=m[0][1],c=m[0][2],d=m[1][0],e=m[1][1],f=m[1][2],
        g=m[2][0],h=m[2][1],i=m[2][2];
    int A=(e*i-f*h)%P, B=(c*h-b*i)%P, C=(b*f-c*e)%P;
    int D=(f*g-d*i)%P, E=(a*i-c*g)%P, F=(c*d-a*f)%P;
    int G=(d*h-e*g)%P, H=(b*g-a*h)%P, I2=(a*e-b*d)%P;
    int det=(a*A+b*D+c*G)%P; det=((det%P)+P)%P;
    if(!det) return 0;
    int di=inv5(det);
    int t[3][3]={{A,B,C},{D,E,F},{G,H,I2}};
    for(int r=0;r<3;r++)for(int s=0;s<3;s++) out[r][s]=((t[r][s]%P)+P)%P*di%P;
    return 1;
}

static void canon(int *A, unsigned char *best){
    const int AL=ATOMLEN;
    int sup[16], ns=0, seen[NG]; memset(seen,0,sizeof seen);
    for(int q=0;q<AL;q++) if(!seen[A[q]]++) sup[ns++]=A[q];
    int have=0; unsigned char cur[16];
    for(int i=0;i<ns;i++)for(int j=0;j<ns;j++){ if(j==i) continue;
      for(int k=0;k<ns;k++){ if(k==i||k==j) continue;
        int m[3][3];
        for(int r=0;r<3;r++){ m[r][0]=vecs[sup[i]][r]; m[r][1]=vecs[sup[j]][r]; m[r][2]=vecs[sup[k]][r]; }
        int mi[3][3];
        if(!matinv(m,mi)) continue;
        /* map only the atom's own 13 elements, not all 125 vectors */
        for(int q=0;q<AL;q++){
            int v=A[q], o0,o1,o2;
            o0=(mi[0][0]*vecs[v][0]+mi[0][1]*vecs[v][1]+mi[0][2]*vecs[v][2])%P;
            o1=(mi[1][0]*vecs[v][0]+mi[1][1]*vecs[v][1]+mi[1][2]*vecs[v][2])%P;
            o2=(mi[2][0]*vecs[v][0]+mi[2][1]*vecs[v][1]+mi[2][2]*vecs[v][2])%P;
            cur[q]=(unsigned char)(o0*25+o1*5+o2);
        }
        for(int x=1;x<AL;x++){ unsigned char t=cur[x]; int y=x-1;
            while(y>=0&&cur[y]>t){cur[y+1]=cur[y];y--;} cur[y+1]=t; }
        if(!have||memcmp(cur,best,AL)<0){ memcpy(best,cur,AL); have=1; }
      }}
}

static unsigned long long h64(unsigned char*p){
    unsigned long long h=1469598103934665603ULL;
    for(int i=0;i<16;i++){h^=p[i];h*=1099511628211ULL;}
    return h;
}
static int insert(unsigned char*c){
    unsigned long long h=h64(c); size_t i=h&(HS-1);
    while(used[i]){ if(!memcmp(tab+16*i,c,16)) return 0; i=(i+1)&(HS-1); }
    used[i]=1; memcpy(tab+16*i,c,16); hcount++; return 1;
}

static void dfs(int start,int len,unsigned long long S[2]){
    if(len==ATOMLEN-1){
        int s0=0,s1=0,s2=0;
        for(int q=0;q<ATOMLEN-1;q++){s0+=vecs[chosen[q]][0];s1+=vecs[chosen[q]][1];s2+=vecs[chosen[q]][2];}
        int w=((P-s0%P)%P)*25+((P-s1%P)%P)*5+((P-s2%P)%P);
        if(!w) return;
        natom++;
        int A[16]; for(int q=0;q<ATOMLEN-1;q++) A[q]=chosen[q]; A[ATOMLEN-1]=w;
        unsigned char c[16]; memset(c,0,16); canon(A,c);
        if(insert(c)){ norbit++; if(nreps<400000) memcpy(reps[nreps++],c,16); }
        return;
    }
    for(int i=start;i<NG;i++){
        if(mult[i]>=4) continue;
        int nv=negv[i];
        if((S[nv>>6]>>(nv&63))&1ULL) continue;
        unsigned long long T[2]={S[0],S[1]};
        for(int q=0;q<NG;q++) if((S[q>>6]>>(q&63))&1ULL){int z=addtab[q][i];T[z>>6]|=1ULL<<(z&63);}
        mult[i]++; chosen[len]=i; dfs(i,len+1,T); mult[i]--;
    }
}
int main(int argc,char**argv){
    if(argc>1) ATOMLEN=atoi(argv[1]);
    tab=calloc(HS,16);
    for(int i=0;i<NG;i++){vecs[i][0]=i/25;vecs[i][1]=(i/5)%5;vecs[i][2]=i%5;}
    for(int i=0;i<NG;i++){int n[3];for(int t=0;t<3;t++)n[t]=(P-vecs[i][t])%P;
        negv[i]=n[0]*25+n[1]*5+n[2];
        for(int j=0;j<NG;j++){int s[3];for(int t=0;t<3;t++)s[t]=(vecs[i][t]+vecs[j][t])%P;
            addtab[i][j]=s[0]*25+s[1]*5+s[2];}}
    unsigned long long S[2]={1ULL,0ULL};
    int init[3]={25,5,1};
    for(int q=0;q<3;q++){int v=init[q];unsigned long long T[2]={S[0],S[1]};
        for(int j=0;j<NG;j++) if((S[j>>6]>>(j&63))&1ULL){int z=addtab[j][v];T[z>>6]|=1ULL<<(z&63);}
        S[0]=T[0];S[1]=T[1]; mult[v]++; chosen[q]=v;}
    clock_t t0=clock();
    dfs(0,3,S);
    printf("atoms of length %d: %lld", ATOMLEN, 0LL), printf("\r"), printf("atoms %lld -> GL(3,5) ORBITS %lld   (%.1fs)\n",
           natom, norbit, (double)(clock()-t0)/CLOCKS_PER_SEC);
    fflush(stdout);
    clock_t t1=clock(); nzs_total=0; sweep_nodes=0;
    for(int i=0;i<nreps;i++) sweep_one(reps[i]);
    printf("SWEEP over %d orbit representatives: %lld nodes, %.1fs\n",
           nreps, sweep_nodes, (double)(clock()-t1)/CLOCKS_PER_SEC);
    printf("ZERO-SUM 5-SHORT-FREE LENGTH-31 COMPLETIONS FOUND: %lld\n", nzs_total);
    return 0;
}
