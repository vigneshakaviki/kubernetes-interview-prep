# DNS lookups fail intermittently across the whole cluster. Root cause?

[↑ Index](./README.md) · [← Prev](./13-after-a-deploy-p99-latency-doubled-but-no-errors.md) · [Next →](./15-a-namespace-is-stuck-terminating-and-wont-delete.md)

**Difficulty:** Hard · **Tags:** `dns` `networking`

**Short answer:** Cluster-wide + intermittent DNS is rarely "CoreDNS crashed" — it's
usually **conntrack/UDP races**, **`ndots:5` amplification**, or **CoreDNS capacity**.
Don't restart CoreDNS reflexively.

**Confirm scope:** many Pods on many nodes → infrastructure, not one app.

**Walk it:**
- **`ndots:5` amplification** — a non-FQDN name tries several search domains first, so one
  external lookup = 4–5 queries. Multiply by load → CoreDNS overload + tail-latency failures.
- **conntrack exhaustion / UDP race** — the classic `musl`/parallel-A+AAAA conntrack
  insert race drops UDP replies intermittently (`nf_conntrack: table full` in `dmesg`).
- **CoreDNS capacity** — under-replicated / CPU-throttled; check its metrics + logs.
- **NetworkPolicy** newly applied blocking egress to kube-dns.

**Fix:** deploy **NodeLocal DNSCache** (biggest win — caches + switches to TCP, kills the
conntrack race), use **FQDNs** or tune `ndots`, scale CoreDNS, raise conntrack limits.
**Tell:** "intermittent, under load, cluster-wide" → amplification/conntrack, not a crash.

---

[↑ Index](./README.md) · [← Prev](./13-after-a-deploy-p99-latency-doubled-but-no-errors.md) · [Next →](./15-a-namespace-is-stuck-terminating-and-wont-delete.md)
