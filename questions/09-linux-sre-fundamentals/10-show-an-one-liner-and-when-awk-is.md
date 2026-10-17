# Show an `awk` one-liner and when awk is the right tool.

[↑ Index](./README.md) · [← Prev](./09-walk-through-a-dns-lookup-app-call-to.md) · [Next →](./11-how-is-monitoring-set-up-on-the-systems.md)

**Difficulty:** Easy · **Tags:** `linux` `scripting`

awk = line/field processor (`$1`, `$NF`, `pattern { action }`).
```bash
awk '{bytes[$1]+=$10} END{for(ip in bytes) print ip,bytes[ip]}' access.log   # bytes per IP
awk '{c[$1]++} END{for(i in c) print c[i],i}' access.log | sort -rn | head    # top talkers
```
**Use for:** column-oriented, aggregate-as-you-stream text — sum/count/filter per key on huge
files, no full load. Graduate to a script when logic gets stateful (JSON → `jq`). During an
incident, a one-pass awk aggregation is often the fastest "which client/endpoint is causing
this."

---

[↑ Index](./README.md) · [← Prev](./09-walk-through-a-dns-lookup-app-call-to.md) · [Next →](./11-how-is-monitoring-set-up-on-the-systems.md)
