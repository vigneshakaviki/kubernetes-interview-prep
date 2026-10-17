# Kubernetes Interview Prep Guide

Open-source bank of **real Kubernetes interview questions** for SRE, Platform, and
DevOps roles — each with a deep answer: the core idea, the *why*, the trade-offs, and
the failure mode a junior misses.

Every entry is an **elaborate interviewer-style question + an in-depth answer** you can
actually learn from — not a link-only checklist. Answers are **original explanations
written for this repo**.

## How to use

- Each folder under [`questions/`](./questions) is one topic; **every question is its own
  page** with prev/next nav, linked from the topic index. Entries are tagged by
  **Difficulty** (Easy → Intermediate → Medium → Advanced → Hard).
- Answers go deep on purpose — read for the *reasoning and trade-offs*, then **say them
  out loud** as if answering the interviewer. Reciting from memory beats re-reading.
- Then **do the labs** in [exercises/hands-on.md](./exercises/hands-on.md) on a local
  cluster (`kind create cluster` / `minikube start`) — interviewers can tell who has
  actually driven a cluster. Keep [cheatsheets/kubectl-debug.md](./cheatsheets/kubectl-debug.md)
  open while you do.

**Suggested path:** 01 → 02 → 03 for fundamentals, then 07 (troubleshooting — the
highest-signal round) with the labs, then 04–06 and 08–10 to round out.

## Contents

**82 questions**, plus hands-on labs and a debug cheatsheet.
📑 **[Browse all 82 in one searchable list →](./questions/README.md)**

| # | Topic | Q | Index |
|---|-------|---|-------|
| 1 | Core concepts & architecture | 16 | [01-core-concepts/](./questions/01-core-concepts/) |
| 2 | Pods & workloads | 11 | [02-pods-workloads/](./questions/02-pods-workloads/) |
| 3 | Networking (Service, Ingress, DNS, NetworkPolicy) | 10 | [03-networking/](./questions/03-networking/) |
| 4 | Storage (PV, PVC, StatefulSet, CSI) | 6 | [04-storage/](./questions/04-storage/) |
| 5 | Scaling & autoscaling (HPA, VPA, Cluster Autoscaler) | 5 | [05-scaling-autoscaling/](./questions/05-scaling-autoscaling/) |
| 6 | RBAC & security | 5 | [06-rbac-security/](./questions/06-rbac-security/) |
| 7 | **Production troubleshooting scenarios** | 11 | [07-troubleshooting-scenarios/](./questions/07-troubleshooting-scenarios/) |
| 8 | Observability & SRE practice | 5 | [08-observability-sre/](./questions/08-observability-sre/) |
| 9 | Linux & SRE fundamentals | 11 | [09-linux-sre-fundamentals/](./questions/09-linux-sre-fundamentals/) |
| 10 | System design & coding | 2 | [10-system-design-coding/](./questions/10-system-design-coding/) |

### Practice & reference

| Type | File |
|------|------|
| 🧪 Hands-on labs (local cluster, collapsible solutions) | [exercises/hands-on.md](./exercises/hands-on.md) |
| ⚡ kubectl debug cheatsheet (triage by symptom) | [cheatsheets/kubectl-debug.md](./cheatsheets/kubectl-debug.md) |

## Contributing

Add real questions you were asked. Read [CONTRIBUTING.md](./CONTRIBUTING.md) and copy
[TEMPLATE.md](./TEMPLATE.md). Write **original** answers — never paste copyrighted text —
tag Difficulty, and put it in the right topic file.

## License

Content: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Attribute when reusing.
