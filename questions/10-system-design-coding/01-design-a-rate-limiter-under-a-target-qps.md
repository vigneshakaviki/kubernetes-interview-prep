# Design a rate limiter under a target QPS. Then make it work across many servers.

[↑ Index](./README.md) · [Next →](./02-count-sessions-per-user-from-a-log-then.md)

**Difficulty:** Medium · **Tags:** `system-design`

**Single node:**
| Algorithm | Behavior |
|-----------|----------|
| **Token bucket** | refill at rate, spend per request, depth allows **bursts** — usual choice |
| **Sliding window** | count in a moving window — avoids fixed-window **boundary spike** |
| **Leaky bucket** | perfectly smooth output rate (shaping) |

**Distributed (the real test):**
- **Shared store (Redis)** — atomic `INCR`+`EXPIRE` / Lua so read-modify-write is race-free.
  Cost: latency + a dependency.
- **Local limits** (global/N) + periodic sync — approximate, lower latency, no hard dep.

**Name the trade-offs:** **fail-open vs fail-closed** when the limiter is down (open =
availability, closed = protection — per endpoint) · hot-key contention (shard the key) ·
per-API-key fairness.

**Lead with:** "what are we protecting, and what happens when the limiter itself fails" — a
limiter that takes down the API when Redis blips is worse than none.

---

[↑ Index](./README.md) · [Next →](./02-count-sessions-per-user-from-a-log-then.md)
