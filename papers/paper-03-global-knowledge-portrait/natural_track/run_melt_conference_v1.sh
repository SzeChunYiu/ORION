#!/bin/bash
set -uo pipefail
module load Java/17.0.6 2>/dev/null || true
export PATH=$HOME/orion-work/maven/bin:$PATH
W=$HOME/orion-work/p3conf; cd $W
curl -sL -o reference-alignment.zip --max-time 120 https://oaei.ontologymatching.org/2019/conference/data/reference-alignment.zip
echo "refs sha256: $(sha256sum reference-alignment.zip | cut -c1-64)"
mkdir -p refs && unzip -oq reference-alignment.zip -d refs
echo "reference alignments: $(find refs -iname '*.rdf' | wc -l)"
find refs -iname "*.rdf" | head -6 | sed 's|.*/|   |'

R=$HOME/orion-work/ORION/development/p3-logmap-manifest-classpath-v11-2026-08-23/runtime
P=$HOME/orion-work/meltproj
OUT=$W/results; rm -rf $OUT; mkdir -p $OUT
CP="$P/target/p3-melt-1.0.jar:$(cd $P && mvn -q -B dependency:build-classpath -Dmdep.outputFile=/dev/stdout 2>/dev/null | tail -1)"

n=0
for ref in $(find refs -iname "*.rdf" | sort); do
  base=$(basename "$ref" .rdf)            # e.g. cmt-conference
  src=${base%%-*}; tgt=${base#*-}
  [ -f "$W/$src.owl" ] || continue
  [ -f "$W/$tgt.owl" ] || continue
  n=$((n+1))
  O=$W/lm/$base; rm -rf $O; mkdir -p $O
  (cd $R && timeout 900 java --add-opens=java.base/java.lang=ALL-UNNAMED -jar logmap-matcher-4.0.jar \
     MATCHER "file:$W/$src.owl" "file:$W/$tgt.owl" "$O" true >/dev/null 2>&1)
  [ -f "$O/logmap2_mappings.rdf" ] || { echo "  $base: no alignment"; continue; }
  L=$W/lt/$base; rm -rf $L; mkdir -p $L/pair
  cp "$W/$src.owl" $L/pair/source.rdf; cp "$W/$tgt.owl" $L/pair/target.rdf; cp "$ref" $L/pair/reference.rdf
  timeout 600 java -cp "$CP" orion.P3Melt "$L" "$O/logmap2_mappings.rdf" "$OUT/$base.json" "LogMap-4.0" 2>/dev/null \
    | grep -E "precision|recall|f1" | tr -d ' ,"' | paste -sd' ' - | sed "s|^|  $base: |"
done
echo "pairs attempted: $n ; scored: $(ls $OUT/*.json 2>/dev/null | wc -l)"
