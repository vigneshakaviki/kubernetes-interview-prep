# Networking

### Q: Service vs Ingress — where does each operate, and why don't you just give every service a LoadBalancer?

**Difficulty:** Easy · **Tags:** `networking`

A **Service** is L4 (TCP/UDP): a stable virtual IP + DNS name that load-balances across
the Pods matched by its selector. An **Ingress** is L7 HTTP(S): host- and path-based
routing, TLS termination, and virtual hosting in front of Services, implemented by an
ingress controller (nginx, Traefik, a cloud ALB). Service = connectivity and L4 balancing;
Ingress = HTTP routing and TLS.

Why not a LoadBalancer per Service: each `type: LoadBalancer` provisions a *real cloud
load balancer* with its own public IP and cost, and you lose shared L7 features (one cert
per LB, no host/path routing, no shared WAF). With dozens of HTTP services that's dozens
of LBs, dozens of certs, and a big bill. An Ingress gives you **one** external LB fronting
many Services with centralized TLS, routing, and policy. The framing: LoadBalancer
Services are right for non-HTTP (gRPC-over-raw-TCP, databases) or a single entry point;
for lots of HTTP apps you want one ingress (or the newer Gateway API) terminating TLS and
routing to ClusterIP Services behind it.

---

### Q: What is a NetworkPolicy, what's the default behavior without one, and what's the gotcha people miss?

**Difficulty:** Medium · **Tags:** `networking` `security`

By default Kubernetes networking is **flat and open**: every Pod can reach every other
Pod across namespaces, no isolation. A **NetworkPolicy** is a namespaced allow-list
selecting Pods and permitting specific ingress/egress by Pod label, namespace, or IP
block. The defining behavior: a policy is **additive and default-deny-once-selected** —
as soon as *any* policy selects a Pod for a direction, everything not explicitly allowed
in that direction is denied for that Pod; Pods that no policy selects remain fully open.

Two gotchas that matter. First, **the API object does nothing without an enforcing CNI**
— Calico, Cilium, etc. implement it; on a CNI that ignores NetworkPolicy, your "deny"
rules silently allow everything, which is a dangerous false sense of security. Second,
people write ingress rules and forget **egress and DNS**: a default-deny-egress policy
that doesn't allow traffic to kube-dns breaks name resolution for every selected Pod, so
the app fails in confusing ways. The answer: NetworkPolicy is how you move from a
flat network to zero-trust segmentation, but you must verify the CNI enforces it, build
default-deny carefully (allowing DNS and necessary egress), and test it — because a policy
that doesn't apply looks identical to one that does until you're breached.

---

### Q: How does in-cluster DNS resolution actually work, and how would you debug a service that "can't resolve"?

**Difficulty:** Medium · **Tags:** `networking` `dns`

**CoreDNS** runs as a Deployment behind a ClusterIP Service (`kube-dns`). The kubelet
writes that Service IP into every Pod's `/etc/resolv.conf` along with search domains
(`namespace.svc.cluster.local`, `svc.cluster.local`, `cluster.local`) and an `ndots:5`
option. So a Pod resolving `myservice` tries the search domains in order, which is why a
bare service name in the same namespace resolves, and why a fully-qualified external name
can incur several failed lookups first (the `ndots:5` tax). A normal Service resolves to
its ClusterIP; a **headless** Service resolves to the individual Pod IPs.

Debugging path, in order: resolve a *known* name from inside an affected Pod (`nslookup
kubernetes.default` or `dig`) to see if it's total DNS failure or one name; check the
Pod's `/etc/resolv.conf`; check the kube-dns Service has endpoints; check the **CoreDNS
Pods** are Ready and read their logs (plugin errors, upstream timeouts); and check a
**NetworkPolicy isn't blocking egress to DNS**. Only then consider CoreDNS capacity
(scale up, enable `autopath`/node-local DNS cache for `ndots` churn). The nuance:
don't restart CoreDNS as a reflex — if resolution is intermittent under load it's usually
capacity/`ndots` amplification or conntrack exhaustion, not a crashed CoreDNS, and
restarting just hides it briefly.

---

### Q: Explain ClusterIP, NodePort, and LoadBalancer, and how they build on each other.

**Difficulty:** Intermediate · **Tags:** `networking`

