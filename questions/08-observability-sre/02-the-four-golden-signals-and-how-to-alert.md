# The four golden signals, and how to alert on them without 3am noise.

[↑ Index](./README.md) · [← Prev](./01-define-sli-slo-sla-and-why-is-the.md) · [Next →](./03-design-a-monitoring-alerting-system-how-do-you.md)

**Difficulty:** Easy · **Tags:** `sre` `monitoring`

**Signals:** **latency** (split success vs error latency), **traffic**, **errors**,
**saturation** (fullest constrained resource).

**Good alerting:**
- Page on **symptoms / SLO burn**, not every cause (one node's CPU ≠ a page).
- **Multi-window burn-rate** (fast 1h + slow 6h) → page on fast budget burn, ticket on slow
  leak.
- Every page **actionable + runbook-linked**; non-actionable → dashboard/ticket or delete.

**Framing:** alert fatigue, not missing alerts, is what makes on-call miss the real incident.

---

[↑ Index](./README.md) · [← Prev](./01-define-sli-slo-sla-and-why-is-the.md) · [Next →](./03-design-a-monitoring-alerting-system-how-do-you.md)
