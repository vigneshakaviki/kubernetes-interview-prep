# Explain PV, PVC, StorageClass, and how dynamic provisioning ties them together.

[↑ Index](./README.md) · [Next →](./02-a-statefulset-pod-is-stuck-on-storage-walk.md)

**Difficulty:** Easy · **Tags:** `storage`

- **PV** — concrete storage in the cluster (cloud disk, NFS) with capacity/access-mode/reclaim.
- **PVC** — a namespaced *request* ("20Gi, RWO") that a Pod references.
- **StorageClass** — names a provisioner + params (disk type, IOPS, zone behavior); enables
  **dynamic** provisioning.

**Flow:** `Pod → PVC → PV → StorageClass → CSI driver → real disk`.
- Static: PVC binds a pre-made PV. Dynamic (normal): provisioner creates the PV on demand.

**Gotcha:** set `volumeBindingMode: WaitForFirstConsumer` on the class → delays disk
creation until a Pod is scheduled, so the disk lands in the **same zone** as the Pod (else
Pod stuck, disk in wrong zone).

---

[↑ Index](./README.md) · [Next →](./02-a-statefulset-pod-is-stuck-on-storage-walk.md)
