# Walk through the PVC→PV binding lifecycle and explain `WaitForFirstConsumer`.

[↑ Index](./README.md) · [← Prev](./04-pv-reclaim-policies-and-how-the-wrong-one.md) · [Next →](./06-can-you-resize-a-persistentvolume-shrink-it.md)

**Difficulty:** Intermediate · **Tags:** `storage`

- PVC starts `Pending` → binds (static: matching PV; dynamic: provisioner makes one) →
  `Bound` → Pod can mount.
- `volumeBindingMode`:
  - **Immediate** (default) — provisions/binds *before* a Pod is scheduled → in multi-zone,
    disk may land in a zone the Pod can't reach → Pod stuck.
  - **WaitForFirstConsumer** — delays until a Pod is scheduled → disk created in the
    **same zone/topology** the scheduler chose.

**Rule:** on any multi-zone cluster with zonal block storage, `WaitForFirstConsumer` should
be the default. Immediate binding is the root cause of "Pod Pending, PVC Bound, wrong zone."

---

[↑ Index](./README.md) · [← Prev](./04-pv-reclaim-policies-and-how-the-wrong-one.md) · [Next →](./06-can-you-resize-a-persistentvolume-shrink-it.md)
