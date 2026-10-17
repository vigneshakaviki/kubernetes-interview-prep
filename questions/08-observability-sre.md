# Observability & SRE Practice

### Q: Define SLI, SLO, and SLA, and explain why the SLO is deliberately set tighter than the SLA.

**Difficulty:** Easy · **Tags:** `sre` `slo`

An **SLI** is the *measured* indicator of service health — a ratio of good events to total,
e.g. "fraction of requests served in under 300ms" or "fraction of requests that aren't
5xx." An **SLO** is the *internal target* for that SLI over a window — "99.9% of requests
succeed over 28 days" — i.e. your reliability goal. An **SLA** is the *external contract*
with customers, with financial or legal consequences if breached. So: SLI = what you
measure, SLO = what you aim for, SLA = what you promise.

The SLO is set **tighter than the SLA on purpose** to create a safety margin: you want your
internal alerting and error budget to fire and force action *before* you're anywhere near
breaching the customer contract. If SLA is 99.5%, you might run a 99.9% SLO so that
degradation triggers your own response with room to spare. The framing: good SLIs
measure the **user's** experience (request success/latency at the edge), not internal proxy
metrics like CPU; you pick a *small number* of SLIs that actually correlate with user pain;
and the whole point of separating SLO from SLA is that reliability is a spectrum you manage
with budget, not a binary you defend at the contract line.

---

### Q: What are the four golden signals, and how do you turn them into alerts that don't page people at 3am for nothing?

**Difficulty:** Easy · **Tags:** `sre` `monitoring`

The four golden signals are **latency, traffic, errors, and saturation**. Latency should
**separate success latency from error latency** (a fast 500 is still a failure, and slow
errors skew percentiles). Traffic is demand (RPS/throughput). Errors is the rate of failed
requests (explicit 5xx plus implicit — wrong content, policy failures). Saturation is how
full the most-constrained resource is (the thing that will tip you over — memory, a
connection pool, queue depth), ideally with a utilization target below 100%.

Turning them into good alerts: page on **symptoms that affect users** (SLO burn), not on
every cause (a single node's CPU isn't a page). Use **SLO burn-rate alerting** —
multi-window (e.g. fast-burn over 1h *and* slow-burn over 6h) — so you page when the error
budget is being consumed dangerously fast and ticket when it's a slow leak, which cuts both
noise and misses. Every page must be **actionable and tied to a runbook**; anything that
isn't gets demoted to a dashboard/ticket or deleted. The framing: alert on the
*user-visible SLI breach*, let dashboards hold the cause metrics for when you're already
engaged, and ruthlessly delete alerts nobody acts on — because alert fatigue, not missing
alerts, is what makes on-call miss the real incident.

---

### Q: Design a monitoring and alerting system for a large K8s platform. How do you specifically prevent alert storms?

**Difficulty:** Medium · **Tags:** `sre` `monitoring` `alerting`

The pipeline: collect **metrics** (Prometheus scraping node-exporter, kube-state-metrics,
control-plane, and app `/metrics`; federation or a long-term store like Thanos/Mimir/Cortex
for scale and retention), **logs** (shipped and aggregated — Loki/ELK), and **traces** (for
request-path latency). Dashboards exist for *debugging once engaged*; alerts exist for
*action*. Route alerts through an alert manager and page via an escalation tool with
severities.

Preventing alert storms is a design concern, not an afterthought: **alert on symptoms /
SLO burn-rate, not every underlying cause**, so one user-facing problem is one page, not
fifty; **group and deduplicate** related alerts (all Pods of one service failing → one
notification); **inhibition** (suppress downstream alerts when a known upstream cause is
already firing — if the whole cluster's API is down, don't also page for every workload
that can't reach it); **multi-window burn-rate** to avoid flapping on transient blips;
**severity routing** (page vs ticket vs dashboard); and dependency-aware silencing during
known maintenance. The framing: the failure mode of monitoring is *too many* alerts,
not too few — a storm during an incident buries the signal and exhausts responders, so you
engineer for *one root cause → one actionable page*, and you treat a noisy alert as a bug to
fix (tune, group, or delete), not background noise to tolerate.

---

### Q: Your service's error budget is nearly exhausted mid-quarter. What actually happens, and what do you do?

**Difficulty:** Medium · **Tags:** `sre` `slo`

The error budget is `100% − SLO` — the amount of unreliability you're *allowed* over the
window. Burning through it means you're at risk of breaching the SLO (and heading toward the
SLA). A mature error-budget policy makes the response **pre-agreed and non-political**: when
the budget is nearly gone, you **freeze risky releases** (feature launches, risky migrations)
and **redirect engineering effort to reliability** — fix the top budget-burners, add the
missing safeguards — until the budget recovers. Meanwhile, dig into *what spent the budget*:
a bad deploy, a flaky dependency, a capacity shortfall, or an unrealistic SLO.

The point of the mechanism is to make the **release-velocity vs reliability** trade-off
explicit and data-driven, instead of a recurring argument between product and SRE. If the
budget is healthy, teams ship fast with confidence; if it's blown, the policy says slow down
— no negotiation needed in the moment. The nuance: if a service **chronically** blows
its budget, the answer isn't eternal feature freeze — it's either the SLO is wrong (too
strict for what users actually need, so loosen it), or the architecture genuinely can't meet
it (invest in reliability), and distinguishing those is the interesting judgment call. An
error budget that's never spent, conversely, means the SLO is too loose and you're leaving
velocity on the table.

---

### Q: How would you monitor the health of a Kubernetes cluster and the workloads on it with Prometheus?

**Difficulty:** Medium · **Tags:** `monitoring` `prometheus`

Layer the sources: **node-exporter** for per-node OS metrics (CPU, memory, disk, network),
**kube-state-metrics** for object state (Pod phases, restart counts, Deployment
desired-vs-available, PVC status, Job success), the **control-plane** (API server latency
and error rate, etcd fsync/commit latency and DB size, scheduler/controller-manager),
**cAdvisor/kubelet** for per-container resource usage, and **app `/metrics`** for business
and golden-signal data. Prometheus discovers targets via Kubernetes service discovery;
for scale and retention you federate or use Thanos/Mimir.

Then alert on the **symptoms** that precede the scenarios in
[07-troubleshooting-scenarios.md](./07-troubleshooting-scenarios.md): rising Pod restarts
and OOMKills, Pods stuck Pending, Deployments with available < desired, nodes reporting
pressure conditions or NotReady, PVCs near full, API-server/etcd latency climbing, and
SLO burn on the user-facing services. The framing: cluster metrics are **leading
indicators** — OOMKills and node `MemoryPressure` tell you an incident is forming before
users feel it — but you still **page on the user-facing SLI**, not on every internal metric,
and keep the cluster-internals metrics on dashboards for root-causing once you're engaged.
Watch Prometheus's own cardinality too: a label explosion (per-Pod, per-request-id labels)
will OOM Prometheus itself, so the monitoring system needs the same discipline you apply to
everything else.
