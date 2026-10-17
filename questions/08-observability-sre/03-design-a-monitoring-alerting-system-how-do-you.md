# Design a monitoring + alerting system. How do you prevent alert storms?

[↑ Index](./README.md) · [← Prev](./02-the-four-golden-signals-and-how-to-alert.md) · [Next →](./04-error-budget-nearly-exhausted-mid-quarter-what-happens.md)

**Difficulty:** Medium · **Tags:** `sre` `monitoring` `alerting`

**Pipeline:** metrics (Prometheus + node-exporter/kube-state-metrics/control-plane/app; Thanos/
Mimir for scale), logs (Loki/ELK), traces → dashboards for *debugging*, alerts for *action*.

**Prevent storms (by design):**
- **Symptom/SLO-burn alerts** → one user problem = one page, not fifty.
- **Group/dedupe** related alerts.
- **Inhibition** — suppress downstream when a known upstream cause fires (API down → don't
  page every workload that can't reach it).
- Multi-window burn-rate (anti-flap) · severity routing (page/ticket/dashboard) ·
  maintenance silencing.

**Framing:** monitoring's failure mode is *too many* alerts → engineer for one-root-cause →
one-page; a noisy alert is a **bug to fix**, not noise to tolerate.

---

[↑ Index](./README.md) · [← Prev](./02-the-four-golden-signals-and-how-to-alert.md) · [Next →](./04-error-budget-nearly-exhausted-mid-quarter-what-happens.md)
