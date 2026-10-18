# Production Troubleshooting Scenarios

The highest-signal interview round. They're testing whether you reason under pressure
without thrashing. **Narrate the method**, not a command dump.

## The method (apply to every scenario)

1. **Protect users first** — severity, error rate, % traffic hit, what changed, is a
   reversible mitigation (rollback / traffic shift / flag) available *now*.
2. **Scope it** — healthy vs unhealthy across Pods / nodes / zones / versions / paths. The
   axis it splits on *is* the clue.
3. **Desired vs observed** — read workload, Pod conditions, controller status, events
   *before* changing anything.
4. **Follow the dependency path** — Deployment → Pod → node → Service/EndpointSlices →
   DNS/NetworkPolicy → storage → external deps.
5. **Mitigate → verify → prevent** — reversible action, confirm *user-facing* recovery,
   name the guardrail. Preserve evidence (logs, failing spec).

---

| # | Question | Difficulty |
|---|----------|------------|
| 1 | [A Pod has been `Pending` for 20 minutes. Walk through it.](./01-a-pod-has-been-for-20-minutes-walk.md) | Medium |
| 2 | [A Pod fails to start — several reasons look similar. How do you tell them apart fast?](./02-a-pod-fails-to-start-several-reasons-look.md) | Medium |
| 3 | [A Pod is in `CrashLoopBackOff`. Find the cause — and why is the status misleading?](./03-a-pod-is-in-find-the-cause-and.md) | Medium |
| 4 | [Pods are `Running` but none are `Ready` and the Service is dead. What's wrong?](./04-pods-are-but-none-are-and-the-service.md) | Medium |
| 5 | [Pods restart specifically during traffic spikes. Diagnose it.](./05-pods-restart-specifically-during-traffic-spikes-diagnose-it.md) | Hard |
| 6 | [One Service returns intermittent 503s. Debug it.](./06-one-service-returns-intermittent-503s-debug-it.md) | Hard |
| 7 | [A Deployment rollout is stuck. What now?](./07-a-deployment-rollout-is-stuck-what-now.md) | Medium |
| 8 | [Traffic doubled but the HPA didn't scale. Why, and how do you confirm each hypothesis?](./08-traffic-doubled-but-the-hpa-didn-t-scale.md) | Hard |
| 9 | [A node goes `NotReady` and its Pods disappear. Respond as on-call.](./09-a-node-goes-and-its-pods-disappear-respond.md) | Hard |
| 10 | [A stateful Pod can't mount its volume. Walk through it — carefully, data is at risk.](./10-a-stateful-pod-can-t-mount-its-volume.md) | Hard |
| 11 | [A distributed database shows data inconsistency across replicas. Causes + investigation.](./11-a-distributed-database-shows-data-inconsistency-across-replicas.md) | Hard |
| 12 | [kubectl is slow and the API server times out cluster-wide. Diagnose it.](./12-kubectl-is-slow-and-the-api-server-times-out.md) | Hard |
| 13 | [After a deploy, p99 latency doubled but error rate is flat. Find it.](./13-after-a-deploy-p99-latency-doubled-but-no-errors.md) | Hard |
| 14 | [DNS lookups fail intermittently across the whole cluster. Root cause?](./14-dns-lookups-fail-intermittently-cluster-wide.md) | Hard |
| 15 | [A namespace is stuck in `Terminating` and won't delete. Why?](./15-a-namespace-is-stuck-terminating-and-wont-delete.md) | Medium |
| 16 | [A node hits `DiskPressure` and starts evicting Pods. Respond.](./16-a-node-hits-diskpressure-and-evicts-pods.md) | Medium |
| 17 | [Workloads (or kubelets) start failing a year in — certificates expired. Handle it.](./17-workloads-fail-tls-after-a-certificate-expired.md) | Hard |
| 18 | [A node drain hangs during a cluster upgrade — Pods won't evict. Why?](./18-a-node-drain-wont-complete-during-an-upgrade.md) | Medium |
| 19 | [Memory climbs all day, then Pods OOM every night. Leak or not?](./19-memory-climbs-all-day-then-pods-oom-every-night.md) | Hard |

[← All topics](../../README.md)
