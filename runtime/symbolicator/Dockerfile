FROM ghcr.io/getsentry/symbolicator:26.9.0@sha256:f38cf17e84e1d6ae0571f326684fdc5f4e7d27fa6bc6c847f687fc51ea8beebc
COPY symbolicator/config.yml /etc/symbolicator/config.yml
CMD ["run", "-c", "/etc/symbolicator/config.yml"]

COPY runtime-manifest.json /runtime-manifest.json
