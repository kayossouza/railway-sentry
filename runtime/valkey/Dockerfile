FROM valkey/valkey:8.1.10-alpine@sha256:081c2f5cb575efc901aa80ff9cdbd1ec6a301682fd35e1ebb4b0990a4a4a8507
CMD ["sh", "-ec", "exec valkey-server --bind 0.0.0.0 :: --appendonly yes --requirepass \"$REDIS_PASSWORD\""]

COPY runtime-manifest.json /runtime-manifest.json
