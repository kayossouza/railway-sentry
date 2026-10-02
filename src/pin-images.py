"""Freeze all base-image tags to registry manifest digests, retaining tag labels."""
import concurrent.futures
import json
import pathlib
import re
import subprocess

root = pathlib.Path(__file__).resolve().parent
files = list(root.glob('*/Dockerfile'))
images = set()
for file in files:
    images.update(re.findall(r'^FROM (\S+)', file.read_text(), re.M))

def resolve(image):
    result = subprocess.run(['docker','buildx','imagetools','inspect',image],text=True,capture_output=True,check=True)
    digest = re.search(r'^Digest:\s+(sha256:\w+)',result.stdout,re.M).group(1)
    return image, digest

with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    pins = dict(pool.map(resolve, sorted(images)))
for file in files:
    content = file.read_text()
    for image,digest in pins.items():
        content = content.replace('FROM '+image+'\n','FROM '+image+'@'+digest+'\n').replace('FROM '+image+' AS','FROM '+image+'@'+digest+' AS')
    file.write_text(content)
(root/'images.lock.json').write_text(json.dumps(pins,indent=2)+'\n')
print('Pinned',len(pins),'image manifests')
