# Pods & Workloads

### Q: Explain liveness, readiness, and startup probes — and a real outage from misconfiguring one.

**Difficulty:** Medium · **Tags:** `probes` `workloads`

**Short answer:** Readiness gates *traffic*, liveness triggers *restarts*, startup
protects *slow boots*. Mixing them up amplifies incidents.

| Probe | Question it answers | On failure |
|-------|--------------------|------------|
| **readiness** | "Ready for traffic *now*?" | removed from Service endpoints — **no restart** |
| **liveness** | "Is it wedged?" | **kills + restarts** the container |
| **startup** | "Finished booting?" | holds off liveness/readiness until it passes |

**The classic outage — liveness probe hitting a dependency:**
- Load rises → app slows → liveness times out → kubelet **restarts** the container.
- Restart drops in-flight work → slower → next probe also fails → **restart storm**.
- A latency blip becomes a full outage, self-inflicted by the probe.

**Rules:**
- Liveness checks **only local liveness** (event loop responsive) — never a downstream.
- Readiness *may* check dependencies (failure just removes traffic, reversible).
- Slow boot → **startup probe**, not a loosened liveness timeout.

```yaml
startupProbe:   { httpGet: {path: /healthz, port: 8080}, failureThreshold: 30, periodSeconds: 5 }  # ~150s budget
readinessProbe: { httpGet: {path: /ready,   port: 8080}, periodSeconds: 5 }
livenessProbe:  { httpGet: {path: /healthz, port: 8080}, periodSeconds: 10, failureThreshold: 3 }
```

---

### Q: Requests vs limits — what each controls, the QoS classes, and what happens at the limit.

**Difficulty:** Easy · **Tags:** `resources` `scheduling`

**Short answer:** Requests = what the **scheduler reserves**; limits = **runtime caps**.
Memory and CPU fail in **opposite** ways at the limit.

**At the limit:**
- **Memory** over limit → **OOMKilled** (hard, exit 137, no grace).
- **CPU** over limit → **throttled** (slowed, *not* killed).

**QoS classes** (derived from how you set requests/limits) drive eviction + OOM score:

| Class | Condition | Evicted |
|-------|-----------|---------|
| **Guaranteed** | requests == limits (cpu+mem, all containers) | last |
| **Burstable** | some requests, not all equal | middle |
| **BestEffort** | nothing set | first |

```yaml
resources:                 # requests == limits  →  Guaranteed
  requests: { cpu: "500m", memory: "512Mi" }
  limits:   { cpu: "500m", memory: "512Mi" }
```

**Staff nuance:**
- CPU limits are contentious — tight CPU limits throttle latency-sensitive services
  *even on an idle node*. Common pattern: set **CPU requests, no CPU limit**; set
  **memory requests == limits** for predictability.
- Requests are a *scheduling* contract; limits a *runtime* one. Over-request wastes
  money + starves the scheduler; under-request invites noisy-neighbor eviction.

---

### Q: Node affinity, taints, tolerations — and how to build a dedicated GPU pool.

**Difficulty:** Medium · **Tags:** `scheduling`

**Short answer:** Affinity = pod *chooses* nodes (attraction). Taint = node *rejects*
pods (repulsion) unless they carry a matching toleration. You usually need **both**.

**Why both:**
- Affinity alone → doesn't stop *other* pods landing on your special nodes.
- Toleration alone → allows the pod on, but doesn't *steer* it there.

**GPU pool recipe:**
```bash
kubectl taint nodes <n> nvidia.com/gpu=present:NoSchedule   # repel everyone else
kubectl label nodes <n> accelerator=a100                    # target for affinity
```
- GPU pods: toleration for the taint **+** required `nodeAffinity` on the label **+** a
  `nvidia.com/gpu` resource request.

**Gotcha:** `NoExecute` taints also **evict running** pods that don't tolerate them
(with optional `tolerationSeconds`) — that's exactly how the node controller drains a
`NotReady` node.

---

### Q: QoS classes and the exact kubelet eviction order under node pressure.

**Difficulty:** Advanced · **Tags:** `resources` `scheduling`

**Short answer:** QoS is *derived*, not declared, and sets eviction priority.

**Eviction order under node pressure** (memory/disk/PID):
1. **BestEffort** first.
2. **Burstable exceeding its requests** (ranked by overage × priority).
3. **Guaranteed** last (only for system-level pressure).

**Independent of node pressure:** a container over its **memory limit** is OOMKilled
immediately, regardless of QoS.

**Key distinctions:**
- Eviction is **graceful** (SIGTERM, honors grace period); OOMKill is **not**.
- `PriorityClass` further shifts eviction order — critical system pods survive.
- → give stateful/latency-critical pods **Guaranteed** QoS + priority, so a batch job's
  spike evicts the batch job, not your database.

---

### Q: Deployment update strategies, and how canary / blue-green fit on top.

**Difficulty:** Intermediate · **Tags:** `deployments` `rollout`

**Native strategies:**
- **RollingUpdate** (default) — incremental, bounded by `maxSurge` / `maxUnavailable`.
  Zero-downtime *if* readiness is honest and the app is backward-compatible.
- **Recreate** — kill all old, then start new. Downtime, but correct when two versions
  can't coexist (incompatible schema, exclusive lock).

**Built on top (not first-class — you need a traffic layer):**
- **Canary** — small % to new version, watch metrics, widen. Crude: two Deployments +
  replica ratio behind one Service. Real: mesh/ingress weight + automated analysis
  (Argo Rollouts / Flagger) that promotes or aborts on SLO signals.
- **Blue-green** — run full new (green) beside old (blue), flip the Service selector,
  keep blue for instant rollback.

