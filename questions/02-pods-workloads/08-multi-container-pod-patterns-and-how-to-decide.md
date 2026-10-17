# Multi-container Pod patterns, and how to decide same-Pod vs separate-Pod.

[↑ Index](./README.md) · [← Prev](./07-init-containers-vs-sidecars-and-what-changed-with.md) · [Next →](./09-job-vs-cronjob-the-knobs-that-decide-correctness.md)

**Difficulty:** Intermediate · **Tags:** `workloads` `patterns`

**Patterns** (all share the Pod's network + volumes):
- **Sidecar** — augments the main container (mesh proxy, log tailer).
- **Ambassador** — proxies the app's *outbound* connections (localhost → sharded DB).
- **Adapter** — transforms the app's *output* for a consumer (logs → Prometheus format).

**Decision rule:** same Pod **only** if they must be co-scheduled + share
lifecycle/network/volumes. Scale/update independently or live on different nodes →
**separate Pods** behind a Service.

**Smell test:** wanting to scale one container but not the other means it was never a
sidecar — it's a separate workload you've coupled, and you pay at every rollout.

---

[↑ Index](./README.md) · [← Prev](./07-init-containers-vs-sidecars-and-what-changed-with.md) · [Next →](./09-job-vs-cronjob-the-knobs-that-decide-correctness.md)
