# kubectl is slow and the API server times out cluster-wide. Diagnose it.

[↑ Index](./README.md) · [← Prev](./11-a-distributed-database-shows-data-inconsistency-across-replicas.md) · [Next →](./13-after-a-deploy-p99-latency-doubled-but-no-errors.md)

**Difficulty:** Hard · **Tags:** `control-plane` `etcd`

**Short answer:** The control plane is the bottleneck — almost always **etcd latency** or
the **API server being hammered**. Running Pods keep serving (data plane survives), so
protect that while you fix the control plane.

**Scope first:** one `kubectl`/client, or everyone? Everyone → control plane, not your laptop.

**Walk it:**
- **etcd** — disk fsync is the usual culprit. Check `etcd_disk_wal_fsync_duration_seconds`
  and `backend_commit` p99; a slow/contended disk stalls every write. Check DB **size vs
  quota** (compaction/defrag overdue → `NOSPACE` alarm → read-only).
- **API server** — `apiserver_request_duration_seconds`, inflight-request saturation. A
  **list-everything client** (bad controller/operator LISTing all Pods repeatedly) or a
  broken **admission webhook** adding latency to every write hammers it.
- **Flooding watchers / hot loops** — a controller stuck re-listing.

**Mitigate (reversible):** throttle/kill the abusive client, scale API servers, defrag
etcd, raise the DB quota. **Prevent:** etcd on fast dedicated disks, watch fsync p99,
scheduled compaction/defrag, `--max-requests-inflight` limits, priority & fairness
(APF), webhook latency SLOs + narrow scope.

---

[↑ Index](./README.md) · [← Prev](./11-a-distributed-database-shows-data-inconsistency-across-replicas.md) · [Next →](./13-after-a-deploy-p99-latency-doubled-but-no-errors.md)
