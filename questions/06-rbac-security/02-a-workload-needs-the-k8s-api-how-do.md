# A workload needs the K8s API. How do you give it exactly what it needs?

[↑ Index](./README.md) · [← Prev](./01-explain-rbac-role-vs-clusterrole-the-bindings-subjects.md) · [Next →](./03-podsecuritypolicy-is-gone-what-replaced-it-and-how.md)

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

[↑ Index](./README.md) · [← Prev](./01-explain-rbac-role-vs-clusterrole-the-bindings-subjects.md) · [Next →](./03-podsecuritypolicy-is-gone-what-replaced-it-and-how.md)
