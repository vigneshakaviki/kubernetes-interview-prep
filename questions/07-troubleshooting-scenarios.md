# Production Troubleshooting Scenarios

The highest-signal part of an SRE/Platform K8s interview. The interviewer isn't testing
whether you can recite a Pod spec — they're testing whether you can reason under pressure
without thrashing. Narrate the *method*, not a list of commands.

## The method (apply it to every scenario)

1. **Protect users first.** Establish blast radius before root cause: severity, error
   rate, what fraction of traffic is affected, what changed recently, and whether a
   reversible mitigation (rollback, traffic shift, feature flag) is available *now*.
2. **Scope the failure.** Compare healthy vs unhealthy along every axis — which Pods,
   nodes, namespaces, zones, versions, request paths. The dimension along which it splits
   *is* the clue.
3. **Compare desired vs observed.** Inspect the workload, Pod conditions, controller
   status, and recent events before you change anything — Kubernetes is a reconcile loop,
   so the gap between spec and status points at the layer that's stuck.
4. **Follow the dependency path.** Deployment → Pod → node → Service/EndpointSlices →
   DNS/NetworkPolicy → storage → external deps. Don't jump layers on a hunch.
5. **Mitigate, verify, prevent.** Prefer reversible actions, confirm *user-facing*
   recovery (not just "the Pod is green"), then name the guardrail that stops a recurrence.

The thread running through all of it: triage the failing object first, read its current
state and recent events, and only then act — preserving evidence (logs, the failing spec)
so you can do a real postmortem.

---

### Q: A Pod has been `Pending` for 20 minutes. Walk me through it without just saying "describe the pod."

**Difficulty:** Medium · **Tags:** `scheduling` `troubleshooting`

`Pending` means one of two things: the scheduler **can't place it**, or it's placed but
the kubelet **can't start it** — and the events tell you which. `kubectl describe pod` and
read the scheduler's per-predicate reasons. If unschedulable, the usual causes:
**requests exceed any node's allocatable** (bin-packing failure — compare the Pod's
requests to node allocatable, remembering system-reserved eats into it); **taints without
a matching toleration**; unsatisfied **nodeSelector/affinity/topology spread**; or an
**unbound PVC** (storage is on the critical path — a zonal disk the scheduler can't match
to a node keeps the Pod Pending). If it's scheduled but not starting, you'll see
image-pull or volume-attach events instead.

Fix the *actual* constraint: correct an over-large request, fix the selector/toleration,
repair the storage provisioner, or add capacity (which, if Cluster Autoscaler is present,
should happen automatically — if it isn't, that's its own bug to chase). The
discipline: **deleting the Pod does nothing** — the controller recreates the identical
spec and it's Pending again; and reflexively adding nodes when the real cause is a typo in
a nodeSelector just burns money. The tell of experience is reading the scheduling
predicate that failed and addressing *that*, not pattern-matching to "add capacity."

---

### Q: A Pod fails to start. There are several reasons that look similar — how do you tell them apart quickly?

**Difficulty:** Medium · **Tags:** `workloads` `troubleshooting`

The Pod's **phase + container state reason** routes the entire investigation, so read that
first (`kubectl get pod` then `describe`). `Pending` → scheduling or volume (above).
`ImagePullBackOff`/`ErrImagePull` → registry reachability, wrong tag, or a missing
`imagePullSecret` — check the exact pull error and whether the node can reach the registry.
`CreateContainerConfigError` → a referenced ConfigMap/Secret is missing or a key is wrong.
`CrashLoopBackOff` → the container *starts then exits* repeatedly (app error, failed probe,
OOM) — a different class entirely. `RunContainerError` → runtime/mount problem.

Once the reason narrows it, go to evidence: `kubectl describe` for events, and
`kubectl logs` (plus `--previous` for a crashed container) for app-level cause. The
point: the mistake juniors make is treating "Pod won't start" as one problem and guessing;
the method is to let the state reason classify it into scheduling / image / config / crash
/ runtime, because each has a different first move. State the decision tree out loud — that
*is* the answer the interviewer wants.

---

### Q: A Pod is in `CrashLoopBackOff`. How do you find the actual cause, and why is the status itself misleading?

**Difficulty:** Medium · **Tags:** `workloads` `troubleshooting`

