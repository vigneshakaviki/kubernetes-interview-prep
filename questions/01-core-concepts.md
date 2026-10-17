# Core Concepts & Architecture

### Q: Walk through what happens when you run `kubectl apply -f deploy.yaml` — and where it can fail.

**Difficulty:** Medium · **Tags:** `architecture` `control-plane`

**Short answer:** `apply` only gets the object *accepted* into etcd. Everything after is
async reconciliation — so you debug by comparing desired vs observed, not by assuming the
command "did" the work.

**The flow:**
1. **kubectl** → three-way merge vs `last-applied` annotation → sends to API server.
2. **API server** → authn → authz (RBAC) → **admission** (mutating webhooks inject/
   default; validating + quota reject) → schema validate → persist in **etcd** (new
   `resourceVersion`). `kubectl` returns here — "created" = *accepted*, not *running*.
3. **Deployment controller** → creates ReplicaSet → **ReplicaSet controller** → Pods.
4. **Scheduler** → filters + scores nodes → writes `nodeName`.
5. **kubelet** on that node → CRI pulls image + starts containers, CSI mounts volumes.
6. **kube-proxy / CNI** → program networking.

**Where it fails:**
| Symptom | Layer |
|---------|-------|
| apply hangs/rejected | admission webhook down; quota; RBAC |
| whole control plane stalls | etcd slow / no quorum |
| Pod `Pending` | no schedulable node |
| `ImagePullBackOff` | registry / tag / secret |
| apply OK but rollout wedged | readiness failing |

---

### Q: What is kube-proxy, its modes, and is it on the data path for every packet?

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

### Q: Deployment vs StatefulSet vs DaemonSet — and a case where the wrong one bites.

**Difficulty:** Medium · **Tags:** `workloads`

| Controller | Pods are | Use for |
|-----------|----------|---------|
| **Deployment** | fungible, stateless | stateless APIs; unordered rollout |
| **StatefulSet** | stable identity + per-Pod PVC + ordered | DBs, quorum systems |
| **DaemonSet** | one per node, auto-covers new nodes | node agents (CNI, logs, exporters) |

**Wrong-choice failure:** running Kafka/ZooKeeper/Postgres-replicas as a **Deployment** —
no stable identity or storage, so on reschedule a broker returns with a new name + empty/
other volume → breaks quorum and replication.

**Rule:** choose by whether *identity + storage must be stable* (StatefulSet), *every node
needs a copy* (DaemonSet), or neither (Deployment — the default).

---

### Q: Pod vs Deployment, and why we never create bare Pods in production.

**Difficulty:** Easy · **Tags:** `workloads`

- **Pod** = smallest schedulable unit (containers sharing IP/localhost + volumes).
  **Mortal, not self-healing** — node dies, nothing recreates it.
- **Deployment** = controller → ReplicaSet → Pods. Reconciles: keeps replica count,
  replaces failures, does rolling updates/rollbacks.

**So:** manage desired state through controllers (healing, rollout, audit). A bare Pod is
only for a throwaway debug shell.

---

### Q: Pods are ephemeral with changing IPs — how does a Service give stable access, and what are EndpointSlices?

**Difficulty:** Easy · **Tags:** `networking`

- **Service** = stable virtual IP + DNS (`name.ns.svc.cluster.local`) outliving any Pod;
  selects Pods by label.
- Control plane tracks which selected Pods are **Ready** and records their IPs in
  **EndpointSlices** (scalable successor to the single `Endpoints` object).
- kube-proxy/CNI load-balances to those live backends.

**Practical consequence:** a `Running`-but-**not-Ready** Pod is pulled from the slice →
stops getting traffic. An **empty EndpointSlice** (selector mismatch / no Ready Pods) is
the first thing to check on connection errors.

---

### Q: I point at lines in a Deployment YAML — which fields must you explain, and which mismatches silently break things?

**Difficulty:** Medium · **Tags:** `workloads` `yaml`

**Know cold:**
- `spec.replicas` — desired count.
- `spec.selector.matchLabels` — which Pods it owns; **immutable** after creation.
- `spec.template.metadata.labels` — must be a superset of the selector or apply is rejected.
- `containers[]`: `image` (digest/immutable tag, never `latest`), `ports`, `env`/`envFrom`,
  `resources.requests|limits`, probes.
