# TIME_WAIT sockets pile up and connections start failing under load. Explain and fix.

[↑ Index](./README.md) · [← Prev](./12-cgroups-memory-limits-and-the-jvm-go-runtime.md)

**Difficulty:** Hard · **Tags:** `networking` `tcp`

**Short answer:** The side that closes a TCP connection sits in **TIME_WAIT (~2×MSL, ~60s)**
to absorb stray packets. Under high **connection churn** (no keep-alive, new connection per
request), TIME_WAIT sockets + outbound connections exhaust the **ephemeral port range** →
`EADDRNOTAVAIL` / connection failures.

**Why it happens:**
- A client/proxy opening a fresh connection per request to the same upstream burns a
  source port each time; ports linger in TIME_WAIT for ~60s → the ~28k default ephemeral
  range (`net.ipv4.ip_local_port_range`) runs dry.
- In K8s this is worse behind **SNAT** (Cluster `externalTrafficPolicy`, egress NAT): many
  Pods share a node's source IP → conntrack + port pressure on one node.

**Diagnose:** `ss -s` (TIME_WAIT count), `ss -tan state time-wait | wc -l`, `dmesg` for port
exhaustion, conntrack table usage.

**Fix (in order of preference):**
- **Reuse connections** — HTTP keep-alive / connection pooling. This is the real fix;
  TIME_WAIT is a *symptom* of churn.
- `net.ipv4.tcp_tw_reuse=1` (safe for outbound) to recycle TIME_WAIT for new connections.
- Widen `ip_local_port_range`.
- **Avoid `SO_LINGER 0` / tcp_tw_recycle** — they cause silent breakage behind NAT.

**Tell:** don't "tune away" TIME_WAIT — it's doing its job. Churn is the bug; pool connections.

---

[↑ Index](./README.md) · [← Prev](./12-cgroups-memory-limits-and-the-jvm-go-runtime.md)
