# How do Pods discover each other — DNS vs env vars — and why is one a trap?

[↑ Index](./README.md) · [← Prev](./08-what-does-a-service-mesh-add-over-plain.md) · [Next →](./10-how-does-an-ingress-handle-tls-path-routing.md)

**Difficulty:** Intermediate · **Tags:** `networking` `dns`

- **Env vars** — `<SVC>_SERVICE_HOST/PORT` injected, **only for Services that existed when
  the Pod started**. The trap: a Pod started before its dependency's Service won't have the
  var → unreachable until recreated. Hidden startup-order coupling → "worked yesterday,
  broke after a restart."
- **DNS** (CoreDNS) — resolvable anytime at `name.ns.svc.cluster.local`, no ordering. **Use
  DNS.**

---

[↑ Index](./README.md) · [← Prev](./08-what-does-a-service-mesh-add-over-plain.md) · [Next →](./10-how-does-an-ingress-handle-tls-path-routing.md)