- `strategy` — `maxSurge` / `maxUnavailable`.

**Silent breakers:** selector ≠ template labels (orphaned Pods) · `latest` tag (a "no-op"
apply pulls a changed image) · no requests (bad placement, HPA has no baseline) ·
`maxUnavailable` too high (rollout drops capacity under load).

---

### Q: Write a Dockerfile for a Python service and justify every line.

**Difficulty:** Easy · **Tags:** `docker` `containers`

```dockerfile
FROM python:3.12-slim          # small, fewer CVEs; avoids alpine/musl wheel pain
WORKDIR /app
COPY requirements.txt .         # copy deps first → pip layer caches until deps change
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN useradd -m app && chown -R app /app
USER app                        # non-root: baseline for Pod Security "restricted"
EXPOSE 8000
CMD ["python", "main.py"]       # exec form → PID 1 gets SIGTERM for graceful shutdown
```

- Layer order by change-frequency = the main build-speed lever.
- Shell-form `CMD` would swallow signals → no graceful shutdown.
- Mention: multi-stage build to drop build tools, pinned base digest, readiness probe
  instead of Docker healthcheck.

---

### Q: etcd's role, consequences of it going unhealthy, and explain Raft like you've operated it.

**Difficulty:** Hard · **Tags:** `architecture` `consensus`

**Role:** the consistent, watchable KV store — single source of truth; only the API
server talks to it.

**Unhealthy:**
- Slow → *every* write stalls, controllers lag.
- No quorum → control plane read-only/unavailable, but **running Pods keep serving**
  (data plane survives a control-plane outage).

**Raft:**
- One **leader** takes all writes, replicates log to followers.
- Entry **commits** once a **majority (quorum)** persists it.
- Leader loss → follower times out → bumps **term** → requests votes → majority wins.
- **Odd member count**: quorum = `floor(n/2)+1`; 3 tolerates 1, 5 tolerates 2. Even
  count buys no extra tolerance.

**Operator reality:** disk-latency sensitive (fsync per commit) → fast disks, watch
`backend commit` p99, keep under DB size quota, **take + test-restore snapshots** (no
tested restore = no DR).

---

### Q: "Do you have Kubernetes experience?" but your company used in-house infra. How do you answer?

**Difficulty:** Easy · **Tags:** `behavioral`

**Weak:** "I wrote YAML and ran `kubectl apply`" → sounds surface-level.

**Strong:** answer at the level of *what orchestration solves* and map your system onto it:
scheduling, self-healing reconcile loops, declarative state, rolling updates, service
discovery/LB, resource isolation, secret distribution.
- "We ran our own platform with the equivalent of a scheduler, a ReplicaSet-style
  controller, and a mesh; here's a trade-off we debated vs how K8s does it."
- Then prove you can ramp: name a non-trivial K8s primitive (PDBs, topology spread,
  admission control) to show depth, not buzzwords.

---

### Q: How does the scheduler place a Pod — and how do you influence or debug it?

**Difficulty:** Advanced · **Tags:** `scheduling` `architecture`

**Two phases per unscheduled Pod:**
1. **Filter (predicates)** — drop nodes that *can't* fit: resources, taints, nodeSelector/
   affinity, pod (anti-)affinity, volume zone, port conflicts.
2. **Score (priorities)** — rank survivors (least-requested, balanced, spread, image
   locality) → bind via `nodeName`.

No node survives → `Pending` + "unschedulable" event.

**Influence:** requests (reserved vs usage), affinity/anti-affinity, taints/tolerations,
`topologySpreadConstraints`, `priorityClass` + **preemption**.

**Debug:** `kubectl describe pod` → per-predicate reason.

**Gotcha:** scheduler decides *placement*, never creates capacity → pair with Cluster
Autoscaler/Karpenter to turn "unschedulable" into new nodes.

---

### Q: Operator pattern and CRDs — when is it right vs over-engineering?

**Difficulty:** Advanced · **Tags:** `architecture` `extensibility`

- **CRD** — registers a new API `kind` (served with the same RBAC/watch/kubectl machinery).
- **Operator** — a controller watching that resource, reconciling reality → spec, encoding
  *day-2 ops* (provision, scale, backup, failover, upgrade).

**Right call:** managing a stateful/complex system whose day-2 ops are domain-specific +
repetitive — i.e. the thing you're automating is a **control loop**.

