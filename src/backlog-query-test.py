"""Verify every SDK receipt and measure the resulting API query burst."""
import datetime,json,pathlib,re,time,urllib.request,urllib.parse
root=pathlib.Path(__file__).resolve().parent
f=json.loads((root.parent/'.cold3-acceptance.json').read_text())
base=json.loads((root/'evidence/cold3-domain.json').read_text())['domain']
log=(root/'evidence/backlog2-sdk.log').read_text()
events=re.findall(r'error_event_id="([a-f0-9]+)"',log)
traces=re.findall(r'trace_id="([a-f0-9]+)"',log)
assert len(set(events))==20 and len(set(traces))==20
measure=[]
def query(label,path,args):
 started=time.monotonic();url=base+path+'?'+urllib.parse.urlencode(args,doseq=True)
 r=urllib.request.urlopen(urllib.request.Request(url,headers={'Authorization':'Bearer '+f['token']}),timeout=30)
 body=r.read();data=json.loads(body)
 (root/'evidence'/f'backlog2-query-{label}.json').write_bytes(body+b'\n')
 measure.append({'label':label,'status':r.status,'response_bytes':len(body),'seconds':time.monotonic()-started,'url':url})
 return data
start=datetime.datetime.now(datetime.timezone.utc).isoformat();spans=0
for i,(event,trace) in enumerate(zip(events,traces)):
 d=query('error-'+str(i),'/api/0/projects/'+f['org']+'/sdk/events/'+event+'/',{})
 assert d['eventID']==event
 d=query('spans-'+str(i),'/api/0/organizations/'+f['org']+'/events/',{'project':f['project_id'],'dataset':'spans','field':['span.op','trace','id','parent_span'],'query':'trace:'+trace,'statsPeriod':'24h'})
 rows=d['data'];spans+=len(rows)
 parent=next(r for r in rows if r['span.op']=='bounty.test');child=next(r for r in rows if r['span.op']=='bounty.child')
 assert child['parent_span']==parent['id'] and child['trace']==parent['trace']==trace
logs=query('logs','/api/0/organizations/'+f['org']+'/events/',{'project':f['project_id'],'dataset':'ourlogs','field':['message','trace','sentry.message.parameter.marker','sentry.message.parameter.pipeline'],'query':'bounty-backlog2-20261001','statsPeriod':'24h','per_page':100})['data']
assert len(logs)==20 and all(r['sentry.message.parameter.pipeline']=='structured-log' for r in logs)
summary={'since':start,'until':datetime.datetime.now(datetime.timezone.utc).isoformat(),'errors':len(events),'logs':len(logs),'spans':spans,'queries':measure}
(root/'evidence/backlog2-query-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print('Stored errors:',len(events),'logs:',len(logs),'spans:',spans,'requests:',len(measure))
