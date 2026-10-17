# Headless Service — how it differs at DNS level, and when you actually need one.

[↑ Index](./README.md) · [← Prev](./04-clusterip-vs-nodeport-vs-loadbalancer-how-they-stack.md) · [Next →](./06-explain-the-pod-networking-model-and-what-a.md)

**Difficulty:** Advanced · **Tags:** `networking` `statefulset`

- `clusterIP: None` → **no VIP, no kube-proxy LB**. DNS returns **A records per Ready Pod**;
  with a StatefulSet, stable per-Pod names (`pod-0.svc...`).

**Need it when the client must address specific Pods:**
- Stateful clusters finding peers by identity (Kafka, ZooKeeper, etcd).
- Client-side load balancing.

**The gRPC tell:** a normal ClusterIP Service under-balances gRPC — HTTP/2 multiplexes many
requests over one long-lived connection that L4 kube-proxy balances only at connect time,
so one backend hogs load. Headless (or a mesh) lets the client see all endpoints and spread.

---

[↑ Index](./README.md) · [← Prev](./04-clusterip-vs-nodeport-vs-loadbalancer-how-they-stack.md) · [Next →](./06-explain-the-pod-networking-model-and-what-a.md)
