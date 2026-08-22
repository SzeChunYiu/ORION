/* Pass 2 of the D_3 decision: exact three-disjoint-zero-sum test on every
 * length-25 candidate produced by pass 1.  Candidates are grouped by their
 * 19-element prefix C, so the expensive R3 state for C is built once per group
 * and only the 6-element tail is re-added per candidate. */
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
typedef unsigned __int128 u128;
#define N 125
static unsigned char ADD[N][N];
static u128 MA[3][5],MB[3][5],ONE=1;
static inline u128 shft(u128 m,int e){
    int dx=e/25,dy=(e/5)%5,dz=e%5;
    if(dz) m=((m&MA[0][dz])<<dz)|((m&MB[0][dz])>>(5-dz));
    if(dy) m=((m&MA[1][dy])<<(5*dy))|((m&MB[1][dy])>>(5*(5-dy)));
    if(dx) m=((m&MA[2][dx])<<(25*dx))|((m&MB[2][dx])>>(25*(5-dx)));
    return m; }
typedef struct { u128 R1; u128 R2[N]; u128 (*R3)[N]; } St;
static void st_init(St*s){ s->R1=0; memset(s->R2,0,sizeof(s->R2));
    memset(s->R3,0,(size_t)N*N*sizeof(u128)); }
static void st_copy(St*d,const St*s){ d->R1=s->R1; memcpy(d->R2,s->R2,sizeof(s->R2));
    memcpy(d->R3,s->R3,(size_t)N*N*sizeof(u128)); }
/* returns 1 normally, 0 if three disjoint nonempty zero-sums now exist */
static int add(St*o,const St*i,int v){
    o->R1 = i->R1 | shft(i->R1,v) | (ONE<<v);
    memcpy(o->R2,i->R2,sizeof(i->R2));
    memcpy(o->R3,i->R3,(size_t)N*N*sizeof(u128));
    for(int s=0;s<N;s++){ u128 row=i->R2[s]; if(!row) continue;
        o->R2[ADD[s][v]] |= row; o->R2[s] |= shft(row,v); }
    for(int s=0;s<N;s++) if((i->R1>>s)&1) o->R2[s] |= (ONE<<v);
    for(int a=0;a<N;a++){ int aa=ADD[a][v]; const u128*ra=i->R3[a];
        for(int b=0;b<N;b++){ u128 c=ra[b]; if(!c) continue;
            o->R3[aa][b] |= c; o->R3[a][ADD[b][v]] |= c; o->R3[a][b] |= shft(c,v); } }
    for(int a=0;a<N;a++){ u128 row=i->R2[a]; if(!row) continue;
        for(int b=0;b<N;b++) if((row>>b)&1) o->R3[a][b] |= (ONE<<v); }
    return !(o->R3[0][0] & ONE);
}
static u128 P3A[N][N],P3B[N][N],P3C[N][N];
int main(int argc,char**argv){
    for(int d=0;d<5;d++){ MA[0][d]=MB[0][d]=MA[1][d]=MB[1][d]=MA[2][d]=MB[2][d]=0;
        for(int i=0;i<125;i++){ int x=i/25,y=(i/5)%5,z=i%5; u128 bb=ONE<<i;
            if(z+d<5)MA[0][d]|=bb; else MB[0][d]|=bb;
            if(y+d<5)MA[1][d]|=bb; else MB[1][d]|=bb;
            if(x+d<5)MA[2][d]|=bb; else MB[2][d]|=bb; } }
    for(int a=0;a<N;a++){ int ax=a/25,ay=(a/5)%5,az=a%5;
        for(int b=0;b<N;b++){ int bx=b/25,by=(b/5)%5,bz=b%5;
            ADD[a][b]=((ax+bx)%5)*25+((ay+by)%5)*5+((az+bz)%5); } }
    St A={0,{0},P3A},B={0,{0},P3B},Cst={0,{0},P3C};
    FILE*f=fopen(argv[1],"r"); FILE*hit=fopen("d3_survivors.txt","w");
    char line[8192]; int prev[19]; int haveprev=0;
    long long cand=0, groups=0, survivors=0, cfail=0;
    while(fgets(line,sizeof(line),f)){
        int vs[32],nv=0; char*p=line;
        while(*p){ if(*p=='['){ int a,b,c; if(sscanf(p,"[%d,%d,%d]",&a,&b,&c)==3&&nv<25) vs[nv++]=a*25+b*5+c; } p++; }
        if(nv!=25) continue;
        cand++;
        int same = haveprev; if(same) for(int i=0;i<19;i++) if(vs[i]!=prev[i]){ same=0; break; }
        if(!same){ groups++;
            st_init(&A); A.R1=0;   /* rebuild the C state */
            St*cur=&A; St*nx=&B; int ok=1;
            for(int i=0;i<19;i++){ if(!add(nx,cur,vs[i])){ ok=0; break; }
                St*t=cur; cur=nx; nx=t; }
            if(!ok){ cfail++; haveprev=0; continue; }
            st_copy(&Cst,cur);
            memcpy(prev,vs,19*sizeof(int)); haveprev=1; }
        St*cur=&A; St*nx=&B; st_copy(cur,&Cst); int ok=1;
        for(int i=19;i<25;i++){ if(!add(nx,cur,vs[i])){ ok=0; break; }
            St*t=cur; cur=nx; nx=t; }
        if(ok){ survivors++;
            for(int i=0;i<25;i++) fprintf(hit,"%s[%d,%d,%d]",i?",":"[",vs[i]/25,(vs[i]/5)%5,vs[i]%5);
            fprintf(hit,"]\n"); fflush(hit); }
        if(cand%20000==0){ fprintf(stderr,"cand=%lld groups=%lld survivors=%lld\n",cand,groups,survivors); fflush(stderr); } }
    fclose(hit);
    printf("{\"pass\":2,\"candidates\":%lld,\"distinct_C_groups\":%lld,\"C_rebuild_failures\":%lld,"
           "\"length25_with_no_three_disjoint\":%lld,\"D_3\":%d,\"terminal\":\"%s\"}\n",
           cand,groups,cfail,survivors, survivors?26:25,
           survivors?"X1F_LOWER_BOUND_RAISED_TO_26":"X1F_EXACT_D3_ESTABLISHED_25");
    return 0; }
