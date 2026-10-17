# etcd's role, consequences of it going unhealthy, and explain Raft like you've operated it.

[↑ Index](./README.md) · [← Prev](./07-write-a-dockerfile-for-a-python-service-and.md) · [Next →](./09-do-you-have-kubernetes-experience-but-your-company.md)

**Difficulty:** Hard · **Tags:** `architecture` `consensus`

**Role:** the consistent, watchable KV store — single source of truth; only the API
server talks to it.

**Unhealthy:**
- Slow → *every* write stalls, controllers lag.
- No quorum → control plane read-only/unavailable, but **running Pods keep serving**
  (data plane survives a control-plane outage).

**Raft:**
- One **leader** takes all writes, replicates log to followers.
- Entry **commits** once a **majority (quorum)** persists it.
- Leader loss → follower times out → bumps **term** → requests votes → majority wins.
- **Odd member count**: quorum = `floor(n/2)+1`; 3 tolerates 1, 5 tolerates 2. Even
  count buys no extra tolerance.

**Operator reality:** disk-latency sensitive (fsync per commit) → fast disks, watch
`backend commit` p99, keep under DB size quota, **take + test-restore snapshots** (no
tested restore = no DR).

---

[↑ Index](./README.md) · [← Prev](./07-write-a-dockerfile-for-a-python-service-and.md) · [Next →](./09-do-you-have-kubernetes-experience-but-your-company.md)
