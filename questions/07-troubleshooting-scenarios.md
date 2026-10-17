# Production Troubleshooting Scenarios

The highest-signal interview round. They're testing whether you reason under pressure
without thrashing. **Narrate the method**, not a command dump.

## The method (apply to every scenario)

1. **Protect users first** — severity, error rate, % traffic hit, what changed, is a
   reversible mitigation (rollback / traffic shift / flag) available *now*.
2. **Scope it** — healthy vs unhealthy across Pods / nodes / zones / versions / paths. The
   axis it splits on *is* the clue.
3. **Desired vs observed** — read workload, Pod conditions, controller status, events
   *before* changing anything.
4. **Follow the dependency path** — Deployment → Pod → node → Service/EndpointSlices →
   DNS/NetworkPolicy → storage → external deps.
5. **Mitigate → verify → prevent** — reversible action, confirm *user-facing* recovery,
   name the guardrail. Preserve evidence (logs, failing spec).

---

### Q: A Pod has been `Pending` for 20 minutes. Walk through it.

**Difficulty:** Medium · **Tags:** `scheduling` `troubleshooting`

**`Pending` = can't schedule, or scheduled-but-won't-start.** `kubectl describe pod` → read
scheduler events.

**Unschedulable causes:**
- Requests > any node's allocatable (remember system-reserved eats allocatable).
- Taints without toleration · unsatisfied nodeSelector/affinity/topology.
- **Unbound PVC** (zonal disk the scheduler can't match).

Scheduled-but-not-starting → image-pull or volume-attach events instead.

**Fix the real constraint**, not the symptom:
- ❌ Deleting the Pod — controller recreates the same spec, still Pending.
- ❌ Adding nodes when it's a nodeSelector typo — burns money.
- ✅ Read the failed predicate, fix *that*.

---

### Q: A Pod fails to start — several reasons look similar. How do you tell them apart fast?

**Difficulty:** Medium · **Tags:** `workloads` `troubleshooting`

The **phase + container-state reason** routes everything (`get` then `describe`):
| Reason | Means | First move |
|--------|-------|-----------|
| `Pending` | scheduling/volume | describe → scheduler events |
| `ImagePullBackOff` | registry/tag/secret | check pull error + node→registry |
| `CreateContainerConfigError` | missing ConfigMap/Secret key | check refs |
| `CrashLoopBackOff` | starts then exits | `logs --previous` |
| `RunContainerError` | runtime/mount | describe events |

**Don't guess one cause** — let the state reason classify it, then go to `describe` + `logs
--previous`. State the decision tree out loud.

---

### Q: A Pod is in `CrashLoopBackOff`. Find the cause — and why is the status misleading?

**Difficulty:** Medium · **Tags:** `workloads` `troubleshooting`

**It's a symptom** — "container keeps exiting, kubelet backing off." The cause is *why*.

**Evidence:**
- `kubectl logs --previous` — the crashed instance's logs (current may be empty).
- Termination **reason + exit code**: non-zero app exit vs `OOMKilled` (137) vs signal.
- Restart count/timing; mounted config/Secrets; probe failures (aggressive liveness can
  *cause* the loop).
- **Correlate first restart** with a deploy / config edit / dependency outage.

**Mitigate:** roll back if a new version harms users — but preserve logs + spec first.

**Tells:** exit 0 looping = wrong command/entrypoint · 137 = memory, not a bug · crashes
only in prod = environment (config/secrets/policy/dependency).

---

### Q: Pods are `Running` but none are `Ready` and the Service is dead. What's wrong?

**Difficulty:** Medium · **Tags:** `probes` `networking`

**`Running` = process; `Ready` = traffic-eligible.** The gap is almost always the
**readiness probe**: wrong port/path, dependency down, slow boot (needs startup probe), or
too-expensive probe.

**Check:** Pod conditions + probe events → **test the readiness endpoint from inside the
Pod** (separates "app not ready" from "probe misconfigured").

**Why it's urgent:** unready Pods are pulled from **EndpointSlices** → Service has no
backends → clients get 503 though every Pod is "up." A readiness probe gated on a flaky
downstream takes the whole service offline when that downstream blips.

---

### Q: Pods restart specifically during traffic spikes. Diagnose it.

**Difficulty:** Hard · **Tags:** `resources` `oom`

Three mechanisms — **telling them apart is the whole game:**
- **Memory limit breach → OOMKilled** (hard, `reason: OOMKilled`, exit 137). ← "restarts on
  spike" is usually this.
- **CPU limit breach → throttled** (slow, *not* killed).
- **Node-pressure eviction** → check node `MemoryPressure`/`DiskPressure`/`PIDPressure`.

**The trap:** raising the memory limit blindly just **moves the failure** — the Pod now
consumes more → the whole **node** hits pressure → evicts *other* tenants → node-wide
incident.

**Decide:** legitimate load (scale deliberately) · leak (fix app) · cold-cache thundering
herd (warm/stagger). And don't confuse CPU throttling (shows as latency) with true OOM.

---

### Q: One Service returns intermittent 503s. Debug it.

**Difficulty:** Hard · **Tags:** `networking` `dns`

**Intermittent = a subset is bad → split errors** by Pod / version / node / zone:
- One version → bad deploy · one node/zone → infra · evenly → upstream (DNS/policy/Service).

**Walk the path:** Service ports → selector → **EndpointSlices** → readiness → direct Pod
curl → DNS → NetworkPolicy.
- **Empty slice** → selector mismatch / no Ready Pods.
- **Populated, one endpoint failing** → bad Pod/node, pull it.

**Tells:** 503s at the rollout boundary = termination race (SIGTERM while still in endpoints
→ preStop sleep) · 503s under load with healthy Pods = connection-pool/keep-alive imbalance
(L4 pinning). Don't restart CoreDNS reflexively.

---

### Q: A Deployment rollout is stuck. What now?

**Difficulty:** Medium · **Tags:** `deployments` `rollout`

`kubectl rollout status` → compare **old vs new ReplicaSet** → inspect **new Pods' events +
logs**. The stall is almost always:
- New Pods not Ready (readiness/crash/OOM) · image pull errors · quota/LimitRange/RBAC/
  admission block.

The rolling strategy is *protecting* you — it won't proceed past `maxUnavailable` while new
Pods aren't Ready, so old Pods keep serving (looks "stuck").

**Act by impact:** old Pods serving + users fine → fix forward or `rollout undo`. Users hurt
→ roll back now.

**Prevent:** sane `maxSurge`/`maxUnavailable`, honest readiness, `progressDeadlineSeconds`
(so it *reports* failed, not hangs), canary + auto-rollback.

**Clarify:** a **PDB governs voluntary evictions, not the rolling-update strategy** — people
conflate them.

---

### Q: Traffic doubled but the HPA didn't scale. Why, and how do you confirm each hypothesis?

**Difficulty:** Hard · **Tags:** `autoscaling` `hpa`

Start at `kubectl describe hpa` → conditions + `current/target`.

| Hypothesis | Confirm with |
|-----------|--------------|
| No CPU request (`<unknown>`) | `kubectl top` vs requests |
| metrics-server broken | its pod health |
| Wrong signal (I/O/queue-bound) | app metric (RPS, queue depth, p99) |
| Hit `maxReplicas` | describe hpa |
| New Pods `Pending` | → Cluster Autoscaler lagging |

**One-liner:** **HPA changes replica count; it does not create node capacity** — "HPA not
scaling" is often Cluster Autoscaler not scaling.

**Prevent:** scale on the metric that tracks load (queue/concurrency/RPS, often via KEDA),
set requests, pair with a node autoscaler, tune stabilization.

---

### Q: A node goes `NotReady` and its Pods disappear. Respond as on-call.

**Difficulty:** Hard · **Tags:** `nodes` `control-plane`

**Scope first:** one node / a zone / control-plane connectivity? Many nodes flipping at once
= usually the control plane or network to it — **don't start rebooting nodes.**

**Single node — descend the stack:** node conditions/taints/lease (kubelet heartbeating?) →
kubelet → runtime → CNI → host resources (disk full `/var`, host OOM, PIDs) → VM/hardware.

**Pods "disappearing" = node controller working:** unreachable node → status `Unknown` →
after grace, `NoExecute` taint evicts Pods → rescheduled on healthy nodes.

**On-call:** protect remaining capacity, **don't drain more nodes** while unstable (cascade
risk). **Prevent:** topology spread + PDBs, system-reserved, node-problem-detector + auto-repair.

---

### Q: A stateful Pod can't mount its volume. Walk through it — carefully, data is at risk.

**Difficulty:** Hard · **Tags:** `storage` `csi`

**Read events across the chain:** Pod → PVC → PV → StorageClass → CSI controller/node logs.

**Causes:** unbound claim · StorageClass/access-mode mismatch (RWX on block) · unsatisfiable
topology (zonal disk vs Pod zone) · **volume still attached elsewhere** (`Multi-Attach`
after ungraceful node failure).

**Safety (the point of the question):**
- ❌ Don't delete the PVC/PV to "reset" — may destroy data.
- ✅ First confirm reclaim policy, data value, snapshot, and that the old node is **fenced**
  before force-detach (force-detaching a live-mounted volume risks corruption).

**Prevent:** storage monitoring, **tested restores**, `WaitForFirstConsumer`, an
attachment-conflict runbook.

---

### Q: A distributed database shows data inconsistency across replicas. Causes + investigation.

**Difficulty:** Hard · **Tags:** `distributed` `databases`

**First:** expected or a real violation? Many systems are **eventually consistent** — a
read off a lagging replica is stale, not wrong. Confirm the consistency model before calling
it a bug.

**True-divergence causes:**
- **Replication lag** · **leader election / split-brain** (two primaries after a partition)
  · **clock skew** (bad last-writer-wins) · **network partition** (independent writes).

**Investigate:** which replicas/keys disagree · replication + leader-change metrics · NTP
drift · were quorum settings actually in force?

**Mitigate:** promote a known-good replica + reconcile; fence the bad node.
**Prevent:** quorum reads/writes, fencing, bounded clock sync; don't route consistency-
sensitive reads to async followers.
