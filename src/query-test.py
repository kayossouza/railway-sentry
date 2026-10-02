"""Authenticated real API acceptance checks. Never emits the bearer token."""
import json
import pathlib
import urllib.parse
import urllib.request
import urllib.error
import sys

root=pathlib.Path(__file__).resolve().parent
fixture=json.loads((root.parent/'.acceptance.json').read_text())
base=json.loads((root/'evidence/domain.json').read_text())['domains'][0]
org=fixture['org']
marker='bounty-sentry-e2e-20261001'
import re
log=(root/'evidence/sdk-emission2.log').read_text()
trace_id=re.search(r'trace_id="([a-f0-9]+)"', log).group(1)
queries={
 'error-issues':('/api/0/projects/'+org+'/sdk/issues/',{'query':marker}),
 'logs':('/api/0/organizations/'+org+'/events/',{'project':fixture['project_id'],'dataset':'ourlogs','field':['timestamp','message','severity','trace','sentry.message.parameter.marker','sentry.message.parameter.pipeline'],'query':marker,'statsPeriod':'24h'}),
 'spans':('/api/0/organizations/'+org+'/events/',{'project':fixture['project_id'],'dataset':'spans','field':['span.op','span.description','trace','id','parent_span'],'query':'trace:'+trace_id,'statsPeriod':'24h'}),
}
queries['event-detail']=('/api/0/projects/'+org+'/sdk/events/cb0bd515af104c0f80eeda14d5c81c01/',{})
results={}
for label,(path,args) in queries.items():
    url=base+path+'?'+urllib.parse.urlencode(args,doseq=True)
    request=urllib.request.Request(url,headers={'Authorization':'Bearer '+fixture['token']})
    try:
        with urllib.request.urlopen(request,timeout=30) as response:
            body=response.read().decode(); code=response.status
    except urllib.error.HTTPError as error:
        code=error.code; body=error.read().decode()
    (root/'evidence'/f'query-{label}.json').write_text(body+'\n')
    results[label]={'status':code,'url':url}
    print(label,code,body[:350])
(root/'evidence/query-results.json').write_text(json.dumps(results,indent=2)+'\n')
