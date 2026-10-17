# Pods & Workloads

### Q: Explain liveness, readiness, and startup probes — and give me a real outage caused by misconfiguring one.

**Difficulty:** Medium · **Tags:** `probes` `workloads`

The three answer different questions. **Readiness** = "should this Pod receive traffic
right now?" — failing it pulls the Pod out of Service EndpointSlices but does **not**
restart it; it's how you gate rollout and drain. **Liveness** = "is this container
wedged and in need of a restart?" — failing it kills and restarts the container.
**Startup** = "has the app finished its slow boot?" — while it's still failing, liveness
and readiness are suppressed, protecting slow starters (JVM warmup, large cache load)
from being killed before they're up.

The classic outage: a **liveness probe that hits a dependency** (or is too aggressive).
Under load the app slows, the liveness probe times out, the kubelet restarts the
container — which drops in-flight work and makes things slower, so the next probe also
fails, and the whole Deployment enters a restart storm that turns a latency blip into a
full outage. The fix and the lesson: liveness should check only *local* liveness (is the
event loop responsive), never downstream health; readiness can check dependencies because
its failure just removes traffic; and slow starts belong in a startup probe, not in a
loosened liveness timeout. The framing: liveness restarts, readiness routes — mix
them up and you amplify incidents instead of containing them.

```yaml
startupProbe:   { httpGet: {path: /healthz, port: 8080}, failureThreshold: 30, periodSeconds: 5 }  # up to ~150s to boot
readinessProbe: { httpGet: {path: /ready,   port: 8080}, periodSeconds: 5 }                        # gates traffic, no restart
livenessProbe:  { httpGet: {path: /healthz, port: 8080}, periodSeconds: 10, failureThreshold: 3 }  # local liveness only
```

---

### Q: Requests vs limits — what does each actually control, what are the QoS classes, and what happens when a container exceeds each?

**Difficulty:** Easy · **Tags:** `resources` `scheduling`

**Requests** are what the scheduler reserves — placement and bin-packing decisions are
made against requests, not real usage, and they're the baseline HPA computes utilization
against. **Limits** are enforced caps at runtime by the kernel. The two resources behave
very differently at the limit: exceeding a **memory** limit gets the container
**OOMKilled** (hard, no grace); exceeding a **CPU** limit causes **throttling** (the
cgroup is given fewer scheduler slices — the app gets slow, not killed).

QoS falls out of how you set them: **Guaranteed** (every container sets
requests == limits for both cpu and mem) is evicted last and least likely to be OOM-
scored; **Burstable** (some requests set, not all equal to limits) can use spare capacity
but is evicted before Guaranteed under node pressure; **BestEffort** (nothing set) is
first to go. The nuance: CPU limits are controversial — tight CPU limits throttle
latency-sensitive services even when the node is idle, so many teams set CPU *requests*
but no CPU *limit* and rely on requests for fairness, while always setting memory
requests == limits to make behavior predictable. Over-requesting wastes money and starves
the scheduler; under-requesting invites noisy-neighbor and eviction. The answer that lands
is understanding that requests are a *scheduling* contract and limits are a *runtime*
one, and that memory and CPU fail in opposite ways.

```yaml
resources:                 # requests == limits for both  ->  QoS: Guaranteed (evicted last)
  requests: { cpu: "500m", memory: "512Mi" }
  limits:   { cpu: "500m", memory: "512Mi" }
# only memory set equal, no cpu limit -> Burstable; nothing set -> BestEffort (evicted first)
```

---

### Q: Explain node affinity, taints, and tolerations, and how you'd use them together to build a dedicated GPU node pool.

**Difficulty:** Medium · **Tags:** `scheduling`

They're two complementary mechanisms. **nodeAffinity** is the Pod expressing a
*preference or requirement* to land on nodes with certain labels
(`requiredDuringScheduling...` is hard, `preferred...` is soft). **Taints** are the
*node repelling* Pods: a taint (`key=value:NoSchedule|PreferNoSchedule|NoExecute`) keeps
Pods off unless they carry a matching **toleration**. Affinity is attraction; taint is
rejection — you usually need both, because affinity alone doesn't stop *other* Pods from
landing on your special nodes, and a toleration alone doesn't *steer* your Pods toward
them.

