# Core Concepts & Architecture

### Q: Walk me through everything that happens when you run `kubectl apply -f deploy.yaml`. Be specific about which component does what, and where it can fail.

**Difficulty:** Medium · **Tags:** `architecture` `control-plane`

`kubectl` resolves the manifest, diffs it against the `last-applied-configuration`
annotation (three-way merge for `apply`), and sends the result to the **API server**.
The API server is the only front door: it authenticates (certs/OIDC/tokens),
authorizes via **RBAC**, runs **admission** (mutating webhooks can inject defaults or a
sidecar; validating webhooks and quota can reject), validates the schema, and persists
the object in **etcd** with a new `resourceVersion`. At this point `kubectl` returns —
"created" means *accepted*, not *running*.

Asynchronously, controllers reconcile. The **Deployment controller** (watching via the
API server's watch cache) sees the spec and creates/updates a **ReplicaSet**; the
ReplicaSet controller creates **Pods**. Each Pod is initially unscheduled; the
**scheduler** filters nodes that can't fit it and scores the rest, then writes a binding
(`spec.nodeName`). The target node's **kubelet** notices a Pod bound to it, calls the
**CRI** runtime to pull images and start containers, sets up volumes via **CSI**, and
reports status back. **kube-proxy**/CNI program networking so the Pod is reachable.

Failure points worth naming: admission webhook down → all applies for that resource
hang or fail; etcd slow/unavailable → whole control plane stalls; no schedulable node →
Pod stuck `Pending`; image/registry problem → `ImagePullBackOff`; the apply succeeding
while the rollout silently wedges on readiness. The point: `apply` is
*declarative intent*; everything after is eventually-consistent reconciliation, so you
debug by comparing desired vs observed, not by assuming the command "did" the work.

---

### Q: What is `kube-proxy`, what are its modes, and is it even on the data path for every packet?

**Difficulty:** Medium · **Tags:** `networking` `architecture`

`kube-proxy` is the node agent that implements the **Service** abstraction. It watches
Services and EndpointSlices and programs the node so that traffic to a Service's virtual
IP is redirected to a healthy backend Pod. Crucially, in the common modes it is **not**
an in-path proxy for each packet — it programs kernel rules and gets out of the way.

**iptables mode**: installs DNAT rules; the kernel rewrites the destination to a random
backend. Simple and ubiquitous, but rules are evaluated roughly linearly, so update and
match cost grows with the number of Services/endpoints — painful at tens of thousands.
**IPVS mode**: uses in-kernel hash tables and real LB algorithms (rr, lc, sh), far
better at scale and with lower latency variance. Newer clusters increasingly bypass
kube-proxy entirely with **eBPF** (Cilium), which replaces the iptables/IPVS machinery.

The nuance: because kube-proxy only load-balances at connection setup, existing
long-lived connections don't rebalance when endpoints change; and Service VIPs aren't
pingable (no host owns them — they exist only as rules). Knowing it's rule-programming,
not a daemon proxying bytes, is what separates a real answer from a textbook one.

---

### Q: Compare Deployment, StatefulSet, and DaemonSet. Give me a concrete case where picking the wrong one bites you.

**Difficulty:** Medium · **Tags:** `workloads`

**Deployment** manages a ReplicaSet of interchangeable, stateless Pods — any replica
serves any request, Pods are fungible, rollouts are unordered and parallel-ish
(`maxSurge`/`maxUnavailable`). **StatefulSet** gives each Pod a stable ordinal identity
(`app-0`, `app-1`), stable per-Pod storage (its own PVC that survives rescheduling), and
ordered, one-at-a-time rollout and scaling, plus stable DNS via a headless Service.
**DaemonSet** runs exactly one Pod per matching node and automatically covers new nodes
— for node-level agents (CNI, log shippers, node-exporter, CSI node plugins).

Concrete failure: running a clustered database (Kafka, ZooKeeper, Postgres with
replicas) as a **Deployment**. Pods share no stable identity or storage, so on reschedule
a broker comes back with a new name and an empty/other volume, breaking quorum and
replication. Conversely, forcing a stateless API onto a StatefulSet buys you slow
ordered rollouts and PVC overhead for nothing. The framing: choose by whether
*identity and storage must be stable* (StatefulSet), *every node needs a copy*
(DaemonSet), or neither (Deployment — the default you should justify moving away from).

---

### Q: A junior asks you the difference between a Pod and a Deployment, and why we never just create Pods in production. What do you tell them?

**Difficulty:** Easy · **Tags:** `workloads`

A **Pod** is the smallest schedulable unit — one or more containers sharing a network
namespace (same IP/localhost) and volumes. It is **mortal and not self-healing**: if the
node dies or the Pod is evicted, nothing recreates it, and it keeps the same identity
only until it's gone.

A **Deployment** is a controller that owns a ReplicaSet, which owns Pods. It continuously
reconciles: keeps the desired replica count, replaces failed Pods, and performs rolling
updates and rollbacks by managing old and new ReplicaSets. So in production you declare a
Deployment (or StatefulSet/DaemonSet/Job as appropriate) and let the controller maintain
the Pods. The framing: you manage *desired state through controllers*, never
imperative one-off Pods, because controllers give you healing, rollout, and auditability.
A bare Pod is only for a throwaway debug shell.

---

### Q: Pods are ephemeral with changing IPs. Explain how a Service gives stable access, and what EndpointSlices have to do with it.

**Difficulty:** Easy · **Tags:** `networking`

A **Service** provides a stable virtual IP and a stable DNS name
(`name.namespace.svc.cluster.local`) that outlive any individual Pod. It selects a set
of Pods by label; the control plane continuously tracks which of those Pods are **Ready**
and records their IPs in **EndpointSlices**. kube-proxy (or a CNI dataplane) uses those
slices to load-balance traffic to the live backends.

EndpointSlices are the scalable successor to the single `Endpoints` object: splitting
endpoints across many smaller objects avoids giant updates when one Pod changes in a
large Service. The practical consequence SREs care about: a Pod that is `Running` but
**not Ready** is pulled out of the EndpointSlice, so it stops receiving traffic — which
is exactly how readiness probes gate rollout and drain. An empty EndpointSlice (selector
mismatch or no Ready Pods) is the first thing to check when a Service returns connection
errors.

---

### Q: I hand you a Deployment YAML and point at a few lines. Which fields must you be able to explain, and which mismatches silently break things?

**Difficulty:** Medium · **Tags:** `workloads` `yaml`

The fields you must know cold: `spec.replicas` (desired count — omit it and HPA/other
controllers interact oddly); `spec.selector.matchLabels` (which Pods this Deployment
owns — **immutable** after creation); `spec.template.metadata.labels` (must be a superset
of the selector, or the API rejects it); `spec.template.spec.containers[]` with `image`
(prefer a digest or immutable tag, never floating `latest`), `ports`, `env`/`envFrom`,
and `resources.requests|limits`; probes (`readinessProbe`/`livenessProbe`/`startupProbe`);
and `strategy` (`RollingUpdate` with `maxSurge`/`maxUnavailable`).

The silent breakers: selector not matching template labels (orphaned Pods or a rejected
apply); `latest` tag so a "no-op" apply pulls a changed image; no resource requests so
the scheduler can't place well and HPA has no CPU baseline; `maxUnavailable` too high so
a rollout drops capacity under load. The answer: I read a manifest by asking
"what is the contract between selector, template, and strategy, and what happens on the
*next* rollout," not by reciting field names.

---

### Q: Write a Dockerfile that runs a Python service, and justify every line like you're in a review.

**Difficulty:** Easy · **Tags:** `docker` `containers`

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN useradd -m app && chown -R app /app
USER app
EXPOSE 8000
CMD ["python", "main.py"]
```

`-slim` keeps the image small (less attack surface, faster pulls) without the breakage
of `alpine`'s musl for many Python wheels. Copying `requirements.txt` *before* the
source means the expensive `pip install` layer is cached and only re-runs when deps
change — ordering layers by change-frequency is the main lever for build speed.
`--no-cache-dir` avoids shipping pip's cache. Running as a **non-root** `USER` is the
line reviewers look for — it's the baseline for Pod Security `restricted`. `CMD` in
**exec form** (JSON array) so the process is PID 1 and receives SIGTERM directly for
graceful shutdown; shell form would swallow signals. The additions I'd mention:
a multi-stage build to drop build tools, a pinned base digest, and a healthcheck handled
by the Pod's readiness probe rather than Docker's.

---

### Q: What is etcd's role, what are the consequences of it going unhealthy, and explain Raft well enough that I believe you've operated it.

**Difficulty:** Hard · **Tags:** `architecture` `consensus`

**etcd** is the cluster's consistent, watchable key-value store — the single source of
truth for every API object. Only the API server talks to it. If etcd is slow, *every*
write stalls and controllers fall behind; if it loses quorum, the control plane goes
read-only/unavailable even though running Pods keep serving (the data plane survives a
control-plane outage, which is a key design property).

etcd uses **Raft** for consensus. One member is **leader** and takes all writes; it
appends each entry to its log and replicates to followers. An entry **commits** once a
**majority (quorum)** has persisted it, then it's applied to the state machine. On leader
loss, followers whose election timeout fires become candidates, bump the **term**, and
request votes; a candidate winning a majority becomes leader. This is why you run an
**odd** number of members (3 tolerates 1 failure, 5 tolerates 2) — quorum is
`floor(n/2)+1`, and an even count buys no extra fault tolerance while raising the quorum
cost. Operator-level reality: etcd is disk-latency sensitive (fsync on every commit), so
put it on fast disks, watch `fsync`/`backend commit` p99, keep the DB under its size
quota, and take/validate regular snapshots — a cluster with no tested etcd restore has
no disaster recovery.

---

### Q: An interviewer asks "do you have Kubernetes experience?" but your company used an in-house orchestrator. How do you answer so you don't sound junior?

**Difficulty:** Easy · **Tags:** `behavioral`

The weak answer — "I wrote YAML and ran `kubectl apply`" — signals you only touched the
surface. Answer at the level of *what orchestration solves* and map your in-house system
onto it: scheduling workloads onto a fleet, self-healing via reconcile loops, declarative
desired state, rolling updates, service discovery and load balancing, resource isolation,
and secrets/config distribution. Say "we didn't run upstream K8s, but our platform had
the equivalent of a scheduler, a ReplicaSet-style controller, and a service mesh;
here's a trade-off we debated and how it compares to how K8s does it."

That reframes the question from "which CLI do you know" to "do you understand distributed
systems operations," which is what a staff interview is actually probing. Then show you
can ramp: name the concrete K8s primitives you've since learned and a non-trivial one
(PDBs, topology spread, admission control) to prove depth, not buzzwords.

---

### Q: How does the scheduler decide where a Pod goes? Take me from a newly created Pod to a bound one, including how you'd influence or debug it.

**Difficulty:** Advanced · **Tags:** `scheduling` `architecture`

The scheduler watches for Pods with no `nodeName` and runs a two-phase cycle per Pod.
**Filtering (predicates)**: eliminate nodes that *cannot* run it — insufficient
allocatable CPU/memory, taints without a matching toleration, unsatisfied
`nodeSelector`/`nodeAffinity`, `podAffinity`/`antiAffinity` conflicts, volume
zone/topology constraints, port conflicts. **Scoring (priorities)**: rank the survivors —
least-requested or balanced resource allocation, affinity preferences, pod topology
spread, image locality — and bind the Pod to the highest scorer by writing `nodeName`.
If no node survives filtering, the Pod stays `Pending` with an "unschedulable" event.

Influence it with requests (the scheduler reserves against requests, not usage),
`nodeAffinity`/anti-affinity, taints/tolerations for dedicated pools,
`topologySpreadConstraints` for HA across zones, and `priorityClass` + **preemption**
(a high-priority Pod can evict lower-priority ones to fit). Debug `Pending` with
`kubectl describe pod` and read the scheduler's per-predicate reason. The
nuance: the scheduler only decides *placement*, it never creates capacity — pairing with
Cluster Autoscaler/Karpenter is what turns "unschedulable" into new nodes. For special
cases you can run a second scheduler or a scheduling-framework plugin.

---

### Q: Explain the operator pattern and CRDs. When is writing an operator the right call versus over-engineering?

**Difficulty:** Advanced · **Tags:** `architecture` `extensibility`

A **CustomResourceDefinition** registers a new API type so the cluster stores and serves
your own `kind` (e.g. `PostgresCluster`) with the same RBAC, watch, and `kubectl`
machinery as built-ins. An **operator** is a custom controller that watches that resource
and runs a reconcile loop driving reality toward the spec — encoding the *operational*
knowledge a human runbook would otherwise hold: provisioning, scaling, backups, failover,
version upgrades.

It's the right call when managing a stateful or complex system whose day-2 operations are
genuinely domain-specific and repetitive — the operator turns "page an engineer to fail
over the DB" into automated reconciliation. It's over-engineering when a Helm chart or a
couple of built-in controllers would do: you now own a controller's correctness
(idempotency, handling partial failure, avoiding hot reconcile loops, status/conditions,
finalizers for cleanup), which is real, ongoing software. The heuristic: reach for
an operator when the thing you're automating is a *control loop* (continuously enforce and
remediate), not a one-time install — otherwise prefer Helm/Kustomize and existing
controllers.

---

### Q: Explain owner references, cascading garbage collection, and finalizers. Then tell me why an object is stuck in `Terminating`.

**Difficulty:** Advanced · **Tags:** `architecture` `lifecycle`

Objects form a tree via **ownerReferences**: a Pod references its ReplicaSet, which
references its Deployment. The **garbage collector** uses this to cascade deletes. When
you delete a parent, propagation policy decides the rest: **Background** (delete parent
now, children async — the default for most), **Foreground** (parent stays in
`Terminating` until children are gone, with a `foregroundDeletion` finalizer), or
**Orphan** (children survive, ownerRef removed).

A **finalizer** is a string key in `metadata.finalizers` that *blocks* actual deletion:
the API server sets `deletionTimestamp` and keeps the object in `Terminating` until a
controller does its cleanup (deprovision a cloud load balancer, drain external state) and
then removes its finalizer; only when the list is empty is the object purged. So an object
stuck in `Terminating` almost always means a finalizer isn't being cleared — the
responsible controller is down, crashed, or deleted — or a foreground cascade is waiting
on a child that itself won't delete. The debug path: `kubectl get -o yaml` and look at
`metadata.finalizers` and `deletionTimestamp`; fix the controller so it completes cleanup.
Force-removing a finalizer unblocks the delete but **leaks** whatever external resource it
was protecting, so it's a last resort, not the fix.

---

### Q: What are Namespaces really for, and how do ResourceQuota and LimitRange prevent one team from taking down a shared cluster?

**Difficulty:** Intermediate · **Tags:** `multi-tenancy`

**Namespaces** partition one cluster into virtual scopes for names, RBAC, quotas, and
network policy — the unit of soft multi-tenancy. The honest caveat: a namespace is **not
a hard security boundary** by itself (shared kernel, shared nodes), so untrusted
multi-tenancy needs more (separate node pools, strict NetworkPolicy, Pod Security,
sometimes separate clusters).

**ResourceQuota** caps aggregate consumption *per namespace* — total CPU/memory
requests and limits, and counts of objects (Pods, Services, PVCs). It stops one team
from scheduling until the whole cluster is starved. A subtle consequence: once a CPU/mem
quota is set, every Pod in that namespace **must** declare requests/limits or it's
rejected — which is where **LimitRange** comes in: it sets per-container defaults and
min/max, so Pods without explicit values still get sane ones and nobody can request an
absurd amount. The framing: Quota is the namespace-wide budget; LimitRange is the
per-object guardrail; together they make a shared cluster behave like it has fair
scheduling, and without them a single misconfigured Deployment with no limits can evict
everyone else under node pressure.

---

### Q: Labels vs annotations — where's the line, and what goes wrong if you blur it?

**Difficulty:** Intermediate · **Tags:** `metadata`

Both are key/value metadata on objects, but they serve different masters. **Labels** are
for *identification and selection*: Service selectors, Deployment→Pod ownership,
`kubectl get -l`, affinity rules, and monitoring groupings all match on labels. They're
indexed and meant to be small, low-cardinality, and queryable. **Annotations** are
arbitrary, possibly large, non-selectable data for tools and humans: build/commit info,
`last-applied-configuration`, ingress-controller config, change-cause.

Blur the line and you get real problems: putting a high-cardinality or frequently
changing value in a **label** (a timestamp, a full URL, a hash per deploy) bloats the
index and can break selectors or monitoring cardinality; conversely, stuffing data you
need to *select on* into an **annotation** means you can't target it with a selector and
have to filter client-side. The rule of thumb: if something decides *which objects
an operation applies to*, it's a label; if it's metadata you only read, it's an
annotation.

---

### Q: Imperative vs declarative kubectl, and walk me through safely rolling back a bad Deployment in production.

**Difficulty:** Intermediate · **Tags:** `kubectl` `operations`

**Imperative** commands state the action — `kubectl create`, `scale`, `set image`,
`delete`. Fast for interactive fixes, but they drift from any source of truth and aren't
reproducible or reviewable. **Declarative** — `kubectl apply -f` (or GitOps via Argo
CD/Flux) — you commit the desired manifest and the system converges to it; this is what
you run production on, because the repo is the audit log and PRs are the change control.

Rollback: first confirm the new version is the cause and capture evidence (`kubectl
rollout status`, logs, the failing Pod spec) before you change anything. Then
`kubectl rollout history deploy/x` to see revisions and `kubectl rollout undo deploy/x
--to-revision=N` to flip back — K8s retains old ReplicaSets (`revisionHistoryLimit`), so
undo just scales the previous ReplicaSet up and the bad one down via the normal rolling
strategy. In a GitOps world the "real" rollback is reverting the git commit so the
cluster doesn't drift back on the next sync. The caveats: rollback is only clean
if the change was backward-compatible — a schema migration or a consumed-then-removed API
can't be undone by scaling Pods, so you need forward-fix or expand/contract migration
discipline, and that's the answer that shows you've actually been on call.

---

### Q: What is Helm, what does it actually buy you, and when would you reach for Kustomize instead?

**Difficulty:** Intermediate · **Tags:** `packaging`

Helm is the K8s package manager. A **chart** is a bundle of templated manifests plus a
`values.yaml` of defaults; installing it creates a named **release** that Helm tracks, so
you can `upgrade`, `rollback`, and `uninstall` a whole application as one unit, and share
charts via repos. It solves two things: *templating/reuse* (one chart rendered per
environment by overriding values) and *lifecycle management* (versioned releases with
rollback) versus hand-maintaining and hand-applying dozens of raw YAMLs.

The trade-off: Helm's Go templating over YAML gets hard to read and debug as charts grow
(whitespace, conditionals, `tpl` gymnastics), and the rendered output isn't obvious from
the source. **Kustomize** (built into `kubectl -k`) takes the opposite approach —
template-free base manifests plus overlays that patch them per environment — which many
teams find cleaner for *their own* apps where they control the YAML. The take: use
Helm to consume third-party/off-the-shelf software (where versioned releases and a
community chart are the point), and Kustomize (or Helm+Kustomize together, or a GitOps
tool rendering either) for your own services; the deciding factor is who owns the
manifests and whether you need packaged, versioned distribution.
