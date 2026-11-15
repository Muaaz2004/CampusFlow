
import argparse,csv,json,random
from pathlib import Path
from datetime import date,datetime,time,timedelta
STOPS=[
("ST01","North Hostel","Residential",31.2560,75.7040),("ST02","South Hostel","Residential",31.2510,75.7045),
("ST03","Main Gate","Entrance",31.2470,75.7060),("ST04","Academic Block A","Academic",31.2530,75.7100),
("ST05","Academic Block B","Academic",31.2500,75.7130),("ST06","Central Library","Academic",31.2540,75.7160),
("ST07","Cafeteria","Food",31.2490,75.7180),("ST08","Sports Complex","Recreation",31.2450,75.7140),
("ST09","Auditorium","Events",31.2580,75.7130),("ST10","Research Park","Academic",31.2600,75.7180),
("ST11","Medical Centre","Services",31.2430,75.7090),("ST12","Transit Hub","Transport",31.2400,75.7040)]
ROUTES=[
("R01","North Loop","ST01","ST07",5.2,["ST01","ST04","ST06","ST05","ST07"]),
("R02","South Connector","ST12","ST03",4.8,["ST12","ST11","ST08","ST05","ST03"]),
("R03","Academic Express","ST02","ST10",6.1,["ST02","ST04","ST06","ST09","ST10"]),
("R04","Campus Circular","ST03","ST01",7.4,["ST03","ST08","ST07","ST06","ST04","ST01"])]
BUSES=[("BUS01",40),("BUS02",40),("BUS03",35),("BUS04",35),("BUS05",30),("BUS06",30)]
TRIP_FIELDS=["trip_id","bus_id","route_id","travel_date","departure_time","arrival_time","hour","day_of_week","day_name","is_weekend","season","weather","temperature_c","rainfall_mm","is_exam_day","is_event_day","available_seats","passenger_count","occupancy_rate","duration_minutes","source_stop","destination_stop","distance_km"]
def season(m):
    return "winter" if m in (12,1,2) else "summer" if m in (3,4,5) else "monsoon" if m in (6,7,8,9) else "autumn"
