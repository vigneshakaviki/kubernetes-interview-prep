# Explain RBAC — Role vs ClusterRole, the bindings, subjects — and why there are no deny rules.

[↑ Index](./README.md) · [Next →](./02-a-workload-needs-the-k8s-api-how-do.md)

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

[↑ Index](./README.md) · [Next →](./02-a-workload-needs-the-k8s-api-how-do.md)
