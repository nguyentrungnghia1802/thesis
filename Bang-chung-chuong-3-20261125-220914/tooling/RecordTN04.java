
import java.nio.file.*;
import java.nio.charset.StandardCharsets;
import java.util.*;
import org.tzi.use.plugins.jacamo.bridge.SourceSnapshot;
import org.tzi.use.plugins.jacamo.bridge.protocol.CanonicalJson;
import org.tzi.use.plugins.jacamo.session.SnapshotVerifier;

/** Records concrete values for the same three inputs as the existing focused JUnit case. */
public class RecordTN04 {
    public static void main(String[] args) throws Exception {
        Path where = Path.of(args[0]);
        Files.createDirectories(where);
        Path fixture = where.resolve("fixture");
        Files.createDirectories(fixture);
        Path csl = fixture.resolve("example.csl"), istar = fixture.resolve("example.istar"), mapping = fixture.resolve("mapping.xml");
        Files.writeString(csl, """
            csl v4.0 Example {
              entity Gauge { attribute reading : Integer required mutable; }
              context Gauge inv Nonnegative: self.reading >= 0;
            }
            """);
        Files.writeString(istar, """
            istar StateGoals { agent Gauge {
              goal Safe : Maintain condition {[ self.reading >= 0 ]}
              goal Done : Achieve
              task ReachedTwo > Done pre {[ true ]} post {[ self.reading >= 2 ]}
              task NonnegativeObserved > Done pre {[ true ]} post {[ self.reading >= 0 ]}
            } }
            """);
        Files.writeString(mapping, """
            <mapping xmlns="urn:use:jacamo-state-mapping:1">
              <attribute source="artifact:unrelated.CustomGauge/property:value" target="Gauge.reading"/>
            </mapping>
            """);
        var first = List.of(gauge(1));
        var replacement = List.of(gauge(2));
        var inputs = List.of(new SourceSnapshot("run",1,true,first),
                     new SourceSnapshot("run",2,false,List.of()),
                     new SourceSnapshot("run",2,true,replacement));
        var outcomes = new ArrayList<SnapshotVerifier.Result>();
        try (var verifier = new SnapshotVerifier(mapping,csl,istar)) {
            for (var input: inputs) {
                var result = verifier.update(input);
                outcomes.add(result);
                var record = Map.of("sequence",input.sequence(),"complete",input.complete(),"artifacts",
                    input.artifacts().stream().map(a->Map.of("identity",a.identity(),"properties",a.properties())).toList(),
                    "decision",result.decision(),"state",result.state());
                System.out.println(new String(CanonicalJson.encode(record),StandardCharsets.UTF_8));
            }
        }
        if (!outcomes.get(0).decision().equals("APPROVE") ||
            !outcomes.get(1).decision().equals("HOLD_UNVERIFIED") ||
            !outcomes.get(2).decision().equals("APPROVE") ||
            outcomes.stream().anyMatch(o->o.state().size()!=1) ||
            !outcomes.get(0).state().equals(outcomes.get(1).state()) ||
            !outcomes.get(0).state().getFirst().get("object").equals(outcomes.get(2).state().getFirst().get("object")))
            throw new AssertionError("Unexpected TN04 state or decision");
    }
    private static SourceSnapshot.Artifact gauge(int value) {
        return new SourceSnapshot.Artifact("physical-1","unrelated.CustomGauge","some-name","/main",Map.of("value",value));
    }
}

