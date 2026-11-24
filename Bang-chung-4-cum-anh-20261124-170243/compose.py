
import os,pathlib,json,re
from PIL import Image
e=pathlib.Path(os.environ["THESIS_EVIDENCE"])
crops={
"mapping":("Auction-trong-Word",[
 ("source",(17,166,862,264)),
 ("oal",(255,166,810,259)),
 ("oal",(806,396,1562,531)),
]),
"goal":("TN05-loi-chuyen-giao",[
 ("before",(18,165,825,264)),
 ("hold",(18,165,825,264)),
 ("marking",(513,165,1162,390)),
 ("ocl",(499,260,1214,552)),
]),
"missing":("TN06-thieu-chuyen-giao",[
 ("hold",(20,130,686,155)),
 ("hold",(684,165,1580,571)),
 ("hold",(20,923,656,943)),
]),
"persistent":("TN07-counter-giu-am",[
 ("counter",(18,550,480,622)),
 ("counter",(753,166,1310,258)),
 ("counter",(987,260,1701,301)),
]),
"restored":("TN07-counter-khoi-phuc",[
 ("counter",(18,550,480,639)),
 ("counter",(753,166,1310,258)),
 ("counter",(987,260,1701,301)),
]),
}
def assemble(crops,folder,name):
    parts=[]
    for stem,rect in crops:
        file=folder/(stem+"-original.png")
        assert file.stat().st_size<450000,file
        with Image.open(file) as im:
            assert im.size==(1920,1080),im.size
            parts.append(im.convert("RGB").crop(rect))
    pad=6
    out=Image.new("RGB",(max(x.width for x in parts)+2*pad,sum(x.height for x in parts)+(len(parts)+1)*pad),"white")
    y=pad
    for im in parts:
        out.paste(im,(pad,y))
        y+=im.height+pad
    dest=e/(name+"-word.png")
    out.save(dest)
    return dest
def rows(path):return [json.loads(line) for line in path.read_text(encoding="utf8").splitlines()]
def snap(row):return row["request"]["snapshot"]
def seq(row):return snap(row)["sequence"]
def prices(row,attr):
 return {a["name"]:a["properties"].get(attr) for a in snap(row)["artifacts"] if a["name"] in ("a1","a2","counter")}
def check_receipt(folder,row):
 receipt=json.loads((folder/f"checkpoint-{seq(row)}.json").read_text(encoding="utf8"))
 assert receipt==row
info={}
for key,(name,cut) in crops.items():
    folder=e/name
    chosen=dict(line.split("=",1) for line in (folder/"selection.txt").read_text().splitlines())
    run=chosen["run"]; sequence=int(chosen["selected"])
    trace=rows(folder/"consumer-history.jsonl")
    row=trace[sequence-1]
    assert seq(row)==sequence and all(r["request"]["run"]==run for r in trace)
    check_receipt(folder,row)
    result=row["response"].get("result",{})
    summary={"folder":name,"run":run,"sequence":sequence,"decision":row["response"]["decision"],"boundary":row["request"]["checkpoint"]["boundary"]}
    if key=="mapping":
        source=prices(row,"best_bid")
        dst={r["id"].strip("'"):float(r["best_bid"]) for r in result["state"] if r["type"]=="Auction"}
        assert source.keys()=={"a1","a2"} and source==dst and source["a1"]!=source["a2"],(source,dst)
        summary["values"]=source
    elif key=="goal":
        prev=trace[sequence-2];check_receipt(folder,prev);assert seq(prev)==sequence-1
        assert row["response"]["decision"]=="HOLD_FAILURE" and prev["response"]["decision"]=="APPROVE"
        assert prices(prev,"best_bid")=={"a1":10,"a2":10} and prices(row,"best_bid")=={"a1":20,"a2":20}
        inv=[c for c in result["checks"] if c["kind"]=="CSL_INVARIANT"]
        assert inv and all(x["verdict"]=="PASS" for x in inv),inv
        assert any(r["element"]=="BidNeverIncreases" and r["status"]=="VIOLATED" and r["context"]==chosen["context"] for r in result["elements"])
        summary|={"previous":seq(prev),"pass_count":len(inv)}
    elif key=="missing":
        assert row["response"]["decision"]=="HOLD_UNVERIFIED" and "ATTRIBUTE_VALUE_MISSING:Auction.best_bid" in row["response"]["diagnostic"]
        assert row["request"]["checkpoint"]["boundary"]=="AGENT_HANDOFF"
        assert str(sequence) in (folder/"producer.log").read_text(encoding="utf8")
    else:
        assert seq(row)==3 and row["request"]["checkpoint"]["boundary"]=="PLAN_COMPLETED"
        expect=[0,1,2,-1]+([2] if key=="restored" else [])
        witness=[int(x) for x in re.findall(r"COUNTER_WITNESS value=(-?\d+)",(folder/"producer.log").read_text(encoding="utf8"))]
        assert witness==expect
        assert prices(row,"value")=={"counter":witness[-1]}
        verdict="PASS" if key=="restored" else "FAIL"
        assert [(x["id"],x["verdict"]) for x in result["checks"] if x["id"]=="Counter::Nonnegative"]==[("Counter::Nonnegative",verdict)]
        assert row["response"]["decision"]==("APPROVE" if key=="restored" else "HOLD_FAILURE")
        summary|={"witness":witness,"nonnegative":verdict}
    summary["image"]=assemble(cut,folder,key).name
    info[key]=summary
(e/"figure-evidence.json").write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding="utf8")
print(json.dumps(info,ensure_ascii=False))

