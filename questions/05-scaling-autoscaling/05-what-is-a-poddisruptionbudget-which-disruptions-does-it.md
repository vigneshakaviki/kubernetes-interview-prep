# What is a PodDisruptionBudget, which disruptions does it govern, and when does it save you?

[↑ Index](./README.md) · [← Prev](./04-how-does-cluster-autoscaler-decide-to-add-remove.md)

**Difficulty:** Advanced · **Tags:** `availability`

- Declares max unavailable from **voluntary** disruptions (`minAvailable` / `maxUnavailable`).
  The eviction API **refuses** an eviction that would breach it.
- Governs: drains, autoscaler scale-down, node-pool upgrades.
- Does **not** govern **involuntary** (node crash, OOM) — can't budget away a crash.

**Saves you:** draining nodes for an upgrade with no PDB can evict all replicas of a quorum
service at once → outage. PDB forces one-at-a-time.

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata: { name: api-pdb }
spec:
  minAvailable: 2            # a drain/scale-down can't take this set below 2
  selector: { matchLabels: { app: api } }
```

**Caveats:** `minAvailable: 100%` **blocks drains entirely** → wedges upgrades/autoscaler.
Only helps with enough replicas (1 replica + `minAvailable: 1` = undrainable).

---

[↑ Index](./README.md) · [← Prev](./04-how-does-cluster-autoscaler-decide-to-add-remove.md)
