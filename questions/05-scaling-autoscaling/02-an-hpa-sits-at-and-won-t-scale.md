# An HPA sits at `<unknown>` and won't scale on CPU. What's wrong?

[↑ Index](./README.md) · [← Prev](./01-hpa-vpa-cluster-autoscaler-what-each-changes-and.md) · [Next →](./03-autoscale-on-something-other-than-cpu-custom-external.md)

**Difficulty:** Medium · **Tags:** `autoscaling` `hpa`

CPU utilization is **relative to the request** → undefined without one.

**`<unknown>` causes:**
- **No CPU request** on the Pods. ← #1
- **metrics-server** down / can't scrape kubelets (TLS).
- Wrong `scaleTargetRef` / no Ready Pods.

**Has metrics but still won't scale:** hit `maxReplicas` · stabilization/scale-down damping
· new Pods stuck `Pending` (→ Cluster Autoscaler) · CPU isn't the real signal (I/O- or
queue-bound).

**Method:** `kubectl describe hpa` → conditions + `current/target` tells you which. Then
check requests → metrics-server → node capacity.

---

[↑ Index](./README.md) · [← Prev](./01-hpa-vpa-cluster-autoscaler-what-each-changes-and.md) · [Next →](./03-autoscale-on-something-other-than-cpu-custom-external.md)
