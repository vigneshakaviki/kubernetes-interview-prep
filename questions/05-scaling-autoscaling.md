# Scaling & Autoscaling

### Q: HPA, VPA, Cluster Autoscaler — what each changes, and how they interact/conflict.

**Difficulty:** Medium · **Tags:** `autoscaling`

| | Changes | Axis |
|--|---------|------|
| **HPA** | replica count | scale out |
| **VPA** | per-Pod requests/limits | scale up (right-size) |
| **Cluster Autoscaler** | node count | capacity |

**Conflicts:**
- **HPA + VPA on the same resource** (both on CPU) → fight (HPA adds replicas to lower CPU
  while VPA raises requests) → oscillation. Supported: VPA on mem + HPA on CPU, or VPA
  recommend-only.
- **HPA without a node autoscaler** → new replicas sit `Pending`. HPA "doesn't scale" when
  the real bottleneck is node capacity.

---

### Q: An HPA sits at `<unknown>` and won't scale on CPU. What's wrong?

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

### Q: Autoscale on something other than CPU — custom/external metrics — and where KEDA fits.

**Difficulty:** Advanced · **Tags:** `autoscaling`

- **Custom metrics** — per-Pod/object app metrics (custom.metrics API, Prometheus Adapter).
- **External metrics** — queue depth, RPS, cloud metrics.
- **KEDA** — add-on with dozens of **scalers** (Kafka lag, SQS, Prometheus, cron) → feeds
  HPA + adds **scale-to-zero**.

**Why it matters:** scaling on **backlog / consumer lag** is more correct + responsive than
CPU for worker pools — it tracks *work to do*, not a lagging side-effect.

**Caveats:** tune per-replica target + cooldown or it thrashes; scale-to-zero adds cold-start
latency (mask with a min floor).

---

### Q: How does Cluster Autoscaler decide to add/remove a node — and why not just watch CPU?

**Difficulty:** Advanced · **Tags:** `autoscaling` `nodes`

Scales on **schedulability, not utilization**:
- **Up** — Pods `Pending` for lack of fit → simulates which node group would make them
  schedulable → grows it.
- **Down** — node underused **and** its Pods can move → drain + remove.

**Blocked scale-down:** PodDisruptionBudget, bare Pods (no controller), local storage
(`emptyDir`/hostPath), "do-not-evict" annotations → one unmovable Pod pins an expensive node.

**Why not CPU:** a node full of high-*request* low-*usage* Pods is "full" to the scheduler —
reservations, not usage, decide fit.

**Note:** depends on accurate **requests**; **Karpenter** provisions right-sized nodes per
pending-Pod shape (better bin-pack, more churn).

---

### Q: What is a PodDisruptionBudget, which disruptions does it govern, and when does it save you?

**Difficulty:** Advanced · **Tags:** `availability`

- Declares max unavailable from **voluntary** disruptions (`minAvailable` / `maxUnavailable`).
  The eviction API **refuses** an eviction that would breach it.
- Governs: drains, autoscaler scale-down, node-pool upgrades.
- Does **not** govern **involuntary** (node crash, OOM) — can't budget away a crash.

**Saves you:** draining nodes for an upgrade with no PDB can evict all replicas of a quorum
service at once → outage. PDB forces one-at-a-time.

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata: { name: api-pdb }
spec:
  minAvailable: 2            # a drain/scale-down can't take this set below 2
  selector: { matchLabels: { app: api } }
```

**Caveats:** `minAvailable: 100%` **blocks drains entirely** → wedges upgrades/autoscaler.
Only helps with enough replicas (1 replica + `minAvailable: 1` = undrainable).
