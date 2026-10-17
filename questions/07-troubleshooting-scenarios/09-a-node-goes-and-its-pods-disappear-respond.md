# A node goes `NotReady` and its Pods disappear. Respond as on-call.

[↑ Index](./README.md) · [← Prev](./08-traffic-doubled-but-the-hpa-didn-t-scale.md) · [Next →](./10-a-stateful-pod-can-t-mount-its-volume.md)

**Difficulty:** Hard · **Tags:** `nodes` `control-plane`

**Scope first:** one node / a zone / control-plane connectivity? Many nodes flipping at once
= usually the control plane or network to it — **don't start rebooting nodes.**

**Single node — descend the stack:** node conditions/taints/lease (kubelet heartbeating?) →
kubelet → runtime → CNI → host resources (disk full `/var`, host OOM, PIDs) → VM/hardware.

**Pods "disappearing" = node controller working:** unreachable node → status `Unknown` →
after grace, `NoExecute` taint evicts Pods → rescheduled on healthy nodes.

**On-call:** protect remaining capacity, **don't drain more nodes** while unstable (cascade
risk). **Prevent:** topology spread + PDBs, system-reserved, node-problem-detector + auto-repair.

---

[↑ Index](./README.md) · [← Prev](./08-traffic-doubled-but-the-hpa-didn-t-scale.md) · [Next →](./10-a-stateful-pod-can-t-mount-its-volume.md)
