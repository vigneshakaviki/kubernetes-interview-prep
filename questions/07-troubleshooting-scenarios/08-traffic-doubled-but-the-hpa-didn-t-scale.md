# Traffic doubled but the HPA didn't scale. Why, and how do you confirm each hypothesis?

[↑ Index](./README.md) · [← Prev](./07-a-deployment-rollout-is-stuck-what-now.md) · [Next →](./09-a-node-goes-and-its-pods-disappear-respond.md)

**Difficulty:** Hard · **Tags:** `autoscaling` `hpa`

Start at `kubectl describe hpa` → conditions + `current/target`.

| Hypothesis | Confirm with |
|-----------|--------------|
| No CPU request (`<unknown>`) | `kubectl top` vs requests |
| metrics-server broken | its pod health |
| Wrong signal (I/O/queue-bound) | app metric (RPS, queue depth, p99) |
| Hit `maxReplicas` | describe hpa |
| New Pods `Pending` | → Cluster Autoscaler lagging |

**One-liner:** **HPA changes replica count; it does not create node capacity** — "HPA not
scaling" is often Cluster Autoscaler not scaling.

**Prevent:** scale on the metric that tracks load (queue/concurrency/RPS, often via KEDA),
set requests, pair with a node autoscaler, tune stabilization.

---

[↑ Index](./README.md) · [← Prev](./07-a-deployment-rollout-is-stuck-what-now.md) · [Next →](./09-a-node-goes-and-its-pods-disappear-respond.md)
