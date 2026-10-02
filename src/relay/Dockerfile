FROM ghcr.io/getsentry/relay:26.9.0@sha256:5e159890e7d01c60a4e2f8bca0d581136a68b8acd509325dc39c333928fd05bb AS relay
FROM python:3.13.7-slim-trixie@sha256:5f55cdf0c5d9dc1a415637a5ccc4a9e18663ad203673173b8cda8f8dcacef689
COPY relay/requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt
COPY --from=relay /bin/relay /bin/relay
COPY common /opt/railway
COPY relay/start.py /opt/railway/start.py
ENV PYTHONPATH=/opt/railway
ENTRYPOINT ["python3", "/opt/railway/start.py"]

COPY runtime-manifest.json /runtime-manifest.json
