# ClusterIP vs NodePort vs LoadBalancer — how they stack.

[↑ Index](./README.md) · [← Prev](./03-how-does-in-cluster-dns-work-and-how.md) · [Next →](./05-headless-service-how-it-differs-at-dns-level.md)

**Difficulty:** Intermediate · **Tags:** `networking`

Each layers on the previous:
| Type | Adds | Reach |
|------|------|-------|
| **ClusterIP** | base VIP | inside cluster only |
| **NodePort** | static port on every node | any node IP:port |
| **LoadBalancer** | cloud LB → NodePorts | external IP |

**`externalTrafficPolicy`:**
- `Cluster` (default) — spreads across all nodes but **SNATs** → hides client IP, extra hop.
- `Local` — preserves client source IP, no extra hop, but only hits nodes **with** a Pod
  (need even spread).

**Rule:** ClusterIP internal; Ingress over ClusterIP for HTTP; LoadBalancer for a true
external entry; `Local` when you need real client IPs.

---

[↑ Index](./README.md) · [← Prev](./03-how-does-in-cluster-dns-work-and-how.md) · [Next →](./05-headless-service-how-it-differs-at-dns-level.md)
