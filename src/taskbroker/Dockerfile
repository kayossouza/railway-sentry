FROM ghcr.io/getsentry/taskbroker:26.9.0@sha256:d20c5883f7d072bdcb0d0f040307b6472d7a9611e0ed3ddfc27c5e1f64b8f9d7
USER root
RUN apt-get update && apt-get install -y --no-install-recommends python3 && rm -rf /var/lib/apt/lists/*
COPY common/wait.py /opt/railway/wait.py
COPY taskbroker/start.py /opt/railway/start.py
COPY upstream/taskbroker.yml /etc/taskbroker/config.yml
CMD ["python3", "/opt/railway/start.py"]

COPY runtime-manifest.json /runtime-manifest.json
