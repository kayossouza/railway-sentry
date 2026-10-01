FROM nginx:1.31.5-alpine@sha256:72ba65eb42c10344912a84ff42408db7d34f2feb642204570ab8fc5ffd29f1d3
COPY gateway/nginx.conf.template /etc/nginx/templates/default.conf.template
ENV NGINX_ENVSUBST_FILTER="WEB_HOST|RELAY_HOST|PRIVATE_HOST|DNS_RESOLVER|PUBLIC_INGESTION"
COPY gateway/start.sh /start.sh
ENTRYPOINT ["sh", "/start.sh"]

COPY runtime-manifest.json /runtime-manifest.json
