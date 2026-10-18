# Memory climbs all day, then Pods OOM every night. Leak or not?

[↑ Index](./README.md) · [← Prev](./18-a-node-drain-wont-complete-during-an-upgrade.md)

**Difficulty:** Hard · **Tags:** `resources` `oom`

**Short answer:** A sawtooth that always OOMs at peak is either a **real leak** or a
**cache/working-set that legitimately exceeds the limit at peak load** — and you must tell
them apart before "just raise the limit."

**Distinguish:**
- Plot **RSS / working set** over days. Leak → climbs and **never recovers** even when
  traffic drops. Cache/load → tracks traffic, drops off-peak.
- Check what the growth *is* (heap profile / pprof / jmap). Unbounded in-memory cache, a
  goroutine/connection leak, or an ever-growing buffer?

**Causes:** genuine leak (unclosed resources, unbounded cache) · cache with no eviction
cap · `GOMEMLIMIT`/JVM heap unset so the runtime doesn't know the cgroup limit and grows
until the kernel OOMKills it.

**Mitigate:** right-size the **memory limit** to real peak + set a runtime memory ceiling
(`GOMEMLIMIT`, `-XX:MaxRAMPercentage`) so the app GCs instead of getting OOMKilled. **Don't
just raise the limit on a leak** — it delays the OOM, doesn't fix it, and risks taking the
**node** down. **Prevent:** cap caches, alert on working-set trend, load-test for leaks.

---

[↑ Index](./README.md) · [← Prev](./18-a-node-drain-wont-complete-during-an-upgrade.md)
