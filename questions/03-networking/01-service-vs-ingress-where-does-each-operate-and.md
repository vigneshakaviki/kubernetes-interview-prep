# Service vs Ingress — where does each operate, and why not a LoadBalancer per service?

[↑ Index](./README.md) · [Next →](./02-what-is-a-networkpolicy-the-default-without-one.md)

**Difficulty:** Easy · **Tags:** `networking`

- **Service** = L4 (TCP/UDP): stable VIP + DNS, load-balances to selected Pods.
- **Ingress** = L7 HTTP(S): host/path routing, TLS termination, virtual hosting — run by
  an ingress controller (nginx, Traefik, cloud ALB).

**Why not `type: LoadBalancer` per service:** each one provisions a **real cloud LB** (own
IP, own cost, one cert, no host/path routing). Dozens of HTTP services → dozens of LBs +
certs + bill. One Ingress fronts many ClusterIP Services with central TLS + routing.

**Rule:** LoadBalancer for non-HTTP (raw TCP, DB) or a single entry point; Ingress (or
Gateway API) for lots of HTTP.

---

[↑ Index](./README.md) · [Next →](./02-what-is-a-networkpolicy-the-default-without-one.md)
