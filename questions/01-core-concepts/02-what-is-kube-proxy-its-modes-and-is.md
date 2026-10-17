# What is kube-proxy, its modes, and is it on the data path for every packet?

[↑ Index](./README.md) · [← Prev](./01-walk-through-what-happens-when-you-run-and.md) · [Next →](./03-deployment-vs-statefulset-vs-daemonset-and-a-case.md)

**Difficulty:** Medium · **Tags:** `networking` `architecture`

**Short answer:** It's the node agent implementing **Services** — but in the common modes
it **programs kernel rules**, it is *not* an in-path proxy per packet.

**Modes:**
- **iptables** — DNAT rules, kernel rewrites dest to a random backend. Ubiquitous, but
  rule update + match cost grow ~linearly → slow at tens of thousands of Services.
- **IPVS** — in-kernel hash tables + real LB algos (rr, lc, sh). Scales far better.
- **eBPF** (Cilium) — replaces kube-proxy entirely.

**Consequences:**
- Load-balances **only at connection setup** → long-lived connections don't rebalance
  when endpoints change.
- Service VIPs aren't pingable — no host owns them, they're just rules.

---

[↑ Index](./README.md) · [← Prev](./01-walk-through-what-happens-when-you-run-and.md) · [Next →](./03-deployment-vs-statefulset-vs-daemonset-and-a-case.md)
