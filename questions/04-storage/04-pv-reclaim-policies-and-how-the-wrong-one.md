# PV reclaim policies, and how the wrong one causes data loss.

[↑ Index](./README.md) · [← Prev](./03-volume-access-modes-and-the-gotcha-with-readwriteonce.md) · [Next →](./05-walk-through-the-pvc-pv-binding-lifecycle-and.md)

**Difficulty:** Intermediate · **Tags:** `storage`

On PVC deletion:
- **Retain** — keeps PV + disk (`Released`); manual reclaim. Safe for precious data.
- **Delete** — removes PV **and** the backing cloud volume. Default for dynamic → **deleting
  a PVC destroys the data**.
- **Recycle** — deprecated.

**Loss scenario:** prod DB's StorageClass left at default `Delete`; someone deletes the
StatefulSet + PVCs → disks vanish, no undo.

**Practice:** `Retain` for stateful/important data; treat PVC delete as destructive (RBAC,
careful automation). Reclaim policy ≠ backup — **reclaim, snapshots, backups are 3 layers**.

---

[↑ Index](./README.md) · [← Prev](./03-volume-access-modes-and-the-gotcha-with-readwriteonce.md) · [Next →](./05-walk-through-the-pvc-pv-binding-lifecycle-and.md)
