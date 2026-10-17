# One Service returns intermittent 503s. Debug it.

[↑ Index](./README.md) · [← Prev](./05-pods-restart-specifically-during-traffic-spikes-diagnose-it.md) · [Next →](./07-a-deployment-rollout-is-stuck-what-now.md)

**Difficulty:** Hard · **Tags:** `networking` `dns`

**Intermittent = a subset is bad → split errors** by Pod / version / node / zone:
- One version → bad deploy · one node/zone → infra · evenly → upstream (DNS/policy/Service).

**Walk the path:** Service ports → selector → **EndpointSlices** → readiness → direct Pod
curl → DNS → NetworkPolicy.
- **Empty slice** → selector mismatch / no Ready Pods.
- **Populated, one endpoint failing** → bad Pod/node, pull it.

**Tells:** 503s at the rollout boundary = termination race (SIGTERM while still in endpoints
→ preStop sleep) · 503s under load with healthy Pods = connection-pool/keep-alive imbalance
(L4 pinning). Don't restart CoreDNS reflexively.

---

[↑ Index](./README.md) · [← Prev](./05-pods-restart-specifically-during-traffic-spikes-diagnose-it.md) · [Next →](./07-a-deployment-rollout-is-stuck-what-now.md)
