/* Control harness: run the SAME add()/R3 machinery pass 2 uses, on sequences
 * whose answer is known independently, and print the verdict. */
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
typedef unsigned __int128 u128;
#define N 125
static unsigned char ADD[N][N];
static u128 MA[3][5],MB[3][5],ONE=1;
static inline u128 shft(u128 m,int e){ int dx=e/25,dy=(e/5)%5,dz=e%5;
    if(dz) m=((m&MA[0][dz])<<dz)|((m&MB[0][dz])>>(5-dz));
    if(dy) m=((m&MA[1][dy])<<(5*dy))|((m&MB[1][dy])>>(5*(5-dy)));
    if(dx) m=((m&MA[2][dx])<<(25*dx))|((m&MB[2][dx])>>(25*(5-dx)));
    return m; }
static u128 R1a,R1b,R2a[N],R2b[N]; static u128 (*R3a)[N],(*R3b)[N];
static int step(int v){
    R1b = R1a | shft(R1a,v) | (ONE<<v);
    memcpy(R2b,R2a,sizeof(R2a)); memcpy(R3b,R3a,(size_t)N*N*sizeof(u128));
    for(int s=0;s<N;s++){ u128 r=R2a[s]; if(!r) continue;
        R2b[ADD[s][v]] |= r; R2b[s] |= shft(r,v); }
    for(int s=0;s<N;s++) if((R1a>>s)&1) R2b[s] |= (ONE<<v);
    for(int a=0;a<N;a++){ int aa=ADD[a][v];
        for(int b=0;b<N;b++){ u128 c=R3a[a][b]; if(!c) continue;
            R3b[aa][b]|=c; R3b[a][ADD[b][v]]|=c; R3b[a][b]|=shft(c,v); } }
    for(int a=0;a<N;a++){ u128 r=R2a[a]; if(!r) continue;
        for(int b=0;b<N;b++) if((r>>b)&1) R3b[a][b] |= (ONE<<v); }
    R1a=R1b; memcpy(R2a,R2b,sizeof(R2a)); memcpy(R3a,R3b,(size_t)N*N*sizeof(u128));
    return 0; }
int main(int argc,char**argv){
    for(int d=0;d<5;d++){ MA[0][d]=MB[0][d]=MA[1][d]=MB[1][d]=MA[2][d]=MB[2][d]=0;
        for(int i=0;i<125;i++){ int x=i/25,y=(i/5)%5,z=i%5; u128 bb=ONE<<i;
            if(z+d<5)MA[0][d]|=bb; else MB[0][d]|=bb;
            if(y+d<5)MA[1][d]|=bb; else MB[1][d]|=bb;
            if(x+d<5)MA[2][d]|=bb; else MB[2][d]|=bb; } }
    for(int a=0;a<N;a++){ int ax=a/25,ay=(a/5)%5,az=a%5;
        for(int b=0;b<N;b++){ int bx=b/25,by=(b/5)%5,bz=b%5;
            ADD[a][b]=((ax+bx)%5)*25+((ay+by)%5)*5+((az+bz)%5); } }
    R3a=malloc((size_t)N*N*sizeof(u128)); R3b=malloc((size_t)N*N*sizeof(u128));
    char line[8192];
    while(fgets(line,sizeof(line),stdin)){
        int vs[64],nv=0; char*p=line;
        while(*p){ if(*p=='['){ int a,b,c; if(sscanf(p,"[%d,%d,%d]",&a,&b,&c)==3) vs[nv++]=a*25+b*5+c; } p++; }
        if(!nv) continue;
        R1a=0; memset(R2a,0,sizeof(R2a)); memset(R3a,0,(size_t)N*N*sizeof(u128));
        for(int i=0;i<nv;i++) step(vs[i]);
        printf("len=%d two_disjoint=%d three_disjoint=%d\n", nv,
               (int)((R2a[0]>>0)&1), (int)((R3a[0][0]>>0)&1));
    }
    return 0; }
