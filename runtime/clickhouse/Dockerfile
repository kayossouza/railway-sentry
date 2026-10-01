FROM altinity/clickhouse-server:25.8.28.10001.altinitystable@sha256:5ad76ea89ca881043b76ddcf2bcf3813663060a03a04b39f5c8ad2ef1dea4b07
COPY upstream/clickhouse.xml /etc/clickhouse-server/config.d/sentry.xml
ENV MAX_MEMORY_USAGE_RATIO=0.3

COPY runtime-manifest.json /runtime-manifest.json
