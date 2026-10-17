# How does an Ingress handle TLS + path routing, and what's its relationship to the controller?

[↑ Index](./README.md) · [← Prev](./09-how-do-pods-discover-each-other-dns-vs.md)

**Difficulty:** Intermediate · **Tags:** `networking` `ingress`

- **Rules** — match host + path → backend Service. `pathType`: `Prefix` / `Exact` /
  `ImplementationSpecific`.
- **TLS** — references a Secret per host; controller **terminates TLS** at the edge
  (cert-manager automates certs).

**Crucial:** the **Ingress object does nothing alone** — a running **ingress controller**
watches it and programs the proxy. "My Ingress isn't working" is often no controller
installed, or `ingressClassName` mismatch.

**Note:** controller-specific behavior lives in **annotations** → non-portable, which is
why the **Gateway API** exists (typed, portable, role-oriented successor).

---

[↑ Index](./README.md) · [← Prev](./09-how-do-pods-discover-each-other-dns-vs.md)