**Over-engineering:** a one-time install a Helm chart or built-in controllers would do —
because you now own controller correctness (idempotency, partial failure, status/
conditions, finalizers, no hot reconcile loops).

---

### Q: Owner references, cascading GC, and finalizers — and why is an object stuck in `Terminating`?

**Difficulty:** Advanced · **Tags:** `architecture` `lifecycle`

- **ownerReferences** form a tree (Pod → ReplicaSet → Deployment); the GC cascades deletes.
- **Propagation:** `Background` (default), `Foreground` (parent stays `Terminating` until
  children gone), `Orphan` (children survive).
- **Finalizer** — a key that **blocks** deletion until a controller does cleanup
  (deprovision a cloud LB) and removes it; only when the list is empty is the object purged.

**Stuck in `Terminating`** = a finalizer isn't being cleared → the responsible controller
is down/crashed/deleted (or a foreground cascade waits on a child).
- Debug: `kubectl get -o yaml` → check `metadata.finalizers` + `deletionTimestamp`; fix
  the controller.
- Force-removing a finalizer unblocks delete but **leaks** the external resource — last
  resort.

---

### Q: Namespaces, ResourceQuota, LimitRange — how do they stop one team taking down a shared cluster?

**Difficulty:** Intermediate · **Tags:** `multi-tenancy`

- **Namespace** — virtual scope for names/RBAC/quota/policy. **Not** a hard security
  boundary (shared kernel/nodes) → untrusted tenancy needs more (node pools, NetworkPolicy,
  Pod Security, sometimes separate clusters).
- **ResourceQuota** — caps aggregate requests/limits + object counts **per namespace**.
- **LimitRange** — per-container defaults + min/max.

**Interaction:** once a CPU/mem quota is set, every Pod **must** declare requests/limits or
it's rejected → LimitRange supplies sane defaults so nothing breaks and nobody requests an
absurd amount.

**Without them:** one Deployment with no limits can evict everyone under node pressure.

---

### Q: Labels vs annotations — where's the line, and what breaks if you blur it?

**Difficulty:** Intermediate · **Tags:** `metadata`

| | Labels | Annotations |
|--|--------|-------------|
| For | **selection** (selectors, ownership, grouping) | arbitrary metadata for tools/humans |
| Shape | small, low-cardinality, indexed | can be large, not selectable |

**Blur it:**
- High-cardinality/changing value in a **label** (timestamp, hash per deploy) → index
  bloat, broken selectors, monitoring cardinality blowup.
- Data you need to select on stuck in an **annotation** → can't target it, filter client-side.

**Rule:** decides *which objects an operation applies to* → label; metadata you only read →
annotation.

---

### Q: Imperative vs declarative kubectl, and safely rolling back a bad Deployment.

**Difficulty:** Intermediate · **Tags:** `kubectl` `operations`

- **Imperative** (`create`, `scale`, `set image`) — fast, drifts from truth, not reviewable.
- **Declarative** (`apply -f`, GitOps) — repo is the audit log + change control. Run prod
  on this.

**Rollback:**
```bash
kubectl rollout history deploy/x
kubectl rollout undo deploy/x --to-revision=N   # scales the old ReplicaSet back up
```
GitOps: the real rollback is **reverting the git commit** (else it drifts back on next sync).

**Caveat:** rollback is clean only if the change was backward-compatible — a schema
migration or consumed-then-removed API **can't** be undone by scaling Pods → need
forward-fix or expand/contract discipline.

---

### Q: What is Helm, what does it buy you, and when would you use Kustomize instead?

**Difficulty:** Intermediate · **Tags:** `packaging`

- **Helm** — package manager. A **chart** = templated manifests + `values.yaml`; installing
  it creates a **release** you can `upgrade`/`rollback`/`uninstall` as a unit. Solves
  templating/reuse + lifecycle.
- **Trade-off:** Go-templated YAML gets hard to read/debug as charts grow.
- **Kustomize** (`kubectl -k`) — template-free base + overlays patched per environment;
  cleaner for *your own* apps where you control the YAML.

**Rule:** Helm to consume third-party software (versioned releases, community charts);
Kustomize (or a GitOps tool rendering either) for your own services. Deciding factor =
who owns the manifests + whether you need packaged, versioned distribution.
