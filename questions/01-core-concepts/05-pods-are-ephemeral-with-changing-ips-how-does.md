# Pods are ephemeral with changing IPs — how does a Service give stable access, and what are EndpointSlices?

[↑ Index](./README.md) · [← Prev](./04-pod-vs-deployment-and-why-we-never-create.md) · [Next →](./06-i-point-at-lines-in-a-deployment-yaml.md)

**Difficulty:** Easy · **Tags:** `networking`

- **Service** = stable virtual IP + DNS (`name.ns.svc.cluster.local`) outliving any Pod;
  selects Pods by label.
- Control plane tracks which selected Pods are **Ready** and records their IPs in
  **EndpointSlices** (scalable successor to the single `Endpoints` object).
- kube-proxy/CNI load-balances to those live backends.

**Practical consequence:** a `Running`-but-**not-Ready** Pod is pulled from the slice →
stops getting traffic. An **empty EndpointSlice** (selector mismatch / no Ready Pods) is
the first thing to check on connection errors.

---

[↑ Index](./README.md) · [← Prev](./04-pod-vs-deployment-and-why-we-never-create.md) · [Next →](./06-i-point-at-lines-in-a-deployment-yaml.md)
