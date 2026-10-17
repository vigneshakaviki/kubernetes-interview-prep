# A Pod has been `Pending` for 20 minutes. Walk through it.

[↑ Index](./README.md) · [Next →](./02-a-pod-fails-to-start-several-reasons-look.md)

**Difficulty:** Medium · **Tags:** `scheduling` `troubleshooting`

**`Pending` = can't schedule, or scheduled-but-won't-start.** `kubectl describe pod` → read
scheduler events.

**Unschedulable causes:**
- Requests > any node's allocatable (remember system-reserved eats allocatable).
- Taints without toleration · unsatisfied nodeSelector/affinity/topology.
- **Unbound PVC** (zonal disk the scheduler can't match).

Scheduled-but-not-starting → image-pull or volume-attach events instead.

**Fix the real constraint**, not the symptom:
- ❌ Deleting the Pod — controller recreates the same spec, still Pending.
- ❌ Adding nodes when it's a nodeSelector typo — burns money.
- ✅ Read the failed predicate, fix *that*.

---

[↑ Index](./README.md) · [Next →](./02-a-pod-fails-to-start-several-reasons-look.md)
