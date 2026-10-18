# How do K8s memory limits map to cgroups, and why does the JVM/Go see the wrong memory?

[↑ Index](./README.md) · [← Prev](./11-how-is-monitoring-set-up-on-the-systems.md) · [Next →](./13-time-wait-pileup-and-ephemeral-port-exhaustion.md)

**Difficulty:** Hard · **Tags:** `linux` `resources`

**Short answer:** A memory **limit** is a **cgroup** `memory.max` (v2) / `memory.limit_in_bytes`
(v1) on the container. Runtimes that read **host** memory instead of the cgroup
over-allocate and get **OOMKilled** by the kernel.

**The mechanism:**
- Container runtime puts each container in a cgroup; the memory limit sets the cgroup cap.
  Exceed it → kernel **OOM killer** targets a process in that cgroup (exit 137), *not* the
  whole node.
- **cgroup v2** (default on modern distros) unifies the hierarchy (`memory.max`,
  `memory.high` for throttling-before-kill) — cleaner accounting than v1.

**Why runtimes get it wrong:**
- Old JVMs read `/proc/meminfo` (**host** RAM, e.g. 64Gi) and size the heap to that, ignoring
  a 512Mi cgroup limit → heap grows → **OOMKilled** despite "plenty of free RAM" on the node.
- Fix: cgroup-aware flags. JVM: `-XX:MaxRAMPercentage` (modern JDKs are container-aware).
  Go: set **`GOMEMLIMIT`** to ~the cgroup limit so the GC runs harder *before* the kernel
  kills it (Go's GC otherwise doesn't know the cap). Node: `--max-old-space-size`.

**Tell:** "OOMKilled but the node has free memory" = a runtime sized to host RAM, not the
cgroup limit. The fix is a runtime memory ceiling, not a bigger limit.

---

[↑ Index](./README.md) · [← Prev](./11-how-is-monitoring-set-up-on-the-systems.md) · [Next →](./13-time-wait-pileup-and-ephemeral-port-exhaustion.md)
