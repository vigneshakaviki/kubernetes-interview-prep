# Job vs CronJob — the knobs that decide correctness under failure.

[↑ Index](./README.md) · [← Prev](./08-multi-container-pod-patterns-and-how-to-decide.md) · [Next →](./10-emptydir-vs-hostpath-vs-pvc-when-each-and.md)

**Difficulty:** Intermediate · **Tags:** `workloads`

**Job knobs:**
- `completions` / `parallelism` — how many successes, how many at once.
- `backoffLimit` — retries before Failed (too high hides a broken job).
- `activeDeadlineSeconds` — hard wall-clock timeout for a hung job.
- `restartPolicy` — `OnFailure` (restart in place) vs `Never` (new pod per attempt, clean logs).

**CronJob knobs:**
- `concurrencyPolicy` — **Allow** (overlap, idempotent jobs), **Forbid** (skip if prior
  running), **Replace** (kill old, start new). ← most-missed.
- `startingDeadlineSeconds` — how late a missed run may still fire.
- `successfulJobsHistoryLimit` / `failedJobsHistoryLimit` — stop Job objects piling up.

**Gotcha:** CronJobs are **at-least-once-ish, not exactly-once** — the job itself must
be **idempotent**. Relying on the scheduler for correctness is the bug.

---

[↑ Index](./README.md) · [← Prev](./08-multi-container-pod-patterns-and-how-to-decide.md) · [Next →](./10-emptydir-vs-hostpath-vs-pvc-when-each-and.md)
