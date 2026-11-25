
from pathlib import Path
from textwrap import dedent
import sys

p=Path(sys.argv[1])
s=p.read_text(encoding='utf8').replace("CaptureThesisViews","CaptureChapter3")
def splice(start, end, code):
    global s
    i=s.index(start)
    j=s.index(end,i)
    s=s[:i]+dedent(code).strip("\n")+"\n"+s[j:]
s=s.replace('            List<Map<String,Object>> trace=records(work);','            Thread.sleep(1150);\n            List<Map<String,Object>> trace=records(work);',1)
splice('            if(mode.equals("mapping")) {','            } else if(mode.equals("goal")) {', '''
            if(mode.equals("mapping")) {
                var difference=trace.stream().filter(CaptureChapter3::differentProgress).findFirst().orElseThrow(
                    ()->new IllegalStateException("Run has no checkpoint with two different ObserveBid statuses"));
                selected=seq(difference);
                require(completedGoals(object(response.get("result"))) == 2,"Two closing goals must be present");
                show(view,split,last,460,"Artifacts","Checkpoints");
                workbench(evidence.resolve("workbench.png"), view, split, "Checkpoints");
                for(var cut:List.of(difference,latest)) {
                    int step=seq(cut);
                    show(view,split,step,490,"Artifacts","iStarSCN");
                    var actual=object(object(cut.get("response")).get("result"));
                    for(String name:List.of("a1","a2")) {
                        var id=auctionId(actual,name);
                        context(view,id,"Markings");
                        String stage=step==selected?"mid":"final";
                        markingView(evidence.resolve(stage+"-"+name),view,id,name);
                    }
                }
''')
s=s.replace('                show(view,split,last-1,560,"Artifacts","Checkpoints");','''                var validSourceReceipt = work.resolve("checkpoint-"+last+".json");
                waitFor(()->Files.isRegularFile(validSourceReceipt),6,"owned producer receipt");
                try {
                    captureSourceOrganization(evidence,work,view,split,last,latest,args[4],args[5]);
                } catch(Exception orgError) {
                    orgError.printStackTrace();
                    Files.writeString(evidence.resolve("moise-error.txt"),orgError.toString());
                }
                show(view,split,last-1,560,"Artifacts","Checkpoints");''',1)
s=s.replace('                table(evidence.resolve("markings.png"),view,"Context",i->true,1,2,3);','                markingView(evidence.resolve("violation-"+auction),view,context,auction);',1)
s=s.replace('                table(evidence.resolve("hold.png"),view,"Checkpoint",i->i>=last-3&&i<last);\n                waitFor','''                table(evidence.resolve("hold.png"),view,"Checkpoint",i->i>=last-3&&i<last);
                show(view,split,last,490,"Artifacts","Checkpoints");
                workbench(evidence.resolve("missing-workbench.png"),view,split,"Checkpoints");
                waitFor''',1)
s=s.replace('                table(evidence.resolve("ocl.png"),view,"Object",i->true,1,2,3,4);\n                show','''                table(evidence.resolve("ocl.png"),view,"Object",i->true,1,2,3,4);
                show(view,split,last,270,"Artifacts","OCL");
                workbench(evidence.resolve("counter-workbench.png"),view,split,"OCL");
                show''',1)
s=s.replace('            for(int sequence:new TreeSet<>(List.of(last,Math.max(1,last-1),selected))) {','            for(int sequence=1;sequence<=last;sequence++) {',1)
s=s.replace('        try {\n            if (mode.equals("mapping")) {','''        try {
            System.out.println("Input MRV: "+Path.of(args[2]).toAbsolutePath());
            if (mode.equals("mapping")) {''',1)
s=s.replace('owner.setAlwaysOnTop(true);','')
s=s.replace('    private static boolean n(Number n,double value)', '''    private static String auctionId(Map<String,Object> result,String name) {
        return rows(result.get("state")).stream()
            .filter(row->("'"+name+"'").equals(row.get("id"))&&"Auction".equals(row.get("type")))
            .map(row->row.get("object").toString()).findFirst().orElseThrow();
    }
    private static String elementStatus(Map<String,Object> result,String context,String element) {
        return rows(result.get("elements")).stream()
            .filter(e->context.equals(e.get("context"))&&element.equals(e.get("element")))
            .map(e->e.get("status").toString()).findFirst().orElse("");
    }
    private static boolean differentProgress(Map<String,Object> cut) {
        if(values(cut,"best_bid").size()!=2)return false;
        var response=object(cut.get("response"));
        if(!"APPROVE".equals(response.get("decision")))return false;
        var result=object(response.get("result"));
        var a1=elementStatus(result,auctionId(result,"a1"),"ObserveBid");
        var a2=elementStatus(result,auctionId(result,"a2"),"ObserveBid");
        return Set.of("PENDING","FULFILLED").contains(a1)&&Set.of("PENDING","FULFILLED").contains(a2)&&!a1.equals(a2);
    }
    private static boolean n(Number n,double value)''',1)
p.write_text(s,encoding='utf8')

