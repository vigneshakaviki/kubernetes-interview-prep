# A node hits `DiskPressure` and starts evicting Pods. Respond.

[↑ Index](./README.md) · [← Prev](./15-a-namespace-is-stuck-terminating-and-wont-delete.md) · [Next →](./17-workloads-fail-tls-after-a-certificate-expired.md)

**Difficulty:** Medium · **Tags:** `nodes` `storage`

**Short answer:** The kubelet is reclaiming **node ephemeral storage** (`/var/lib/...`).
Find what's filling it — usually **image bloat, container logs, or emptyDir** — because
eviction only buys time.

**What fills a node disk:**
- **Container logs** — a chatty Pod with no log rotation flooding `/var/log/containers`.
- **Image accumulation** — many image versions; kubelet GC thresholds misconfigured.
- **emptyDir / overlay writes** — a Pod writing lots to its writable layer or an emptyDir
  with no `sizeLimit`.
- **A Pod exceeding `ephemeral-storage` limits** (if set) → it gets evicted specifically.

**Investigate:** `df -h` on the node, `du -sh /var/lib/docker|containerd/*`,
`crictl images`, check which Pod's logs/writable layer is largest.

**Mitigate:** clear dead images (`crictl rmi --prune`), rotate/ship logs, cordon + drain
if the node's unhealthy. **Prevent:** set container **log rotation**, `ephemeral-storage`
requests/limits, `emptyDir.sizeLimit`, kubelet image-GC thresholds, and alert on node disk
*before* `DiskPressure` (it's a leading indicator).

---

[↑ Index](./README.md) · [← Prev](./15-a-namespace-is-stuck-terminating-and-wont-delete.md) · [Next →](./17-workloads-fail-tls-after-a-certificate-expired.md)
