/* GL(3,5)-canonicalization of length-L sequences over F_5^3 with rank-3 support.
 * Canonical form C(S) = lex-min over ordered independent triples T from supp(S)
 * of sort_ascending( A_T(S) ), where A_T is the unique g in GL(3,5) with
 * g(T) = (e1,e2,e3).   Row-vector convention: v |-> v*M, V*M = I  =>  M = V^{-1}.
 * Also emits |Stab(C)| = #{ordered indep triples T' in supp(C) : A_{T'}(C) = C}
 * and N(C) = #{ordered indep triples in supp(C) with m(u1)<=m(u2)<=m(u3)}.  */
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#define MAXL 32
static int L = 19;
static int INV5[5] = {0,1,3,2,4};      /* multiplicative inverses mod 5 (INV5[0] unused) */

static inline int m5(int x){ x%=5; if(x<0)x+=5; return x; }

/* decode code -> row vector */
static inline void dec(int c,int*v){ v[0]=c/25; v[1]=(c/5)%5; v[2]=c%5; }
static inline int enc(int a,int b,int c){ return 25*a+5*b+c; }

/* 3x3 inverse mod 5 via adjugate.  returns 0 if singular. */
static int inv3(const int A[3][3], int B[3][3]){
    int d = A[0][0]*(A[1][1]*A[2][2]-A[1][2]*A[2][1])
          - A[0][1]*(A[1][0]*A[2][2]-A[1][2]*A[2][0])
          + A[0][2]*(A[1][0]*A[2][1]-A[1][1]*A[2][0]);
    d = m5(d);
    if(!d) return 0;
    int id = INV5[d];
    /* adj(A)_{ij} = cofactor_{ji} */
    int C[3][3];
    C[0][0]= A[1][1]*A[2][2]-A[1][2]*A[2][1];
    C[0][1]=-(A[1][0]*A[2][2]-A[1][2]*A[2][0]);
    C[0][2]= A[1][0]*A[2][1]-A[1][1]*A[2][0];
    C[1][0]=-(A[0][1]*A[2][2]-A[0][2]*A[2][1]);
    C[1][1]= A[0][0]*A[2][2]-A[0][2]*A[2][0];
    C[1][2]=-(A[0][0]*A[2][1]-A[0][1]*A[2][0]);
    C[2][0]= A[0][1]*A[1][2]-A[0][2]*A[1][1];
    C[2][1]=-(A[0][0]*A[1][2]-A[0][2]*A[1][0]);
    C[2][2]= A[0][0]*A[1][1]-A[0][1]*A[1][0];
    for(int i=0;i<3;i++) for(int j=0;j<3;j++) B[i][j]=m5(m5(C[j][i])*id);
    return 1;
}

/* --- per-sequence workspace --- */
static int supc[MAXL], supm[MAXL], K;      /* support codes (ascending) + mults */
static int supv[MAXL][3];

static void build_support(const int*seq,int n){
    int cnt[125]; memset(cnt,0,sizeof(cnt));
    for(int i=0;i<n;i++) cnt[seq[i]]++;
    K=0;
    for(int c=1;c<125;c++) if(cnt[c]){ supc[K]=c; supm[K]=cnt[c]; dec(c,supv[K]); K++; }
}

typedef struct { int code, mult; } PM;
static int cmp_pm(const void*a,const void*b){ return ((PM*)a)->code - ((PM*)b)->code; }

/* apply M to current support, expand to sorted length-n code list in out[] */
static void image(const int M[3][3], int*out){
    PM p[MAXL];
    for(int i=0;i<K;i++){
        int a=m5(supv[i][0]*M[0][0]+supv[i][1]*M[1][0]+supv[i][2]*M[2][0]);
        int b=m5(supv[i][0]*M[0][1]+supv[i][1]*M[1][1]+supv[i][2]*M[2][1]);
        int c=m5(supv[i][0]*M[0][2]+supv[i][1]*M[1][2]+supv[i][2]*M[2][2]);
        p[i].code=enc(a,b,c); p[i].mult=supm[i];
    }
    qsort(p,K,sizeof(PM),cmp_pm);
    int t=0;
    for(int i=0;i<K;i++) for(int r=0;r<p[i].mult;r++) out[t++]=p[i].code;
}

