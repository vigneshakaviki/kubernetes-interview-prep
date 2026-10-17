# How does Cluster Autoscaler decide to add/remove a node — and why not just watch CPU?

[↑ Index](./README.md) · [← Prev](./03-autoscale-on-something-other-than-cpu-custom-external.md) · [Next →](./05-what-is-a-poddisruptionbudget-which-disruptions-does-it.md)

**Difficulty:** Advanced · **Tags:** `autoscaling` `nodes`

Scales on **schedulability, not utilization**:
- **Up** — Pods `Pending` for lack of fit → simulates which node group would make them
  schedulable → grows it.
- **Down** — node underused **and** its Pods can move → drain + remove.

**Blocked scale-down:** PodDisruptionBudget, bare Pods (no controller), local storage
(`emptyDir`/hostPath), "do-not-evict" annotations → one unmovable Pod pins an expensive node.

**Why not CPU:** a node full of high-*request* low-*usage* Pods is "full" to the scheduler —
reservations, not usage, decide fit.

**Note:** depends on accurate **requests**; **Karpenter** provisions right-sized nodes per
pending-Pod shape (better bin-pack, more churn).

---

[↑ Index](./README.md) · [← Prev](./03-autoscale-on-something-other-than-cpu-custom-external.md) · [Next →](./05-what-is-a-poddisruptionbudget-which-disruptions-does-it.md)
