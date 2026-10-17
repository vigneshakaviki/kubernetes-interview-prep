# How does in-cluster DNS work, and how do you debug "can't resolve"?

[↑ Index](./README.md) · [← Prev](./02-what-is-a-networkpolicy-the-default-without-one.md) · [Next →](./04-clusterip-vs-nodeport-vs-loadbalancer-how-they-stack.md)

**Difficulty:** Medium · **Tags:** `networking` `dns`

- **CoreDNS** runs behind a ClusterIP Service. Each Pod's `/etc/resolv.conf` → that IP +
  search domains + `ndots:5`.
- Bare name in same namespace resolves via search domains; FQDN external name can incur
  several failed lookups first (the `ndots` tax).

**Debug order:**
1. Resolve a *known* name from the Pod (`nslookup kubernetes.default`) — total failure vs one name?
2. Check `/etc/resolv.conf`.
3. kube-dns Service has endpoints?
4. **CoreDNS Pods** Ready + logs.
5. NetworkPolicy blocking DNS egress?

**Gotcha:** don't restart CoreDNS reflexively — intermittent-under-load DNS is usually
`ndots` amplification / conntrack exhaustion, which a restart only hides. Fix: NodeLocal
DNSCache, `ndots` tuning / FQDNs.

---

[↑ Index](./README.md) · [← Prev](./02-what-is-a-networkpolicy-the-default-without-one.md) · [Next →](./04-clusterip-vs-nodeport-vs-loadbalancer-how-they-stack.md)
