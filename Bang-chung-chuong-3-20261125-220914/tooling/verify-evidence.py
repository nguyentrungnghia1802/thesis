
from collections import Counter
from pathlib import Path
import gzip
import hashlib
import json
import re
import sys

e=Path(sys.argv[1])
thesis=e.parent

def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))

def records(path):
    if path.suffix==".gz":
        results=gzip.open(path,"rt",encoding="utf-8")
    else:
        results=path.open(encoding="utf-8-sig")
    with results:
        return [json.loads(line) for line in results if line.strip()]

def snapshot(row):
    return row["request"]["snapshot"]

def seq(row):
    return snapshot(row)["sequence"]

def decision(row):
    return row["response"]["decision"]

def values(snapshot_row,key):
    return {a["name"]:a["properties"][key] for a in snapshot(snapshot_row)["artifacts"] if key in a["properties"]}

def snapshot_state(row):
    return row["response"]["result"]["state"]

def fulfilled(row):
    return {(x["context"],x["actor"],x["element"]) for x in row["response"]["result"]["elements"] if x["status"]=="FULFILLED"}

def map_auctions(row):
    return {entity["id"].strip("'"):entity for entity in snapshot_state(row) if entity["type"]=="Auction"}

def elements_of(row, obj):
    return {x["element"]:x["status"] for x in row["response"]["result"]["elements"] if x["context"]==obj}

def time_seq(rs):
    assert [seq(r) for r in rs]==list(range(1,len(rs)+1))
    return {seq(r):r for r in rs}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def confirm_receipts(rs,folder):
    for r in rs:
        receipt=load(folder/f"checkpoint-{seq(r)}.json")
        assert r==receipt,(folder,seq(r))
    return len(rs)

original=thesis/"Bang-chung-Chuong-3-20261123-220539"/"TN01"
oldtrace=original/"run"/"consumer-history.jsonl"
live=records(oldtrace)
old=time_seq(live)
acks=confirm_receipts(live,original/"run")
replay=load(e/"TN02"/"replay.json")
comparison=[]
assert len(replay["events"])==replay["evaluatedCheckpoints"]
for rep in replay["events"]:
    source=old[rep["sequence"]]
    r=source["response"]["result"]
    pc={
        "sequence":seq(source),
        "decision_original":decision(source),
        "decision_replay":rep["decision"],
        "decision_match":rep["decision"]==decision(source),
        "fulfilled_count_original":len(fulfilled(source)),
        "fulfilled_count_replay":len(rep["fulfilledElements"]),
        "fulfilled_match":{(x["context"],x["actor"],x["element"]) for x in rep["fulfilledElements"]}==fulfilled(source),
        "failed_invariants_match": set(rep["failedInvariants"])=={c["id"] for c in r["checks"] if c["kind"]=="CSL_INVARIANT" and c["verdict"]=="FAIL"},
        "violated_goals_match": set(rep["violatedGoals"])=={x["element"] for x in r["elements"] if x["status"]=="VIOLATED"},
    }
    comparison.append(pc)
assert len(comparison)==len(live)
assert [x["sequence"] for x in comparison]==list(range(1,len(live)+1))
assert all(x["decision_match"] and x["fulfilled_match"] and x["failed_invariants_match"] and x["violated_goals_match"] for x in comparison)
final=live[-1]
assert all(elements_of(final,entity["object"])["AuctionCompleted"]=="FULFILLED" for entity in map_auctions(final).values())
arch_compare={
    "run": live[0]["request"]["run"],"checkpoint_count":len(live),"acks":acks,
    "decision_matches":sum(x["decision_match"] for x in comparison),
    "fulfilled_matches":sum(x["fulfilled_match"] for x in comparison),
    "firstHoldSequence":replay["firstHoldSequence"],"decision":replay["decision"],
    "terminal_contexts":{name:element["object"] for name,element in map_auctions(final).items()},
    "inputs":{p.name:sha(p) for p in (oldtrace,*(original/"input"/p for p in ("attribute-mapping.xml","auction.csl","auction.istar")))},
    "steps":comparison,
}
(e/"TN02"/"comparison.json").write_text(json.dumps(arch_compare,indent=2),encoding="utf-8")
assert "REPLAY checkpoints=58 decision=APPROVE firstHold=0" in (e/"TN02"/"replay.log").read_text(encoding="utf-8-sig")
for number,expected in ((39,{"a1":"PENDING","a2":"PENDING"}),(42,{"a1":"PENDING","a2":"FULFILLED"})):
    assert {name:elements_of(old[number],entity["object"])["ObserveBid"]
            for name,entity in map_auctions(old[number]).items()}==expected
