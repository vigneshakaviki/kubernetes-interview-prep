# Node affinity, taints, tolerations — and how to build a dedicated GPU pool.

[↑ Index](./README.md) · [← Prev](./02-requests-vs-limits-what-each-controls-the-qos.md) · [Next →](./04-qos-classes-and-the-exact-kubelet-eviction-order.md)

**Difficulty:** Medium · **Tags:** `scheduling`

**Short answer:** Affinity = pod *chooses* nodes (attraction). Taint = node *rejects*
pods (repulsion) unless they carry a matching toleration. You usually need **both**.

**Why both:**
- Affinity alone → doesn't stop *other* pods landing on your special nodes.
- Toleration alone → allows the pod on, but doesn't *steer* it there.

**GPU pool recipe:**
```bash
kubectl taint nodes <n> nvidia.com/gpu=present:NoSchedule   # repel everyone else
kubectl label nodes <n> accelerator=a100                    # target for affinity
```
- GPU pods: toleration for the taint **+** required `nodeAffinity` on the label **+** a
  `nvidia.com/gpu` resource request.

**Gotcha:** `NoExecute` taints also **evict running** pods that don't tolerate them
(with optional `tolerationSeconds`) — that's exactly how the node controller drains a
`NotReady` node.

---

[↑ Index](./README.md) · [← Prev](./02-requests-vs-limits-what-each-controls-the-qos.md) · [Next →](./04-qos-classes-and-the-exact-kubelet-eviction-order.md)
