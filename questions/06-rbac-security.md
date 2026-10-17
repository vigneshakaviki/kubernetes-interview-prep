# RBAC & Security

### Q: Explain Kubernetes RBAC end to end — Role vs ClusterRole, the bindings, subjects — and why there are no deny rules.

**Difficulty:** Medium · **Tags:** `rbac` `security`

RBAC grants permission to perform **verbs** (`get`, `list`, `watch`, `create`, `update`,
`patch`, `delete`) on **resources** (optionally narrowed to specific names or
subresources). A **Role** is namespaced — its rules apply only within one namespace. A
**ClusterRole** is cluster-scoped and also the way to grant access to cluster-scoped
resources (nodes, PVs) or to define a reusable permission set. The bindings connect
subjects to roles: a **RoleBinding** grants a Role (or a ClusterRole) **within a single
namespace**; a **ClusterRoleBinding** grants a ClusterRole **cluster-wide**. Subjects are
**Users**, **Groups** (both external identities K8s doesn't manage itself), and
**ServiceAccounts** (in-cluster identities for workloads).

The "no deny" design is deliberate and important: rules are **purely additive** — there is
no explicit deny, and permission is the union of everything granted to the subject. So you
achieve least privilege by **granting narrowly**, not by granting broadly and carving out
exceptions. A subtle trap is that a ClusterRole bound with a *RoleBinding* is scoped to
that namespace (useful for reusing a standard role per-namespace), while the *same*
ClusterRole bound with a ClusterRoleBinding is cluster-wide — people accidentally grant
cluster-wide access this way. The framing: audit effective permissions with
`kubectl auth can-i --list`, prefer per-namespace RoleBindings of shared ClusterRoles,
treat `cluster-admin` and wildcard verbs/resources as alarms, and remember RBAC authorizes
*the API* — it's one layer, not your whole security model.

```yaml
# least-privilege: a SA that can only read pods in namespace "demo"
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata: { namespace: demo, name: pod-reader }
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "watch"]     # no create/delete, no secrets, no wildcards
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata: { namespace: demo, name: pod-reader-bind }
subjects: [{ kind: ServiceAccount, name: my-app, namespace: demo }]
roleRef: { kind: Role, name: pod-reader, apiGroup: rbac.authorization.k8s.io }
```

---

### Q: A workload needs to call the Kubernetes API. How do you give it exactly the access it needs and nothing more?

**Difficulty:** Medium · **Tags:** `rbac` `serviceaccount`

Give the workload its **own dedicated ServiceAccount** (never the namespace `default`),
create a **Role** with only the verbs/resources it actually needs, and bind them with a
**RoleBinding** in that namespace. The ServiceAccount's token is projected into the Pod
(modern clusters use short-lived, audience-scoped projected tokens rather than
never-expiring secrets), and the client library uses it automatically. If the Pod doesn't
talk to the API at all, set `automountServiceAccountToken: false` so no token is mounted
to steal.

The least-privilege discipline: start from zero and add the specific verbs
(`get`/`list`/`watch` on the specific resource, in the specific namespace) the code needs
— confirmed by reading the code or watching `kubectl auth can-i` — rather than reusing a
broad role. Avoid wildcard resources/verbs and avoid binding to a ClusterRole unless the
workload genuinely needs cluster scope. The additions worth saying: a leaked
ServiceAccount token is a credential, so scope it tightly and prefer short-lived projected
tokens; for cloud API access, bind the ServiceAccount to a cloud IAM role (IRSA / Workload
Identity) instead of mounting static cloud keys; and remember that `get secret` is a
high-value permission — a role that can read secrets in a namespace effectively has
whatever those secrets protect.

---

### Q: PodSecurityPolicy is gone. Explain what replaced it and how you'd enforce "no root, no privileged" across the cluster.

**Difficulty:** Advanced · **Tags:** `security`

PodSecurityPolicy was deprecated and removed in 1.25. Its built-in replacement is **Pod
Security Admission (PSA)** — an admission controller that enforces the **Pod Security
Standards** at the **namespace** level via labels. The three standards: **privileged** (no
restrictions), **baseline** (block known privilege escalations — hostPath, host namespaces,
privileged containers), and **restricted** (hardened — must run as non-root, drop all
capabilities, seccomp `RuntimeDefault`, no privilege escalation). Each namespace can set
`enforce`, `audit`, and `warn` modes independently, so you can roll out by *warning* first,
then *enforcing*.

To enforce "no root, no privileged" cluster-wide: label namespaces with
`pod-security.kubernetes.io/enforce: restricted` (or at least `baseline`), typically with a
default applied to all namespaces and exceptions only where justified (a CNI DaemonSet
legitimately needs privilege). PSA is intentionally coarse (three tiers, namespace-level);
when you need **finer or custom** policy — "images must come from our registry," "every Pod
must set resource limits," "no `latest` tags" — you add a **policy admission webhook** like
**OPA Gatekeeper** or **Kyverno**, which can validate (reject) and even mutate. The
framing: PSA is the baseline guardrail you turn on everywhere in audit-then-enforce
fashion; Gatekeeper/Kyverno is for organization-specific policy-as-code — and both are
*admission-time* controls, complemented at runtime by seccomp/AppArmor and by RBAC limiting
who can label namespaces (or they'll just relax the policy).

---

### Q: Validating vs mutating admission webhooks — what's the order, and why does it matter for things like sidecar injection?

**Difficulty:** Advanced · **Tags:** `security` `architecture`

Admission runs **after** authentication and authorization but **before** the object is
persisted to etcd, in a fixed order: built-in mutating admission, then **mutating
webhooks**, then schema validation and quota, then built-in validating admission and
**validating webhooks**. **Mutating** webhooks run first and may *change* the object —
inject defaults, add labels, or inject a sidecar. **Validating** webhooks run last and may
only *accept or reject* — they can't modify, which is what makes them safe for policy
enforcement (deterministic allow/deny).

The ordering matters: because mutation precedes validation, a mesh's sidecar-injection
webhook (mutating) adds the proxy container *before* a policy webhook (validating) checks
the final Pod — so the injected sidecar is subject to policy, which is usually what you
want. The operational warnings: a webhook is on the **critical path** of every
matching API write, so if the webhook service is down, `failurePolicy: Fail` means those
writes (and your deploys, and possibly system Pods) **stop**, while `failurePolicy:
Ignore` opens a security gap — so you scope webhooks narrowly with `namespaceSelector`/
`objectSelector`, exclude kube-system, run the webhook HA, and watch its latency. A badly
scoped `failurePolicy: Fail` webhook that goes down is a classic self-inflicted cluster
outage, and knowing that is the senior signal.

---

### Q: Secrets are only base64-encoded in etcd. Give me the full layered approach to actually securing them.

**Difficulty:** Advanced · **Tags:** `security` `secrets`

base64 is encoding, not encryption, so a default Secret is effectively plaintext to anyone
who can read etcd or has `get secret` RBAC. The layers, from the cluster outward:
**(1) Encryption at rest** — configure the API server's `EncryptionConfiguration` with a
**KMS** provider so Secrets are encrypted with an external key before hitting etcd (identity
encoding is not enough; a KMS provider also gives you key rotation and that the key isn't
on the etcd disk). **(2) RBAC** — treat `get`/`list`/`watch` on secrets as a high-value
permission, scope it to the few ServiceAccounts/users that need it, and remember anyone who
can `exec` into a Pod or read its ServiceAccount token can reach that Pod's mounted
secrets. **(3) External secret stores** — Vault, cloud secret managers, surfaced via the
**External Secrets Operator** or the **Secrets Store CSI driver**, so the source of truth is
an auditable, rotating store and secrets aren't permanently parked in etcd. **(4) Hygiene** —
never bake secrets into images or commit them in manifests; use short-lived, dynamically
issued credentials where possible.

The nuance to add: rotation strategy depends on how the Pod consumes the secret —
file-mounted secrets update in place (eventually) so apps can reload, but env-var secrets
are fixed at Pod start and require a restart to pick up a new value, so "rotate the secret"
isn't complete without "restart/reload the consumers." And the strongest posture is to
minimize long-lived secrets entirely: workload identity (IRSA/Workload Identity) for cloud
APIs, mTLS identities from a mesh for service-to-service, and dynamic DB credentials from
Vault — so there's less static secret material to protect in the first place.
