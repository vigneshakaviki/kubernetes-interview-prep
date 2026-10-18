# A node drain hangs during a cluster upgrade — Pods won't evict. Why?

[↑ Index](./README.md) · [← Prev](./17-workloads-fail-tls-after-a-certificate-expired.md) · [Next →](./19-memory-climbs-all-day-then-pods-oom-every-night.md)

**Difficulty:** Medium · **Tags:** `nodes` `availability`

**Short answer:** `kubectl drain` uses the **eviction API**, which respects
**PodDisruptionBudgets**. A too-strict PDB (or a Pod that can't be moved) blocks it
indefinitely — by design, to protect availability.

**Causes the drain blocks on:**
- **PDB would be violated** — e.g. `minAvailable: 100%` or only enough replicas to satisfy
  the budget already elsewhere → eviction refused.
- **Pod has no controller** (bare Pod) → drain won't evict without `--force`.
- **Local storage** (`emptyDir`) → needs `--delete-emptydir-data`.
- **Pod stuck `Terminating`** (long/absent grace, stuck finalizer, unresponsive preStop).

**Diagnose:** `kubectl get pdb -A` (check `ALLOWED DISRUPTIONS: 0`), drain output names the
blocking Pod/PDB.

**Fix:** scale the workload up so the PDB allows one disruption, relax an over-strict PDB,
or address the unmovable Pod. **Prevent:** PDBs sized for maintenance (never 100%), enough
replicas, and sane termination grace. The lesson: the drain hanging is the PDB **doing its
job** — don't `--force` past it blindly on a quorum service.

---

[↑ Index](./README.md) · [← Prev](./17-workloads-fail-tls-after-a-certificate-expired.md) · [Next →](./19-memory-climbs-all-day-then-pods-oom-every-night.md)
