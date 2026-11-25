
    private static Map<String,Object> identified(List<Map<String,Object>> entries,String key,String value) {
        return entries.stream().filter(s->value.equals(s.get(key))).findFirst().orElseThrow(
            ()->new IllegalArgumentException("Missing "+key+"="+value));
    }
    private static boolean hasLink(Map<String,Object> object,String relation,String left,String right) {
        return rows(object.get("_links")).stream().anyMatch(link->relation.equals(link.get("relation"))&&
            link.get("ends") instanceof List<?> ends&&new HashSet<>(ends).equals(Set.of(left,right)));
    }
    private static void captureSourceOrganization(Path evidence,Path work,JPanel view,JSplitPane split,int sequence,
                                                  Map<String,Object> cut,String node,String script) throws Exception {
        var request=object(cut.get("request"));
        var response=object(cut.get("response"));
        var snapshot=object(request.get("snapshot"));
        var source=rows(snapshot.get("nodes"));
        var state=rows(object(response.get("result")).get("state"));
        var sourceBob=identified(source,"name","bob");
        var sourceGroup=identified(source,"name","agrp");
        require("agent".equals(sourceBob.get("kind"))&&"group".equals(sourceGroup.get("kind")),"Wrong organization node types");
        require(rows(snapshot.get("enactments")).stream().anyMatch(
            role->"auctioneer".equals(role.get("role"))&&sourceBob.get("identity").equals(role.get("player"))&&sourceGroup.get("identity").equals(role.get("context"))),
            "JaCaMo did not report bob as auctioneer of agrp");
        require(Boolean.TRUE.equals(snapshot.get("complete")),"Organization cut must be complete");
        require("HOLD_FAILURE".equals(response.get("decision")),"Moise view requires source still held at the evidence cut");
        var bob=identified(state,"name","'bob'").get("object").toString();
        var group=identified(state,"name","'agrp'").get("object").toString();
        var role=identified(state,"type","auctioneer");
        var roleId=role.get("object").toString();
        require(hasLink(role,"Plays",bob,roleId)&&hasLink(role,"InContext",group,roleId),"Projection does not reproduce group and role assignment");

        var producerLog=work.resolve("producer.log");
        final var output=Files.readString(producerLog);
        var match=java.util.regex.Pattern.compile("Moise Http Server running on http://[^/\\s]+:(\\d+)").matcher(output);
        require(match.find(),"The owned producer did not expose its Moise inspector");
        var proc=new ProcessBuilder(node,script,match.group(1),evidence.toString(),"bob","auctioneer","agrp")
            .redirectErrorStream(true).redirectOutput(evidence.resolve("moise-capture.log").toFile()).start();
        if(!proc.waitFor(23,java.util.concurrent.TimeUnit.SECONDS)){
            proc.destroyForcibly();
            throw new IllegalStateException("Timed out capturing the Moise inspector");
        }
        require(proc.exitValue()==0,"Moise capture failed: "+Files.readString(evidence.resolve("moise-capture.log")));
        var newest=readReport(work);
        require(newest.equals(cut),"The source advanced during Moise capture");
        require(ProcessHandle.of(producerPid(view)).orElseThrow().isAlive(),"Source must remain live and held");
        show(view,split,sequence,220,"Artifacts","OAL State");
        diagram(evidence.resolve("oal-layout-before.png"),view,"AolDiagram");
        onEdt(()->{
            var diagram=(org.tzi.use.gui.views.diagrams.DiagramView)find(view,c->c.isShowing()&&"AolDiagram".equals(c.getClass().getSimpleName()));
            require(diagram!=null,"No OAL diagram");
            var placed=new ArrayList<org.tzi.use.gui.views.diagrams.elements.PlaceableNode>();
            diagram.getGraph().iterator().forEachRemaining(placed::add);
            var highlighted=new LinkedHashMap<String,org.tzi.use.gui.views.diagrams.elements.PlaceableNode>();
            int other=0;
            for(var n:placed) {
                if(n.getId().endsWith(bob)){n.setPosition(43,30);highlighted.put("bob",n);}
                else if(n.getId().endsWith(roleId)){n.setPosition(43,143);highlighted.put("auctioneer",n);}
                else if(n.getId().endsWith(group)){n.setPosition(43,270);highlighted.put("agrp",n);}
                else {n.setPosition(446+(other%3)*365,35+(other/3)*148);other++;}
                diagram.invalidateNode(n);
            }
            require(highlighted.size()==3,"All three projected objects must be visible");
            Dimension previous=diagram.getSize();
            try {
                panelImage(evidence.resolve("oal-org-original.png"),diagram,1610,700);
                var boxes=new StringBuilder();
                for(String label:List.of("bob","auctioneer","agrp")){
                    var n=highlighted.get(label);
                    boxes.append(label).append('\t').append(n.getX()).append('\t').append(n.getY()).append('\t')
                         .append(n.getWidth()).append('\t').append(n.getHeight()).append('\n');
                }
                Files.writeString(evidence.resolve("oal-org-boxes.tsv"),boxes.toString());
            } finally {
                diagram.setSize(previous);
            }
            return null;
        });
        require(readReport(work).equals(cut),"The source advanced during OAL capture");
        Files.writeString(evidence.resolve("organization-selection.txt"),"run="+request.get("run")+"\ncheckpoint="+sequence
            +"\nplayer=bob\nrole=auctioneer\ngroup=agrp\ndecision="+response.get("decision")
            +"\nlinks=Plays,InContext\n");
    }

