# Scaling & Autoscaling

### Q: HPA, VPA, and Cluster Autoscaler all "autoscale." Explain what each one actually changes and how they interact (and conflict).

**Difficulty:** Medium · **Tags:** `autoscaling`

They operate on three different axes. **HPA** changes the **replica count** of a workload
based on metrics (CPU/memory utilization, custom, or external). **VPA** changes a Pod's
**resource requests/limits** — it right-sizes a single Pod rather than adding more.
**Cluster Autoscaler** (or Karpenter) changes the **number of nodes** — it adds nodes when
Pods can't schedule and removes underused ones. So: HPA scales out, VPA scales up, CA
provides the capacity for either to land.

The interactions are where people get burned. HPA and VPA on the **same resource**
(both reacting to CPU) **fight each other** — HPA adds replicas to lower per-Pod CPU while
VPA raises per-Pod requests, oscillating; the supported combo is VPA on memory + HPA on
CPU, or VPA in "recommend only" mode. And HPA scaling out is useless if there's no room:
it creates Pods that sit `Pending` until **Cluster Autoscaler** adds nodes — so HPA and CA
must be paired, and HPA alone "doesn't scale" when the real bottleneck is node capacity.
The framing: pick HPA for stateless request-driven scaling, VPA (carefully, often
recommend-only) for right-sizing singletons and batch, and always back HPA with a node
autoscaler — and never run HPA and VPA on the same signal.

---

### Q: An HPA is sitting at `<unknown>` and won't scale on CPU. What are all the things that could be wrong?

**Difficulty:** Medium · **Tags:** `autoscaling` `hpa`

`<unknown>` means the HPA can't compute utilization, and CPU utilization is defined as
usage **relative to the Pod's CPU request** — so the first and most common cause is that
the Pods have **no CPU request set**, making the ratio undefined. Second: the
**metrics-server** (or custom/external metrics adapter) isn't installed, is crashing, or
can't scrape kubelets (TLS/`--kubelet-insecure-tls` issues), so there's simply no metric
to read. Third: the HPA's `scaleTargetRef` points at the wrong workload or a workload with
no Ready Pods to measure.

Beyond `<unknown>`, an HPA that *has* metrics but still won't scale: it's hit
`maxReplicas`; the stabilization window / scale-down policy is damping it; the Pods it
created are stuck `Pending` (no node capacity → pair with Cluster Autoscaler); or CPU just
isn't the real demand signal (the app is I/O- or queue-bound, so CPU stays flat while the
backlog grows). The method: `kubectl describe hpa` and read the conditions and
`current/target` — it tells you explicitly whether metrics are missing (`<unknown>`), the
target is being met, or scaling is capped — and *then* check requests, metrics-server, and
node capacity in that order. The deeper point: autoscaling on the wrong metric is worse
than not autoscaling, so choose the signal that actually tracks load.

---

### Q: How would you autoscale on something other than CPU — custom or external metrics — and where does KEDA fit?

**Difficulty:** Advanced · **Tags:** `autoscaling`

Many services aren't CPU-bound; the real demand signal is queue depth, requests per
second, p99 latency, or concurrency. HPA supports this through the metrics APIs:
**custom metrics** (per-Pod or per-object app metrics served via the custom.metrics API,
typically backed by Prometheus Adapter) and **external metrics** (signals from outside the
cluster — a cloud queue's depth, a managed broker's lag). You point the HPA at those
instead of (or alongside) CPU.

**KEDA** is the add-on that makes event-driven autoscaling practical: it ships dozens of
**scalers** (Kafka lag, SQS/RabbitMQ depth, Prometheus queries, cron, cloud metrics),
translates them into the metrics HPA consumes, and — critically — adds **scale-to-zero**,
so an idle consumer drops to no Pods and spins up on the first event. That's ideal for
bursty, event-driven, or expensive-when-idle workloads. The nuance: scaling on a
backlog metric (queue depth / consumer lag) is usually far more responsive and correct
than CPU for worker pools, because it scales with *work to be done* rather than a lagging
side-effect of it — but you must tune the target per-replica value and the cooldown, or
you'll thrash, and scale-to-zero adds cold-start latency you have to accept or mask with a
minimum replica floor.

---

### Q: How does the Cluster Autoscaler decide to add or remove a node, and why doesn't it just watch CPU?

**Difficulty:** Advanced · **Tags:** `autoscaling` `nodes`

It scales on **schedulability, not utilization**. Scale **up**: when Pods are `Pending`
because no existing node can fit them, CA simulates which node group, if expanded, would
make those Pods schedulable (respecting requests, taints, affinity, topology) and grows
that group. Scale **down**: when a node's utilization is below a threshold *and* all its
Pods could be rescheduled elsewhere, CA cordons/drains and removes it. It deliberately
ignores raw CPU% because a node packed with Pods that *request* a lot but *use* little is
still "full" from the scheduler's view — reservations, not usage, determine whether the
next Pod fits.

Scale-down is the subtle part: CA won't remove a node if doing so would violate a
**PodDisruptionBudget**, if Pods have no controller (bare Pods), use local storage
(`emptyDir`/hostPath it can't move), or carry "do not evict" annotations — so a single
unmovable Pod can pin an expensive node forever. The framing: CA correctness
depends on **accurate resource requests** (garbage requests → wrong packing and cost) and
**PDBs that allow disruption** — and the modern alternative, **Karpenter**, skips fixed
node groups and provisions right-sized nodes per pending-Pod shape, which bin-packs better
and cuts cost, at the price of more node churn to manage. "It scales on Pending Pods and
request-based packing, not CPU" is the sentence that shows you've operated it.

---

### Q: What is a PodDisruptionBudget, exactly which disruptions does it govern, and when is it the thing standing between you and an outage?

**Difficulty:** Advanced · **Tags:** `availability`

A **PDB** declares how much of a Pod set may be unavailable from **voluntary**
disruptions — you set `minAvailable` (keep at least N/percent up) or `maxUnavailable`
(let at most N/percent go down). The eviction API checks the PDB and **refuses** an
eviction that would breach it. The key scoping: it governs **voluntary** disruptions —
`kubectl drain`, Cluster Autoscaler scale-down, node-pool upgrades, anything using the
eviction API — and does **not** protect against **involuntary** ones (a node kernel panic,
hardware failure, OOMKill); you can't budget away a crash.

Where it saves you: during routine node maintenance you drain nodes one by one, and
without a PDB the drain can evict *all* replicas of a quorum service at once (taking down
etcd/ZooKeeper/a 3-replica API), whereas a PDB forces the drain to wait and go one Pod at
a time, preserving quorum/capacity. The classic self-inflicted outage is draining a node
pool for an upgrade with no PDBs and watching a critical service blink out. The
caveats: a PDB that's too strict (`minAvailable: 100%`) **blocks drains entirely** and
wedges your node upgrades/autoscaler, so it's a balance; PDBs only help if the workload
has enough replicas to begin with (a 1-replica Deployment with `minAvailable: 1` just
makes it undrainable); and they're the required companion to spread constraints for safe
day-2 operations.

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata: { name: api-pdb }
spec:
  minAvailable: 2            # a drain/scale-down can't take this set below 2 ready Pods
  selector: { matchLabels: { app: api } }
# minAvailable: 100% would make the set undrainable and wedge node upgrades — don't.
```