`CrashLoopBackOff` is a **symptom, not a cause** — it only means "the container keeps
exiting and the kubelet is backing off between restarts with increasing delay." The cause
is why it exits. Read `kubectl logs --previous` (the *previous* instance's logs, since the
current one may have just started), the last **termination reason and exit code** (a
non-zero app exit vs `OOMKilled` vs a signal tells very different stories), the restart
count and timing, and the events. Check mounted config/Secrets (a bad value crashes on
boot) and **probe failures** (an over-aggressive liveness probe can *cause* the crash loop
by killing a healthy-but-slow container).

Then **correlate the first restart** with a change: a deploy, a config/Secret edit, or a
dependency outage — the timeline usually names the culprit. Mitigation: if a new version is
harming users, **roll back**, but preserve the failing Pod's logs and spec first (don't
delete your only evidence to "clean up"). The nuance: exit code 0 looping means the
process thinks it finished (wrong command/entrypoint); `OOMKilled` means it's a memory
problem, not a code bug (scenario on resource limits); and if it crashes only in prod, suspect
environment — config, secrets, network policy, or a dependency that's reachable in staging
but not prod.

---

### Q: Pods are `Running` but the Service has no healthy endpoints — none are `Ready`. What's going on?

**Difficulty:** Medium · **Tags:** `probes` `networking`

`Running` is *process* state; `Ready` is *traffic eligibility* — and the gap between them
is almost always the **readiness probe**. Something is making it fail: the probe points at
the wrong port/path, the app's dependency (DB, cache) is unavailable so the app correctly
reports not-ready, the app is still warming up (needs a **startup probe**), or the probe is
so expensive it times out under load. Inspect Pod conditions and probe events
(`kubectl describe pod`), then **test the readiness endpoint from the Pod's own network
context** (exec in and curl it) to separate "app says not ready" from "probe is
misconfigured."

The consequence that makes this urgent: unready Pods are **removed from EndpointSlices**,
so the Service has no backends and clients get connection refused / 503 even though every
Pod is "up." That's why a readiness probe that depends on a flaky downstream can take your
whole service offline the moment that downstream blips — a readiness probe failing en masse
is often a dependency problem wearing a Kubernetes costume. The fixes: readiness may
check dependencies but should fail *closed* carefully; use a **startup probe** for slow
boots so liveness doesn't kill them; and make sure a transient dependency hiccup doesn't
simultaneously mark every replica unready (consider not gating readiness on a soft
dependency).

---

### Q: Pods restart specifically during traffic spikes. Diagnose it.

**Difficulty:** Hard · **Tags:** `resources` `oom`

Three usual mechanisms, and distinguishing them is the whole game: **container OOMKill**,
**node-pressure eviction**, and **CPU throttling**. The critical distinction — a **memory**
limit breach gets the container **OOMKilled** (hard termination, `reason: OOMKilled`, exit
137), while a **CPU** limit breach causes **throttling** (the app gets slow, latency
spikes, but it is *not* killed). So "restarts during spikes" usually means memory: under
load the working set grows past the limit and the kernel kills it. For OOM, check the
termination reason, memory working set vs limit, and recent deploys (did a change raise
memory use?). For eviction, check **node** conditions — `MemoryPressure`, `DiskPressure`,
`PIDPressure` — and compare Pod usage to requests, since the kubelet evicts BestEffort and
over-request Burstable Pods first when the node is squeezed.

Mitigation and the trap: right-size requests/limits, hunt a genuine leak, add capacity, or
shed load — but **raising the memory limit blindly just moves the failure**: now the Pod
can consume more, so instead of one Pod dying, the whole **node** hits memory pressure and
evicts *other* tenants, turning a contained crash into a node-wide incident. The
framing: decide whether this is legitimate load (scale out / size up deliberately), a leak
(fix the app), or a thundering-herd of cold caches on spike (warm them / stagger). And
separate CPU throttling (shows as latency, not restarts — often a too-tight CPU limit on a
latency-sensitive service) from true OOM, because the fixes are opposite directions.

---

### Q: One Service returns intermittent 503s — not constant, just some requests. Debug it.

**Difficulty:** Hard · **Tags:** `networking` `dns`

"Intermittent" is the clue: a **subset** is bad, so first **split the errors** by Pod,
version, node, and zone. If 503s cluster on one version → bad deploy. On one node/zone →
infrastructure. Evenly across all → something upstream (DNS, policy, the Service
definition). Then walk the path deliberately: **Service** ports and targetPort → **selector**
correctness → **EndpointSlices** → **readiness** of the backing Pods → **direct Pod
connectivity** (exec and curl a Pod IP, bypassing the Service) → **DNS** → **NetworkPolicy**.

