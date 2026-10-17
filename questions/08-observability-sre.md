# Observability & SRE Practice

### Q: Define SLI, SLO, SLA — and why is the SLO set tighter than the SLA?

**Difficulty:** Easy · **Tags:** `sre` `slo`

| | Is | Example |
|--|----|---------|
| **SLI** | measured indicator | % requests < 300ms |
| **SLO** | internal target | 99.9% over 28d |
| **SLA** | external contract (+penalty) | 99.5% or refund |

**Why SLO tighter than SLA:** safety margin — your alerting/error-budget fires **before**
you breach the customer contract.

**Good SLIs** measure the **user's** experience (edge success/latency), not CPU; pick a
*small* number that correlate with pain.

---

### Q: The four golden signals, and how to alert on them without 3am noise.

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

### Q: Design a monitoring + alerting system. How do you prevent alert storms?

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

### Q: Error budget nearly exhausted mid-quarter — what happens and what do you do?

**Difficulty:** Medium · **Tags:** `sre` `slo`

Budget = `100% − SLO`. Nearly gone → the **pre-agreed policy** kicks in (non-political):
- **Freeze risky releases**, redirect effort to **reliability** until it recovers.
- Dig into *what spent it* — bad deploy / flaky dep / capacity / unrealistic SLO.

**Point:** makes the velocity-vs-reliability trade-off explicit + data-driven.

**Nuance:**
- **Chronically** blown → SLO is wrong (loosen) **or** architecture can't meet it (invest) —
  not eternal freeze.
- **Never** spent → SLO too loose, leaving velocity on the table.

---

### Q: Monitor cluster + workload health with Prometheus — how?

**Difficulty:** Medium · **Tags:** `monitoring` `prometheus`

**Sources:** node-exporter (hosts) · kube-state-metrics (object state: Pod phase, restarts,
desired-vs-available, PVCs) · control-plane (API latency, etcd fsync/DB size) · cAdvisor/
kubelet (container usage) · app `/metrics`. SD via Kubernetes; Thanos/Mimir for retention.

**Alert on leading indicators** (precede the [scenarios](./07-troubleshooting-scenarios.md)):
rising restarts/OOMKills, Pending Pods, available < desired, node pressure/NotReady, PVC near
full, API/etcd latency — **but page on the user-facing SLI**, keep internals on dashboards.

**Gotcha:** watch Prometheus's own **cardinality** — a per-request-id label will OOM
Prometheus itself.
