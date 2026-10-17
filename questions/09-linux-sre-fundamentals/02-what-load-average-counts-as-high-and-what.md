# What load average counts as "high," and what does it measure?

[↑ Index](./README.md) · [← Prev](./01-disk-i-o-on-a-host-is-very.md) · [Next →](./03-hard-link-vs-soft-link-real-differences-and.md)

**Difficulty:** Easy · **Tags:** `linux`

**It's not pure CPU** — Linux load = processes **runnable OR in uninterruptible (D) sleep**
(includes I/O wait), EW-averaged over 1/5/15 min.

- `load ≈ nproc` → fully used; `load/nproc > 1` → queuing; `> 2–3×` → trouble.
- Read the **1/5/15 triple** for direction.

**Skill:** load 30 on 8 cores could be CPU-bound (`top` high `%us`) **or** I/O-wait (D-state
on slow disk, CPUs idle) — opposite fixes. Cross-check `top`/`vmstat`.

---

[↑ Index](./README.md) · [← Prev](./01-disk-i-o-on-a-host-is-very.md) · [Next →](./03-hard-link-vs-soft-link-real-differences-and.md)
