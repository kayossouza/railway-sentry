"""Authenticated acceptance results; never prints the bearer token."""
import json,pathlib,re,urllib.request,urllib.parse,urllib.error
root=pathlib.Path(__file__).resolve().parent
f=json.loads((root.parent/'.cold4-acceptance.json').read_text())
base=json.loads((root/'evidence/cold4-domain.json').read_text())['domain']
log=(root/'evidence/final-sdk.log').read_text()
event=re.findall(r'error_event_id="([a-f0-9]+)"',log) or re.findall(r'"error_event_id":\s*"([a-f0-9]+)"',log)
trace=re.findall(r'trace_id="([a-f0-9]+)"',log) or re.findall(r'"trace_id":\s*"([a-f0-9]+)"',log)
assert event and trace,'SDK receipt missing'
queries={
 'error':('/api/0/projects/'+f['org']+'/sdk/events/'+event[-1]+'/',{}),
 'logs':('/api/0/organizations/'+f['org']+'/events/',{'project':f['project_id'],'dataset':'ourlogs','field':['message','trace','sentry.message.parameter.marker','sentry.message.parameter.pipeline'],'query':'bounty-final-20261001','statsPeriod':'24h'}),
 'spans':('/api/0/organizations/'+f['org']+'/events/',{'project':f['project_id'],'dataset':'spans','field':['span.op','span.description','trace','id','parent_span'],'query':'trace:'+trace[-1],'statsPeriod':'24h'}),
}
for label,(path,args) in queries.items():
 url=base+path+'?'+urllib.parse.urlencode(args,doseq=True)
 try:
  r=urllib.request.urlopen(urllib.request.Request(url,headers={'Authorization':'Bearer '+f['token']}),timeout=30);status=r.status;body=r.read().decode()
 except urllib.error.HTTPError as e:status=e.code;body=e.read().decode()
 (root/'evidence'/f'final-query-{label}.json').write_text(body+'\n')
 print(label,status,body[:250],flush=True)
 assert status==200
 data=json.loads(body)
 if label=='error':assert data['eventID']==event[-1]
 elif label=='logs':
  assert any(row['sentry.message.parameter.marker']=='bounty-final-20261001' and row['sentry.message.parameter.pipeline']=='structured-log' for row in data['data'])
 else:
  rows=data['data']
  parent=next(row for row in rows if row['span.op']=='bounty.test')
  child=next(row for row in rows if row['span.op']=='bounty.child')
  assert child['parent_span']==parent['id'] and child['trace']==parent['trace']==trace[-1]
