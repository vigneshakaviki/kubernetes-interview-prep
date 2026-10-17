# Walk through a DNS lookup, app call to answer.

[↑ Index](./README.md) · [← Prev](./08-linux-signals-sigterm-vs-sigkill-vs-sighup-and.md) · [Next →](./10-show-an-one-liner-and-when-awk-is.md)

**Difficulty:** Medium · **Tags:** `networking` `dns`

1. `getaddrinfo` → **`nsswitch.conf`** order → cache → **`/etc/hosts`** → DNS.
2. Query resolver(s) in **`/etc/resolv.conf`**.
3. Recursive resolver: **root → TLD → authoritative**, caching per **TTL**.
4. Answer returns → app connects. Debug: `dig +trace`.

**K8s:** Pod `resolv.conf` → CoreDNS + search domains + **`ndots:5`** → a non-FQDN name
tries several cluster suffixes **before** external → one lookup becomes 4–5 queries. Fix:
NodeLocal DNSCache, FQDNs. "DNS slow" is usually this amplification, not unhealthy CoreDNS.

---

[↑ Index](./README.md) · [← Prev](./08-linux-signals-sigterm-vs-sigkill-vs-sighup-and.md) · [Next →](./10-show-an-one-liner-and-when-awk-is.md)
