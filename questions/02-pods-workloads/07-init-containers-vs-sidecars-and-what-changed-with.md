# Init containers vs sidecars — and what changed with native sidecar support.

[↑ Index](./README.md) · [← Prev](./06-configmap-vs-secret-and-if-secrets-aren-t.md) · [Next →](./08-multi-container-pod-patterns-and-how-to-decide.md)

**Difficulty:** Intermediate · **Tags:** `workloads`

| | Runs | Purpose |
|--|------|---------|
| **init container** | to completion, in order, *before* app | wait-for-dep, migration, fetch config |
| **sidecar** | *alongside* app, whole life | proxy, log shipper, metrics adapter |

**The old problem** (sidecar as a plain `containers[]` entry):
- No guarantee the sidecar was ready **before** the app.
- Sidecar didn't stop cleanly on shutdown → mesh proxy dying first stranded outbound
  calls; a never-exiting sidecar **blocked Job completion**.

**Native sidecar (1.29 GA):** an **init container with `restartPolicy: Always`** —
starts before main, terminates after it, and lets Jobs complete. Use it when ordering
with the main container matters (mesh, credential refreshers); plain init containers
remain for one-shot preconditions.

---

[↑ Index](./README.md) · [← Prev](./06-configmap-vs-secret-and-if-secrets-aren-t.md) · [Next →](./08-multi-container-pod-patterns-and-how-to-decide.md)
