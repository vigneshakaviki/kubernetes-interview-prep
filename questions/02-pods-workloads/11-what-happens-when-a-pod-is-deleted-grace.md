# What happens when a Pod is deleted — grace period, preStop, SIGTERM — and why a short grace period drops requests.

[↑ Index](./README.md) · [← Prev](./10-emptydir-vs-hostpath-vs-pvc-when-each-and.md) · [Next →](./12-controlled-canary-of-a-statefulset.md)

**Difficulty:** Intermediate · **Tags:** `lifecycle`

**Sequence on delete:**
1. `deletionTimestamp` set → Pod `Terminating`.
2. **In parallel:** removed from EndpointSlices (new traffic stops — *eventually*) **and**
   kubelet runs **preStop** hook → sends **SIGTERM** to PID 1.
3. App drains (stop accepting, finish in-flight).
4. After `terminationGracePeriodSeconds` (default 30) → **SIGKILL**.

**Two causes of dropped requests:**
- Grace period **shorter than longest in-flight request** → SIGKILL mid-request.
- **Endpoint-removal vs SIGTERM race** — endpoint updates propagate async, so a load
  balancer may send new requests to a pod that *already* got SIGTERM → errors at the
  *start* of termination.

**Fix:** a **preStop `sleep`** (few seconds) lets endpoint removal propagate while the
app still serves, + grace period > p99 request time + a real SIGTERM handler. Graceful
shutdown is a distributed-systems **race**, not just "handle the signal."

---

[↑ Index](./README.md) · [← Prev](./10-emptydir-vs-hostpath-vs-pvc-when-each-and.md) · [Next →](./12-controlled-canary-of-a-statefulset.md)
