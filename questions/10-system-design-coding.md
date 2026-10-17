# System Design & Coding

SRE coding = log/text processing + practical design (rate limiters, monitoring), not hard
algorithms. They want production reasoning — failure modes, idempotency, consistency.

### Q: Design a rate limiter under a target QPS. Then make it work across many servers.

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

### Q: Count sessions per user from a `timestamp, user, action` log. Then scale past memory.

**Difficulty:** Medium · **Tags:** `coding` `logs`

**Define a session first** (ask): events for a user with gaps < timeout T = one session.

**In-memory:** group by user → sort by timestamp → sweep, new session when gap ≥ T.
`O(n log n)` (sort-dominated). Edge cases: out-of-order timestamps, tie at exactly T,
interleaved users.

**Scale past memory (the point):**
- **Log roughly time-ordered** → stream, keep only per-user *last-seen + count* in a map.
  `O(users)` memory, single pass, `O(n)`. ← prefer this.
- **Not ordered + users don't fit** → external sort by (user, timestamp) + streaming pass,
  **or** shard by `hash(user)` across workers (map-reduce).

**Framing:** state your memory assumption, prefer single-pass bounded-memory when ordered
(real log streams usually are). It's a streaming/aggregation problem, not a clever-algorithm
one. Handle malformed lines + clock skew — real logs have both.