**Framing:** rolling update = *how pods are replaced*; canary/blue-green = *how traffic
shifts and how fast you can abort* — the latter is where the reliability win is.

---

### Q: ConfigMap vs Secret — and if Secrets aren't encrypted, how do you secure them?

**Difficulty:** Intermediate · **Tags:** `config` `security`

**Short answer:** Both inject config as env/files. ConfigMap = non-sensitive, Secret =
sensitive — but a Secret is only **base64-encoded, not encrypted**. base64 ≠ security.

**Secure in layers:**
- **Encryption at rest** — API-server `EncryptionConfiguration` + KMS provider, so etcd
  holds ciphertext.
- **RBAC** — `get`/`list` on secrets is high-value; scope it tight. Anyone who can
  `exec` into the pod or read its SA token reads mounted secrets too.
- **External store** — Vault / cloud SM via External Secrets Operator or CSI driver;
  secrets short-lived, not parked in etcd.
- **Hygiene** — never bake into images or commit in manifests.

**Rotation gotcha:** file-mounted secrets update in place (eventually) → app can reload;
**env-var secrets are fixed at pod start** → need a restart to rotate.

---

### Q: Init containers vs sidecars — and what changed with native sidecar support.

**Difficulty:** Intermediate · **Tags:** `workloads`

| | Runs | Purpose |
|--|------|---------|
| **init container** | to completion, in order, *before* app | wait-for-dep, migration, fetch config |
| **sidecar** | *alongside* app, whole life | proxy, log shipper, metrics adapter |

**The old problem** (sidecar as a plain `containers[]` entry):
- No guarantee the sidecar was ready **before** the app.
- Sidecar didn't stop cleanly on shutdown → mesh proxy dying first stranded outbound
  calls; a never-exiting sidecar **blocked Job completion**.

**Native sidecar (1.29 GA):** an **init container with `restartPolicy: Always`** —
starts before main, terminates after it, and lets Jobs complete. Use it when ordering
with the main container matters (mesh, credential refreshers); plain init containers
remain for one-shot preconditions.

---

### Q: Multi-container Pod patterns, and how to decide same-Pod vs separate-Pod.

**Difficulty:** Intermediate · **Tags:** `workloads` `patterns`

**Patterns** (all share the Pod's network + volumes):
- **Sidecar** — augments the main container (mesh proxy, log tailer).
- **Ambassador** — proxies the app's *outbound* connections (localhost → sharded DB).
- **Adapter** — transforms the app's *output* for a consumer (logs → Prometheus format).

**Decision rule:** same Pod **only** if they must be co-scheduled + share
lifecycle/network/volumes. Scale/update independently or live on different nodes →
**separate Pods** behind a Service.

**Smell test:** wanting to scale one container but not the other means it was never a
sidecar — it's a separate workload you've coupled, and you pay at every rollout.

---

### Q: Job vs CronJob — the knobs that decide correctness under failure.

**Difficulty:** Intermediate · **Tags:** `workloads`

**Job knobs:**
- `completions` / `parallelism` — how many successes, how many at once.
- `backoffLimit` — retries before Failed (too high hides a broken job).
- `activeDeadlineSeconds` — hard wall-clock timeout for a hung job.
- `restartPolicy` — `OnFailure` (restart in place) vs `Never` (new pod per attempt, clean logs).

**CronJob knobs:**
- `concurrencyPolicy` — **Allow** (overlap, idempotent jobs), **Forbid** (skip if prior
  running), **Replace** (kill old, start new). ← most-missed.
- `startingDeadlineSeconds` — how late a missed run may still fire.
- `successfulJobsHistoryLimit` / `failedJobsHistoryLimit` — stop Job objects piling up.

**Gotcha:** CronJobs are **at-least-once-ish, not exactly-once** — the job itself must
be **idempotent**. Relying on the scheduler for correctness is the bug.

---

### Q: emptyDir vs hostPath vs PVC — when each, and the hostPath trap.

**Difficulty:** Intermediate · **Tags:** `storage` `workloads`

| Volume | Lifetime | Use for |
|--------|----------|---------|
| **emptyDir** | dies with the Pod | scratch, cache, share between containers (`medium: Memory` for RAM) |
| **hostPath** | node's filesystem | node agents only (CNI/CSI/log collectors) |
| **PVC** | survives rescheduling | any data that must outlive the Pod |

**The hostPath trap:**
- **Security** — a window into the host (`/var/run/docker.sock` → node escape).
- **Reliability** — data gone if the Pod lands on another node; no tenant isolation.
- → treat it as a privileged, node-pinned escape hatch; gate it with Pod Security.

---

### Q: What happens when a Pod is deleted — grace period, preStop, SIGTERM — and why a short grace period drops requests.

**Difficulty:** Intermediate · **Tags:** `lifecycle`

**Sequence on delete:**
1. `deletionTimestamp` set → Pod `Terminating`.
2. **In parallel:** removed from EndpointSlices (new traffic stops — *eventually*) **and**
   kubelet runs **preStop** hook → sends **SIGTERM** to PID 1.
3. App drains (stop accepting, finish in-flight).
4. After `terminationGracePeriodSeconds` (default 30) → **SIGKILL**.

**Two causes of dropped requests:**
- Grace period **shorter than longest in-flight request** → SIGKILL mid-request.
- **Endpoint-removal vs SIGTERM race** — endpoint updates propagate async, so a load
  balancer may send new requests to a pod that *already* got SIGTERM → errors at the
  *start* of termination.

**Fix:** a **preStop `sleep`** (few seconds) lets endpoint removal propagate while the
app still serves, + grace period > p99 request time + a real SIGTERM handler. Graceful
shutdown is a distributed-systems **race**, not just "handle the signal."
