# Design a multi-region Kubernetes setup — traffic, data, failover.

[↑ Index](./README.md) · [← Prev](./02-count-sessions-per-user-from-a-log-then.md)

**Difficulty:** Hard · **Tags:** `system-design` `multi-region`

**Short answer:** Run **independent clusters per region** (not one stretched cluster),
route users with **global DNS/anycast + health checks**, and let **data consistency**
drive the hard decisions. Failover is a data problem, not a traffic problem.

**Why not one stretched cluster:** etcd needs low-latency quorum (<~10ms RTT) — spanning
regions breaks it (split-brain, slow writes). So: **cluster per region**, each with its own
control plane.

**Traffic routing:**
- **GeoDNS / global LB / anycast** (Route 53 latency/geo, Cloudflare, GCLB) → nearest healthy
  region. Per-region health checks pull a dead region out of rotation.
- Below that, per-cluster ingress. Service discovery across clusters via a **multi-cluster
  mesh** (Istio multi-primary) or Cilium ClusterMesh if services must call cross-region.

**Data — the crux:**
| Pattern | Consistency | Failover |
|---------|-------------|----------|
| Active-passive (1 primary region) | strong, simple | promote replica; RPO = replication lag |
| Active-active, regional sharding | strong per shard | route by shard key |
| Active-active, global DB (Spanner/Cockroach) | tunable, higher latency | automatic |

**Failover plan:** define **RTO/RPO**, automate replica promotion + DNS cutover, and
**practice it** (game days) — an untested failover is a hope. Watch for the split-brain
trap: two regions both thinking they're primary → need fencing/consensus on who's writer.

**Also:** config/secrets replicated (GitOps per cluster), images in regional registries,
and quotas so a failover surge doesn't overwhelm the surviving region (capacity for N-1).

---

[↑ Index](./README.md) · [← Prev](./02-count-sessions-per-user-from-a-log-then.md)