Interpret what you find: an **empty EndpointSlice** means selector mismatch or no Ready
Pods (the Service points at nothing). A **populated** slice where one endpoint fails means
a specific bad Pod/node — pull it. If it's DNS, resolve a *known* name from the same
namespace context first, then check `/etc/resolv.conf`, the kube-dns Service endpoints, and
CoreDNS Pods/logs — and **don't restart CoreDNS reflexively**, because intermittent DNS
under load is usually capacity / `ndots` amplification / conntrack exhaustion, which a
restart only masks. The nuance: intermittent 503s at exactly the rollout boundary
often mean the **termination race** (Pods getting SIGTERM while still in endpoints — fix
with a preStop sleep); 503s under load with healthy Pods can be connection-pool or
keep-alive imbalance (L4 pinning long-lived connections to one backend). The method —
split, then walk the path — matters more than any single command.

---

### Q: A Deployment rollout is stuck — not progressing, not failing cleanly. What now?

**Difficulty:** Medium · **Tags:** `deployments` `rollout`

`kubectl rollout status deploy/x` to confirm it's wedged, then compare the **old vs new
ReplicaSet** (`kubectl get rs`) — the new one is trying to come up and can't. Inspect the
**new Pods' events and logs**: the stall is almost always **new Pods not becoming Ready**
(readiness failing, crash loop, OOM), **image pull errors**, or an admission/quota block
(ResourceQuota exhausted, a LimitRange rejecting the Pod, RBAC, or a failing admission
webhook). The rolling strategy then does exactly what it should — it won't proceed past
`maxUnavailable` while new Pods aren't Ready — so it holds, old Pods keep serving, and it
looks "stuck" when it's actually protecting you.

Mitigation by impact: if old Pods are still serving and users are fine, you have time to
fix forward or `kubectl rollout undo`. If the partial rollout is hurting users, roll back
now. Prevention is the richer part of the answer: sane `maxSurge`/`maxUnavailable`, honest
readiness probes, a `progressDeadlineSeconds` so a stuck rollout is *reported* as failed
rather than hanging silently, canary + automated analysis to catch bad versions before full
rollout, and automated rollback criteria. The clarification to volunteer: a
**PodDisruptionBudget governs voluntary evictions (drains/autoscaler), not the Deployment's
rolling-update strategy** — people conflate them; the rolling update is bounded by
`maxUnavailable`, and if *that's* why it won't proceed, the fix is the strategy, not the
PDB.

---

### Q: Traffic doubled but the HPA didn't scale. Why, and how do you confirm each hypothesis?

**Difficulty:** Hard · **Tags:** `autoscaling` `hpa`

Start at `kubectl describe hpa` and read the conditions + `current/target` — it tells you
immediately whether metrics are missing, the target is "met," or scaling is capped. The
causes: **no CPU requests** on the Pods, so utilization is undefined (`<unknown>`) and HPA
can't act; **metrics unavailable** (metrics-server down / custom-metrics adapter broken);
**wrong demand signal** — the app is I/O- or queue-bound so CPU stays flat while latency
and backlog climb, and HPA happily does nothing because its metric isn't moving; hitting
**maxReplicas**; or new replicas that **can't schedule or start** fast enough (Pending for
lack of node capacity, or slow startup), so replica count rises on paper but ready capacity
doesn't.

Confirm each: `describe hpa` for metrics/target/cap, `kubectl top pods` vs requests for the
CPU story, check metrics-server health, check whether new Pods are Pending (→ Cluster
Autoscaler not keeping up), and look at an app-level load metric (RPS, queue depth, p99) to
see if CPU is even the right signal. Prevention: scale on the metric that **actually tracks
load** (queue depth / concurrency / RPS via custom or external metrics, often via KEDA),
set CPU requests, pair HPA with a node autoscaler, and tune the stabilization window to
avoid flapping. The one-liner: **HPA changes replica count; it does not create node
capacity** — if the real bottleneck is nodes, HPA "not scaling" is really Cluster Autoscaler
not scaling, and you must name that distinction.

---

### Q: A node goes `NotReady` and its Pods start disappearing. Walk me through your response as the on-call.

**Difficulty:** Hard · **Tags:** `nodes` `control-plane`

