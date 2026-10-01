FROM ghcr.io/getsentry/sentry:26.9.0@sha256:7621804a7e234eee6150c9fe255f781e178640605e389235ab6c2490b8afe68b
RUN pip install --no-deps https://github.com/getsentry/sentry-nodestore-s3/archive/a1457f93d266485d101ae3b29fa03028bb3d63c2.tar.gz
COPY upstream/sentry.conf.py /etc/sentry/upstream.py
COPY sentry-config/sentry.conf.py /etc/sentry/sentry.conf.py
COPY sentry-config/config.yml /etc/sentry/config.yml
COPY common /opt/railway
COPY sentry-config /opt/railway/sentry-config
COPY sentry-consumers /opt/railway/service
ENV SENTRY_CONF=/etc/sentry PYTHONPATH=/opt/railway
ENTRYPOINT ["python3", "/opt/railway/service/start.py"]

COPY runtime-manifest.json /runtime-manifest.json
