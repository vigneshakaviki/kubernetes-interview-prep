# kube-proxy iptables vs IPVS — what breaks at scale?

[↑ Index](./README.md) · [← Prev](./06-explain-the-pod-networking-model-and-what-a.md) · [Next →](./08-what-does-a-service-mesh-add-over-plain.md)

**Difficulty:** Advanced · **Tags:** `networking`

- **iptables** — chains of DNAT rules; both **update** (resync rewrites big rule sets) and
  **match** cost grow ~linearly → at thousands of Services, slow endpoint propagation
  (seconds) + latency/jitter.
- **IPVS** — in-kernel hash tables (O(1) lookup) + real LB algos → scales, lower/consistent
  latency, faster updates.

**Note:** IPVS still uses iptables for some filtering/NodePort; the modern move is an
**eBPF** dataplane (Cilium) replacing both. Name the *actual* failure (linear rule scaling),
not just "IPVS faster."

---

[↑ Index](./README.md) · [← Prev](./06-explain-the-pod-networking-model-and-what-a.md) · [Next →](./08-what-does-a-service-mesh-add-over-plain.md)
