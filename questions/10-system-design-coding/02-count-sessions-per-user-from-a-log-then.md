# Count sessions per user from a `timestamp, user, action` log. Then scale past memory.

[↑ Index](./README.md) · [← Prev](./01-design-a-rate-limiter-under-a-target-qps.md) · [Next →](./03-design-multi-region-kubernetes.md)

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

---

[↑ Index](./README.md) · [← Prev](./01-design-a-rate-limiter-under-a-target-qps.md) · [Next →](./03-design-multi-region-kubernetes.md)
