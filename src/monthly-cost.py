"""Extrapolate measured idle series at published container rates, without forecasts."""
import datetime as dt
import json
import pathlib
from evidence_files import read

root = pathlib.Path(__file__).resolve().parent
rows = []
for path in sorted((root / 'evidence').glob('cold4-idle-*.json')):
    data = json.loads(read(path))
    if 'measurements' not in data or data.get('service') == 'sdk':
        continue
    row = {'service': data['service']}
    for meter, key in [('MEMORY_USAGE_GB', 'ram_gb'), ('CPU_USAGE', 'vcpu')]:
        points = data['measurements'][meter]
        assert len(points) > 1, (path, meter)
        duration = (dt.datetime.fromisoformat(points[-1]['ts']) -
                    dt.datetime.fromisoformat(points[0]['ts'])).total_seconds() / 60
        integral = sum((a['value'] + b['value']) / 2 *
                       (dt.datetime.fromisoformat(b['ts']) -
                        dt.datetime.fromisoformat(a['ts'])).total_seconds() / 60
                       for a, b in zip(points, points[1:]))
        row[key] = integral / duration
        row[key + '_sample_minutes'] = duration
    rows.append(row)
assert len(rows) == 14
ram = sum(row['ram_gb'] for row in rows)
cpu = sum(row['vcpu'] for row in rows)
result = {
    'created_at_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
    'source': 'https://docs.railway.com/pricing/plans',
    'method': 'Time-weighted mean per service using actual first/last sample timestamps; excludes SDK',
    'scenario': 'Repeat observed healthy idle resource use continuously for 30 days; no workload growth assumed',
    'month_minutes': 30 * 24 * 60,
    'ram_gb_mean': ram, 'cpu_vcpu_mean': cpu,
    'ram_usd_30_days': ram * .000231 * 43200,
    'cpu_usd_30_days': cpu * .000463 * 43200,
    'compute_usd_30_days': (ram * .000231 + cpu * .000463) * 43200,
    'monthly_total_formula': 'compute + 0.15*mean_billable_volume_GB + 0.05*monthly_service_egress_GB + 0.015*billable_bucket_GB_month; plan credits apply workspace-wide',
    'limitation': 'Compute-only measured-idle extrapolation, not an invoice or full monthly forecast. No invented storage/traffic/retention inputs.',
    'services': rows,
}
(root / 'evidence/monthly-cost.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({key: result[key] for key in ['ram_gb_mean', 'cpu_vcpu_mean', 'compute_usd_30_days']}))
