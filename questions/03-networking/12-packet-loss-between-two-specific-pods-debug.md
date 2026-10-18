# Two specific Pods have intermittent packet loss (others are fine). Debug methodically.

[↑ Index](./README.md) · [← Prev](./11-trace-external-packet-through-a-loadbalancer-service.md)

**Difficulty:** Hard · **Tags:** `networking` `cni`

**Short answer:** "Specific pair, intermittent" points at the **data path between their
nodes** — MTU/overlay fragmentation, conntrack, or a policy — not the app. Work L3→L4 and
isolate the variable (same node? same zone?).

**Isolate:**
- Are the two Pods on the **same node or different**? Loss only cross-node → node-to-node
  path (overlay/MTU). Same node → CNI/veth/conntrack local.

**Walk it:**
- **MTU mismatch** — the #1 cause of *intermittent* loss. Overlay (VXLAN) adds ~50 bytes;
  if Pod MTU > path MTU, large packets fragment/drop while small ones (ping) pass → "ping
  works, transfers hang." Test: `ping -M do -s 1472` and shrink to find the ceiling.
- **conntrack** — table full (`dmesg: nf_conntrack: table full`) drops flows under churn.
- **NetworkPolicy** — a policy intermittently matching (label churn) blocking some flows.
- **Underlay** — one bad node NIC / one overloaded node; check per-node, not per-Pod.

**Tools:** `tcpdump` on both Pod veths + both node interfaces simultaneously — see where the
packet disappears. `conntrack -S` for drops. `ethtool -S` for NIC errors.

**Fix:** set correct Pod MTU for the overlay, raise conntrack limits, replace the bad node.
The tell: **large-packet-only loss = MTU**, every single time.

---

[↑ Index](./README.md) · [← Prev](./11-trace-external-packet-through-a-loadbalancer-service.md)
