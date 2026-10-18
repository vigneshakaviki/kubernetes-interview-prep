# What's the HPA's actual scaling formula, and why does it flap?

[↑ Index](./README.md) · [← Prev](./05-what-is-a-poddisruptionbudget-which-disruptions-does-it.md)

**Difficulty:** Advanced · **Tags:** `autoscaling` `hpa`

**Short answer:** HPA computes
`desiredReplicas = ceil(currentReplicas × currentMetric / targetMetric)`,
clamped to min/max, with a **tolerance** band and **stabilization windows** to damp
oscillation.

**The formula in practice:**
- 4 replicas at 80% CPU, target 50% → `ceil(4 × 80/50) = ceil(6.4) = 7`.
- **Tolerance (default 10%)** — if the ratio is within ±10% of target, HPA does nothing →
  avoids churn around the setpoint.
- Metrics are averaged across Ready Pods; not-yet-Ready and recently-started Pods are
  handled specially so cold starts don't skew the average.

**Why it flaps:**
- **Metric lag + a slow-to-warm app** — scale up → new Pods cold → metric spikes again →
  scale up more → overshoot → scale down → repeat.
- Scale-up is fast by default; **scale-down** is guarded by a **stabilization window**
  (default 300s) that uses the *highest* recent recommendation → prevents thrashing down.
- Scaling on a **spiky metric** (raw RPS) instead of a smoothed one.

**Fix:** tune `behavior.scaleDown`/`scaleUp` policies + stabilization windows, scale on a
smoother signal (or queue depth), set realistic targets, and add a startup probe so warm-up
doesn't feed the loop. The lever interviewers look for: **scale up quick, scale down slow.**

---

[↑ Index](./README.md) · [← Prev](./05-what-is-a-poddisruptionbudget-which-disruptions-does-it.md)
