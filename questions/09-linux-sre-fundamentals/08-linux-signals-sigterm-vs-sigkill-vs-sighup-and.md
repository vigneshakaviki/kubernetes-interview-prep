# Linux signals — SIGTERM vs SIGKILL vs SIGHUP — and the K8s mapping.

[↑ Index](./README.md) · [← Prev](./07-vs.md) · [Next →](./09-walk-through-a-dns-lookup-app-call-to.md)

**Difficulty:** Easy · **Tags:** `linux` `processes`

| Signal | Behavior |
|--------|----------|
| **SIGTERM (15)** | polite, **catchable** → flush/cleanup/exit; default `kill` |
| **SIGKILL (9)** | **uncatchable**, instant, no cleanup → last resort |
| **SIGHUP (1)** | daemons conventionally **reload config** |

**K8s mirror:** delete → preStop hook → **SIGTERM** → wait `terminationGracePeriodSeconds`
(30) → **SIGKILL**.
- PID 1 must **forward SIGTERM** to children (shell-form CMD swallows it → use exec form or
  `tini`). Grace period must exceed longest in-flight request, or graceful shutdown is a lie.

---

[↑ Index](./README.md) · [← Prev](./07-vs.md) · [Next →](./09-walk-through-a-dns-lookup-app-call-to.md)
