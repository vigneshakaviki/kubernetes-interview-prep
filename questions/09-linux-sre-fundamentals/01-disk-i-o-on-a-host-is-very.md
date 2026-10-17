# Disk I/O on a host is very high. Find the cause.

[↑ Index](./README.md) · [Next →](./02-what-load-average-counts-as-high-and-what.md)

**Difficulty:** Medium · **Tags:** `linux` `performance`

**Confirm it's I/O-bound first:** `vmstat 1` (high `wa`), `top` (processes in **D state**).
```bash
iostat -x 1     # %util (saturated near 100), await (latency/IO), r/s w/s
iotop           # which process (or pidstat -d 1)
lsof -p <pid>   # which files
```
**Check swap:** `si`/`so` in vmstat — if swapping, the real problem is **memory**, not disk.

**Fix by category:** runaway query/job (throttle/fix) · log flood (rotate/ship) · swap
thrash (memory) · failing disk (`dmesg`, `smartctl`).

**K8s tie-in:** node I/O is often one Pod without I/O limits, or emptyDir/log growth filling
the node disk → `DiskPressure` eviction. Correlate to the cgroup/Pod.

---

[↑ Index](./README.md) · [Next →](./02-what-load-average-counts-as-high-and-what.md)
