# What does a service mesh add over plain K8s networking, and what's the cost?

[↑ Index](./README.md) · [← Prev](./07-kube-proxy-iptables-vs-ipvs-what-breaks-at.md) · [Next →](./09-how-do-pods-discover-each-other-dns-vs.md)

**Difficulty:** Advanced · **Tags:** `networking` `mesh`

**Adds** (via sidecar / eBPF data plane, no app changes):
- **mTLS** everywhere (identity-based authn/encryption).
- **L7 traffic control** — weighted canary, retries, timeouts, circuit breaking, fault injection.
- **Rich telemetry** — per-route golden signals, tracing.

**Cost:** per-Pod sidecar CPU/mem + extra hop (latency); big operational complexity (control-
plane upgrades, cert rotation, "app or proxy?" debugging). → newer **ambient/eBPF** meshes
cut per-Pod overhead.

**Rule:** adopt for genuine mTLS/zero-trust across many services, automated progressive
delivery, or uniform L7 telemetry — not because it's fashionable.

---

[↑ Index](./README.md) · [← Prev](./07-kube-proxy-iptables-vs-ipvs-what-breaks-at.md) · [Next →](./09-how-do-pods-discover-each-other-dns-vs.md)
