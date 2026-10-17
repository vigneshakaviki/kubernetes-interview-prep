# System Design & Coding

SRE coding is less about hard algorithms and more about log/text processing and practical
system design (rate limiters, monitoring, health registries). The interviewer wants
production reasoning — failure modes, idempotency, distributed consistency — not just a
working function.

### Q: Design a rate limiter that keeps API calls under a target QPS. Then make it work across many servers.

**Difficulty:** Medium · **Tags:** `system-design`

Single-node first. **Token bucket** is the usual choice: tokens refill at the limit rate up
to a bucket depth, each request spends one, and an empty bucket rejects (or queues). The
depth allows controlled **bursts** while the refill enforces the average rate — this is why
it's preferred over a naive fixed counter. **Sliding window** (log or weighted counter)
counts requests in a moving window and avoids the **boundary spike** of fixed windows (where
a client can send 2× the limit across a window edge). Leaky bucket is the variant when you
want a perfectly smooth output rate (shaping, not just limiting).

The follow-up is always **distributed**, and it's the real test: per-node limits don't
enforce a global QPS, so you either (a) keep counters in a **shared store** (Redis) with an
**atomic** increment/check — a Lua script or `INCR`+`EXPIRE` so the read-modify-write is
race-free — accepting the latency and the store as a dependency, or (b) keep **local** limits
(global_limit / N nodes) with periodic sync, accepting approximate enforcement for lower
latency and no hard dependency. Name the trade-offs: **fail-open vs fail-closed** when the
limiter/store is unavailable (open = availability over protection, closed = protection over
availability — pick per endpoint), clock/skew handling for windows, hot-key contention on a
single counter (shard the key), and fairness across clients (per-API-key buckets). Staff-
level answer leads with "what are we protecting and what happens when the limiter itself
fails," because a rate limiter that takes down the API when Redis blips is worse than no
limiter.

---

### Q: Given a log file of `timestamp, user, action` lines, count sessions per user. Then scale it to a file that doesn't fit in memory.

**Difficulty:** Medium · **Tags:** `coding` `logs`

Define a session first (ask the interviewer): typically events for a user with gaps under a
timeout T belong to one session; a gap ≥ T starts a new one. In-memory approach: group
events by user, sort each user's events by timestamp, then sweep — increment the session
count whenever the gap since that user's previous event exceeds T. Complexity is
`O(n log n)` dominated by the sort; one linear pass per user after grouping. Watch the edge
cases interviewers probe: out-of-order timestamps (must sort, can't assume order),
tie-breaking at exactly T, and events from many users interleaved.

The scale follow-up is the point: for a file that doesn't fit in memory, you can't hold all
events. Options — **(1)** if the log is already roughly time-ordered, stream it and keep only
per-user *last-seen timestamp* + *session count* in a hash map (O(number of users) memory,
single pass, O(n) time); **(2)** if not ordered and users don't fit in memory either,
**external sort** by (user, timestamp) then a single streaming pass, or shard by
`hash(user)` across workers (map-reduce) so each worker handles a user subset that fits.
The framing: state your memory assumption explicitly, prefer the **single-pass
bounded-memory** solution when the data is ordered (which real log streams usually are), and
recognize this is a streaming/aggregation problem — the same shape as computing sessions in a
metrics pipeline — not a clever-algorithm problem. Mention you'd handle malformed lines and
clock skew, because real logs have both.
