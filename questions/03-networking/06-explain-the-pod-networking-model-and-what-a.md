# Explain the Pod networking model and what a CNI is responsible for.

[↑ Index](./README.md) · [← Prev](./05-headless-service-how-it-differs-at-dns-level.md) · [Next →](./07-kube-proxy-iptables-vs-ipvs-what-breaks-at.md)

**Difficulty:** Advanced · **Tags:** `networking` `cni`

**Model (hard rules):** every Pod has its own IP · all Pods reach each other **without
NAT** · the IP a Pod sees == the IP others use. K8s delegates this to a **CNI** plugin.

**CNI responsibilities:**
- **IPAM** — allocate Pod IP from the node/cluster CIDR.
- Wire the Pod netns (veth → bridge or direct routes).
- Cross-node routing: **overlay** (VXLAN/Geneve — works anywhere, costs overhead + MTU) or
  **native routing / BGP** (faster, needs underlay support).
- Often **NetworkPolicy enforcement** + extras (eBPF kube-proxy replacement; VPC-native
  IPs that can exhaust ENIs).

**Framing:** CNI choice drives IP density, encapsulation overhead, policy enforcement, and
VPC integration — an architectural decision, not a checkbox.

---

[↑ Index](./README.md) · [← Prev](./05-headless-service-how-it-differs-at-dns-level.md) · [Next →](./07-kube-proxy-iptables-vs-ipvs-what-breaks-at.md)
