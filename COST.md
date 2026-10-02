# Measured cost

See [the measured window, raw calculation and scope](VALIDATION.md#cost).
Railway publishes RAM at $0.000231/GB-minute and CPU at $0.000463/vCPU-minute.
The thirty-day compute scenario is `(9.31265506742857 × 0.000231 +
0.17020029523809524 × 0.000463) × 43,200 = $96.33712567411749`.

This is a measured-load scenario, not a bill or capacity guarantee. Volumes,
bucket storage, service egress, growth and plan minimums/included credits apply
separately. Bucket endpoints use public TLS; uploads incur service egress.
[Official pricing](https://docs.railway.com/reference/pricing/plans).
