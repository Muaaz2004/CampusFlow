
import argparse,csv,json
from pathlib import Path
def rows(p):
    with open(p,newline="",encoding="utf-8") as f:return list(csv.DictReader(f))
def validate(project):
    p=Path(project);raw=p/"data/raw";m=json.loads((p/"data/metadata/dataset_metadata.json").read_text())
    stops=rows(raw/"stops.csv");routes=rows(raw/"routes.csv");links=rows(raw/"route_stops.csv");trips=rows(raw/"trips.csv");weather=rows(raw/"weather.csv")
    ids={x["stop_id"] for x in stops};rids={x["route_id"] for x in routes};errs=[];checks=[]
    def ck(n,ok,detail=""):
        checks.append({"check":n,"passed":bool(ok),"detail":detail})
        if not ok:errs.append(n)
    ck("12 unique stops",len(stops)==12 and len(ids)==12,str(len(stops)))
    ck("4 unique routes",len(routes)==4 and len(rids)==4,str(len(routes)))
    ck("route-stop foreign keys",all(x["stop_id"] in ids and x["route_id"] in rids for x in links))
    ck("route endpoint foreign keys",all(x["start_stop"] in ids and x["end_stop"] in ids for x in routes))
    ck("trip count",len(trips)==m["trip_count"],str(len(trips)))
    ck("weather calendar coverage",len(weather)==m["calendar_days"],str(len(weather)))
    ck("trip route references",all(x["route_id"] in rids for x in trips))
    ck("passenger capacity bounds",all(0<=int(x["passenger_count"])<=int(x["available_seats"]) for x in trips))
    ck("occupancy range",all(0<=float(x["occupancy_rate"])<=1 for x in trips))
    ev=[json.loads(x) for x in (raw/"boarding_events.jsonl").read_text(encoding="utf-8").splitlines() if x]
    by={}
    for e in ev:by.setdefault(e["trip_id"],[]).append(e)
    consistent=len(ev)==2*len(trips)
    for t in trips:
        es=sorted(by.get(t["trip_id"],[]),key=lambda x:x["event_sequence"]);n=int(t["passenger_count"])
        if len(es)!=2 or es[0]["event_type"]!="BOARD" or es[0]["passenger_delta"]!=n or es[1]["event_type"]!="ALIGHT" or es[1]["passenger_delta"]!=-n or es[1]["occupancy_after"]!=0:
            consistent=False;break
    ck("two consistent events per trip",consistent,str(len(ev)))
    ck("synthetic labeling",m.get("synthetic") is True and all(e.get("synthetic") is True for e in ev))
    report={"valid":not errs,"checks":checks,"errors":errs,"counts":{"stops":len(stops),"routes":len(routes),"route_stop_links":len(links),"trips":len(trips),"weather_days":len(weather),"boarding_events":len(ev)}}
    (p/"reports").mkdir(exist_ok=True);(p/"reports/validation_report.json").write_text(json.dumps(report,indent=2))
    return report
if __name__=="__main__":
    a=argparse.ArgumentParser();a.add_argument("--project-root",default=".");args=a.parse_args();r=validate(args.project_root);print(json.dumps(r,indent=2));raise SystemExit(0 if r["valid"] else 1)
