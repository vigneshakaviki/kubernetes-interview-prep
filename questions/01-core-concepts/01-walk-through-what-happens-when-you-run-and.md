# Walk through what happens when you run `kubectl apply -f deploy.yaml` — and where it can fail.

[↑ Index](./README.md) · [Next →](./02-what-is-kube-proxy-its-modes-and-is.md)

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

[↑ Index](./README.md) · [Next →](./02-what-is-kube-proxy-its-modes-and-is.md)
