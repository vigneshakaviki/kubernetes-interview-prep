# Imperative vs declarative kubectl, and safely rolling back a bad Deployment.

[↑ Index](./README.md) · [← Prev](./14-labels-vs-annotations-where-s-the-line-and.md) · [Next →](./16-what-is-helm-what-does-it-buy-you.md)

**Difficulty:** Intermediate · **Tags:** `kubectl` `operations`

- **Imperative** (`create`, `scale`, `set image`) — fast, drifts from truth, not reviewable.
- **Declarative** (`apply -f`, GitOps) — repo is the audit log + change control. Run prod
  on this.

**Rollback:**
```bash
kubectl rollout history deploy/x
kubectl rollout undo deploy/x --to-revision=N   # scales the old ReplicaSet back up
```
GitOps: the real rollback is **reverting the git commit** (else it drifts back on next sync).

**Caveat:** rollback is clean only if the change was backward-compatible — a schema
migration or consumed-then-removed API **can't** be undone by scaling Pods → need
forward-fix or expand/contract discipline.

---

[↑ Index](./README.md) · [← Prev](./14-labels-vs-annotations-where-s-the-line-and.md) · [Next →](./16-what-is-helm-what-does-it-buy-you.md)
