# Monitor cluster + workload health with Prometheus — how?

[↑ Index](./README.md) · [← Prev](./04-error-budget-nearly-exhausted-mid-quarter-what-happens.md)

**Difficulty:** Medium · **Tags:** `monitoring` `prometheus`

**Sources:** node-exporter (hosts) · kube-state-metrics (object state: Pod phase, restarts,
desired-vs-available, PVCs) · control-plane (API latency, etcd fsync/DB size) · cAdvisor/
kubelet (container usage) · app `/metrics`. SD via Kubernetes; Thanos/Mimir for retention.

**Alert on leading indicators** (precede the [scenarios](./07-troubleshooting-scenarios.md)):
rising restarts/OOMKills, Pending Pods, available < desired, node pressure/NotReady, PVC near
full, API/etcd latency — **but page on the user-facing SLI**, keep internals on dashboards.

**Gotcha:** watch Prometheus's own **cardinality** — a per-request-id label will OOM
Prometheus itself.

---

[↑ Index](./README.md) · [← Prev](./04-error-budget-nearly-exhausted-mid-quarter-what-happens.md)
