# Explain informers, watch/list, resourceVersion — and why a controller must tolerate stale caches.

[↑ Index](./README.md) · [← Prev](./17-api-priority-and-fairness-what-it-protects.md)

**Difficulty:** Hard · **Tags:** `controllers` `architecture`

**Short answer:** Controllers don't poll — they **LIST then WATCH**, maintaining a local
cache (informer) updated by an event stream. That cache is **eventually consistent**, so
correct controllers reconcile from desired-vs-observed and tolerate staleness, never assume
their cache is authoritative *now*.

**The machinery:**
- **Informer** = Reflector (LIST to seed + WATCH to stream deltas) → DeltaFIFO → local
  **Indexer** (the cache) → event handlers enqueue keys → workqueue → reconcile.
- **resourceVersion** — an opaque etcd revision; WATCH resumes from the last seen RV. A
  stale/compacted RV → **410 Gone** → the informer **re-LISTs** (relist storm risk).
- **Periodic resync** — re-runs reconcile from cache to catch missed edge cases, *not* a
  re-fetch from etcd.

**Why tolerate staleness:**
- The cache lags etcd by the watch delay → you may act on an old object. So you reconcile
  **idempotently** toward spec, use **optimistic concurrency** (update carries RV → 409
  Conflict on stale write → requeue), and never `get` from the cache and assume it's live
  for a critical decision.

**Failure modes:** a hot relist loop (compaction/410) hammering the API (see APF); a
controller treating cache as truth and double-acting; dropped events on a slow handler.

---

[↑ Index](./README.md) · [← Prev](./17-api-priority-and-fairness-what-it-protects.md)
