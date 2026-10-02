"""Run only with the two disposable-project credential files mounted explicitly."""
import boto3,hashlib,json,pathlib,sys
from botocore.config import Config
root=pathlib.Path('/task')
mode=sys.argv[1]
manifest=[]
for label in ['node','file']:
    cred=json.loads((root/f'.{label}-credentials.json').read_text())
    client=boto3.client('s3',endpoint_url=cred['endpoint'],region_name=cred['region'],aws_access_key_id=cred['accessKeyId'],aws_secret_access_key=cred['secretAccessKey'],config=Config(s3={'addressing_style':'path'}))
    directory=root/'.bucket-backup'/label
    directory.mkdir(parents=True,exist_ok=True)
    if mode=='backup':
        for page in client.get_paginator('list_objects_v2').paginate(Bucket=cred['bucketName']):
            for obj in page.get('Contents',[]):
                response=client.get_object(Bucket=cred['bucketName'],Key=obj['Key'])
                data=response['Body'].read(); sha=hashlib.sha256(data).hexdigest()
                (directory/sha).write_bytes(data)
                manifest.append({'store':label,'key':obj['Key'],'sha256':sha,'bytes':len(data),'metadata':response.get('Metadata',{}),'contentType':response.get('ContentType','application/octet-stream'),'contentEncoding':response.get('ContentEncoding')})
    elif mode=='restore':
        for obj in json.loads((root/'.bucket-backup/manifest.json').read_text()):
            if obj['store']!=label:continue
            client.delete_object(Bucket=cred['bucketName'],Key=obj['key'])
            try:client.head_object(Bucket=cred['bucketName'],Key=obj['key']);raise AssertionError('Object not deleted')
            except client.exceptions.ClientError as e:
                assert e.response['ResponseMetadata']['HTTPStatusCode']==404
            data=(directory/obj['sha256']).read_bytes()
            assert hashlib.sha256(data).hexdigest()==obj['sha256']
            args={'Bucket':cred['bucketName'],'Key':obj['key'],'Body':data,'Metadata':obj['metadata'],'ContentType':obj['contentType']}
            if obj['contentEncoding']:args['ContentEncoding']=obj['contentEncoding']
            client.put_object(**args)
            restored=client.get_object(Bucket=cred['bucketName'],Key=obj['key'])['Body'].read()
            assert hashlib.sha256(restored).hexdigest()==obj['sha256']
            print('Restored',label,obj['key'],len(data),flush=True)
if mode=='backup':
    (root/'.bucket-backup/manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('Backed up objects:',len(manifest),'bytes:',sum(x['bytes'] for x in manifest))