They're a stack, each layering on the previous. **ClusterIP** (default) is an
internal-only virtual IP reachable from inside the cluster — the base case, fine for
service-to-service traffic. **NodePort** builds on ClusterIP by also opening a static
high port (30000–32767 by default) on **every** node that forwards to the Service; any
node's IP:nodePort reaches the Service even if no backend Pod runs there. **LoadBalancer**
builds on NodePort by asking the cloud provider to provision an external load balancer
whose targets are those NodePorts, giving you a stable external IP.

The practical implications: NodePort is rarely exposed directly to users (ugly ports, you
must manage which node IPs clients hit) — it's mostly a building block or for on-prem with
an external LB in front. LoadBalancer is clean but costs one cloud LB per Service. And
`externalTrafficPolicy` matters: `Cluster` (default) load-balances across all nodes but
SNATs, hiding the client IP and adding a hop; `Local` preserves the client source IP and
avoids the extra hop but only sends traffic to nodes that *have* a backend Pod (so you
need healthy Pods spread across nodes). The answer: pick ClusterIP for internal,
front HTTP with an Ingress over ClusterIP, use LoadBalancer for a true external entry
point, and know that `externalTrafficPolicy: Local` is the knob for real client IPs at the
cost of even Pod spreading.

---

### Q: What's a headless Service, how does it differ at the DNS level, and when do you actually need one?

**Difficulty:** Advanced · **Tags:** `networking` `statefulset`

A headless Service sets `clusterIP: None`. That means **no virtual IP and no kube-proxy
load-balancing** — instead of resolving to one VIP, the Service's DNS name returns **A
records for each Ready backing Pod**. With a StatefulSet it also gives each Pod a stable
per-Pod DNS name (`pod-0.svc.namespace.svc.cluster.local`).

You need it whenever the client must address **specific** Pods rather than "any backend."
The canonical cases: stateful clustered systems where members must find each other by
stable identity (Kafka brokers, ZooKeeper/etcd peers, a database's primary vs replicas);
client-side load balancing where the client (e.g. a gRPC client) wants the full set of
endpoints and does its own balancing rather than being pinned to one connection by L4
NAT; and peer discovery in general. The nuance: a normal ClusterIP Service with
gRPC famously under-balances because HTTP/2 multiplexes many requests over one long-lived
connection that L4 kube-proxy load-balances only at connect time — so all requests hog one
backend. A headless Service (or a mesh) lets the client see all endpoints and spread
requests properly. That gRPC detail is the one that signals real experience.

---

### Q: Explain the Kubernetes Pod networking model and what a CNI plugin is responsible for.

**Difficulty:** Advanced · **Tags:** `networking` `cni`

The model has a few hard rules: every Pod gets its own IP, every Pod can reach every
other Pod **without NAT**, and the IP a Pod sees itself as is the IP others use to reach
it. Containers within a Pod share that one network namespace (localhost between them).
Kubernetes itself doesn't implement any of this — it delegates to a **CNI** plugin via a
standard interface the kubelet calls when a Pod is created/destroyed.

The CNI (Calico, Cilium, flannel, cloud VPC CNIs) is responsible for **IPAM** (allocating
a Pod IP from the cluster/node CIDR), wiring the Pod's network namespace (veth pair into
the node bridge or direct routes), and making Pod-to-Pod routing work across nodes —
either with an **overlay** (encapsulate packets in VXLAN/Geneve, works anywhere, costs
some overhead and MTU) or **native/unencapsulated routing** (program the underlay/VPC or
BGP, faster, needs network support). Many CNIs also enforce **NetworkPolicy** and provide
features like eBPF-based kube-proxy replacement (Cilium) or using real VPC IPs for Pods
(AWS VPC CNI, so Pods are first-class in the VPC but you can exhaust ENIs/IPs). The
framing: the CNI choice drives your IP density limits, whether you pay encapsulation
overhead, how NetworkPolicy is enforced, and how Pods integrate with the cloud network —
it's an architectural decision, not a checkbox, and "we use an overlay vs we route native
VPC IPs" has real consequences for scale and observability.

---

### Q: kube-proxy iptables mode vs IPVS mode — what breaks at scale and why does IPVS help?

**Difficulty:** Advanced · **Tags:** `networking`

Both program the node so Service VIP traffic reaches backend Pods, but their data
structures differ. **iptables mode** writes chains of DNAT rules; for a packet to be
matched, the kernel walks rules, and both rule *updates* (resyncs rewrite large rule sets)
and *matching* cost grow roughly linearly with the number of Services and endpoints. At
thousands of Services you see slow rule reprogramming (endpoint changes take seconds to
propagate) and added latency/jitter. **IPVS mode** uses in-kernel hash tables with O(1)
lookup and offers real load-balancing algorithms (round-robin, least-connection, source
hashing), so it scales to large Service counts with lower and more consistent latency and
faster updates.

