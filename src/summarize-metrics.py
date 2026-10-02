"""Sampled usage, not invoice accounting. Integrates provided GB and vCPU series."""
import datetime
import json
import pathlib
import sys
from evidence_files import read

root=pathlib.Path(__file__).resolve().parent
label=sys.argv[1]
rows=[]

def integral(points):
    total=0
    for a,b in zip(points,points[1:]):
        minutes=(datetime.datetime.fromisoformat(b['ts'])-datetime.datetime.fromisoformat(a['ts'])).total_seconds()/60
        total+=(a['value']+b['value'])/2*minutes
    return total

ids_path=root/'evidence'/f'{label}-service-ids.json'
ids=json.loads(read(ids_path if ids_path.exists() else root/'evidence/service-ids.json'))
for name in sorted(ids):
    path=root/'evidence'/f'{label}-{name}.json'
    data=json.loads(read(path))
    if 'measurements' not in data: continue
    series=data['measurements']
    ram=series['MEMORY_USAGE_GB']
    cpu=series['CPU_USAGE']
    rows.append({'service':data['service'],'window':data['window'],
                 'RAM_GB_peak':max((p['value'] for p in ram),default=0),
                 'CPU_vCPU_peak':max((p['value'] for p in cpu),default=0),
                 'RAM_GB_minutes_sampled':integral(ram),
                 'CPU_vCPU_minutes_sampled':integral(cpu)})
summary={'phase':label,'method':'trapezoidal integration of Railway CLI raw samples; zero/missing samples are not a tested idle baseline',
         'samples':rows,'sampled_compute_USD':sum(r['RAM_GB_minutes_sampled']*.000231+r['CPU_vCPU_minutes_sampled']*.000463 for r in rows)}
(root/'evidence'/f'{label}-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({'services':len(rows),'sampled_compute_USD':summary['sampled_compute_USD']}))
