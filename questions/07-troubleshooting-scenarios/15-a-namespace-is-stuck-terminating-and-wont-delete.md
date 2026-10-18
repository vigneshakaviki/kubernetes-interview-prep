# A namespace is stuck in `Terminating` and won't delete. Why?

[↑ Index](./README.md) · [← Prev](./14-dns-lookups-fail-intermittently-cluster-wide.md) · [Next →](./16-a-node-hits-diskpressure-and-evicts-pods.md)

**Difficulty:** Medium · **Tags:** `lifecycle` `control-plane`

**Short answer:** Two usual causes — **a resource with a finalizer** that isn't being
cleared, or a **broken APIService** so the namespace controller can't enumerate what to
delete.

**Diagnose:**
```bash
kubectl get ns <ns> -o yaml      # .status.conditions says WHY
kubectl api-resources --verbs=list --namespaced -o name \
  | xargs -n1 kubectl get -n <ns> --show-kind --ignore-not-found   # leftover objects
kubectl get apiservices | grep -v True   # a False/unavailable aggregated API blocks it
```

**Causes:**
- **Finalizer** on a leftover object (a CRD whose operator is gone) → nothing removes the
  finalizer → object (and namespace) hangs.
- **Dead APIService** (metrics-server / a webhook-backed aggregated API down) → the
  namespace controller errors listing that group → stuck on `NamespaceDeletionDiscoveryFailure`.

**Fix:** restore/remove the dead APIService or the operator so the finalizer clears
normally. **Last resort:** manually remove the finalizer — but that **leaks** whatever it
was protecting. Never blindly `kubectl edit` the namespace finalizer without knowing what's stuck.

---

[↑ Index](./README.md) · [← Prev](./14-dns-lookups-fail-intermittently-cluster-wide.md) · [Next →](./16-a-node-hits-diskpressure-and-evicts-pods.md)
