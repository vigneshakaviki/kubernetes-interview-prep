# Requests vs limits — what each controls, the QoS classes, and what happens at the limit.

[↑ Index](./README.md) · [← Prev](./01-explain-liveness-readiness-and-startup-probes-and-a.md) · [Next →](./03-node-affinity-taints-tolerations-and-how-to-build.md)

**Difficulty:** Easy · **Tags:** `resources` `scheduling`

**Short answer:** Requests = what the **scheduler reserves**; limits = **runtime caps**.
Memory and CPU fail in **opposite** ways at the limit.

**At the limit:**
- **Memory** over limit → **OOMKilled** (hard, exit 137, no grace).
- **CPU** over limit → **throttled** (slowed, *not* killed).

**QoS classes** (derived from how you set requests/limits) drive eviction + OOM score:

| Class | Condition | Evicted |
|-------|-----------|---------|
| **Guaranteed** | requests == limits (cpu+mem, all containers) | last |
| **Burstable** | some requests, not all equal | middle |
| **BestEffort** | nothing set | first |

```yaml
resources:                 # requests == limits  →  Guaranteed
  requests: { cpu: "500m", memory: "512Mi" }
  limits:   { cpu: "500m", memory: "512Mi" }
```

**Staff nuance:**
- CPU limits are contentious — tight CPU limits throttle latency-sensitive services
  *even on an idle node*. Common pattern: set **CPU requests, no CPU limit**; set
  **memory requests == limits** for predictability.
- Requests are a *scheduling* contract; limits a *runtime* one. Over-request wastes
  money + starves the scheduler; under-request invites noisy-neighbor eviction.

---

[↑ Index](./README.md) · [← Prev](./01-explain-liveness-readiness-and-startup-probes-and-a.md) · [Next →](./03-node-affinity-taints-tolerations-and-how-to-build.md)
