# Core Concepts & Architecture

| # | Question | Difficulty |
|---|----------|------------|
| 1 | [Walk through what happens when you run `kubectl apply -f deploy.yaml` — and where it can fail.](./01-walk-through-what-happens-when-you-run-and.md) | Medium |
| 2 | [What is kube-proxy, its modes, and is it on the data path for every packet?](./02-what-is-kube-proxy-its-modes-and-is.md) | Medium |
| 3 | [Deployment vs StatefulSet vs DaemonSet — and a case where the wrong one bites.](./03-deployment-vs-statefulset-vs-daemonset-and-a-case.md) | Medium |
| 4 | [Pod vs Deployment, and why we never create bare Pods in production.](./04-pod-vs-deployment-and-why-we-never-create.md) | Easy |
| 5 | [Pods are ephemeral with changing IPs — how does a Service give stable access, and what are EndpointSlices?](./05-pods-are-ephemeral-with-changing-ips-how-does.md) | Easy |
| 6 | [I point at lines in a Deployment YAML — which fields must you explain, and which mismatches silently break things?](./06-i-point-at-lines-in-a-deployment-yaml.md) | Medium |
| 7 | [Write a Dockerfile for a Python service and justify every line.](./07-write-a-dockerfile-for-a-python-service-and.md) | Easy |
| 8 | [etcd's role, consequences of it going unhealthy, and explain Raft like you've operated it.](./08-etcd-s-role-consequences-of-it-going-unhealthy.md) | Hard |
| 9 | ["Do you have Kubernetes experience?" but your company used in-house infra. How do you answer?](./09-do-you-have-kubernetes-experience-but-your-company.md) | Easy |
| 10 | [How does the scheduler place a Pod — and how do you influence or debug it?](./10-how-does-the-scheduler-place-a-pod-and.md) | Advanced |
| 11 | [Operator pattern and CRDs — when is it right vs over-engineering?](./11-operator-pattern-and-crds-when-is-it-right.md) | Advanced |
| 12 | [Owner references, cascading GC, and finalizers — and why is an object stuck in `Terminating`?](./12-owner-references-cascading-gc-and-finalizers-and-why.md) | Advanced |
| 13 | [Namespaces, ResourceQuota, LimitRange — how do they stop one team taking down a shared cluster?](./13-namespaces-resourcequota-limitrange-how-do-they-stop-one.md) | Intermediate |
| 14 | [Labels vs annotations — where's the line, and what breaks if you blur it?](./14-labels-vs-annotations-where-s-the-line-and.md) | Intermediate |
| 15 | [Imperative vs declarative kubectl, and safely rolling back a bad Deployment.](./15-imperative-vs-declarative-kubectl-and-safely-rolling-back.md) | Intermediate |
| 16 | [What is Helm, what does it buy you, and when would you use Kustomize instead?](./16-what-is-helm-what-does-it-buy-you.md) | Intermediate |

[← All topics](../../README.md)
