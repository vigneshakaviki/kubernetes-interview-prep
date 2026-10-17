# What is Helm, what does it buy you, and when would you use Kustomize instead?

[↑ Index](./README.md) · [← Prev](./15-imperative-vs-declarative-kubectl-and-safely-rolling-back.md)

**Difficulty:** Intermediate · **Tags:** `packaging`

- **Helm** — package manager. A **chart** = templated manifests + `values.yaml`; installing
  it creates a **release** you can `upgrade`/`rollback`/`uninstall` as a unit. Solves
  templating/reuse + lifecycle.
- **Trade-off:** Go-templated YAML gets hard to read/debug as charts grow.
- **Kustomize** (`kubectl -k`) — template-free base + overlays patched per environment;
  cleaner for *your own* apps where you control the YAML.

**Rule:** Helm to consume third-party software (versioned releases, community charts);
Kustomize (or a GitOps tool rendering either) for your own services. Deciding factor =
who owns the manifests + whether you need packaged, versioned distribution.

---

[↑ Index](./README.md) · [← Prev](./15-imperative-vs-declarative-kubectl-and-safely-rolling-back.md)
