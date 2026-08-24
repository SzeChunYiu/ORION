#!/bin/bash
set -uo pipefail
export PATH=$HOME/orion-work/maven/bin:$PATH
module load Java/17.0.6 2>/dev/null || true
P=$HOME/orion-work/meltproj
cat > $P/src/main/java/orion/P3Melt.java <<'JAVA'
package orion;

import de.uni_mannheim.informatik.dws.melt.matching_data.LocalTrack;
import de.uni_mannheim.informatik.dws.melt.matching_data.TestCase;
import de.uni_mannheim.informatik.dws.melt.matching_eval.ExecutionResult;
import de.uni_mannheim.informatik.dws.melt.matching_eval.evaluator.metric.cm.ConfusionMatrix;
import de.uni_mannheim.informatik.dws.melt.matching_eval.evaluator.metric.cm.ConfusionMatrixMetric;
import de.uni_mannheim.informatik.dws.melt.yet_another_alignment_api.Alignment;
import java.io.File;
import java.io.PrintWriter;

/** Score a matcher alignment against the OFFICIAL OAEI reference using MELT's
 *  own ConfusionMatrixMetric. No metric is recomputed locally. */
public class P3Melt {
    public static void main(String[] args) throws Exception {
        LocalTrack track = new LocalTrack("oaei-anatomy-local", "1.0", new File(args[0]));
        TestCase tc = track.getTestCases().get(0);
        Alignment ref = tc.getParsedReferenceAlignment();
        Alignment sys = new Alignment(new File(args[1]));
        ExecutionResult er = new ExecutionResult(tc, args[3], sys, ref);
        ConfusionMatrix cm = new ConfusionMatrixMetric().get(er);
        StringBuilder b = new StringBuilder();
        b.append("{\n");
        b.append("  \"melt_version\": \"3.3\",\n");
        b.append("  \"metric\": \"de.uni_mannheim.informatik.dws.melt.matching_eval.evaluator.metric.cm.ConfusionMatrixMetric\",\n");
        b.append("  \"test_case\": \"").append(tc.getName()).append("\",\n");
        b.append("  \"matcher\": \"").append(args[3]).append("\",\n");
        b.append("  \"reference_correspondences\": ").append(ref.size()).append(",\n");
        b.append("  \"system_correspondences\": ").append(sys.size()).append(",\n");
        b.append("  \"true_positives\": ").append(cm.getTruePositiveSize()).append(",\n");
        b.append("  \"false_positives\": ").append(cm.getFalsePositiveSize()).append(",\n");
        b.append("  \"false_negatives\": ").append(cm.getFalseNegativeSize()).append(",\n");
        b.append("  \"precision\": ").append(cm.getPrecision()).append(",\n");
        b.append("  \"recall\": ").append(cm.getRecall()).append(",\n");
        b.append("  \"f1\": ").append(cm.getF1measure()).append("\n");
        b.append("}\n");
        System.out.print(b);
        try (PrintWriter w = new PrintWriter(new File(args[2]))) { w.print(b); }
    }
}
JAVA
cd $P && timeout 600 mvn -q -B -DskipTests package 2>&1 | grep -E "ERROR|cannot find symbol|BUILD FAIL" | head -8
CP="target/p3-melt-1.0.jar:$(mvn -q -B dependency:build-classpath -Dmdep.outputFile=/dev/stdout 2>/dev/null | tail -1)"
timeout 1800 java -cp "$CP" orion.P3Melt \
  "$HOME/orion-work/p3nat/localtrack" \
  "$HOME/orion-work/p3nat/logmap-out/logmap2_mappings.rdf" \
  "$HOME/orion-work/out/P3_MELT_ANATOMY_LOGMAP.json" "LogMap-4.0" 2>&1 | tail -18