def write(path,rows):
    with open(path,"w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def build(out,trips=30000,days=365,seed=20261105,start_date="2025-01-01"):
    out=Path(out);raw=out/"data/raw";meta=out/"data/metadata";raw.mkdir(parents=True,exist_ok=True);meta.mkdir(parents=True,exist_ok=True)
    r=random.Random(seed);start=date.fromisoformat(start_date);dates=[start+timedelta(days=i) for i in range(days)]
    stops=[dict(stop_id=a,stop_name=b,zone=c,latitude=d,longitude=e,is_synthetic="true") for a,b,c,d,e in STOPS];write(raw/"stops.csv",stops)
    rr=[];rs=[]
    for rid,name,src,dst,dist,seq in ROUTES:
        rr.append(dict(route_id=rid,route_name=name,start_stop=src,end_stop=dst,distance_km=dist,is_synthetic="true"))
        for n,sid in enumerate(seq,1):rs.append(dict(route_id=rid,stop_id=sid,stop_sequence=n,distance_from_previous_km=round(dist/(len(seq)-1),2) if n>1 else 0))
    write(raw/"routes.csv",rr);write(raw/"route_stops.csv",rs)
    weather=[];wxmap={}
    for d in dates:
        sea=season(d.month);temp=round({"winter":13,"summer":31,"monsoon":27,"autumn":23}[sea]+r.uniform(-5,5),1)
        rain=round(r.uniform(0,2),1)
        if sea=="monsoon" and r.random()<.42:rain=round(r.uniform(3,25),1)
        elif r.random()<.08:rain=round(r.uniform(2,10),1)
        cond="rainy" if rain>=3 else "cloudy" if r.random()<.25 else "clear"
        x=dict(date=d.isoformat(),temperature_c=temp,rainfall_mm=rain,weather_condition=cond,season=sea,is_synthetic="true")
        weather.append(x);wxmap[d]=x
    write(raw/"weather.csv",weather)
    trips_rows=[];events=[]
    hours=[7,8,9,10,11,12,13,14,15,16,17,18,19,20];weights=[3,8,12,7,5,7,6,5,6,10,12,9,4,2]
    for i in range(trips):
        d=dates[r.randrange(days)];rid,name,src,dst,dist,seq=r.choice(ROUTES);bus,cap=r.choice(BUSES)
        h=r.choices(hours,weights=weights)[0];minute=r.choice(range(0,60,5));dep=datetime.combine(d,time(h,minute))
        duration=max(10,round(dist*r.uniform(3,4.8)+r.uniform(2,7)));arr=dep+timedelta(minutes=duration)
        dow=d.weekday();weekend=dow>=5;sea=season(d.month);wx=wxmap[d]
        exam=int((d.month in (5,12) and 5<=d.day<=20 and r.random()<.35) or (d.month in (4,11) and 10<=d.day<=24 and r.random()<.12))
        event=int(r.random()<(.10 if dow<5 else .06))
        hf=dict(zip(hours,[.55,1.25,1.45,.9,.7,.95,.85,.7,.8,1,1.35,1.2,.65,.4]))[h]
        expected=cap*.55*hf*(.55 if weekend else 1)*{"R01":1.1,"R02":.85,"R03":1.2,"R04":1}[rid]*(.88 if wx["weather_condition"]=="rainy" else 1)*(1.18 if exam else 1)*(1.25 if event else 1)
        count=max(0,min(cap,round(r.gauss(expected,max(2,cap*.1)))))
        tid=f"TRIP{i+1:06d}"
        t=dict(trip_id=tid,bus_id=bus,route_id=rid,travel_date=d.isoformat(),departure_time=dep.strftime("%H:%M:%S"),arrival_time=arr.strftime("%H:%M:%S"),hour=h,day_of_week=dow,day_name=d.strftime("%A"),is_weekend=int(weekend),season=sea,weather=wx["weather_condition"],temperature_c=wx["temperature_c"],rainfall_mm=wx["rainfall_mm"],is_exam_day=exam,is_event_day=event,available_seats=cap,passenger_count=count,occupancy_rate=round(count/cap,4),duration_minutes=duration,source_stop=src,destination_stop=dst,distance_km=dist)
        trips_rows.append(t)
        events.extend([
          dict(event_id=f"EVT{i*2+1:07d}",event_timestamp=dep.isoformat(timespec="seconds"),trip_id=tid,bus_id=bus,route_id=rid,stop_id=src,event_type="BOARD",passenger_delta=count,occupancy_after=count,event_sequence=1,synthetic=True),
          dict(event_id=f"EVT{i*2+2:07d}",event_timestamp=arr.isoformat(timespec="seconds"),trip_id=tid,bus_id=bus,route_id=rid,stop_id=dst,event_type="ALIGHT",passenger_delta=-count,occupancy_after=0,event_sequence=2,synthetic=True)])
    write(raw/"trips.csv",trips_rows)
    with open(raw/"boarding_events.jsonl","w",encoding="utf-8") as f:
        for e in events:f.write(json.dumps(e,separators=(",",":"))+"\n")
    m=dict(project="CampusFlow",dataset_version="1.0.0",synthetic=True,description="Fictional campus shuttle data for coursework; not real ridership.",seed=seed,start_date=start.isoformat(),end_date=dates[-1].isoformat(),calendar_days=days,trip_count=trips,event_count=len(events),stop_count=len(STOPS),route_count=len(ROUTES),bus_count=len(BUSES))
    (meta/"dataset_metadata.json").write_text(json.dumps(m,indent=2),encoding="utf-8")
    return m
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--output-dir",default=".");p.add_argument("--trips",type=int,default=30000);p.add_argument("--days",type=int,default=365);p.add_argument("--seed",type=int,default=20261105);p.add_argument("--start-date",default="2025-01-01");a=p.parse_args()
    if a.trips<1 or a.days<1:p.error("trips and days must be positive")
    print(json.dumps(build(a.output_dir,a.trips,a.days,a.seed,a.start_date),indent=2))
