# Volume access modes, and the gotcha with ReadWriteOnce.

[↑ Index](./README.md) · [← Prev](./02-a-statefulset-pod-is-stuck-on-storage-walk.md) · [Next →](./04-pv-reclaim-policies-and-how-the-wrong-one.md)

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

[↑ Index](./README.md) · [← Prev](./02-a-statefulset-pod-is-stuck-on-storage-walk.md) · [Next →](./04-pv-reclaim-policies-and-how-the-wrong-one.md)
