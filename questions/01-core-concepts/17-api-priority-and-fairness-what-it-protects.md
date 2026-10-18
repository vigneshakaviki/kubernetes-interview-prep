# API Priority & Fairness (APF) — what problem does it solve, and how?

[↑ Index](./README.md) · [← Prev](./16-what-is-helm-what-does-it-buy-you.md) · [Next →](./18-informers-watch-list-and-stale-caches.md)

**Difficulty:** Hard · **Tags:** `control-plane` `reliability`

**Short answer:** APF stops a single misbehaving client (a hot-looping controller
LISTing all Pods) from starving the API server and taking down the control plane. It
replaces the old global `--max-requests-inflight` blunt limit with **fair, prioritized
queueing**.

**Mechanism:**
- **FlowSchema** — matches requests (by user/SA/verb/resource) to a priority level + a
  **flow distinguisher** (e.g. per-user), so one noisy client can't crowd others.
- **PriorityLevelConfiguration** — each level gets a share of concurrency + its own queues;
  levels are isolated, so leader-election/system traffic (`system`, `leader-election`) is
  protected from bulk `workload-low` traffic.
- Requests over budget are **queued then rejected with 429** (`Retry-After`), not dropped
  blindly.

**Why it matters:** a runaway operator relisting everything used to brown out *every*
client; APF confines the blast radius to that flow.

**Debug:** `apiserver_flowcontrol_rejected_requests_total`,
`_current_inflight_requests`, `_request_wait_duration_seconds` by priority level →
shows which flow is saturating. Mitigate: fix the client's LIST→watch usage; as a lever,
tune the FlowSchema/PL shares.

---

[↑ Index](./README.md) · [← Prev](./16-what-is-helm-what-does-it-buy-you.md) · [Next →](./18-informers-watch-list-and-stale-caches.md)
