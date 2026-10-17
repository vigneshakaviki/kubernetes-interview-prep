# A Deployment rollout is stuck. What now?

[↑ Index](./README.md) · [← Prev](./06-one-service-returns-intermittent-503s-debug-it.md) · [Next →](./08-traffic-doubled-but-the-hpa-didn-t-scale.md)

**Difficulty:** Medium · **Tags:** `deployments` `rollout`

`kubectl rollout status` → compare **old vs new ReplicaSet** → inspect **new Pods' events +
logs**. The stall is almost always:
- New Pods not Ready (readiness/crash/OOM) · image pull errors · quota/LimitRange/RBAC/
  admission block.

The rolling strategy is *protecting* you — it won't proceed past `maxUnavailable` while new
Pods aren't Ready, so old Pods keep serving (looks "stuck").

**Act by impact:** old Pods serving + users fine → fix forward or `rollout undo`. Users hurt
→ roll back now.

**Prevent:** sane `maxSurge`/`maxUnavailable`, honest readiness, `progressDeadlineSeconds`
(so it *reports* failed, not hangs), canary + auto-rollback.

**Clarify:** a **PDB governs voluntary evictions, not the rolling-update strategy** — people
conflate them.

---

[↑ Index](./README.md) · [← Prev](./06-one-service-returns-intermittent-503s-debug-it.md) · [Next →](./08-traffic-doubled-but-the-hpa-didn-t-scale.md)
