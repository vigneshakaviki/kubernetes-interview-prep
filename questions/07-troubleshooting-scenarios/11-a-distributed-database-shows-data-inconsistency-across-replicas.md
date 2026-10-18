# A distributed database shows data inconsistency across replicas. Causes + investigation.

[↑ Index](./README.md) · [← Prev](./10-a-stateful-pod-can-t-mount-its-volume.md) · [Next →](./12-kubectl-is-slow-and-the-api-server-times-out.md)

**Difficulty:** Hard · **Tags:** `distributed` `databases`

**First:** expected or a real violation? Many systems are **eventually consistent** — a
read off a lagging replica is stale, not wrong. Confirm the consistency model before calling
it a bug.

**True-divergence causes:**
- **Replication lag** · **leader election / split-brain** (two primaries after a partition)
  · **clock skew** (bad last-writer-wins) · **network partition** (independent writes).

**Investigate:** which replicas/keys disagree · replication + leader-change metrics · NTP
drift · were quorum settings actually in force?

**Mitigate:** promote a known-good replica + reconcile; fence the bad node.
**Prevent:** quorum reads/writes, fencing, bounded clock sync; don't route consistency-
sensitive reads to async followers.

---

[↑ Index](./README.md) · [← Prev](./10-a-stateful-pod-can-t-mount-its-volume.md) · [Next →](./12-kubectl-is-slow-and-the-api-server-times-out.md)
