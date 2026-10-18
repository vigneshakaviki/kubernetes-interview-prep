# After a deploy, p99 latency doubled but error rate is flat. Find it.

[↑ Index](./README.md) · [← Prev](./12-kubectl-is-slow-and-the-api-server-times-out.md) · [Next →](./14-dns-lookups-fail-intermittently-cluster-wide.md)

**Difficulty:** Hard · **Tags:** `performance` `rollout`

**Short answer:** No errors + higher latency = the app is *working but slower*. Prime
suspects that a deploy introduces: **CPU throttling**, **GC/warmup**, **cold caches**, or
a **changed dependency call pattern**.

**Confirm it's the new version:** compare p99 of old vs new Pods (by version label) — did
it jump exactly at rollout?

**Likely causes:**
- **CPU throttling** — new version set (or lowered) a CPU **limit**; check
  `container_cpu_cfs_throttled_seconds`. Throttling shows as latency, never restarts.
- **Cold cache / JIT/JVM warmup** — new Pods start empty; latency recovers after warm-up →
  use a **startup probe** + cache pre-warm, and slow the rollout.
- **More/slower downstream calls** — N+1 queries, a new sync call, lost connection pooling.
- **Node packing** — new Pods landed on busier nodes (noisy neighbor); check per-node.

**Mitigate:** roll back if users hurt. **Prevent:** canary + automated latency analysis
(Argo Rollouts/Flagger) that aborts on p99 regression *before* full rollout.

---

[↑ Index](./README.md) · [← Prev](./12-kubectl-is-slow-and-the-api-server-times-out.md) · [Next →](./14-dns-lookups-fail-intermittently-cluster-wide.md)
