# Storage

### Q: Explain PV, PVC, and StorageClass, and how dynamic provisioning ties them together.

**Difficulty:** Easy · **Tags:** `storage`

A **PersistentVolume** is a concrete piece of storage in the cluster (a cloud disk, an
NFS export) with a capacity, access mode, and reclaim policy. A
**PersistentVolumeClaim** is a *request* by a workload — "I need 20Gi, ReadWriteOnce" —
that is namespaced and what a Pod actually references. A **StorageClass** names a
provisioner and parameters (disk type, IOPS, filesystem, zone behavior) and is the key to
**dynamic** provisioning.

Statically, an admin pre-creates PVs and a PVC binds to a matching one. Dynamically — the
normal case — the PVC names a StorageClass, the class's **CSI provisioner** creates a PV
(and the backing cloud volume) on demand, and binds it. So the flow a Pod depends on is
**Pod → PVC → PV → StorageClass → CSI driver → real disk**. The nuance: the
StorageClass is where you encode the important defaults — `reclaimPolicy`,
`allowVolumeExpansion`, and especially `volumeBindingMode: WaitForFirstConsumer`, which
delays creating the disk until a Pod is scheduled so the disk lands in the *same zone* as
the Pod (get this wrong and your Pod is stuck because its disk is in another zone).

---

### Q: A StatefulSet Pod is stuck `Pending` on storage. Walk through the causes.

**Difficulty:** Hard · **Tags:** `storage` `statefulset`

A StatefulSet creates a PVC per Pod from its `volumeClaimTemplates`, so storage is on the
critical path to scheduling. The causes, roughly in order of how often they bite: the PVC
is **unbound** (no provisioner, provisioner erroring, or a static setup with no matching
PV); a **StorageClass / access-mode mismatch** (the requested class doesn't exist, or you
asked for ReadWriteMany on block storage that only does ReadWriteOnce);
**zone/topology unsatisfiable** (the disk exists in zone A but the Pod can only schedule
in zone B — classic when `WaitForFirstConsumer` isn't set, so the disk was provisioned
before the Pod was placed); or the **volume is still attached elsewhere** (an RWO disk
can't attach to a new node until it's detached from the old one, which stalls after an
ungraceful node failure).