/* canonicalize seq (length n) into can[]; returns number of independent triples tried */
static long canonicalize(const int*seq,int n,int*can){
    build_support(seq,n);
    int best[MAXL], cur[MAXL]; int have=0; long tried=0;
    for(int i=0;i<K;i++) for(int j=0;j<K;j++){ if(j==i) continue;
      for(int l=0;l<K;l++){ if(l==i||l==j) continue;
        int V[3][3],M[3][3];
        memcpy(V[0],supv[i],3*sizeof(int));
        memcpy(V[1],supv[j],3*sizeof(int));
        memcpy(V[2],supv[l],3*sizeof(int));
        if(!inv3(V,M)) continue;
        tried++;
        image(M,cur);
        if(!have || memcmp(cur,best,n*sizeof(int))<0){ memcpy(best,cur,n*sizeof(int)); have=1; }
      }}
    memcpy(can,best,n*sizeof(int));
    return have? tried : -1;
}

/* |Stab(C)| for a canonical form C (already the sorted expansion) */
static long stab_of(const int*C,int n){
    build_support(C,n);
    int cur[MAXL]; long s=0;
    for(int i=0;i<K;i++) for(int j=0;j<K;j++){ if(j==i) continue;
      for(int l=0;l<K;l++){ if(l==i||l==j) continue;
        int V[3][3],M[3][3];
        memcpy(V[0],supv[i],3*sizeof(int));
        memcpy(V[1],supv[j],3*sizeof(int));
        memcpy(V[2],supv[l],3*sizeof(int));
        if(!inv3(V,M)) continue;
        image(M,cur);
        if(!memcmp(cur,C,n*sizeof(int))) s++;
      }}
    return s;
}

/* N(C) = # ordered indep triples in supp(C) with m(u1)<=m(u2)<=m(u3) */
static long normcount(const int*C,int n){
    build_support(C,n);
    long s=0;
    for(int i=0;i<K;i++) for(int j=0;j<K;j++){ if(j==i) continue;
      for(int l=0;l<K;l++){ if(l==i||l==j) continue;
        if(!(supm[i]<=supm[j] && supm[j]<=supm[l])) continue;
        int V[3][3],M[3][3];
        memcpy(V[0],supv[i],3*sizeof(int));
        memcpy(V[1],supv[j],3*sizeof(int));
        memcpy(V[2],supv[l],3*sizeof(int));
        if(!inv3(V,M)) continue;
        s++;
      }}
    return s;
}

int main(int argc,char**argv){
    /* modes: canon  (stdin lines -> canonical form per line)
              stab   (stdin lines are canonical forms -> print stab and normcount) */
    const char*mode = argc>1? argv[1] : "canon";
    if(argc>2) L=atoi(argv[2]);
    char line[8192]; int seq[MAXL], can[MAXL];
    while(fgets(line,sizeof(line),stdin)){
        int nv=0, ntot=0; char*p=line;
        while(*p){ if(*p=='['){ int a,b,c;
              if(sscanf(p,"[%d,%d,%d]",&a,&b,&c)==3){ ntot++; if(nv<L) seq[nv++]=enc(a,b,c);} } p++; }
        if(nv!=L || ntot!=L){ fprintf(stderr,"BAD LINE nv=%d ntot=%d (L=%d)\n",nv,ntot,L); return 2; }
        if(!strcmp(mode,"canon")){
            long t=canonicalize(seq,L,can);
            if(t<0){ fprintf(stderr,"RANK<3\n"); return 3; }
            for(int i=0;i<L;i++) printf("%s%d",i?" ":"",can[i]);
            printf("\n");
        } else {
            long s=stab_of(seq,L), nc=normcount(seq,L);
            printf("%ld %ld\n",s,nc);
        }
    }
    return 0;
}
