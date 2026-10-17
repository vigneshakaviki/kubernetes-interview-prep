# HPA, VPA, Cluster Autoscaler — what each changes, and how they interact/conflict.

[↑ Index](./README.md) · [Next →](./02-an-hpa-sits-at-and-won-t-scale.md)

**Difficulty:** Medium · **Tags:** `autoscaling`

| | Changes | Axis |
|--|---------|------|
| **HPA** | replica count | scale out |
| **VPA** | per-Pod requests/limits | scale up (right-size) |
| **Cluster Autoscaler** | node count | capacity |

**Conflicts:**
- **HPA + VPA on the same resource** (both on CPU) → fight (HPA adds replicas to lower CPU
  while VPA raises requests) → oscillation. Supported: VPA on mem + HPA on CPU, or VPA
  recommend-only.
- **HPA without a node autoscaler** → new replicas sit `Pending`. HPA "doesn't scale" when
  the real bottleneck is node capacity.

---

[↑ Index](./README.md) · [Next →](./02-an-hpa-sits-at-and-won-t-scale.md)
