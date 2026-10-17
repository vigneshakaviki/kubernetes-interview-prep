# All Questions

Every question in one place — use Ctrl-F. Each links to its own page.

**82 questions** — Easy 14 · Intermediate 18 · Medium 28 · Advanced 14 · Hard 8

## Core Concepts & Architecture  ·  [index](./01-core-concepts/)

| Question | Difficulty |
|----------|------------|
| [Walk through what happens when you run `kubectl apply -f deploy.yaml` — and where it can fail.](./01-core-concepts/01-walk-through-what-happens-when-you-run-and.md) | Medium |
| [What is kube-proxy, its modes, and is it on the data path for every packet?](./01-core-concepts/02-what-is-kube-proxy-its-modes-and-is.md) | Medium |
| [Deployment vs StatefulSet vs DaemonSet — and a case where the wrong one bites.](./01-core-concepts/03-deployment-vs-statefulset-vs-daemonset-and-a-case.md) | Medium |
| [Pod vs Deployment, and why we never create bare Pods in production.](./01-core-concepts/04-pod-vs-deployment-and-why-we-never-create.md) | Easy |
| [Pods are ephemeral with changing IPs — how does a Service give stable access, and what are EndpointSlices?](./01-core-concepts/05-pods-are-ephemeral-with-changing-ips-how-does.md) | Easy |
| [I point at lines in a Deployment YAML — which fields must you explain, and which mismatches silently break things?](./01-core-concepts/06-i-point-at-lines-in-a-deployment-yaml.md) | Medium |
| [Write a Dockerfile for a Python service and justify every line.](./01-core-concepts/07-write-a-dockerfile-for-a-python-service-and.md) | Easy |
| [etcd's role, consequences of it going unhealthy, and explain Raft like you've operated it.](./01-core-concepts/08-etcd-s-role-consequences-of-it-going-unhealthy.md) | Hard |
| ["Do you have Kubernetes experience?" but your company used in-house infra. How do you answer?](./01-core-concepts/09-do-you-have-kubernetes-experience-but-your-company.md) | Easy |
| [How does the scheduler place a Pod — and how do you influence or debug it?](./01-core-concepts/10-how-does-the-scheduler-place-a-pod-and.md) | Advanced |
| [Operator pattern and CRDs — when is it right vs over-engineering?](./01-core-concepts/11-operator-pattern-and-crds-when-is-it-right.md) | Advanced |
| [Owner references, cascading GC, and finalizers — and why is an object stuck in `Terminating`?](./01-core-concepts/12-owner-references-cascading-gc-and-finalizers-and-why.md) | Advanced |
| [Namespaces, ResourceQuota, LimitRange — how do they stop one team taking down a shared cluster?](./01-core-concepts/13-namespaces-resourcequota-limitrange-how-do-they-stop-one.md) | Intermediate |
| [Labels vs annotations — where's the line, and what breaks if you blur it?](./01-core-concepts/14-labels-vs-annotations-where-s-the-line-and.md) | Intermediate |
| [Imperative vs declarative kubectl, and safely rolling back a bad Deployment.](./01-core-concepts/15-imperative-vs-declarative-kubectl-and-safely-rolling-back.md) | Intermediate |
| [What is Helm, what does it buy you, and when would you use Kustomize instead?](./01-core-concepts/16-what-is-helm-what-does-it-buy-you.md) | Intermediate |

## Pods & Workloads  ·  [index](./02-pods-workloads/)

| Question | Difficulty |
|----------|------------|
| [Explain liveness, readiness, and startup probes — and a real outage from misconfiguring one.](./02-pods-workloads/01-explain-liveness-readiness-and-startup-probes-and-a.md) | Medium |
| [Requests vs limits — what each controls, the QoS classes, and what happens at the limit.](./02-pods-workloads/02-requests-vs-limits-what-each-controls-the-qos.md) | Easy |
| [Node affinity, taints, tolerations — and how to build a dedicated GPU pool.](./02-pods-workloads/03-node-affinity-taints-tolerations-and-how-to-build.md) | Medium |
| [QoS classes and the exact kubelet eviction order under node pressure.](./02-pods-workloads/04-qos-classes-and-the-exact-kubelet-eviction-order.md) | Advanced |
| [Deployment update strategies, and how canary / blue-green fit on top.](./02-pods-workloads/05-deployment-update-strategies-and-how-canary-blue-green.md) | Intermediate |
| [ConfigMap vs Secret — and if Secrets aren't encrypted, how do you secure them?](./02-pods-workloads/06-configmap-vs-secret-and-if-secrets-aren-t.md) | Intermediate |
| [Init containers vs sidecars — and what changed with native sidecar support.](./02-pods-workloads/07-init-containers-vs-sidecars-and-what-changed-with.md) | Intermediate |
| [Multi-container Pod patterns, and how to decide same-Pod vs separate-Pod.](./02-pods-workloads/08-multi-container-pod-patterns-and-how-to-decide.md) | Intermediate |
| [Job vs CronJob — the knobs that decide correctness under failure.](./02-pods-workloads/09-job-vs-cronjob-the-knobs-that-decide-correctness.md) | Intermediate |
| [emptyDir vs hostPath vs PVC — when each, and the hostPath trap.](./02-pods-workloads/10-emptydir-vs-hostpath-vs-pvc-when-each-and.md) | Intermediate |
| [What happens when a Pod is deleted — grace period, preStop, SIGTERM — and why a short grace period drops requests.](./02-pods-workloads/11-what-happens-when-a-pod-is-deleted-grace.md) | Intermediate |

## Networking  ·  [index](./03-networking/)

| Question | Difficulty |
|----------|------------|
| [Service vs Ingress — where does each operate, and why not a LoadBalancer per service?](./03-networking/01-service-vs-ingress-where-does-each-operate-and.md) | Easy |
| [What is a NetworkPolicy, the default without one, and the gotcha people miss?](./03-networking/02-what-is-a-networkpolicy-the-default-without-one.md) | Medium |
| [How does in-cluster DNS work, and how do you debug "can't resolve"?](./03-networking/03-how-does-in-cluster-dns-work-and-how.md) | Medium |
| [ClusterIP vs NodePort vs LoadBalancer — how they stack.](./03-networking/04-clusterip-vs-nodeport-vs-loadbalancer-how-they-stack.md) | Intermediate |
| [Headless Service — how it differs at DNS level, and when you actually need one.](./03-networking/05-headless-service-how-it-differs-at-dns-level.md) | Advanced |
| [Explain the Pod networking model and what a CNI is responsible for.](./03-networking/06-explain-the-pod-networking-model-and-what-a.md) | Advanced |
| [kube-proxy iptables vs IPVS — what breaks at scale?](./03-networking/07-kube-proxy-iptables-vs-ipvs-what-breaks-at.md) | Advanced |
| [What does a service mesh add over plain K8s networking, and what's the cost?](./03-networking/08-what-does-a-service-mesh-add-over-plain.md) | Advanced |
| [How do Pods discover each other — DNS vs env vars — and why is one a trap?](./03-networking/09-how-do-pods-discover-each-other-dns-vs.md) | Intermediate |
| [How does an Ingress handle TLS + path routing, and what's its relationship to the controller?](./03-networking/10-how-does-an-ingress-handle-tls-path-routing.md) | Intermediate |

## Storage  ·  [index](./04-storage/)

| Question | Difficulty |
|----------|------------|
| [Explain PV, PVC, StorageClass, and how dynamic provisioning ties them together.](./04-storage/01-explain-pv-pvc-storageclass-and-how-dynamic-provisioning.md) | Easy |
| [A StatefulSet Pod is stuck `Pending` on storage. Walk through the causes.](./04-storage/02-a-statefulset-pod-is-stuck-on-storage-walk.md) | Hard |
| [Volume access modes, and the gotcha with ReadWriteOnce.](./04-storage/03-volume-access-modes-and-the-gotcha-with-readwriteonce.md) | Intermediate |
| [PV reclaim policies, and how the wrong one causes data loss.](./04-storage/04-pv-reclaim-policies-and-how-the-wrong-one.md) | Intermediate |
| [Walk through the PVC→PV binding lifecycle and explain `WaitForFirstConsumer`.](./04-storage/05-walk-through-the-pvc-pv-binding-lifecycle-and.md) | Intermediate |
| [Can you resize a PersistentVolume? Shrink it?](./04-storage/06-can-you-resize-a-persistentvolume-shrink-it.md) | Intermediate |

## Scaling & Autoscaling  ·  [index](./05-scaling-autoscaling/)

| Question | Difficulty |
|----------|------------|
| [HPA, VPA, Cluster Autoscaler — what each changes, and how they interact/conflict.](./05-scaling-autoscaling/01-hpa-vpa-cluster-autoscaler-what-each-changes-and.md) | Medium |
| [An HPA sits at `<unknown>` and won't scale on CPU. What's wrong?](./05-scaling-autoscaling/02-an-hpa-sits-at-and-won-t-scale.md) | Medium |
| [Autoscale on something other than CPU — custom/external metrics — and where KEDA fits.](./05-scaling-autoscaling/03-autoscale-on-something-other-than-cpu-custom-external.md) | Advanced |
| [How does Cluster Autoscaler decide to add/remove a node — and why not just watch CPU?](./05-scaling-autoscaling/04-how-does-cluster-autoscaler-decide-to-add-remove.md) | Advanced |
| [What is a PodDisruptionBudget, which disruptions does it govern, and when does it save you?](./05-scaling-autoscaling/05-what-is-a-poddisruptionbudget-which-disruptions-does-it.md) | Advanced |

## RBAC & Security  ·  [index](./06-rbac-security/)

| Question | Difficulty |
|----------|------------|
| [Explain RBAC — Role vs ClusterRole, the bindings, subjects — and why there are no deny rules.](./06-rbac-security/01-explain-rbac-role-vs-clusterrole-the-bindings-subjects.md) | Medium |
| [A workload needs the K8s API. How do you give it exactly what it needs?](./06-rbac-security/02-a-workload-needs-the-k8s-api-how-do.md) | Medium |
| [PodSecurityPolicy is gone. What replaced it, and how do you enforce "no root, no privileged"?](./06-rbac-security/03-podsecuritypolicy-is-gone-what-replaced-it-and-how.md) | Advanced |
| [Validating vs mutating admission webhooks — order, and why it matters for sidecar injection.](./06-rbac-security/04-validating-vs-mutating-admission-webhooks-order-and-why.md) | Advanced |
| [Secrets are only base64 in etcd. Give the full layered approach to securing them.](./06-rbac-security/05-secrets-are-only-base64-in-etcd-give-the.md) | Advanced |

## Production Troubleshooting Scenarios  ·  [index](./07-troubleshooting-scenarios/)

| Question | Difficulty |
|----------|------------|
| [A Pod has been `Pending` for 20 minutes. Walk through it.](./07-troubleshooting-scenarios/01-a-pod-has-been-for-20-minutes-walk.md) | Medium |
| [A Pod fails to start — several reasons look similar. How do you tell them apart fast?](./07-troubleshooting-scenarios/02-a-pod-fails-to-start-several-reasons-look.md) | Medium |
| [A Pod is in `CrashLoopBackOff`. Find the cause — and why is the status misleading?](./07-troubleshooting-scenarios/03-a-pod-is-in-find-the-cause-and.md) | Medium |
| [Pods are `Running` but none are `Ready` and the Service is dead. What's wrong?](./07-troubleshooting-scenarios/04-pods-are-but-none-are-and-the-service.md) | Medium |
| [Pods restart specifically during traffic spikes. Diagnose it.](./07-troubleshooting-scenarios/05-pods-restart-specifically-during-traffic-spikes-diagnose-it.md) | Hard |
| [One Service returns intermittent 503s. Debug it.](./07-troubleshooting-scenarios/06-one-service-returns-intermittent-503s-debug-it.md) | Hard |
| [A Deployment rollout is stuck. What now?](./07-troubleshooting-scenarios/07-a-deployment-rollout-is-stuck-what-now.md) | Medium |
| [Traffic doubled but the HPA didn't scale. Why, and how do you confirm each hypothesis?](./07-troubleshooting-scenarios/08-traffic-doubled-but-the-hpa-didn-t-scale.md) | Hard |
| [A node goes `NotReady` and its Pods disappear. Respond as on-call.](./07-troubleshooting-scenarios/09-a-node-goes-and-its-pods-disappear-respond.md) | Hard |
| [A stateful Pod can't mount its volume. Walk through it — carefully, data is at risk.](./07-troubleshooting-scenarios/10-a-stateful-pod-can-t-mount-its-volume.md) | Hard |
| [A distributed database shows data inconsistency across replicas. Causes + investigation.](./07-troubleshooting-scenarios/11-a-distributed-database-shows-data-inconsistency-across-replicas.md) | Hard |

## Observability & SRE Practice  ·  [index](./08-observability-sre/)

| Question | Difficulty |
|----------|------------|
| [Define SLI, SLO, SLA — and why is the SLO set tighter than the SLA?](./08-observability-sre/01-define-sli-slo-sla-and-why-is-the.md) | Easy |
| [The four golden signals, and how to alert on them without 3am noise.](./08-observability-sre/02-the-four-golden-signals-and-how-to-alert.md) | Easy |
| [Design a monitoring + alerting system. How do you prevent alert storms?](./08-observability-sre/03-design-a-monitoring-alerting-system-how-do-you.md) | Medium |
| [Error budget nearly exhausted mid-quarter — what happens and what do you do?](./08-observability-sre/04-error-budget-nearly-exhausted-mid-quarter-what-happens.md) | Medium |
| [Monitor cluster + workload health with Prometheus — how?](./08-observability-sre/05-monitor-cluster-workload-health-with-prometheus-how.md) | Medium |

## Linux & SRE Fundamentals  ·  [index](./09-linux-sre-fundamentals/)

| Question | Difficulty |
|----------|------------|
| [Disk I/O on a host is very high. Find the cause.](./09-linux-sre-fundamentals/01-disk-i-o-on-a-host-is-very.md) | Medium |
| [What load average counts as "high," and what does it measure?](./09-linux-sre-fundamentals/02-what-load-average-counts-as-high-and-what.md) | Easy |
| [Hard link vs soft link — real differences and where each breaks.](./09-linux-sre-fundamentals/03-hard-link-vs-soft-link-real-differences-and.md) | Easy |
| [`df` and `du` disagree. Why, and how do you find the culprit?](./09-linux-sre-fundamentals/04-and-disagree-why-and-how-do-you-find.md) | Medium |
| [A machine's CPU spikes. Handle it start to finish.](./09-linux-sre-fundamentals/05-a-machine-s-cpu-spikes-handle-it-start.md) | Medium |
| [Service latency is high. Use `netstat`/`ss`, `tcpdump`, `traceroute` to localize it.](./09-linux-sre-fundamentals/06-service-latency-is-high-use-to-localize-it.md) | Medium |
| [`dig` vs `nslookup`?](./09-linux-sre-fundamentals/07-vs.md) | Easy |
| [Linux signals — SIGTERM vs SIGKILL vs SIGHUP — and the K8s mapping.](./09-linux-sre-fundamentals/08-linux-signals-sigterm-vs-sigkill-vs-sighup-and.md) | Easy |
| [Walk through a DNS lookup, app call to answer.](./09-linux-sre-fundamentals/09-walk-through-a-dns-lookup-app-call-to.md) | Medium |
| [Show an `awk` one-liner and when awk is the right tool.](./09-linux-sre-fundamentals/10-show-an-one-liner-and-when-awk-is.md) | Easy |
| [How is monitoring set up on the systems you run, end to end?](./09-linux-sre-fundamentals/11-how-is-monitoring-set-up-on-the-systems.md) | Medium |

## System Design & Coding  ·  [index](./10-system-design-coding/)

| Question | Difficulty |
|----------|------------|
| [Design a rate limiter under a target QPS. Then make it work across many servers.](./10-system-design-coding/01-design-a-rate-limiter-under-a-target-qps.md) | Medium |
| [Count sessions per user from a `timestamp, user, action` log. Then scale past memory.](./10-system-design-coding/02-count-sessions-per-user-from-a-log-then.md) | Medium |

[← Home](../README.md)
