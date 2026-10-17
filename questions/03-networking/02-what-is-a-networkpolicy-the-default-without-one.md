# What is a NetworkPolicy, the default without one, and the gotcha people miss?

[↑ Index](./README.md) · [← Prev](./01-service-vs-ingress-where-does-each-operate-and.md) · [Next →](./03-how-does-in-cluster-dns-work-and-how.md)

**Difficulty:** Medium · **Tags:** `networking` `security`

- **Default:** flat + open — every Pod reaches every Pod, no isolation.
- **NetworkPolicy:** namespaced allow-list by Pod label / namespace / IP block.
- **Behavior:** additive + **default-deny-once-selected** — once any policy selects a Pod
  for a direction, all not-allowed traffic in that direction is denied; unselected Pods
  stay open.

**Two gotchas:**
1. **Does nothing without an enforcing CNI** (Calico/Cilium) — on a CNI that ignores it,
   your "deny" silently allows → false security.
2. People write ingress rules + forget **egress/DNS** — a default-deny-egress that doesn't
   allow kube-dns breaks name resolution for every selected Pod.

---

[↑ Index](./README.md) · [← Prev](./01-service-vs-ingress-where-does-each-operate-and.md) · [Next →](./03-how-does-in-cluster-dns-work-and-how.md)
