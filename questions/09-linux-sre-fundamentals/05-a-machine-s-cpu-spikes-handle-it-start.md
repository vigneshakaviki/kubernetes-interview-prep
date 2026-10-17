# A machine's CPU spikes. Handle it start to finish.

[↑ Index](./README.md) · [← Prev](./04-and-disagree-why-and-how-do-you-find.md) · [Next →](./06-service-latency-is-high-use-to-localize-it.md)

**Difficulty:** Medium · **Tags:** `linux` `performance`

```bash
top / htop          # hot process
pidstat 1 / perf top # user vs system time, which threads/functions
vmstat 1            # separate compute from run-queue vs I/O-wait
```
- High **user** → app work; high **system** → syscalls/contention (locks, context switches,
  softirq). Profile (perf/pprof) for the hot path.

**Classify + act:** legitimate load → scale (HPA/CA) · regression → correlate deploy, **roll
back** · runaway/leak → throttle/restart while fixing. Mitigate reversibly first.

**K8s tie-in:** node spike is often a noisy Pod with no CPU request, or **CPU throttling** on
a Pod *with* a tight limit (shows as app latency, not node busyness).

---

[↑ Index](./README.md) · [← Prev](./04-and-disagree-why-and-how-do-you-find.md) · [Next →](./06-service-latency-is-high-use-to-localize-it.md)
