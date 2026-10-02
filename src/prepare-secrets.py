"""Generate installation secrets once locally; never use deterministic IaC hashes."""
import json, pathlib, secrets, os
root=pathlib.Path(__file__).resolve().parent
path=root/'.railway/secrets.json'
if path.exists():
    print('Existing installation secrets preserved')
else:
    values={}
    for name in json.loads((root/'services.json').read_text()):
        for key,value in json.loads((root/name/'variables.json').read_text()).items():
            if value.startswith('${{secret('):
                length=int(value.split('(')[1].split(')')[0])
                values[name+'.'+key]=secrets.token_hex((length+1)//2)[:length]
    fd=os.open(path, os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'w') as output:json.dump(values,output)
    print('Installation secrets generated; keep .railway/secrets.json private')
