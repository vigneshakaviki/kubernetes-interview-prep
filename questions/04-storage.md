# Storage

### Q: Explain PV, PVC, StorageClass, and how dynamic provisioning ties them together.

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

### Q: A StatefulSet Pod is stuck `Pending` on storage. Walk through the causes.

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

### Q: Volume access modes, and the gotcha with ReadWriteOnce.

**Difficulty:** Intermediate · **Tags:** `storage`

| Mode | Access |
|------|--------|
| **RWO** | RW by a single **node** (most block storage) |
| **ROX** | RO by many nodes |
| **RWX** | RW by many nodes — needs a shared FS (NFS/CephFS/EFS) |
| **RWOP** | RW by exactly one **Pod** (stricter than RWO) |

**Gotchas:**
- RWO is "once per **node**," not per Pod — multiple Pods on the *same* node can share it.
- RWO **can't attach to a Pod on another node** while still attached → `Multi-Attach` error
  + stuck Pod during rollout/node failure.
- Need many Pods on many nodes writing one volume → that's **RWX + shared FS**, not block.

---

### Q: PV reclaim policies, and how the wrong one causes data loss.

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

### Q: Walk through the PVC→PV binding lifecycle and explain `WaitForFirstConsumer`.

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

### Q: Can you resize a PersistentVolume? Shrink it?

**Difficulty:** Intermediate · **Tags:** `storage`

- **Grow:** yes, if StorageClass has `allowVolumeExpansion: true` + CSI supports it. Edit the
  PVC's requested size → volume + filesystem expand (online for many drivers; some need a
  Pod restart to finish).
- **Shrink:** **no** — unsupported.

**Implications:**
- Expansion is one-way → right-size conservatively, grow later. Don't over-provision up front.
- Monitor/alert before full — a full PV wedges a stateful app (writes fail, DB read-only),
  and discovering `allowVolumeExpansion: false` under pressure is a bad time.
