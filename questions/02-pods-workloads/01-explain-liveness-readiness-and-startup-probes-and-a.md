# Explain liveness, readiness, and startup probes — and a real outage from misconfiguring one.

[↑ Index](./README.md) · [Next →](./02-requests-vs-limits-what-each-controls-the-qos.md)

**Difficulty:** Medium · **Tags:** `probes` `workloads`

**Short answer:** Readiness gates *traffic*, liveness triggers *restarts*, startup
protects *slow boots*. Mixing them up amplifies incidents.

| Probe | Question it answers | On failure |
|-------|--------------------|------------|
| **readiness** | "Ready for traffic *now*?" | removed from Service endpoints — **no restart** |
| **liveness** | "Is it wedged?" | **kills + restarts** the container |
| **startup** | "Finished booting?" | holds off liveness/readiness until it passes |

**The classic outage — liveness probe hitting a dependency:**
- Load rises → app slows → liveness times out → kubelet **restarts** the container.
- Restart drops in-flight work → slower → next probe also fails → **restart storm**.
- A latency blip becomes a full outage, self-inflicted by the probe.

**Rules:**
- Liveness checks **only local liveness** (event loop responsive) — never a downstream.
- Readiness *may* check dependencies (failure just removes traffic, reversible).
- Slow boot → **startup probe**, not a loosened liveness timeout.

```yaml
startupProbe:   { httpGet: {path: /healthz, port: 8080}, failureThreshold: 30, periodSeconds: 5 }  # ~150s budget
readinessProbe: { httpGet: {path: /ready,   port: 8080}, periodSeconds: 5 }
livenessProbe:  { httpGet: {path: /healthz, port: 8080}, periodSeconds: 10, failureThreshold: 3 }
```

---

[↑ Index](./README.md) · [Next →](./02-requests-vs-limits-what-each-controls-the-qos.md)
