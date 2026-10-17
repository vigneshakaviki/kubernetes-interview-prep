# Validating vs mutating admission webhooks — order, and why it matters for sidecar injection.

[↑ Index](./README.md) · [← Prev](./03-podsecuritypolicy-is-gone-what-replaced-it-and-how.md) · [Next →](./05-secrets-are-only-base64-in-etcd-give-the.md)

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

[↑ Index](./README.md) · [← Prev](./03-podsecuritypolicy-is-gone-what-replaced-it-and-how.md) · [Next →](./05-secrets-are-only-base64-in-etcd-give-the.md)
