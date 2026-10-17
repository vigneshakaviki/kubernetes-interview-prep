# Error budget nearly exhausted mid-quarter — what happens and what do you do?

[↑ Index](./README.md) · [← Prev](./03-design-a-monitoring-alerting-system-how-do-you.md) · [Next →](./05-monitor-cluster-workload-health-with-prometheus-how.md)

**Difficulty:** Medium · **Tags:** `sre` `slo`

Budget = `100% − SLO`. Nearly gone → the **pre-agreed policy** kicks in (non-political):
- **Freeze risky releases**, redirect effort to **reliability** until it recovers.
- Dig into *what spent it* — bad deploy / flaky dep / capacity / unrealistic SLO.

**Point:** makes the velocity-vs-reliability trade-off explicit + data-driven.

**Nuance:**
- **Chronically** blown → SLO is wrong (loosen) **or** architecture can't meet it (invest) —
  not eternal freeze.
- **Never** spent → SLO too loose, leaving velocity on the table.

---

[↑ Index](./README.md) · [← Prev](./03-design-a-monitoring-alerting-system-how-do-you.md) · [Next →](./05-monitor-cluster-workload-health-with-prometheus-how.md)
