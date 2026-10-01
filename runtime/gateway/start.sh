#!/bin/sh
set -eu
export PUBLIC_INGESTION="${PUBLIC_INGESTION:-false}"
export WEB_HOST="${WEB_HOST:-web.railway.internal}"
export PRIVATE_HOST="${PRIVATE_HOST:-gateway.railway.internal}"
export DNS_RESOLVER="$(awk '/^nameserver/{print $2; exit}' /etc/resolv.conf)"
case "$DNS_RESOLVER" in *:*) DNS_RESOLVER="[$DNS_RESOLVER]";; esac
export DNS_RESOLVER
# No ingestion listener until all processing groups are ready.
deadline=$(( $(date +%s) + ${STARTUP_TIMEOUT:-900} ))
for host in "$SENTRY_CONSUMERS_HOST" "$SNUBA_CONSUMERS_HOST" "$TASKS_HOST"; do
    until wget -q -T 5 -O /dev/null "http://$host:8080/ready"; do
        [ "$(date +%s)" -lt "$deadline" ] || exit 1
        sleep 3
    done
done
exec /docker-entrypoint.sh nginx -g 'daemon off;'
