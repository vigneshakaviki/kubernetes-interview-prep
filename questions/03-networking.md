# Networking

### Q: Service vs Ingress — where does each operate, and why not a LoadBalancer per service?

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

### Q: What is a NetworkPolicy, the default without one, and the gotcha people miss?

**Difficulty:** Medium · **Tags:** `networking` `security`

- **Default:** flat + open — every Pod reaches every Pod, no isolation.
- **NetworkPolicy:** namespaced allow-list by Pod label / namespace / IP block.
- **Behavior:** additive + **default-deny-once-selected** — once any policy selects a Pod
  for a direction, all not-allowed traffic in that direction is denied; unselected Pods
  stay open.

**Two gotchas:**
1. **Does nothing without an enforcing CNI** (Calico/Cilium) — on a CNI that ignores it,
   your "deny" silently allows → false security.
2. People write ingress rules + forget **egress/DNS** — a default-deny-egress that doesn't
   allow kube-dns breaks name resolution for every selected Pod.

---

### Q: How does in-cluster DNS work, and how do you debug "can't resolve"?

**Difficulty:** Medium · **Tags:** `networking` `dns`

- **CoreDNS** runs behind a ClusterIP Service. Each Pod's `/etc/resolv.conf` → that IP +
  search domains + `ndots:5`.
- Bare name in same namespace resolves via search domains; FQDN external name can incur
  several failed lookups first (the `ndots` tax).

**Debug order:**
1. Resolve a *known* name from the Pod (`nslookup kubernetes.default`) — total failure vs one name?
2. Check `/etc/resolv.conf`.
3. kube-dns Service has endpoints?
4. **CoreDNS Pods** Ready + logs.
5. NetworkPolicy blocking DNS egress?

**Gotcha:** don't restart CoreDNS reflexively — intermittent-under-load DNS is usually
`ndots` amplification / conntrack exhaustion, which a restart only hides. Fix: NodeLocal
DNSCache, `ndots` tuning / FQDNs.

---

### Q: ClusterIP vs NodePort vs LoadBalancer — how they stack.

**Difficulty:** Intermediate · **Tags:** `networking`

Each layers on the previous:
| Type | Adds | Reach |
|------|------|-------|
| **ClusterIP** | base VIP | inside cluster only |
| **NodePort** | static port on every node | any node IP:port |
| **LoadBalancer** | cloud LB → NodePorts | external IP |

**`externalTrafficPolicy`:**
- `Cluster` (default) — spreads across all nodes but **SNATs** → hides client IP, extra hop.
- `Local` — preserves client source IP, no extra hop, but only hits nodes **with** a Pod
  (need even spread).

**Rule:** ClusterIP internal; Ingress over ClusterIP for HTTP; LoadBalancer for a true
external entry; `Local` when you need real client IPs.

---

### Q: Headless Service — how it differs at DNS level, and when you actually need one.

**Difficulty:** Advanced · **Tags:** `networking` `statefulset`

- `clusterIP: None` → **no VIP, no kube-proxy LB**. DNS returns **A records per Ready Pod**;
  with a StatefulSet, stable per-Pod names (`pod-0.svc...`).

**Need it when the client must address specific Pods:**
- Stateful clusters finding peers by identity (Kafka, ZooKeeper, etcd).
- Client-side load balancing.

**The gRPC tell:** a normal ClusterIP Service under-balances gRPC — HTTP/2 multiplexes many
requests over one long-lived connection that L4 kube-proxy balances only at connect time,
so one backend hogs load. Headless (or a mesh) lets the client see all endpoints and spread.

---

### Q: Explain the Pod networking model and what a CNI is responsible for.

**Difficulty:** Advanced · **Tags:** `networking` `cni`

**Model (hard rules):** every Pod has its own IP · all Pods reach each other **without
NAT** · the IP a Pod sees == the IP others use. K8s delegates this to a **CNI** plugin.

**CNI responsibilities:**
- **IPAM** — allocate Pod IP from the node/cluster CIDR.
- Wire the Pod netns (veth → bridge or direct routes).
- Cross-node routing: **overlay** (VXLAN/Geneve — works anywhere, costs overhead + MTU) or
  **native routing / BGP** (faster, needs underlay support).
- Often **NetworkPolicy enforcement** + extras (eBPF kube-proxy replacement; VPC-native
  IPs that can exhaust ENIs).

**Framing:** CNI choice drives IP density, encapsulation overhead, policy enforcement, and
VPC integration — an architectural decision, not a checkbox.

---

### Q: kube-proxy iptables vs IPVS — what breaks at scale?

**Difficulty:** Advanced · **Tags:** `networking`

- **iptables** — chains of DNAT rules; both **update** (resync rewrites big rule sets) and
  **match** cost grow ~linearly → at thousands of Services, slow endpoint propagation
  (seconds) + latency/jitter.
- **IPVS** — in-kernel hash tables (O(1) lookup) + real LB algos → scales, lower/consistent
  latency, faster updates.

**Note:** IPVS still uses iptables for some filtering/NodePort; the modern move is an
**eBPF** dataplane (Cilium) replacing both. Name the *actual* failure (linear rule scaling),
not just "IPVS faster."

---

### Q: What does a service mesh add over plain K8s networking, and what's the cost?

**Difficulty:** Advanced · **Tags:** `networking` `mesh`

**Adds** (via sidecar / eBPF data plane, no app changes):
- **mTLS** everywhere (identity-based authn/encryption).
- **L7 traffic control** — weighted canary, retries, timeouts, circuit breaking, fault injection.
- **Rich telemetry** — per-route golden signals, tracing.

**Cost:** per-Pod sidecar CPU/mem + extra hop (latency); big operational complexity (control-
plane upgrades, cert rotation, "app or proxy?" debugging). → newer **ambient/eBPF** meshes
cut per-Pod overhead.

**Rule:** adopt for genuine mTLS/zero-trust across many services, automated progressive
delivery, or uniform L7 telemetry — not because it's fashionable.

---

### Q: How do Pods discover each other — DNS vs env vars — and why is one a trap?

**Difficulty:** Intermediate · **Tags:** `networking` `dns`

- **Env vars** — `<SVC>_SERVICE_HOST/PORT` injected, **only for Services that existed when
  the Pod started**. The trap: a Pod started before its dependency's Service won't have the
  var → unreachable until recreated. Hidden startup-order coupling → "worked yesterday,
  broke after a restart."
- **DNS** (CoreDNS) — resolvable anytime at `name.ns.svc.cluster.local`, no ordering. **Use
  DNS.**

---

### Q: How does an Ingress handle TLS + path routing, and what's its relationship to the controller?

**Difficulty:** Intermediate · **Tags:** `networking` `ingress`

- **Rules** — match host + path → backend Service. `pathType`: `Prefix` / `Exact` /
  `ImplementationSpecific`.
- **TLS** — references a Secret per host; controller **terminates TLS** at the edge
  (cert-manager automates certs).

**Crucial:** the **Ingress object does nothing alone** — a running **ingress controller**
watches it and programs the proxy. "My Ingress isn't working" is often no controller
installed, or `ingressClassName` mismatch.

**Note:** controller-specific behavior lives in **annotations** → non-portable, which is
why the **Gateway API** exists (typed, portable, role-oriented successor).
