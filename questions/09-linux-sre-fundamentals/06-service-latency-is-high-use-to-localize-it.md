# Service latency is high. Use `netstat`/`ss`, `tcpdump`, `traceroute` to localize it.

[↑ Index](./README.md) · [← Prev](./05-a-machine-s-cpu-spikes-handle-it-start.md) · [Next →](./07-vs.md)

**Difficulty:** Medium · **Tags:** `networking` `troubleshooting`

- **`traceroute`/`mtr`** — per-hop latency/loss (prove/exonerate the network).
- **`ss`/`netstat`** — socket state: backlog overflow (app not accepting), piles of
  `TIME_WAIT`/`CLOSE_WAIT` (churn/leak), retransmits, ephemeral-port exhaustion.
- **`tcpdump`** — slow SYN/SYN-ACK (setup), retransmits (loss), gap before first byte
  (server think-time vs network), TLS handshake stalls.

Combine with app traces to split **network time** from **server time**.

**K8s tie-in:** latency often comes from plumbing — conntrack exhaustion, DNS `ndots:5`
amplification, iptables rule bloat, SNAT/`externalTrafficPolicy` hops.

---

[↑ Index](./README.md) · [← Prev](./05-a-machine-s-cpu-spikes-handle-it-start.md) · [Next →](./07-vs.md)
