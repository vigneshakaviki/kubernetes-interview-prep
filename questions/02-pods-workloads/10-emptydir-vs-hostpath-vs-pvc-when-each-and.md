# emptyDir vs hostPath vs PVC — when each, and the hostPath trap.

[↑ Index](./README.md) · [← Prev](./09-job-vs-cronjob-the-knobs-that-decide-correctness.md) · [Next →](./11-what-happens-when-a-pod-is-deleted-grace.md)

**Difficulty:** Intermediate · **Tags:** `storage` `workloads`

| Volume | Lifetime | Use for |
|--------|----------|---------|
| **emptyDir** | dies with the Pod | scratch, cache, share between containers (`medium: Memory` for RAM) |
| **hostPath** | node's filesystem | node agents only (CNI/CSI/log collectors) |
| **PVC** | survives rescheduling | any data that must outlive the Pod |

**The hostPath trap:**
- **Security** — a window into the host (`/var/run/docker.sock` → node escape).
- **Reliability** — data gone if the Pod lands on another node; no tenant isolation.
- → treat it as a privileged, node-pinned escape hatch; gate it with Pod Security.

---

[↑ Index](./README.md) · [← Prev](./09-job-vs-cronjob-the-knobs-that-decide-correctness.md) · [Next →](./11-what-happens-when-a-pod-is-deleted-grace.md)
