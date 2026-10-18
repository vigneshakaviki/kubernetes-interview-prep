# How is monitoring set up on the systems you run, end to end?

[↑ Index](./README.md) · [← Prev](./10-show-an-one-liner-and-when-awk-is.md) · [Next →](./12-cgroups-memory-limits-and-the-jvm-go-runtime.md)

**Difficulty:** Medium · **Tags:** `sre` `monitoring`

**Three pillars + response:** metrics (exporters + app `/metrics` → Prometheus → Grafana),
logs (shipped + aggregated — Loki/ELK), traces → **alerting on SLOs/golden signals** routed
by severity, every alert runbook-linked.

**SRE framing (vs "we have Grafana"):** page on **user-facing symptoms / SLO burn**, not
every cause; dashboards for root-cause *once engaged*; cluster internals (restarts, node
pressure, etcd latency) are **leading indicators** you trend, not page on.

**Gotcha:** the monitoring system needs the same rigor — bounded cardinality, tested alert
routing, pruned noisy alerts.

---

[↑ Index](./README.md) · [← Prev](./10-show-an-one-liner-and-when-awk-is.md) · [Next →](./12-cgroups-memory-limits-and-the-jvm-go-runtime.md)
