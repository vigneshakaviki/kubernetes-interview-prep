# Owner references, cascading GC, and finalizers — and why is an object stuck in `Terminating`?

[↑ Index](./README.md) · [← Prev](./11-operator-pattern-and-crds-when-is-it-right.md) · [Next →](./13-namespaces-resourcequota-limitrange-how-do-they-stop-one.md)

**Difficulty:** Advanced · **Tags:** `architecture` `lifecycle`

- **ownerReferences** form a tree (Pod → ReplicaSet → Deployment); the GC cascades deletes.
- **Propagation:** `Background` (default), `Foreground` (parent stays `Terminating` until
  children gone), `Orphan` (children survive).
- **Finalizer** — a key that **blocks** deletion until a controller does cleanup
  (deprovision a cloud LB) and removes it; only when the list is empty is the object purged.

**Stuck in `Terminating`** = a finalizer isn't being cleared → the responsible controller
is down/crashed/deleted (or a foreground cascade waits on a child).
- Debug: `kubectl get -o yaml` → check `metadata.finalizers` + `deletionTimestamp`; fix
  the controller.
- Force-removing a finalizer unblocks delete but **leaks** the external resource — last
  resort.

---

[↑ Index](./README.md) · [← Prev](./11-operator-pattern-and-crds-when-is-it-right.md) · [Next →](./13-namespaces-resourcequota-limitrange-how-do-they-stop-one.md)
