FROM ghcr.io/getsentry/taskbroker:26.9.0@sha256:d20c5883f7d072bdcb0d0f040307b6472d7a9611e0ed3ddfc27c5e1f64b8f9d7
COPY upstream/taskbroker.yml /etc/taskbroker/config.yml
CMD ["/opt/taskbroker", "-c", "/etc/taskbroker/config.yml"]

COPY runtime-manifest.json /runtime-manifest.json
