# Pods restart specifically during traffic spikes. Diagnose it.

[↑ Index](./README.md) · [← Prev](./04-pods-are-but-none-are-and-the-service.md) · [Next →](./06-one-service-returns-intermittent-503s-debug-it.md)

**Difficulty:** Hard · **Tags:** `resources` `oom`

Three mechanisms — **telling them apart is the whole game:**
- **Memory limit breach → OOMKilled** (hard, `reason: OOMKilled`, exit 137). ← "restarts on
  spike" is usually this.
- **CPU limit breach → throttled** (slow, *not* killed).
- **Node-pressure eviction** → check node `MemoryPressure`/`DiskPressure`/`PIDPressure`.

**The trap:** raising the memory limit blindly just **moves the failure** — the Pod now
consumes more → the whole **node** hits pressure → evicts *other* tenants → node-wide
incident.

**Decide:** legitimate load (scale deliberately) · leak (fix app) · cold-cache thundering
herd (warm/stagger). And don't confuse CPU throttling (shows as latency) with true OOM.

---

[↑ Index](./README.md) · [← Prev](./04-pods-are-but-none-are-and-the-service.md) · [Next →](./06-one-service-returns-intermittent-503s-debug-it.md)
