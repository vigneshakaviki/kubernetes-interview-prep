# Namespaces, ResourceQuota, LimitRange — how do they stop one team taking down a shared cluster?

[↑ Index](./README.md) · [← Prev](./12-owner-references-cascading-gc-and-finalizers-and-why.md) · [Next →](./14-labels-vs-annotations-where-s-the-line-and.md)

**Difficulty:** Intermediate · **Tags:** `multi-tenancy`

- **Namespace** — virtual scope for names/RBAC/quota/policy. **Not** a hard security
  boundary (shared kernel/nodes) → untrusted tenancy needs more (node pools, NetworkPolicy,
  Pod Security, sometimes separate clusters).
- **ResourceQuota** — caps aggregate requests/limits + object counts **per namespace**.
- **LimitRange** — per-container defaults + min/max.

**Interaction:** once a CPU/mem quota is set, every Pod **must** declare requests/limits or
it's rejected → LimitRange supplies sane defaults so nothing breaks and nobody requests an
absurd amount.

**Without them:** one Deployment with no limits can evict everyone under node pressure.

---

[↑ Index](./README.md) · [← Prev](./12-owner-references-cascading-gc-and-finalizers-and-why.md) · [Next →](./14-labels-vs-annotations-where-s-the-line-and.md)
