# Linux & SRE Fundamentals

The host is where "the Pod is fine but the node is on fire" incidents get solved. Answer
like someone who's been paged, not a man-page.

### Q: Disk I/O on a host is very high. Find the cause.

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

### Q: What load average counts as "high," and what does it measure?

**Difficulty:** Easy · **Tags:** `linux`

**It's not pure CPU** — Linux load = processes **runnable OR in uninterruptible (D) sleep**
(includes I/O wait), EW-averaged over 1/5/15 min.

- `load ≈ nproc` → fully used; `load/nproc > 1` → queuing; `> 2–3×` → trouble.
- Read the **1/5/15 triple** for direction.

**Skill:** load 30 on 8 cores could be CPU-bound (`top` high `%us`) **or** I/O-wait (D-state
on slow disk, CPUs idle) — opposite fixes. Cross-check `top`/`vmstat`.

---

### Q: Hard link vs soft link — real differences and where each breaks.

**Difficulty:** Easy · **Tags:** `linux` `filesystem`

| | Hard link | Soft (symlink) |
|--|-----------|----------------|
| Is | 2nd dir entry → same **inode** | small file holding a **path** |
| Cross-FS / dirs | no | yes |
| Delete original | data survives (until last link) | **dangles** (broken) |

**Examples:** log rotation + deploy `current →` symlinks use **soft** (atomic repoint across
dirs); dedup/backup tools use **hard** (many names, same bytes, no copy).

---

### Q: `df` and `du` disagree. Why, and how do you find the culprit?

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

### Q: A machine's CPU spikes. Handle it start to finish.

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

### Q: Service latency is high. Use `netstat`/`ss`, `tcpdump`, `traceroute` to localize it.

**Difficulty:** Medium · **Tags:** `networking` `troubleshooting`

- **`traceroute`/`mtr`** — per-hop latency/loss (prove/exonerate the network).
- **`ss`/`netstat`** — socket state: backlog overflow (app not accepting), piles of
  `TIME_WAIT`/`CLOSE_WAIT` (churn/leak), retransmits, ephemeral-port exhaustion.
- **`tcpdump`** — slow SYN/SYN-ACK (setup), retransmits (loss), gap before first byte
  (server think-time vs network), TLS handshake stalls.

Combine with app traces to split **network time** from **server time**.

**K8s tie-in:** latency often comes from plumbing — conntrack exhaustion, DNS `ndots:5`
amplification, iptables rule bloat, SNAT/`externalTrafficPolicy` hops.

---

### Q: `dig` vs `nslookup`?

**Difficulty:** Easy · **Tags:** `networking` `dns`

- **`dig`** — precise, scriptable, full sections, `@resolver` targeting, **`+trace`** (root →
  TLD → authoritative). Use for debugging.
- **`nslookup`** — older, interactive, less precise (does internal lookups).

```bash
dig +trace name          # where resolution breaks
dig name @1.1.1.1        # compare resolvers (stale/split-horizon)
```
**K8s:** `dig` from inside a Pod against kube-dns to reproduce what the app's resolver sees;
check `ndots`/search-domain amplification.

---

### Q: Linux signals — SIGTERM vs SIGKILL vs SIGHUP — and the K8s mapping.

**Difficulty:** Easy · **Tags:** `linux` `processes`

| Signal | Behavior |
|--------|----------|
| **SIGTERM (15)** | polite, **catchable** → flush/cleanup/exit; default `kill` |
| **SIGKILL (9)** | **uncatchable**, instant, no cleanup → last resort |
| **SIGHUP (1)** | daemons conventionally **reload config** |

**K8s mirror:** delete → preStop hook → **SIGTERM** → wait `terminationGracePeriodSeconds`
(30) → **SIGKILL**.
- PID 1 must **forward SIGTERM** to children (shell-form CMD swallows it → use exec form or
  `tini`). Grace period must exceed longest in-flight request, or graceful shutdown is a lie.

---

### Q: Walk through a DNS lookup, app call to answer.

**Difficulty:** Medium · **Tags:** `networking` `dns`

1. `getaddrinfo` → **`nsswitch.conf`** order → cache → **`/etc/hosts`** → DNS.
2. Query resolver(s) in **`/etc/resolv.conf`**.
3. Recursive resolver: **root → TLD → authoritative**, caching per **TTL**.
4. Answer returns → app connects. Debug: `dig +trace`.

**K8s:** Pod `resolv.conf` → CoreDNS + search domains + **`ndots:5`** → a non-FQDN name
tries several cluster suffixes **before** external → one lookup becomes 4–5 queries. Fix:
NodeLocal DNSCache, FQDNs. "DNS slow" is usually this amplification, not unhealthy CoreDNS.

---

### Q: Show an `awk` one-liner and when awk is the right tool.

**Difficulty:** Easy · **Tags:** `linux` `scripting`

awk = line/field processor (`$1`, `$NF`, `pattern { action }`).
```bash
awk '{bytes[$1]+=$10} END{for(ip in bytes) print ip,bytes[ip]}' access.log   # bytes per IP
awk '{c[$1]++} END{for(i in c) print c[i],i}' access.log | sort -rn | head    # top talkers
```
**Use for:** column-oriented, aggregate-as-you-stream text — sum/count/filter per key on huge
files, no full load. Graduate to a script when logic gets stateful (JSON → `jq`). During an
incident, a one-pass awk aggregation is often the fastest "which client/endpoint is causing
this."

---

### Q: How is monitoring set up on the systems you run, end to end?

**Difficulty:** Medium · **Tags:** `sre` `monitoring`

**Three pillars + response:** metrics (exporters + app `/metrics` → Prometheus → Grafana),
logs (shipped + aggregated — Loki/ELK), traces → **alerting on SLOs/golden signals** routed
by severity, every alert runbook-linked.

**SRE framing (vs "we have Grafana"):** page on **user-facing symptoms / SLO burn**, not
every cause; dashboards for root-cause *once engaged*; cluster internals (restarts, node
pressure, etcd latency) are **leading indicators** you trend, not page on.

**Gotcha:** the monitoring system needs the same rigor — bounded cardinality, tested alert
routing, pruned noisy alerts.
