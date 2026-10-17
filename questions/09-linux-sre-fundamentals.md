# Linux & SRE Fundamentals

SRE screens still lean hard on Linux and network internals — the host is where "the Pod is
fine but the node is on fire" incidents get solved. Answer these like someone who has
actually been paged, not like a man-page.

### Q: Disk I/O on a host is very high. Walk me through finding the cause.

**Difficulty:** Medium · **Tags:** `linux` `performance`

Confirm it's really I/O-bound before chasing ghosts: `vmstat 1` (high `wa`/iowait) and
`top` (processes in uninterruptible **D state**) tell you the CPU is waiting on disk. Then
quantify the device with `iostat -x 1` — watch `%util` (near 100% = saturated), `await`
(latency per I/O), and `r/s`/`w/s` + throughput. Attribute it to a process with `iotop` (or
`pidstat -d 1`), then to *what* that process is doing: `lsof -p <pid>` for the files,
whether it's a bad query, a log flood, checkpointing, or **swap thrashing** (check
`si`/`so` in vmstat — if the box is swapping, the real problem is memory, not disk).

Having found it, decide the fix by category: a runaway query/job (fix the app or throttle
it), log volume (rotate/ship instead of writing locally), swap thrash (add memory / fix the
leak), or a genuinely undersized/failing disk (`dmesg`, `smartctl` for hardware errors;
move to faster storage). The nuance on Kubernetes: high node I/O is often **one
noisy Pod** without I/O limits starving others, or **emptyDir/log growth filling the node
disk**, which then triggers `DiskPressure` eviction — so correlate the host finding back to
which Pod/cgroup is responsible rather than treating the node in isolation.

---

### Q: What load average counts as "high," and what does load average actually measure?

**Difficulty:** Easy · **Tags:** `linux`

Load average is the exponentially-weighted count of processes **runnable or in
uninterruptible sleep (D state)** over 1/5/15 minutes — so on Linux it's *not* pure CPU
demand; it includes tasks blocked on I/O. "High" is therefore relative to core count:
load ≈ `nproc` means roughly fully utilized; sustained `load/nproc > 1` means tasks are
queuing; `> 2–3×` cores is real trouble. Always read the **1/5/15 triple** to see
direction — 1-min far above 15-min means a spike that's climbing; the reverse means it's
subsiding.

The interpretive skill is separating *why* load is high: a load of 30 on an 8-core box
could be CPU-bound work (then `top` shows high `%us`/`%sy` and run-queue depth) or it could
be **I/O wait** (processes stuck in D state on a slow disk/NFS, with CPUs actually idle) —
completely different problems with opposite fixes. The answer: don't treat load as
a single gauge; cross-check with `top`/`vmstat` to decide if you're CPU-saturated,
I/O-blocked, or memory-thrashing, because "load is high" alone tells you *that* something's
wrong, not *what*.

---

### Q: Hard link vs soft (symbolic) link — the real differences and where each breaks.

**Difficulty:** Easy · **Tags:** `linux` `filesystem`

A **hard link** is a second directory entry pointing at the *same inode* — same data, same
permissions, same everything; the file's data is only freed when the **last** hard link is
removed (the link count hits zero). Because it references an inode, it **cannot cross
filesystems** (inodes are filesystem-local) and traditionally cannot link directories. A
**soft/symbolic link** is a tiny separate file containing a *path* to the target; it can
cross filesystems, can point at directories, but **breaks (dangles)** if the target is
moved or deleted — because it only stores the path, not a reference to the data.

The practical consequences: deleting the original of a *hard* link leaves the data fully
intact (other links still reference the inode); deleting the target of a *soft* link leaves
a broken symlink. Soft links can also introduce a resolution hop and loops. The
example: log rotation and "current → versioned" deploy symlinks use **soft** links
deliberately so you can atomically repoint them across directories; hard links show up in
dedup/backup tooling where you want multiple names for the same bytes without copying.

---

### Q: `df` and `du` disagree on how much disk is used. Why, and how do you find the culprit?

**Difficulty:** Medium · **Tags:** `linux` `filesystem`

`du` walks the directory tree and sums the sizes of files it can **see**; `df` asks the
**filesystem** how many blocks are allocated. They diverge most famously when a file has
been **deleted but is still held open** by a running process: `unlink` removes the directory
entry (so `du` can no longer see it) but the inode's blocks aren't freed until the last file
descriptor closes — so `df` still counts them as used. The symptom: "I deleted the huge log,
but `df` still says the disk is full."

