# Pods are `Running` but none are `Ready` and the Service is dead. What's wrong?

[↑ Index](./README.md) · [← Prev](./03-a-pod-is-in-find-the-cause-and.md) · [Next →](./05-pods-restart-specifically-during-traffic-spikes-diagnose-it.md)

**Difficulty:** Medium · **Tags:** `probes` `networking`

**`Running` = process; `Ready` = traffic-eligible.** The gap is almost always the
**readiness probe**: wrong port/path, dependency down, slow boot (needs startup probe), or
too-expensive probe.

**Check:** Pod conditions + probe events → **test the readiness endpoint from inside the
Pod** (separates "app not ready" from "probe misconfigured").

**Why it's urgent:** unready Pods are pulled from **EndpointSlices** → Service has no
backends → clients get 503 though every Pod is "up." A readiness probe gated on a flaky
downstream takes the whole service offline when that downstream blips.

---

[↑ Index](./README.md) · [← Prev](./03-a-pod-is-in-find-the-cause-and.md) · [Next →](./05-pods-restart-specifically-during-traffic-spikes-diagnose-it.md)