The nuance: IPVS still falls back to iptables for some packet filtering and
NodePort handling, so it's not a total replacement; and the modern trend is to drop
kube-proxy entirely for an **eBPF** dataplane (Cilium) that implements Service routing in
the kernel's eBPF hooks, avoiding both iptables and IPVS limitations and giving better
observability. The answer that lands: name the actual failure (linear rule scaling →
slow endpoint propagation and latency at thousands of Services), not just "IPVS is
faster."

---

### Q: What does a service mesh add over plain Kubernetes networking, and what's the cost?

**Difficulty:** Advanced · **Tags:** `networking` `mesh`

Plain K8s gives you L4 Services, DNS, and NetworkPolicy — but no application-layer
traffic control, no mutual auth between services, and limited visibility into
service-to-service calls. A **mesh** (Istio, Linkerd, or newer ambient/eBPF designs)
inserts a data plane — classically a per-Pod **sidecar proxy** — that transparently
intercepts traffic and adds: **mTLS** everywhere (identity-based encryption and authn
between services without app changes), **L7 traffic management** (weighted canary splits,
retries, timeouts, circuit breaking, fault injection), and **rich telemetry** (per-route
golden signals, distributed tracing headers).

The cost is real and worth stating: a sidecar per Pod means extra CPU/memory and an extra
network hop (latency), plus significant operational complexity (control-plane upgrades,
cert rotation, debugging "is it the app or the proxy?"). That's why newer **sidecarless /
ambient** meshes push the data plane to a per-node eBPF layer to cut the per-Pod overhead.
The framing: adopt a mesh when you specifically need mTLS/zero-trust across many
services, progressive delivery with automated canary analysis, or uniform L7 telemetry —
and *not* just because it's fashionable, because you're trading a pile of operational
complexity for those features. If you only need a couple of those, an ingress + good
client libraries + NetworkPolicy may be cheaper.

---

### Q: How do Pods discover each other — DNS vs environment variables — and why is one of them a trap?

**Difficulty:** Intermediate · **Tags:** `networking` `dns`

Two mechanisms exist. **Environment variables**: for each Service, the kubelet injects
`<SVC>_SERVICE_HOST` / `<SVC>_SERVICE_PORT` into Pods. **DNS** (CoreDNS): every Service is
resolvable at `name.namespace.svc.cluster.local` at any time.

The env-var approach is the trap: those variables are injected **only for Services that
already existed when the Pod started**. So a Pod started before its dependency's Service
won't have the variable, and the dependency becomes unreachable until the Pod is recreated
— an ordering dependency that's invisible and bites you after an unrelated restart. It
also pollutes the environment and can't represent Services created later. **DNS has no
such ordering problem** — resolution is dynamic — so it's the correct, order-independent
way to do service discovery, and it's what you should always use. The point: the
env-var mechanism is a legacy convenience; relying on it couples startup order between
unrelated workloads, which is exactly the kind of hidden coupling that causes a "worked
yesterday, broke after a restart" incident.

---

### Q: How does an Ingress handle TLS and path-based routing, and what's the relationship between the Ingress object and the controller?

**Difficulty:** Intermediate · **Tags:** `networking` `ingress`

An **Ingress** object is a set of rules: match on host and path, route to a backend
Service + port. `pathType` controls matching — `Prefix` (match a path prefix), `Exact`
(full match), or `ImplementationSpecific` (controller-defined, e.g. regex on nginx). TLS
is configured by referencing a **Secret** (cert + key) per host in the `tls` section; the
**ingress controller terminates TLS** at the edge and forwards (usually plaintext or
re-encrypted) to the Service. cert-manager commonly automates issuing/renewing those
certs from Let's Encrypt.

The crucial relationship: the **Ingress object is just declarative config; it does nothing
on its own**. A running **ingress controller** (nginx, Traefik, HAProxy, a cloud
controller) watches Ingress objects and programs the actual proxy/load balancer that moves
traffic. No controller, no effect — a common "my Ingress isn't working" cause is that none
is installed, or the Ingress's `ingressClassName` doesn't match the installed controller.
The additions: annotations are where controller-specific behavior lives (rewrite,
rate limit, auth, timeouts), which makes Ingress non-portable across controllers — one of
the reasons the **Gateway API** was created as a more expressive, role-oriented,
portable successor that models gateways, routes, and TLS as first-class typed resources.
