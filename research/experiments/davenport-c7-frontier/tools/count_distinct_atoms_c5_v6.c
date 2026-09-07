/* Is the enumeration generating each atom multiset ONCE?
 * A length-L atom M is zero-sum, so for EVERY element x of M, M\{x} sums to -x.
 * If M\{x} is also zero-sum-free, the DFS generates M with x as the completion.
 * So M is generated once per such x -- i.e. the raw count is (prefix,completion)
 * PAIRS, not distinct atoms.  Count distinct multisets to check. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define P 5
#define NG 125
static int addtab[NG][NG], negv[NG], vecs[NG][3];
static int mult[NG], chosen[16], AL=13;
static long long raw, distinct, badmult;
#define HB 24
#define HS (1<<HB)
static unsigned char *tab; static unsigned char *used;
static unsigned long long h64(unsigned char*p,int n){
    unsigned long long h=1469598103934665603ULL;
    for(int i=0;i<n;i++){h^=p[i];h*=1099511628211ULL;} return h;}
static int ins(unsigned char*c){
    unsigned long long h=h64(c,16); size_t i=h&(HS-1);
    while(used[i]){ if(!memcmp(tab+16*i,c,16)) return 0; i=(i+1)&(HS-1);} 
    used[i]=1; memcpy(tab+16*i,c,16); return 1;}
static void dfs(int start,int len,unsigned long long S[2]){
    if(len==AL-1){
        int s0=0,s1=0,s2=0;
        for(int q=0;q<AL-1;q++){s0+=vecs[chosen[q]][0];s1+=vecs[chosen[q]][1];s2+=vecs[chosen[q]][2];}
        int w=((P-s0%P)%P)*25+((P-s1%P)%P)*5+((P-s2%P)%P);
        if(!w) return;
        raw++;
        /* multiplicity check: w may push an element to 5 copies -> NOT an atom */
        int c5=1; for(int q=0;q<AL-1;q++) if(chosen[q]==w) c5++;
        if(c5>=5){ badmult++; return; }
        unsigned char m[16]; memset(m,0,16);
        for(int q=0;q<AL-1;q++) m[q]=(unsigned char)chosen[q];
        m[AL-1]=(unsigned char)w;
        for(int x=1;x<AL;x++){unsigned char t=m[x];int y=x-1;
            while(y>=0&&m[y]>t){m[y+1]=m[y];y--;} m[y+1]=t;}
        if(ins(m)) distinct++;
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
    if(argc>1) AL=atoi(argv[1]);
    tab=calloc(HS,16); used=calloc(HS,1);
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
    dfs(0,3,S);
    printf("L=%d: raw (prefix,completion) pairs %lld ; rejected for multiplicity 5: %lld ; "
           "DISTINCT atom multisets %lld ; inflation factor %.2f\n",
           AL, raw, badmult, distinct, distinct? (double)raw/distinct : 0.0);
    return 0;
}
