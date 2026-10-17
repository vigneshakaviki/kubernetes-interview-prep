# Deployment vs StatefulSet vs DaemonSet — and a case where the wrong one bites.

[↑ Index](./README.md) · [← Prev](./02-what-is-kube-proxy-its-modes-and-is.md) · [Next →](./04-pod-vs-deployment-and-why-we-never-create.md)

**Difficulty:** Medium · **Tags:** `workloads`

| Controller | Pods are | Use for |
|-----------|----------|---------|
| **Deployment** | fungible, stateless | stateless APIs; unordered rollout |
| **StatefulSet** | stable identity + per-Pod PVC + ordered | DBs, quorum systems |
| **DaemonSet** | one per node, auto-covers new nodes | node agents (CNI, logs, exporters) |

**Wrong-choice failure:** running Kafka/ZooKeeper/Postgres-replicas as a **Deployment** —
no stable identity or storage, so on reschedule a broker returns with a new name + empty/
other volume → breaks quorum and replication.

**Rule:** choose by whether *identity + storage must be stable* (StatefulSet), *every node
needs a copy* (DaemonSet), or neither (Deployment — the default).

---

[↑ Index](./README.md) · [← Prev](./02-what-is-kube-proxy-its-modes-and-is.md) · [Next →](./04-pod-vs-deployment-and-why-we-never-create.md)
