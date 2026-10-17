# How does the scheduler place a Pod — and how do you influence or debug it?

[↑ Index](./README.md) · [← Prev](./09-do-you-have-kubernetes-experience-but-your-company.md) · [Next →](./11-operator-pattern-and-crds-when-is-it-right.md)

**Difficulty:** Advanced · **Tags:** `scheduling` `architecture`

**Two phases per unscheduled Pod:**
1. **Filter (predicates)** — drop nodes that *can't* fit: resources, taints, nodeSelector/
   affinity, pod (anti-)affinity, volume zone, port conflicts.
2. **Score (priorities)** — rank survivors (least-requested, balanced, spread, image
   locality) → bind via `nodeName`.

No node survives → `Pending` + "unschedulable" event.

**Influence:** requests (reserved vs usage), affinity/anti-affinity, taints/tolerations,
`topologySpreadConstraints`, `priorityClass` + **preemption**.

**Debug:** `kubectl describe pod` → per-predicate reason.

**Gotcha:** scheduler decides *placement*, never creates capacity → pair with Cluster
Autoscaler/Karpenter to turn "unschedulable" into new nodes.

---

[↑ Index](./README.md) · [← Prev](./09-do-you-have-kubernetes-experience-but-your-company.md) · [Next →](./11-operator-pattern-and-crds-when-is-it-right.md)