print("Original receipts and reevaluated results match at",len(comparison),"checkpoints")

supp=thesis/"Du-lieu-thuc-nghiem-bo-sung-20261124"
old_variants=[]
for case in ["TN05-hop-le-gom-plan","TN05-loi-gom-plan","TN05-hop-le-chuyen-giao","TN05-loi-chuyen-giao"]:
    d=supp/case
    archive=records(d/"consumer-history.jsonl.gz")
    by_no=time_seq(archive)
    summary=load(d/"result.json")
    assert len(archive)==summary["checkpoints"]
    assert Counter(decision(r) for r in archive)==summary["decisions"]
    for item in d.glob("receipt-*.json"):
        receipt=load(item)
        assert by_no[seq(receipt)]==receipt
    bids=[tuple(float(x) for x in match) for match in re.findall(
        r"VERIFICATION_ORACLE BID previous=(\S+) input=(\S+) actual=(\S+)",
        (d/"producer.log").read_text(encoding="utf-8-sig")
    )]
    later=[(previous,bid,actual) for previous,bid,actual in bids if (previous,bid)==(10.0,20.0)]
    assert len(later)==2
    is_fault="loi-" in case
    assert all(x[2]==(20 if is_fault else 10) for x in later)
    before_after={a:[(seq(r),v) for r in archive if (v:=values(r,"best_bid").get(a)) in (10,20)] for a in ("a1","a2")}
    if not is_fault:
        assert all(any(v==10 for _,v in readings) and all(v==10 for _,v in readings) for readings in before_after.values())
    if is_fault and "gom-plan" in case:
        assert all(any(v==20 for _,v in readings) and all(v==20 for _,v in readings) for readings in before_after.values())
    if is_fault and "chuyen-giao" in case:
        first=summary["firstHoldSequence"]
        for name in ("a1","a2"):
            assert values(by_no[first-1],"best_bid")[name]==10 and values(by_no[first],"best_bid")[name]==20
        assert by_no[first]["request"]["checkpoint"]["boundary"]=="AGENT_HANDOFF" and decision(by_no[first])=="HOLD_FAILURE"
    old_variants.append(dict(case=case,run=archive[0]["request"]["run"],count=len(archive),
                 decisions=summary["decisions"],bids_later=later,price_cuts=before_after,
                 hold=summary["firstHoldSequence"],blocked_probe=summary["expectedBlockedProbe"],
                 blocked_probe_ran=summary["continuationProbeObserved"]))
(e/"TN05-doi-chung.json").write_text(json.dumps(old_variants,indent=2),encoding="utf-8")

def completed_at_cut(row):
    return len(map_auctions(row))==2 and all(elements_of(row,a["object"])["AuctionCompleted"]=="FULFILLED" for a in map_auctions(row).values())

def read_fresh(name):
    d=e/name
    fields=dict(x.split("=",1) for x in (d/"selection.txt").read_text(encoding="utf8").splitlines())
    data=records(d/"consumer-history.jsonl")
    inspect=time_seq(data)
    acks=confirm_receipts(data,d)
    assert int(fields["latest"])==len(data) and fields["run"]==data[-1]["request"]["run"]
    return d, fields, data, inspect, acks

used={"TN01":"TN01-in","TN03":"TN03-in","TN05":"TN05-chuyen-giao","TN06":"TN06-chuyen-giao-trinhbay",
      "TN07-negative":"TN07-giu-am-in","TN07-recovered":"TN07-khoi-phuc-in","Workbench":"TN01-trinhbay"}
