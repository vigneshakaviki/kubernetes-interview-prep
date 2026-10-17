# Pod vs Deployment, and why we never create bare Pods in production.

[↑ Index](./README.md) · [← Prev](./03-deployment-vs-statefulset-vs-daemonset-and-a-case.md) · [Next →](./05-pods-are-ephemeral-with-changing-ips-how-does.md)

**Difficulty:** Easy · **Tags:** `workloads`

- **Pod** = smallest schedulable unit (containers sharing IP/localhost + volumes).
  **Mortal, not self-healing** — node dies, nothing recreates it.
- **Deployment** = controller → ReplicaSet → Pods. Reconciles: keeps replica count,
  replaces failures, does rolling updates/rollbacks.

**So:** manage desired state through controllers (healing, rollout, audit). A bare Pod is
only for a throwaway debug shell.

---

[↑ Index](./README.md) · [← Prev](./03-deployment-vs-statefulset-vs-daemonset-and-a-case.md) · [Next →](./05-pods-are-ephemeral-with-changing-ips-how-does.md)
