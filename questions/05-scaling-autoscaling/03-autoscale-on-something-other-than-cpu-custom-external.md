# Autoscale on something other than CPU — custom/external metrics — and where KEDA fits.

[↑ Index](./README.md) · [← Prev](./02-an-hpa-sits-at-and-won-t-scale.md) · [Next →](./04-how-does-cluster-autoscaler-decide-to-add-remove.md)

**Difficulty:** Advanced · **Tags:** `autoscaling`

- **Custom metrics** — per-Pod/object app metrics (custom.metrics API, Prometheus Adapter).
- **External metrics** — queue depth, RPS, cloud metrics.
- **KEDA** — add-on with dozens of **scalers** (Kafka lag, SQS, Prometheus, cron) → feeds
  HPA + adds **scale-to-zero**.

**Why it matters:** scaling on **backlog / consumer lag** is more correct + responsive than
CPU for worker pools — it tracks *work to do*, not a lagging side-effect.

**Caveats:** tune per-replica target + cooldown or it thrashes; scale-to-zero adds cold-start
latency (mask with a min floor).

---

[↑ Index](./README.md) · [← Prev](./02-an-hpa-sits-at-and-won-t-scale.md) · [Next →](./04-how-does-cluster-autoscaler-decide-to-add-remove.md)
