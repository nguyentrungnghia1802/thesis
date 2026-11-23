import hashlib,json,os,pathlib
p=pathlib.Path(os.environ["THESIS_EVIDENCE"])
def read(case):
    folder=p/case/"run"
    trace=[json.loads(line) for line in (folder/"consumer-history.jsonl").read_text(encoding="utf8").splitlines()]
    receipts=[]
    for entry in trace:
        q,r=entry["request"],entry["response"]; seq=q["snapshot"]["sequence"]
        saved=json.loads((folder/f"checkpoint-{seq}.json").read_text(encoding="utf8"))
        receipts.append(saved==entry and q["token"]==r["token"] and q["run"]==r["run"] and q["cut"]==r["cut"])
    return trace,receipts
live,ar=read("TN01")
counter,cr=read("TN03")
replay=json.loads((p/"TN02/replay.json").read_text())
def statuses(rows):
    return sorted((x["context"],x["actor"],x["element"]) for x in rows if x.get("status","FULFILLED")=="FULFILLED")
matches=[]
for e,t in zip(live,replay["events"]):
    r=e["response"]; matches.append([r["result"]["sequence"],r["result"]["sequence"]==t["sequence"],
                             r["decision"]==t["decision"],statuses(r["result"]["elements"])==statuses(t["fulfilledElements"])])
assert all(all(row[1:]) for row in matches) and len(matches)==len(live)==len(replay["events"])
assert all(ar+cr)
def rows(e):
    q,r=e["request"],e["response"]
    source=q["snapshot"]
    context={s["sourceIdentity"]:s for s in r["result"]["state"] if s["type"] in ("Auction","Counter")}
    out=[]
    for a in source["artifacts"]:
        c=next((v for k,v in context.items() if k==q["run"]+":"+a["identity"]+":"+v["type"]),None)
        if c is None: continue
        name=c["object"]
        marked={x["element"]:x["status"] for x in r["result"]["elements"] if x["context"]==name}
        checks={x["id"]:x["verdict"] for x in r["result"]["checks"] if x["context"]==name and x["kind"]=="CSL_INVARIANT"}
        properties=a["properties"]
        for k,v in properties.items():
            if k in c:
                raw=c[k]
                if isinstance(v,bool): assert str(v).lower()==raw
                elif isinstance(v,(int,float)): assert float(raw)==float(v)
                else: assert raw=="'"+v+"'"
        out.append(dict(artifact=a["name"],identity=a["identity"],csl_object=name,check_values=properties,markings=marked,checks=checks))
    out.sort(key=lambda x:x["artifact"])
    return dict(run=q["run"],sequence=source["sequence"],epoch=q["cut"]["epoch"],plan=q["plan"],
        boundary=q["checkpoint"]["boundary"],merged=q["checkpoint"]["mergedPlans"],outcome=q["outcome"],decision=r["decision"],objects=out)
allA=[rows(e) for e in live]
allC=[rows(e) for e in counter]
pending=next(r for r in allA if any(e["markings"].get("ObserveBid")=="PENDING" for e in r["objects"]))
drop=next(r for r in allA if any(float(e["check_values"].get("best_bid",1.7976931348623157e308))<1.7976931348623157e308 for e in r["objects"]))
data=dict(auction_count=len(live),auction_receipts=sum(ar),counter_count=len(counter),counter_receipts=sum(cr),
    parity=matches,pending=pending,drop=drop,auction_final=allA[-1],counter=allC)
(p/"TN02/comparison.json").write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf8")
print(json.dumps(data|{"parity":f"{len(matches)}/{len(live)}"},ensure_ascii=False,indent=2))