First scope it: is it **one node**, a **whole zone**, or a **control-plane connectivity**
problem (many nodes flipping NotReady at once usually means the nodes are fine and the
*control plane* or network to it is the issue — don't start rebooting nodes). For a single
node, read its **conditions** (`Ready`, `MemoryPressure`, `DiskPressure`, `PIDPressure`),
**taints**, the node **lease** (is the kubelet still heartbeating?), and events. Then
descend the stack: **kubelet** (down/crashed/cert-expired), **container runtime**, **CNI**
(node networking dead), **host resources** (disk full on `/var`, OOM at the host level, PID
exhaustion), and finally the **underlying VM/hardware**.

The Pods "disappearing" is the **node controller** doing its job: when a node is
unreachable it marks the node's status `Unknown` and, after a grace period, the Pods get a
`NoExecute` taint and are evicted/rescheduled elsewhere (controllers recreate them on
healthy nodes). As on-call, **protect remaining capacity** — make sure the rescheduled Pods
have somewhere to go, and **don't drain more nodes** while things are unstable (that's how a
one-node blip becomes a cascading capacity collapse). The prevention: topology spread
+ PDBs so losing a node/zone doesn't take a service below quorum, system-reserved so the
kubelet doesn't get starved by workloads, node problem detector + automated repair/replace,
and alerting on node conditions as leading indicators rather than waiting for NotReady.

---

### Q: A stateful Pod can't mount its volume. Walk through it — carefully, because the wrong move loses data.

**Difficulty:** Hard · **Tags:** `storage` `csi`

Read events across the whole chain, because the error could be at any link: **Pod → PVC →
PV → StorageClass → CSI controller/node plugins** (`kubectl describe` each, plus CSI pod
logs). The causes cluster into: **unbound claim** (no provisioner / provisioner erroring /
no matching static PV); **StorageClass or access-mode mismatch** (class missing, or RWX
requested on block storage); **unsatisfiable topology** (a zonal disk in a zone the Pod
can't schedule into — the `WaitForFirstConsumer` story); or **volume still attached
elsewhere** (`Multi-Attach` — common after an ungraceful node failure where the old
attachment wasn't released, so the new Pod can't attach the RWO disk).

The safety discipline is the point of this question: **do not casually delete the PVC or
PV** to "reset it" — depending on reclaim policy that destroys the data. Before any
destructive action, confirm the **reclaim policy**, whether the data is precious, whether a
**snapshot** exists, and whether the old node is truly gone before force-detaching (force-
detaching a volume still mounted by a live node risks corruption). For `Multi-Attach` after
a node failure, the correct move is to ensure the old node is dead/fenced, then let the
attachment release (or force-detach only once fenced). The prevention: storage
monitoring and capacity alerts, **tested restores** (a snapshot you've never restored is a
hope, not a backup), topology-aware provisioning (`WaitForFirstConsumer`), and a documented
attachment-conflict runbook so the 3am on-call doesn't improvise a `kubectl delete pvc`.

---

### Q: A distributed database shows data inconsistency across replicas. What are the likely causes and how do you investigate?

**Difficulty:** Hard · **Tags:** `distributed` `databases`

First decide whether it's *expected* or a real violation: many systems are **eventually
consistent**, so a reader hitting a lagging replica sees stale-but-not-wrong data — confirm
the consistency model before calling it a bug. If it's a true divergence, the usual causes:
**replication lag** (follower behind the leader — reads routed to it look inconsistent);
**leader election / split-brain** (a partition or failover left two nodes believing they're
primary, so both accepted conflicting writes); **clock skew** (last-writer-wins ordering
goes wrong when node clocks disagree); and **network partition** (each side accepted writes
independently and they must now be reconciled).

Investigate: identify *which* replicas disagree and on which keys, pull replication/lag
metrics and recent **leader-change** events, check **NTP/clock drift** across nodes, and
review whether quorum/consistency settings were actually in force for the writes in
question. Mitigate by promoting a known-good replica and reconciling from it (or restoring
from backup for the diverged data), and fence the bad node. The prevention: use
**quorum reads/writes** (so a single lagging/partitioned node can't serve or accept
divergent data), **fencing/STONITH** to prevent two leaders, and bounded clock sync — and
architecturally, don't route consistency-sensitive reads to async followers. The senior
signal is leading with "is this the system's *designed* consistency or an actual
violation," because half of these pages are someone reading a replica and being surprised by
eventual consistency.