Find it with `lsof | grep deleted` (or `lsof +L1`), which lists open files with a link
count of zero — the process and fd holding the space. The fix is to get that process to
release the fd: truncate the file it's writing (`: > /proc/<pid>/fd/<n>` or `truncate -s 0`)
or restart/signal the process to reopen its log. The extras: the two can also differ
because of **sparse files** (apparent size vs allocated blocks), **filesystem overhead /
reserved blocks** (ext4 reserves ~5% for root), and **mount shadowing** (a mount over a
non-empty directory hides files `du` won't descend into). Naming the deleted-open-file case
first is the senior tell — it's the one that actually pages you.

---

### Q: A machine's CPU usage spikes. How do you handle it, start to finish?

**Difficulty:** Medium · **Tags:** `linux` `performance`

Find the hot process (`top`/`htop`), then characterize it: `pidstat 1` or `perf top` to see
**user vs system** time and which functions/threads burn CPU — user time points at the app's
own work, high system time points at syscalls/contention (lock spinning, excessive context
switches, softirq/network). Separate real compute from **run-queue contention** and from
**I/O wait** masquerading as "busy" (`vmstat`, load vs `nproc`). For a JVM/Go service, a
CPU profile (`perf`, async-profiler, pprof) pinpoints the hot path.

Then classify and act: **legitimate load** → scale out / add capacity (and in K8s let
HPA/Cluster-Autoscaler do it); **a regression** → correlate with the last deploy and **roll
back**; **a runaway/leak** (GC storm, infinite loop, retry amplification) → mitigate by
throttling/restarting the offender while you fix the code. Mitigate reversibly first
(protect the SLO), then fix root cause. The nuance on Kubernetes: a node CPU spike
is often one Pod without sensible CPU requests acting as a noisy neighbor, or **CPU
throttling** on a Pod *with* a tight CPU limit (which shows as app latency, not node
busyness) — so decide whether you're looking at the host, the cgroup, or a specific
workload before you touch anything.

---

### Q: Service latency is high. How do you use `netstat`/`ss`, `tcpdump`, and `traceroute` to localize it?

**Difficulty:** Medium · **Tags:** `networking` `troubleshooting`

Localize *where* the time goes before assuming it's the app. **`traceroute`/`mtr`** shows
per-hop latency and loss along the network path — useful to prove (or exonerate) the network
between client and server. **`ss`/`netstat`** inspects socket state on the host: a growing
**accept queue / backlog overflow** (the app isn't accepting fast enough), piles of
**`TIME_WAIT`/`CLOSE_WAIT`** (connection churn or a leak of unclosed sockets),
**retransmits**, or connection-pool/ephemeral-port exhaustion. **`tcpdump`** captures the
actual exchange — slow SYN/SYN-ACK (connection setup latency), retransmissions (loss), a
long gap before the first response byte (server think-time vs network), or TLS-handshake
stalls.

Combine with application traces so you can split **network time** (hops, retransmits,
handshake) from **server time** (the gap between request arrival and first response).
The framing on Kubernetes: added latency and jitter frequently come from the *plumbing*
— **conntrack table exhaustion** dropping connections, **DNS** (`ndots:5` amplification
turning one lookup into several) adding tail latency, kube-proxy **iptables** rule bloat at
scale, or SNAT/`externalTrafficPolicy` adding a hop and hiding the client IP — so a
latency investigation that only looks at the app misses the most common Kubernetes causes.

---

### Q: `dig` vs `nslookup` — which do you reach for and why?

**Difficulty:** Easy · **Tags:** `networking` `dns`

Both resolve names, but **`dig`** is the tool for debugging: precise, scriptable output with
the full answer/authority/additional sections, query flags, the ability to target a specific
resolver (`dig @8.8.8.8 name`), and **`+trace`** to walk the delegation from the root through
the TLD to the authoritative server — which is how you find *where* resolution breaks.
**`nslookup`** is older, more interactive/beginner-friendly, and its output is less precise
and sometimes misleading (it does its own internal lookups). For real diagnosis, `dig`.

The use: `dig +trace name` to see the full resolution chain; `dig name @<resolver>`
to compare what different resolvers return (cache poisoning / stale cache / split-horizon);
`dig +short` for scripts; and checking TTLs in the answer when you suspect caching is
serving stale records after a failover. In Kubernetes specifically you'd `dig` from inside a
Pod against the kube-dns Service IP to reproduce what the app's resolver sees, and check the
`ndots`/search-domain behavior that turns an external lookup into several cluster-domain
attempts first.

---

### Q: Explain Linux signals — SIGTERM vs SIGKILL vs SIGHUP — and how they map to Kubernetes Pod termination.

**Difficulty:** Easy · **Tags:** `linux` `processes`

**SIGTERM (15)** politely asks a process to terminate — it's **catchable**, so a
well-behaved process traps it to flush buffers, close connections, and exit cleanly; it's
the default of `kill`. **SIGKILL (9)** is **uncatchable and unblockable** — the kernel
destroys the process immediately with no cleanup, risking lost in-flight work or corrupt
state, so it's a last resort. **SIGHUP (1)** historically meant the controlling terminal
hung up, but daemons conventionally trap it to **reload configuration** without restarting.
(**SIGINT (2)** is Ctrl-C; **SIGSTOP/SIGCONT** pause/resume.)

Kubernetes mirrors this exactly: on Pod deletion the kubelet runs the optional **preStop**
hook, sends **SIGTERM** to the container's PID 1 for graceful drain, waits
`terminationGracePeriodSeconds` (default 30), then sends **SIGKILL** to whatever's left. So
an app that ignores SIGTERM gets hard-killed at the end of the grace period and drops
in-flight requests. The connections: the container's **PID 1 must actually forward
SIGTERM** to child processes (a shell-form `CMD` or a non-init PID 1 can swallow it — hence
`exec`-form entrypoints or a tiny init like `tini`), and the grace period must exceed your
longest in-flight request or graceful shutdown is a lie. Knowing that SIGKILL can't be
trapped is why you never rely on it for cleanup.

---

### Q: Walk through a DNS lookup from the application call to the answer.

**Difficulty:** Medium · **Tags:** `networking` `dns`

The app calls a resolver function (`getaddrinfo`), which consults **`nsswitch.conf`** for
the lookup order — typically local first: the in-process/OS cache, then **`/etc/hosts`**,
then DNS. For DNS it builds a query to the resolver(s) in **`/etc/resolv.conf`**. That
resolver, if recursive, does the real work: query a **root** server (→ referral to the TLD),
then the **TLD** server (→ referral to the authoritative nameserver), then the
**authoritative** server for the actual record, caching each result for its **TTL**. The
answer returns to the stub resolver and the app connects.

Debug it with `dig +trace` to watch that whole chain, and check the resolver config and TTLs
when results look stale. The Kubernetes version: a Pod's `/etc/resolv.conf` points
at the **CoreDNS** Service with search domains (`ns.svc.cluster.local`, …) and `ndots:5`,
which means a non-FQDN name tries several cluster-local suffixes *before* going external —
so a single external lookup can become 4–5 queries, amplifying load and tail latency. That's
why high-DNS-QPS clusters add **NodeLocal DNSCache** and why `ndots` tuning / using FQDNs
(trailing dot) is a real performance lever, and why "DNS is slow" is often this amplification
rather than CoreDNS being unhealthy.

---

### Q: Show me an `awk` one-liner and explain when awk is the right tool.

**Difficulty:** Easy · **Tags:** `linux` `scripting`

awk is a line-and-field processor: it splits each input line into fields (`$1`, `$2`, …,
`$NF` is the last) and runs `pattern { action }` blocks. A common SRE one-liner — sum a
numeric column grouped by a key, e.g. total bytes per source IP from a log:

```bash
awk '{ bytes[$1] += $10 } END { for (ip in bytes) print ip, bytes[ip] }' access.log
```

Or top talkers by request count: `awk '{c[$1]++} END{for(i in c) print c[i], i}' access.log
| sort -rn | head`. awk shines for **column-oriented, aggregate-as-you-stream** text work —
summing/counting/filtering fields, computing per-key totals, reformatting columns — on
arbitrarily large files without loading them into memory. The framing: reach for awk
(or `cut`/`sort`/`uniq -c`) for quick field aggregation during an incident when you don't
have a metrics pipeline for that dimension; graduate to a real script/language when the logic
gets stateful or needs structure (JSON → `jq`), but a one-pass awk aggregation over a log is
often the fastest way to answer "which client/endpoint is causing this" at 3am.

---

### Q: How is monitoring set up on the systems you run, end to end?

**Difficulty:** Medium · **Tags:** `sre` `monitoring`

A complete answer spans the three pillars and the response path. **Metrics**: exporters and
app instrumentation scraped by Prometheus (node-exporter for hosts, kube-state-metrics for
K8s objects, app `/metrics`), with long-term storage and dashboards (Grafana). **Logs**:
structured logs shipped off the host and aggregated (Loki/ELK) so you're not SSHing into
nodes during an incident. **Traces**: distributed tracing for request-path latency across
services. On top sits **alerting** driven by **SLOs and golden signals**, routed by severity
through an alert manager to an on-call/escalation tool, with every alert tied to a runbook.

The SRE framing is what distinguishes this from "we have Grafana": you **alert on
user-facing symptoms / SLO burn-rate**, not on every cause; dashboards exist to root-cause
*once engaged*; and cluster-internal signals (Pod restarts, node pressure, etcd latency) are
**leading indicators** you watch and trend rather than page on individually. Cross-links to
[08-observability-sre.md](./08-observability-sre.md) for golden signals, burn-rate alerting,
and error budgets. The closer: the monitoring system itself needs the same rigor —
bounded metric cardinality (a per-request-id label will OOM Prometheus), tested alert
routing (a page nobody receives is worse than no page), and regular pruning of noisy alerts,
because the real-world failure of monitoring is drowning the on-call in noise during the one
incident that mattered.
