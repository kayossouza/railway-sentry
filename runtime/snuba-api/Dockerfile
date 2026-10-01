FROM ghcr.io/getsentry/snuba:26.9.0@sha256:72c5420ee02f2626e39c65e27c1f7e38f20d59a291112905715753bc442fc155
COPY common /opt/railway
COPY snuba-api /opt/railway/service
ENV PYTHONPATH=/opt/railway SNUBA_SETTINGS=self_hosted
ENTRYPOINT ["python3", "/opt/railway/service/start.py"]

COPY runtime-manifest.json /runtime-manifest.json