facts={}
for code,name in used.items():
    folder, meta, trace, rows, acks=read_fresh(name)
    latest=trace[-1]
    final=seq(latest)
    fields=dict(folder=name,run=meta["run"],short=meta["run"][:8],end=final,acks=acks,
                decision=decision(latest),boundary=latest["request"]["checkpoint"]["boundary"],
                counts=dict(Counter(decision(r) for r in trace)))
    if code=="TN01":
        selected=int(meta["selected"])
        mid=rows[selected]
        def auction_details(record):
            raw=values(record,"best_bid")
            a=map_auctions(record)
            assert len(a)==2 and set(raw)==set(a)
            assert len({row["object"] for row in a.values()})==2
            details={}
            for name,data in a.items():
                assert float(data["best_bid"])==float(raw[name])
                statuses=elements_of(record,data["object"])
                details[name]=dict(price=raw[name],initial=float(raw[name])>=1.7976931348623157e308,
                    object=data["object"],bid=statuses["ObserveBid"],finished=statuses["AuctionCompleted"],
                    safe=statuses["SafeBid"])
            return details
        fields["mid"]=selected
        fields["mid_decision"]=decision(mid)
        fields["mid_details"]=auction_details(mid)
        fields["end_details"]=auction_details(latest)
        fields["mid_invariants"]=[x["verdict"] for x in mid["response"]["result"]["checks"] if x["kind"]=="CSL_INVARIANT"]
        assert {d["bid"] for d in fields["mid_details"].values()}=={"PENDING","FULFILLED"}
        assert all(d["finished"]=="FULFILLED" for d in fields["end_details"].values())
        assert all(x=="PASS" for x in fields["mid_invariants"])
        assert all(fields["mid_details"][a]["object"]==fields["end_details"][a]["object"] for a in ("a1","a2"))
    if code in ("TN03","TN07-negative","TN07-recovered"):
        v=values(latest,"value")["counter"]
        a=next(o for o in snapshot_state(latest) if o["type"]=="Counter")
        assert int(a["value"])==v
        check=next(c for c in latest["response"]["result"]["checks"] if c["id"]=="Counter::Nonnegative")
        assert check["verdict"]==("PASS" if v>=0 else "FAIL")
        fields.update(value=v,nonnegative=check["verdict"],safe=elements_of(latest,a["object"])["SafeValue"],outcome=latest["request"]["outcome"])
        if code.startswith("TN07"):
            counts=list(map(int,re.findall(r"COUNTER_WITNESS value=(-?[0-9]+)",(folder/"producer.log").read_text(encoding="utf8"))))
            assert counts[-1]==v and -1 in counts and counts.index(-1)>=1
            if code=="TN07-recovered": assert counts[-2:]==[-1,2]
            fields["witness"]=counts
    if code=="TN05":
        initials=values(rows[final-1],"best_bid")
        changed=values(latest,"best_bid")
        assert list(initials.values())==[10,10] and list(changed.values())==[20,20]
        assert fields["decision"]=="HOLD_FAILURE" and fields["boundary"]=="AGENT_HANDOFF"
        inv=[c for c in latest["response"]["result"]["checks"] if c["kind"]=="CSL_INVARIANT"]
        assert inv and all(a["verdict"]=="PASS" for a in inv)
        ctx=meta["context"]
        which=next(name for name,o in map_auctions(latest).items() if o["object"]==ctx)
        assert elements_of(latest,ctx)["BidNeverIncreases"]=="VIOLATED"
        assert "VERIFICATION_NEXT_PLAN after_bid_2" not in (folder/"producer.log").read_text(encoding="utf8")
        fields.update(before=final-1,case_context=which,invariants=len(inv))
        org=dict(x.split("=",1) for x in (folder/"organization-selection.txt").read_text().splitlines())
        assert org["run"]==meta["run"] and int(org["checkpoint"])==final
        assert "bob plays auctioneer" in (folder/"moise-group.txt").read_text()
    if code=="TN06":
        assert snapshot(latest)["complete"] is True
        assert not latest["response"]["result"]
        assert "ATTRIBUTE_VALUE_MISSING:Auction.best_bid" in latest["response"]["diagnostic"]
        assert decision(latest)=="HOLD_UNVERIFIED"
        assert snapshot(latest)["artifacts"]
        fields["artifacts"]=sorted(a["name"] for a in snapshot(latest)["artifacts"])
        assert all("best_bid" not in artifact["properties"] for artifact in snapshot(latest)["artifacts"])
        assert fields["boundary"]=="AGENT_HANDOFF"
    if code=="Workbench": assert completed_at_cut(latest)
    facts[code]=fields
tn04=records(e/"TN04"/"verifier-trace.jsonl")
assert [r["decision"] for r in tn04]==["APPROVE","HOLD_UNVERIFIED","APPROVE"]
assert [r["complete"] for r in tn04]==[True,False,True]
assert [r["state"][0]["reading"] for r in tn04]==["1","1","2"]
assert len({r["state"][0]["object"] for r in tn04})==1
assert tn04[1]["artifacts"]==[] and tn04[1]["state"]==tn04[0]["state"]
assert "Tests run: 1, Failures: 0, Errors: 0, Skipped: 0" in (e/"TN04"/"org.tzi.use.plugins.jacamo.bridge.CslStateVerifierTest.txt").read_text()
facts.update(TN04=tn04,TN02={k:v for k,v in arch_compare.items() if k!="steps"},
    reference_TN05=old_variants)
(e/"facts.json").write_text(json.dumps(facts,ensure_ascii=False,indent=2),encoding="utf-8")
for code in used:
    f=facts[code]
    print(code,f["short"],f["end"],f["decision"],"receipts",f["acks"])

