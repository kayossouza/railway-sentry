"""Upload the final candidate to the second, empty-state disposable project."""
import concurrent.futures,json,pathlib,subprocess
root=pathlib.Path(__file__).resolve().parent
work=root.parent/'test2'
s=json.loads(subprocess.check_output(['railway','status','--json'],cwd=work))
assert s['id']=='91d7ec9f-de08-466d-aebf-d5c102a31ed1' and s['name']=='bounty-test-sentry-3'
def deploy(name):
 args=['railway','up','--project',s['id'],'--environment','production','--service',name,'--detach','--path-as-root',str(root)]
 r=subprocess.run(args,cwd=work,capture_output=True,text=True)
 (root/'evidence'/f'cold3-upload-{name}.txt').write_text(r.stdout+r.stderr)
 print(name,r.returncode,flush=True)
 assert r.returncode==0
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
 list(pool.map(deploy,json.loads((root/'services.json').read_text())))
