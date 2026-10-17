# "Do you have Kubernetes experience?" but your company used in-house infra. How do you answer?

[↑ Index](./README.md) · [← Prev](./08-etcd-s-role-consequences-of-it-going-unhealthy.md) · [Next →](./10-how-does-the-scheduler-place-a-pod-and.md)

**Difficulty:** Easy · **Tags:** `behavioral`

**Weak:** "I wrote YAML and ran `kubectl apply`" → sounds surface-level.

**Strong:** answer at the level of *what orchestration solves* and map your system onto it:
scheduling, self-healing reconcile loops, declarative state, rolling updates, service
discovery/LB, resource isolation, secret distribution.
- "We ran our own platform with the equivalent of a scheduler, a ReplicaSet-style
  controller, and a mesh; here's a trade-off we debated vs how K8s does it."
- Then prove you can ramp: name a non-trivial K8s primitive (PDBs, topology spread,
  admission control) to show depth, not buzzwords.

---

[↑ Index](./README.md) · [← Prev](./08-etcd-s-role-consequences-of-it-going-unhealthy.md) · [Next →](./10-how-does-the-scheduler-place-a-pod-and.md)
