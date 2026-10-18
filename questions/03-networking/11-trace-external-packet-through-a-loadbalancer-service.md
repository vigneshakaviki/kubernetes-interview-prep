# Trace an external packet to a Pod through a LoadBalancer Service — and contrast `externalTrafficPolicy` Cluster vs Local.

[↑ Index](./README.md) · [← Prev](./10-how-does-an-ingress-handle-tls-path-routing.md) · [Next →](./12-packet-loss-between-two-specific-pods-debug.md)

**Difficulty:** Hard · **Tags:** `networking` `loadbalancer`

**Short answer:** Cloud LB → a node's NodePort → kube-proxy DNAT → a backend Pod. The
`externalTrafficPolicy` decides whether there's an **extra hop + SNAT** (Cluster) or
**client-IP preservation but uneven spread** (Local).

**`Cluster` (default):**
- LB targets **all** nodes. Packet lands on *any* node, kube-proxy may DNAT to a Pod on
  **another** node → second hop + **SNAT** (source rewritten to the node IP).
- ✅ even load spreading. ❌ client IP **hidden**, extra hop/latency.

**`Local`:**
- LB health-checks and targets **only nodes that have a backing Pod**; kube-proxy routes
  only to local Pods, **no SNAT**.
- ✅ real **client source IP** preserved, no extra hop. ❌ spread is **per-node**, so uneven
  if Pods aren't balanced across nodes; a node with 3 Pods and a node with 1 get equal LB
  share → hotspots.

**Implications:**
- Need client IP (allow-lists, rate-limiting, geo, logging) → `Local` + spread Pods evenly
  (topology constraints) + tune the LB health check.
- The "my app sees all traffic from node IPs" bug = `Cluster` + SNAT. Switch to `Local` or
  read `X-Forwarded-For` at an L7 ingress instead.

---

[↑ Index](./README.md) · [← Prev](./10-how-does-an-ingress-handle-tls-path-routing.md) · [Next →](./12-packet-loss-between-two-specific-pods-debug.md)
