# A Pod is in `CrashLoopBackOff`. Find the cause — and why is the status misleading?

[↑ Index](./README.md) · [← Prev](./02-a-pod-fails-to-start-several-reasons-look.md) · [Next →](./04-pods-are-but-none-are-and-the-service.md)

**Difficulty:** Medium · **Tags:** `workloads` `troubleshooting`

**It's a symptom** — "container keeps exiting, kubelet backing off." The cause is *why*.

**Evidence:**
- `kubectl logs --previous` — the crashed instance's logs (current may be empty).
- Termination **reason + exit code**: non-zero app exit vs `OOMKilled` (137) vs signal.
- Restart count/timing; mounted config/Secrets; probe failures (aggressive liveness can
  *cause* the loop).
- **Correlate first restart** with a deploy / config edit / dependency outage.

**Mitigate:** roll back if a new version harms users — but preserve logs + spec first.

**Tells:** exit 0 looping = wrong command/entrypoint · 137 = memory, not a bug · crashes
only in prod = environment (config/secrets/policy/dependency).

---

[↑ Index](./README.md) · [← Prev](./02-a-pod-fails-to-start-several-reasons-look.md) · [Next →](./04-pods-are-but-none-are-and-the-service.md)
