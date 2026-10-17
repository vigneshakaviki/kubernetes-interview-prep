# Hands-On Exercises

Reading answers isn't enough — interviewers can tell who has actually driven a cluster.
Spin up a local one (`kind create cluster` or `minikube start`) and do these. Solutions
are collapsed; **try first, then expand**.

> Tip: `alias k=kubectl`, and `kubectl explain <resource>.spec` is your friend in a
> no-internet interview environment.

---

### E1. Diagnose a CrashLoopBackOff without the app logs being obvious.

Deploy a Pod that exits 1 on startup. Find the root cause using only `kubectl`, then
explain which command told you what.

<details><summary>Solution</summary>

```bash
kubectl run crasher --image=busybox --restart=Never -- /bin/sh -c "echo boot; exit 1"
kubectl get pod crasher -o wide                 # see CrashLoopBackOff + restart count
kubectl describe pod crasher                    # events, last state, exit code
kubectl logs crasher --previous                 # logs of the crashed instance
kubectl get pod crasher -o jsonpath='{.status.containerStatuses[0].lastState.terminated.exitCode}{"\n"}'
```

`describe` gives you the termination **reason + exit code** and restart timing;
`logs --previous` is the key flag — the current attempt may have no output yet, the
*previous* one does. Exit 1 = app error; exit 137 = OOMKilled (different problem).
</details>

---

### E2. A Service returns nothing. Prove whether it's a selector, readiness, or DNS problem.

Create a Deployment + Service where the Service selector **doesn't match** the Pod
labels. Diagnose the empty-endpoints symptom.

<details><summary>Solution</summary>

```bash
kubectl create deploy web --image=nginx --replicas=2
kubectl expose deploy web --port=80 --selector=app=wrong   # intentional mismatch
kubectl get endpointslices -l kubernetes.io/service-name=web   # EMPTY = the smoking gun
kubectl describe svc web                                       # selector vs pod labels
kubectl get pods --show-labels                                 # actual labels
```

Empty EndpointSlice → selector mismatch or no Ready Pods. Fix:
`kubectl set selector svc web 'app=web'` (or edit) and re-check the slice fills.
To test readiness vs selector, `kubectl get pods` for Ready state; to test DNS,
`kubectl run t --rm -it --image=busybox -- nslookup web`.
</details>

---

### E3. Make a Pod land on a specific node pool and nowhere else.

Taint a node and use a toleration + nodeAffinity so one Pod runs only there.

<details><summary>Solution</summary>

```bash
kubectl taint nodes <node> dedicated=batch:NoSchedule
kubectl label nodes <node> pool=batch
```
```yaml
spec:
  tolerations:
  - key: dedicated
    operator: Equal
    value: batch
    effect: NoSchedule
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
        - matchExpressions: [{ key: pool, operator: In, values: [batch] }]
```

Toleration alone lets it *onto* the tainted node but doesn't *steer* it there; affinity
alone doesn't stop other Pods landing on it. You need both — taint repels everyone else,
affinity pulls this Pod in.
</details>

---

### E4. Trigger and read an OOMKill.

Run a Pod with a 50Mi memory limit that allocates more, confirm it's OOMKilled (not
evicted, not throttled).

<details><summary>Solution</summary>

```bash
kubectl run oom --image=polinux/stress --restart=Never \
  --limits=memory=50Mi -- stress --vm 1 --vm-bytes 150M --vm-hang 1
kubectl get pod oom -o jsonpath='{.status.containerStatuses[0].lastState.terminated.reason}{"\n"}'
# -> OOMKilled   (exit code 137)
```

Memory limit breach = hard kill (OOMKilled/137). Contrast with a CPU limit, which
*throttles* (slow) and never kills. This is the distinction every spike-restart question
is probing.
</details>

---

### E5. Do a rolling update, watch it, then roll it back.

Update an image, observe the rollout, then undo to the previous revision.

<details><summary>Solution</summary>

```bash
kubectl create deploy web --image=nginx:1.25
kubectl set image deploy/web nginx=nginx:1.26 && kubectl rollout status deploy/web
kubectl rollout history deploy/web
kubectl rollout undo deploy/web            # back to previous revision
kubectl get rs -l app=web                  # old RS scaled up, new scaled to 0
```

Undo just scales the previous ReplicaSet back up via the normal rolling strategy — which
is why it only works cleanly for backward-compatible changes (a schema migration can't be
undone by scaling Pods).
</details>

---

### E6. Write a NetworkPolicy that default-denies ingress but allows one app.

Lock down a namespace so only Pods labeled `role=frontend` can reach `app=api`.

<details><summary>Solution</summary>

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: api-allow-frontend, namespace: demo }
spec:
  podSelector: { matchLabels: { app: api } }
  policyTypes: [Ingress]
  ingress:
  - from:
    - podSelector: { matchLabels: { role: frontend } }
```

Verify with a `kubectl exec` curl from a frontend Pod (allowed) and a random Pod (denied).
Gotcha: this only works if the CNI **enforces** NetworkPolicy (Calico/Cilium) — kind's
default CNI does not, so install one. And if you add a default-deny *egress* policy later,
remember to allow DNS or everything breaks.
</details>

---

### E7. Autoscale a Deployment and explain why it might not scale.

Add an HPA on CPU and generate load. Then deliberately remove the CPU request and show
the HPA go to `<unknown>`.

<details><summary>Solution</summary>

```bash
kubectl autoscale deploy web --cpu-percent=50 --min=1 --max=5
kubectl get hpa web            # with requests set: shows current/target %
# remove the container's resources.requests.cpu, re-apply:
kubectl get hpa web            # -> TARGETS <unknown>/50%
kubectl describe hpa web       # condition explains the missing metric
```

CPU utilization is relative to the **request**, so no request = undefined = `<unknown>`.
Also needs metrics-server running. This is the #1 "HPA won't scale" cause.
</details>

---

### E8. Debug a Pod that has no shell (distroless) using an ephemeral container.

<details><summary>Solution</summary>

```bash
kubectl debug -it <pod> --image=busybox --target=<container>
# shares the target's process namespace — inspect without a shell in the app image
```

`kubectl debug` attaches an **ephemeral container** to a running Pod — the modern way to
troubleshoot distroless/minimal images that have no shell, without rebuilding or
restarting the Pod. Also `kubectl debug node/<node> -it --image=busybox` to get onto a
node.
</details>
