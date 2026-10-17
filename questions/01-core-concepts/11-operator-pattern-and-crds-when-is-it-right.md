# Operator pattern and CRDs — when is it right vs over-engineering?

[↑ Index](./README.md) · [← Prev](./10-how-does-the-scheduler-place-a-pod-and.md) · [Next →](./12-owner-references-cascading-gc-and-finalizers-and-why.md)

**Difficulty:** Advanced · **Tags:** `architecture` `extensibility`

- **CRD** — registers a new API `kind` (served with the same RBAC/watch/kubectl machinery).
- **Operator** — a controller watching that resource, reconciling reality → spec, encoding
  *day-2 ops* (provision, scale, backup, failover, upgrade).

**Right call:** managing a stateful/complex system whose day-2 ops are domain-specific +
repetitive — i.e. the thing you're automating is a **control loop**.

**Over-engineering:** a one-time install a Helm chart or built-in controllers would do —
because you now own controller correctness (idempotency, partial failure, status/
conditions, finalizers, no hot reconcile loops).

---

[↑ Index](./README.md) · [← Prev](./10-how-does-the-scheduler-place-a-pod-and.md) · [Next →](./12-owner-references-cascading-gc-and-finalizers-and-why.md)
