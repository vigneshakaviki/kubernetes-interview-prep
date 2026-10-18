# How do you canary a StatefulSet rollout — update one replica and hold?

[↑ Index](./README.md) · [← Prev](./11-what-happens-when-a-pod-is-deleted-grace.md)

**Difficulty:** Advanced · **Tags:** `statefulset` `rollout`

**Short answer:** StatefulSets don't have surge/canary like Deployments — you control the
rollout with `updateStrategy`: a **RollingUpdate `partition`** (canary by ordinal) or
**`OnDelete`** (manual, pod-by-pod).

**Partitioned rolling update:**
```yaml
updateStrategy:
  type: RollingUpdate
  rollingUpdate:
    partition: 3        # only pods with ordinal >= 3 get the new revision
```
- Set `partition` to `replicas-1` → only the **highest ordinal** updates → bake/observe →
  lower it step by step → 0 updates the rest. Updates go **high ordinal → low**, one at a
  time, each waiting for Ready.

**`OnDelete`:** controller updates a pod only when you **delete it** — fully manual canary,
useful for DBs where you want to drain/checkpoint a member before it restarts.

**Why it's different from a Deployment:** stable identity + per-pod PVC mean you can't just
spin up a surge replica — the new pod *is* `app-N` reusing its volume. So canary = "which
ordinals run the new revision," not "a separate ReplicaSet."

**Gotcha:** rollout is serial and Ready-gated, so one unhealthy member **stalls** the whole
rollout (by design — protects quorum). Pair with a PodDisruptionBudget for node ops.

---

[↑ Index](./README.md) · [← Prev](./11-what-happens-when-a-pod-is-deleted-grace.md)
