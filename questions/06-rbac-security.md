# RBAC & Security

### Q: Explain RBAC — Role vs ClusterRole, the bindings, subjects — and why there are no deny rules.

**Difficulty:** Medium · **Tags:** `rbac` `security`

- **Verbs** (`get`/`list`/`watch`/`create`/`update`/`patch`/`delete`) on **resources**.
- **Role** = namespaced. **ClusterRole** = cluster-scoped / reusable / for cluster-scoped
  resources (nodes, PVs).
- **RoleBinding** grants a Role *or* ClusterRole **within one namespace**;
  **ClusterRoleBinding** grants **cluster-wide**.
- **Subjects:** Users, Groups (external), ServiceAccounts (in-cluster).

**No deny by design:** rules are **purely additive** — permission = union of all grants. You
get least privilege by **granting narrowly**, not by carving exceptions.

**Trap:** a ClusterRole bound via a *RoleBinding* is namespace-scoped; the same ClusterRole
via a *ClusterRoleBinding* is cluster-wide — easy to over-grant. Audit with
`kubectl auth can-i --list`. Treat `cluster-admin` + wildcards as alarms.

---

### Q: A workload needs the K8s API. How do you give it exactly what it needs?

**Difficulty:** Medium · **Tags:** `rbac` `serviceaccount`

- **Dedicated ServiceAccount** (never `default`) + a **Role** with only needed verbs +
  a **RoleBinding** in that namespace.
- No API access needed → `automountServiceAccountToken: false`.

```yaml
kind: Role
metadata: { namespace: demo, name: pod-reader }
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get","list","watch"]      # no create/delete, no secrets, no wildcards
---
kind: RoleBinding
metadata: { namespace: demo, name: pod-reader-bind }
subjects: [{ kind: ServiceAccount, name: my-app, namespace: demo }]
roleRef: { kind: Role, name: pod-reader, apiGroup: rbac.authorization.k8s.io }
```

**Notes:** prefer short-lived projected tokens · for cloud APIs use **IRSA / Workload
Identity** (not static keys) · `get secret` is high-value — a role that reads secrets owns
whatever they protect.

---

### Q: PodSecurityPolicy is gone. What replaced it, and how do you enforce "no root, no privileged"?

**Difficulty:** Advanced · **Tags:** `security`

PSP removed in 1.25 → **Pod Security Admission (PSA)**, enforcing the **Pod Security
Standards** per namespace via labels:
| Standard | Means |
|----------|-------|
| **privileged** | no restriction |
| **baseline** | block known escalations (hostPath, host ns, privileged) |
| **restricted** | hardened: non-root, drop caps, seccomp RuntimeDefault |

- Modes: `enforce` / `audit` / `warn` → roll out warn-then-enforce.
- Enforce cluster-wide: label namespaces `pod-security.kubernetes.io/enforce: restricted`,
  default-all + justified exceptions (a CNI DaemonSet needs privilege).

**Finer/custom policy** ("images from our registry only", "must set limits") → admission
webhook: **OPA Gatekeeper** or **Kyverno**. Lock down who can label namespaces.

---

### Q: Validating vs mutating admission webhooks — order, and why it matters for sidecar injection.

**Difficulty:** Advanced · **Tags:** `security` `architecture`

Admission runs after authn/authz, before etcd, in order:
**mutating webhooks → validation/quota → validating webhooks**.
- **Mutating** — can *change* the object (inject sidecar, add defaults). Runs first.
- **Validating** — accept/reject only (deterministic policy). Runs last.

**Order matters:** mesh sidecar-injection (mutating) adds the proxy *before* a policy webhook
(validating) checks the final Pod → injected sidecar is subject to policy.

**Operational warning:** a webhook is on the **critical path** of every matching write.
`failurePolicy: Fail` + webhook down → **writes stop** (deploys, maybe system Pods);
`Ignore` → security gap. → scope narrowly (`namespaceSelector`/`objectSelector`), exclude
kube-system, run HA, watch latency. A bad `Fail` webhook going down = self-inflicted outage.

---

### Q: Secrets are only base64 in etcd. Give the full layered approach to securing them.

**Difficulty:** Advanced · **Tags:** `security` `secrets`

base64 = encoding, not encryption. Layers outward:
1. **Encryption at rest** — API-server `EncryptionConfiguration` + **KMS** provider →
   ciphertext in etcd (+ key rotation, key off the etcd disk).
2. **RBAC** — `get`/`list`/`watch` on secrets is high-value; scope tight. `exec` into a Pod
   or its SA token also reads mounted secrets.
3. **External store** — Vault / cloud SM via External Secrets Operator or CSI driver →
   short-lived, auditable, rotating; not parked in etcd.
4. **Hygiene** — never in images or manifests.

**Rotation nuance:** file-mounted secrets update in place (app reloads); **env-var secrets
fixed at Pod start** → need restart. Strongest posture: minimize long-lived secrets
(workload identity, mesh mTLS, dynamic DB creds).