Dedicated GPU pool, done right: label the GPU nodes (`accelerator=nvidia-a100`) **and**
taint them (`nvidia.com/gpu=present:NoSchedule`). GPU workloads then get a toleration for
that taint (so they're allowed on) *and* a required nodeAffinity for the label (so they
actually go there) — plus a `nvidia.com/gpu` resource request so the scheduler counts
them. The taint keeps random CPU Pods off the expensive hardware; the affinity + resource
request pins the GPU Pods onto it. The addition: `NoExecute` taints also *evict*
already-running Pods that don't tolerate them (with an optional `tolerationSeconds`),
which is exactly how the node controller drains a `NotReady` node — so taints are both a
scheduling and an eviction tool.

---

### Q: Walk me through the QoS classes and the exact order the kubelet evicts Pods under node pressure.

**Difficulty:** Advanced · **Tags:** `resources` `scheduling`

A Pod's QoS is derived, not declared. **Guaranteed**: every container sets requests and
limits equal for both CPU and memory. **Burstable**: at least one request is set but it's
not fully Guaranteed. **BestEffort**: no requests or limits anywhere. This class drives
both the Linux OOM score and the kubelet's eviction ranking.

When a node hits an eviction threshold (memory, disk, PID pressure), the kubelet reclaims
by evicting Pods in order: **BestEffort first**, then **Burstable Pods that are exceeding
their requests** (ranked by how far over request they are, weighted by priority), and
**Guaranteed last** — Guaranteed Pods are only evicted for system-level pressure, not for
exceeding their own (equal) limits, since they can't. Independently, if a single
container blows its **memory limit**, it's OOMKilled immediately regardless of node
pressure. The points: eviction is *graceful* (SIGTERM, honors grace period) while
OOMKill is not; `PriorityClass` modifies eviction ordering so critical system Pods
survive; and this is why you give latency-critical or stateful Pods Guaranteed QoS and
appropriate priority — so a batch job's memory spike evicts the batch job, not your
database.

---

### Q: Explain the Deployment update strategies, and how canary and blue-green deployments fit on top of what K8s gives you natively.

**Difficulty:** Intermediate · **Tags:** `deployments` `rollout`

