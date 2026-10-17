# Deployment update strategies, and how canary / blue-green fit on top.

[↑ Index](./README.md) · [← Prev](./04-qos-classes-and-the-exact-kubelet-eviction-order.md) · [Next →](./06-configmap-vs-secret-and-if-secrets-aren-t.md)

**Difficulty:** Intermediate · **Tags:** `deployments` `rollout`

**Native strategies:**
- **RollingUpdate** (default) — incremental, bounded by `maxSurge` / `maxUnavailable`.
  Zero-downtime *if* readiness is honest and the app is backward-compatible.
- **Recreate** — kill all old, then start new. Downtime, but correct when two versions
  can't coexist (incompatible schema, exclusive lock).

**Built on top (not first-class — you need a traffic layer):**
- **Canary** — small % to new version, watch metrics, widen. Crude: two Deployments +
  replica ratio behind one Service. Real: mesh/ingress weight + automated analysis
  (Argo Rollouts / Flagger) that promotes or aborts on SLO signals.
- **Blue-green** — run full new (green) beside old (blue), flip the Service selector,
  keep blue for instant rollback.

**Framing:** rolling update = *how pods are replaced*; canary/blue-green = *how traffic
shifts and how fast you can abort* — the latter is where the reliability win is.

---

[↑ Index](./README.md) · [← Prev](./04-qos-classes-and-the-exact-kubelet-eviction-order.md) · [Next →](./06-configmap-vs-secret-and-if-secrets-aren-t.md)
