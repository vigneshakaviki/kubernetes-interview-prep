# `df` and `du` disagree. Why, and how do you find the culprit?

[↑ Index](./README.md) · [← Prev](./03-hard-link-vs-soft-link-real-differences-and.md) · [Next →](./05-a-machine-s-cpu-spikes-handle-it-start.md)

**Difficulty:** Medium · **Tags:** `linux` `filesystem`

- `du` sums files it can **see**; `df` asks the **filesystem** for allocated blocks.
- **Classic divergence:** a file **deleted but still held open** — `unlink` removes the dir
  entry (du can't see it) but blocks aren't freed until the fd closes (df still counts them).
  "Deleted the huge log, df still full."

```bash
lsof | grep deleted     # or: lsof +L1  → the process + fd holding it
: > /proc/<pid>/fd/<n>  # or restart the process to release
```
**Also:** sparse files (apparent vs allocated), reserved blocks (ext4 ~5%), mount shadowing.
Naming the deleted-open-file case first is the senior tell.

---

[↑ Index](./README.md) · [← Prev](./03-hard-link-vs-soft-link-real-differences-and.md) · [Next →](./05-a-machine-s-cpu-spikes-handle-it-start.md)
