# PodSecurityPolicy is gone. What replaced it, and how do you enforce "no root, no privileged"?

[↑ Index](./README.md) · [← Prev](./02-a-workload-needs-the-k8s-api-how-do.md) · [Next →](./04-validating-vs-mutating-admission-webhooks-order-and-why.md)

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

[↑ Index](./README.md) · [← Prev](./02-a-workload-needs-the-k8s-api-how-do.md) · [Next →](./04-validating-vs-mutating-admission-webhooks-order-and-why.md)
