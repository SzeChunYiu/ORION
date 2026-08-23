#include <stdio.h>
#include <string.h>
typedef unsigned long long u64;
#define MAXW 96
static u64 M[200][MAXW]; static int NM, NW; static u64 LAST;
int main(int argc,char**argv){
    FILE*f=fopen(argv[1],"r"); int np;
    if(fscanf(f,"%d %d",&np,&NM)!=2){ fprintf(stderr,"bad header\n"); return 2; }
    NW=(np+63)/64; LAST=(np%64)?((1ULL<<(np%64))-1):~0ULL;
    for(int i=0;i<NM;i++) for(int w=0;w<NW;w++) if(fscanf(f,"%llu",&M[i][w])!=1) return 3;
    fclose(f);
    long long tried=0;
    for(int a=0;a<NM;a++)
    for(int b=a+1;b<NM;b++){
        u64 ab[MAXW]; for(int w=0;w<NW;w++) ab[w]=M[a][w]|M[b][w];
        for(int c=b+1;c<NM;c++){
            u64 abc[MAXW]; for(int w=0;w<NW;w++) abc[w]=ab[w]|M[c][w];
            for(int d=c+1;d<NM;d++){
                tried++;
                int ok=1;
                for(int w=0;w<NW;w++){
                    u64 u=abc[w]|M[d][w];
                    u64 want=(w==NW-1)?LAST:~0ULL;
                    if((u&want)!=want){ ok=0; break; }
                }
                if(ok){ printf("{\"k4_cover_exists\":true,\"masks\":[%d,%d,%d,%d]}\n",a,b,c,d); return 0; }
            }
        }
    }
    printf("{\"k4_cover_exists\":false,\"subsets_tried\":%lld,\"distinct_masks\":%d,\"pairs\":%d}\n",tried,NM,np);
    return 0;
}
