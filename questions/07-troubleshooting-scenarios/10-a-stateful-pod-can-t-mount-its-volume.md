# A stateful Pod can't mount its volume. Walk through it — carefully, data is at risk.

[↑ Index](./README.md) · [← Prev](./09-a-node-goes-and-its-pods-disappear-respond.md) · [Next →](./11-a-distributed-database-shows-data-inconsistency-across-replicas.md)

**Difficulty:** Hard · **Tags:** `storage` `csi`

**Read events across the chain:** Pod → PVC → PV → StorageClass → CSI controller/node logs.

**Causes:** unbound claim · StorageClass/access-mode mismatch (RWX on block) · unsatisfiable
topology (zonal disk vs Pod zone) · **volume still attached elsewhere** (`Multi-Attach`
after ungraceful node failure).

**Safety (the point of the question):**
- ❌ Don't delete the PVC/PV to "reset" — may destroy data.
- ✅ First confirm reclaim policy, data value, snapshot, and that the old node is **fenced**
  before force-detach (force-detaching a live-mounted volume risks corruption).

**Prevent:** storage monitoring, **tested restores**, `WaitForFirstConsumer`, an
attachment-conflict runbook.

---

[↑ Index](./README.md) · [← Prev](./09-a-node-goes-and-its-pods-disappear-respond.md) · [Next →](./11-a-distributed-database-shows-data-inconsistency-across-replicas.md)
