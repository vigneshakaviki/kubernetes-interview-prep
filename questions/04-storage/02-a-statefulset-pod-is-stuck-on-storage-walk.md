# A StatefulSet Pod is stuck `Pending` on storage. Walk through the causes.

[↑ Index](./README.md) · [← Prev](./01-explain-pv-pvc-storageclass-and-how-dynamic-provisioning.md) · [Next →](./03-volume-access-modes-and-the-gotcha-with-readwriteonce.md)

**Difficulty:** Hard · **Tags:** `storage` `statefulset`

StatefulSet creates a PVC per Pod → storage is on the critical path.

**Causes (most common first):**
- **Unbound PVC** — no/erroring provisioner, or no matching static PV.
- **StorageClass / access-mode mismatch** — class missing; RWX asked on block storage.
- **Zone/topology unsatisfiable** — disk in zone A, Pod can only land in zone B
  (the `WaitForFirstConsumer` story).
- **Volume still attached elsewhere** — RWO `Multi-Attach` after ungraceful node failure.

**Method:** `describe` the Pod → PVC → PV, check StorageClass + CSI logs → waiting on
binding, attachment, or topology?

**Safety:** **do not** delete the PVC/PV to "reset" — may destroy data. First confirm
reclaim policy, data value, snapshot, and that the old node is truly gone before force-detach.

---

[↑ Index](./README.md) · [← Prev](./01-explain-pv-pvc-storageclass-and-how-dynamic-provisioning.md) · [Next →](./03-volume-access-modes-and-the-gotcha-with-readwriteonce.md)
