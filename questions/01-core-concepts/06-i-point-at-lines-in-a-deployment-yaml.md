# I point at lines in a Deployment YAML — which fields must you explain, and which mismatches silently break things?

[↑ Index](./README.md) · [← Prev](./05-pods-are-ephemeral-with-changing-ips-how-does.md) · [Next →](./07-write-a-dockerfile-for-a-python-service-and.md)

**Difficulty:** Medium · **Tags:** `workloads` `yaml`

**Know cold:**
- `spec.replicas` — desired count.
- `spec.selector.matchLabels` — which Pods it owns; **immutable** after creation.
- `spec.template.metadata.labels` — must be a superset of the selector or apply is rejected.
- `containers[]`: `image` (digest/immutable tag, never `latest`), `ports`, `env`/`envFrom`,
  `resources.requests|limits`, probes.
- `strategy` — `maxSurge` / `maxUnavailable`.

**Silent breakers:** selector ≠ template labels (orphaned Pods) · `latest` tag (a "no-op"
apply pulls a changed image) · no requests (bad placement, HPA has no baseline) ·
`maxUnavailable` too high (rollout drops capacity under load).

---

[↑ Index](./README.md) · [← Prev](./05-pods-are-ephemeral-with-changing-ips-how-does.md) · [Next →](./07-write-a-dockerfile-for-a-python-service-and.md)
