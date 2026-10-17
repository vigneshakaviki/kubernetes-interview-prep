# QoS classes and the exact kubelet eviction order under node pressure.

[↑ Index](./README.md) · [← Prev](./03-node-affinity-taints-tolerations-and-how-to-build.md) · [Next →](./05-deployment-update-strategies-and-how-canary-blue-green.md)

**Difficulty:** Advanced · **Tags:** `resources` `scheduling`

**Short answer:** QoS is *derived*, not declared, and sets eviction priority.

**Eviction order under node pressure** (memory/disk/PID):
1. **BestEffort** first.
2. **Burstable exceeding its requests** (ranked by overage × priority).
3. **Guaranteed** last (only for system-level pressure).

**Independent of node pressure:** a container over its **memory limit** is OOMKilled
immediately, regardless of QoS.

**Key distinctions:**
- Eviction is **graceful** (SIGTERM, honors grace period); OOMKill is **not**.
- `PriorityClass` further shifts eviction order — critical system pods survive.
- → give stateful/latency-critical pods **Guaranteed** QoS + priority, so a batch job's
  spike evicts the batch job, not your database.

---

[↑ Index](./README.md) · [← Prev](./03-node-affinity-taints-tolerations-and-how-to-build.md) · [Next →](./05-deployment-update-strategies-and-how-canary-blue-green.md)