Natively a Deployment offers two strategies. **RollingUpdate** (default) replaces Pods
incrementally, bounded by `maxSurge` (how many extra above desired you'll create) and
`maxUnavailable` (how many below desired you'll tolerate) — zero-downtime if readiness
probes are honest and the app is backward-compatible. **Recreate** tears down all old
Pods before starting new ones — causes downtime, but it's correct when two versions
genuinely can't coexist (incompatible schema, exclusive locks).

Canary and blue-green aren't first-class Deployment strategies — you build them.
**Canary**: send a small fraction of traffic to the new version and watch metrics before
widening. Crudely you can do it with two Deployments and replica ratios behind one
Service, but real canaries use a mesh or ingress that splits by weight (and ideally an
automated analysis tool like Argo Rollouts/Flagger that promotes or aborts on SLO
signals). **Blue-green**: run the full new version (green) alongside the old (blue) and
flip the Service selector/ingress to green once validated, keeping blue ready for instant
rollback. The framing: rolling update is about *how Pods are replaced*; canary and
blue-green are about *how traffic is shifted and how fast you can abort* — the latter
needs a traffic-control layer and a metrics-driven promotion gate, which is where the real
reliability win is.

---

### Q: ConfigMap vs Secret — and if I told you Secrets aren't encrypted by default, how would you actually secure them?

**Difficulty:** Intermediate · **Tags:** `config` `security`

Both inject configuration into Pods as environment variables or mounted files, and both
decouple config from the image. The intent differs: **ConfigMap** for non-sensitive
config, **Secret** for sensitive values. But a Secret is only **base64-encoded**, not
encrypted — base64 is encoding, not security — so by default a Secret sitting in etcd and
visible to anyone with `get secret` RBAC is effectively plaintext.

Securing them, in layers: enable **encryption-at-rest** in the API server
(`EncryptionConfiguration` backed by a KMS provider, so etcd holds ciphertext, not
identity-encoded data); lock down **RBAC** so `get`/`list` on secrets is tightly scoped
(and remember that a Pod's ServiceAccount token and anyone who can `exec` into the Pod can
read mounted secrets); prefer an **external secret manager** (Vault, cloud secret
managers) surfaced via the External Secrets Operator or the Secrets Store CSI driver, so
secrets are short-lived and not permanently parked in etcd; and never bake secrets into
images or commit them to manifests. Operational nuance: secrets mounted as files update
in place (eventually) when the Secret changes, while env-var secrets are fixed at Pod
start — so rotation strategy depends on how you consume them. The answer names the
threat model (who can read etcd, who has RBAC, who can exec) rather than just saying "use
a Secret."

---

### Q: Init containers vs sidecars — and what changed with native sidecar support?

**Difficulty:** Intermediate · **Tags:** `workloads`

**Init containers** run to completion, sequentially, *before* any app container starts —
for ordered setup: wait for a dependency to be reachable, run a schema migration, fetch
config or certs into a shared `emptyDir`. If an init container fails, the Pod keeps
retrying it and the app never starts, which is intentional (don't start the app until
preconditions hold). A **sidecar** runs *alongside* the main container for the Pod's whole
life — a proxy (mesh), log shipper, or metrics adapter sharing the Pod's network and
volumes.

Historically sidecars were just extra containers in `spec.containers`, which created two
problems: no ordering guarantee that the sidecar was ready before the app, and sidecars
didn't stop cleanly on Pod termination (a mesh proxy dying first could strand the app's
outbound calls; a sidecar never exiting could block Job completion). Since 1.28+/1.29 GA,
a **native sidecar** is an **init container with `restartPolicy: Always`** — it starts
before the main containers (and stays running), and it's terminated *after* them on
shutdown, fixing both the startup-order and teardown-order problems, and letting Jobs
complete even with a long-lived sidecar. The point: reach for native sidecars when
ordering with the main container matters (meshes, credential refreshers); plain init
containers remain the tool for one-shot preconditions.

---

### Q: What are the common multi-container Pod patterns, and how do you decide something belongs in the same Pod versus its own Pod?

**Difficulty:** Intermediate · **Tags:** `workloads` `patterns`

The three named patterns: **sidecar** (augments the main container — a mesh proxy, a log
tailer, a config reloader), **ambassador** (a local proxy that brokers the app's
*outbound* connections — e.g. a connection-pooling proxy to a sharded database so the app
just talks to localhost), and **adapter** (transforms the app's *output* into what a
consumer expects — e.g. reformatting logs or exposing app internals as Prometheus
metrics). All containers in a Pod share the network namespace (localhost, same IP) and can
share volumes.

The decision rule: put containers in the **same Pod only when they must be co-scheduled on
the same node and share lifecycle/network/volumes** — they scale together, fail together,
and can't be placed independently. If they can scale independently, be updated
independently, or live on different nodes, they belong in **separate Pods** connected by a
Service. The smell test: if you find yourself wanting to scale one container but
not the other in a Pod, it was never a sidecar — it's a separate workload you've
accidentally coupled, and you'll pay for it at every rollout.

---

### Q: Job vs CronJob — explain the knobs that decide correctness under failure.

**Difficulty:** Intermediate · **Tags:** `workloads`

A **Job** runs Pods until a defined number succeed; a **CronJob** creates Jobs on a cron
schedule. The knobs that actually matter for correctness: `completions` and `parallelism`
(how many successful runs total, and how many at once — with a work queue you set
parallelism and let Pods drain the queue); `backoffLimit` (how many retries before the Job
is marked Failed — too high hides a broken job, too low gives up on transient errors);
`activeDeadlineSeconds` (hard wall-clock timeout so a hung Job doesn't run forever); and
the Pod `restartPolicy` (`OnFailure` restarts the container in place, `Never` creates a
new Pod per attempt — which you want for clean per-attempt logs).

For CronJob specifically: `concurrencyPolicy` is the one people get wrong — **Allow**
(overlapping runs, fine for idempotent jobs), **Forbid** (skip the new run if the prior is
still going, for non-reentrant jobs), **Replace** (kill the old, start the new).
`startingDeadlineSeconds` bounds how late a missed run (controller was down, node
pressure) may still fire, and `successfulJobsHistoryLimit`/`failedJobsHistoryLimit` keep
old Job objects from piling up. The framing: the interesting question is always
*"what happens when a run overlaps, times out, or the controller was down during the
scheduled time"* — CronJobs give at-least-once-ish semantics, not exactly-once, so the job
itself must be idempotent; relying on the scheduler for correctness is the bug.

---

### Q: emptyDir vs hostPath vs a PVC — when each, and what's the trap with hostPath?

**Difficulty:** Intermediate · **Tags:** `storage` `workloads`

**emptyDir** is scratch space created when the Pod is assigned to a node and **deleted
when the Pod leaves** — perfect for caches, scratch files, or sharing data between
containers in the same Pod. It can even be memory-backed (`medium: Memory`) for speed.
**hostPath** mounts a path from the *node's* filesystem into the Pod. **A PVC** is a claim
on real persistent storage (via a PV/StorageClass) that survives Pod rescheduling — the
only option for data that must outlive the Pod.

The hostPath trap: it binds the Pod to one node's local filesystem and gives it a window
into the host. That's a **security risk** (a Pod mounting `/var/run/docker.sock` or host
paths can escalate off the node) and a **portability/reliability risk** (the data is gone
if the Pod lands on a different node, and there's no isolation from other node tenants).
So hostPath is legitimate for node-level agents that genuinely need host access
(DaemonSets reading `/proc`, CNI/CSI plugins, log collectors) and almost never for app
workloads. The answer: for ephemeral intra-Pod data use emptyDir; for persistent
app data always use a PVC; treat hostPath as a privileged, node-pinned escape hatch you
justify, and gate it with Pod Security so random workloads can't use it.

---

### Q: Walk me through exactly what happens when a Pod is deleted — grace period, preStop, SIGTERM — and how a short grace period causes dropped requests.

**Difficulty:** Intermediate · **Tags:** `lifecycle`

On delete, the API server sets a `deletionTimestamp` and the Pod enters `Terminating`.
Two things happen in parallel: the Pod is **removed from Service EndpointSlices** (so new
traffic stops routing to it — eventually, since that propagation to every kube-proxy isn't
instant), and the kubelet begins shutdown — it runs the optional **preStop** hook, then
sends **SIGTERM** to the container's PID 1. The app should catch SIGTERM, stop accepting
new work, and finish in-flight requests. After `terminationGracePeriodSeconds` (default
30), anything still alive gets **SIGKILL**.

The dropped-requests failure has two causes, often together. First, a **grace period
shorter than the app's longest in-flight request** means SIGKILL lands mid-request.
Second, and subtler, is the **race between endpoint removal and SIGTERM**: because
EndpointSlice updates propagate asynchronously, a load balancer may still send new
requests to a Pod that has *already* received SIGTERM and stopped accepting them — so you
get connection errors at the *start* of termination, not the end. The standard fix is a
**preStop `sleep`** (a few seconds) before SIGTERM, letting endpoint removal propagate
while the app still serves, plus a grace period comfortably longer than your p99 request
time and a SIGTERM handler that drains. The point: graceful shutdown is a
distributed-systems race, not just "handle the signal" — the sleep exists precisely
because readiness/endpoint propagation and signal delivery aren't synchronized.