The method: read events across the whole chain — `kubectl describe` the **Pod**, the
**PVC**, the **PV**, and look at the StorageClass and CSI controller/node logs. That tells
you whether you're waiting on binding, on attachment, or on a topology conflict. Staff-
level discipline: **do not** "fix" it by deleting the PVC or PV — that can destroy data
depending on reclaim policy. First confirm the reclaim policy, whether the data is
precious, whether a snapshot exists, and whether the old attachment is truly gone
(force-detach only after verifying the old node won't write). The prevention story:
`WaitForFirstConsumer`, topology-aware provisioning, and a runbook for attachment
conflicts after node failure.

---

### Q: Explain the volume access modes, and the gotcha people hit with ReadWriteOnce.

**Difficulty:** Intermediate · **Tags:** `storage`

Four modes. **ReadWriteOnce (RWO)** — mounted read-write by a single **node** (most block
storage: EBS, PD, Azure Disk). **ReadOnlyMany (ROX)** — read-only by many nodes.
**ReadWriteMany (RWX)** — read-write by many nodes simultaneously, which requires a shared
filesystem (NFS, CephFS, EFS/Filestore), *not* ordinary block storage.
**ReadWriteOncePod (RWOP)** — read-write by exactly one **Pod** (stricter than RWO, which
is per-node).

The gotcha: RWO is "once per **node**," not "once per Pod" — multiple Pods on the *same*
node can share an RWO volume, which surprises people who assume exclusivity. The bigger
operational trap is that an RWO volume **cannot attach to a Pod on a different node while
still attached to the old one**, so during a rolling update or node failure you can get a
`Multi-Attach` error and a stuck Pod until the old attachment is released — which is
exactly why RWO workloads should use `Recreate`-style handling or proper detach-on-drain,
and why StatefulSets pin a Pod's PVC to the Pod's identity. The point: if you
genuinely need many Pods on many nodes writing the same volume, you need RWX and a shared
filesystem — forcing RWX semantics onto block storage is a design error.

---

### Q: What are PV reclaim policies, and how does picking the wrong one cause data loss?

**Difficulty:** Intermediate · **Tags:** `storage`

The reclaim policy governs what happens to the PV (and its backing storage) when its PVC
is deleted. **Retain** keeps the PV and the underlying disk intact, moving the PV to
`Released`; the data survives and an admin must manually reclaim or re-bind it — the safe
choice for anything precious. **Delete** removes the PV *and* deletes the backing cloud
volume — convenient and the default for dynamically provisioned storage, but it means
deleting a PVC **destroys the data**. **Recycle** is deprecated.

The data-loss scenario is mundane and common: a production database's StorageClass is left
at the default `Delete`, someone deletes the StatefulSet and its PVCs (or a cleanup script
does), and the cloud disks vanish with the data — no undo. The practice: set
`reclaimPolicy: Retain` on StorageClasses used for stateful/important data, treat PVC
deletion as a destructive operation gated like any other (RBAC, careful automation), and
back the whole thing with real backups/snapshots because reclaim policy is *not* a backup
— Retain protects against an accidental PVC delete, not against corruption or a region
outage. The answer that signals seniority is naming that reclaim policy, snapshots, and
backups are three different layers of protection.

---

### Q: Walk me through the PVC→PV binding lifecycle, and explain `WaitForFirstConsumer`.

**Difficulty:** Intermediate · **Tags:** `storage`

A PVC specifies size, access mode, and optionally a StorageClass, and starts `Pending`.
**Static binding**: the control plane finds a pre-existing PV that satisfies the claim and
binds them (`Bound`). **Dynamic binding**: the named StorageClass's provisioner creates a
PV sized to the claim and binds it. The Pod can only mount once the PVC is `Bound`. On PVC
deletion the PV follows its reclaim policy (`Retain`/`Delete`).

`volumeBindingMode` is the part that matters for correctness. The default, **Immediate**,
provisions and binds the volume as soon as the PVC is created — *before* any Pod is
scheduled. In a multi-zone cluster that's a bug waiting to happen: the disk is created in
some zone, then the scheduler may want to place the Pod in a *different* zone, and now the
Pod can't run because the zonal disk is unreachable. **WaitForFirstConsumer** fixes this by
delaying provisioning/binding until a Pod referencing the PVC is being scheduled, so the
volume is created in the **same zone/topology** the scheduler chose for the Pod. Staff-
level framing: on any multi-zone cluster with zonal block storage, `WaitForFirstConsumer`
should be the default on your StorageClasses — Immediate binding is the root cause of a
whole category of "Pod Pending, PVC Bound, but in the wrong zone" incidents.

---

### Q: Can you resize a PersistentVolume? Shrink it? What are the constraints?

**Difficulty:** Intermediate · **Tags:** `storage`

You can **grow** a PV if the StorageClass has `allowVolumeExpansion: true` and the CSI
driver supports expansion: you edit the PVC's `spec.resources.requests.storage` to a
larger value, the CSI driver expands the backing volume, and the filesystem is grown —
online (no restart) for many modern drivers, though some older ones need the Pod to
restart to finish the filesystem resize. You **cannot shrink** a PVC — Kubernetes doesn't
support reducing volume size (shrinking filesystems safely is risky and generally
unsupported by the providers).

The nuance: expansion only goes one way, so right-size conservatively and grow as
needed rather than over-provisioning up front "to be safe," since you can't walk it back
without migrating data to a new, smaller volume. For capacity planning, monitor
filesystem usage and automate/alert before you hit full — a full PV can wedge a stateful
workload (writes fail, DB goes read-only) and expansion under pressure is a bad time to
discover your StorageClass had `allowVolumeExpansion: false`. The thorough answer also
mentions that expansion applies to the PVC/filesystem, so stateful apps that cache
capacity may need a nudge to see the new space.
