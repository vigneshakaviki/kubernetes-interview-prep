# Define SLI, SLO, SLA — and why is the SLO set tighter than the SLA?

[↑ Index](./README.md) · [Next →](./02-the-four-golden-signals-and-how-to-alert.md)

**Difficulty:** Easy · **Tags:** `sre` `slo`

| | Is | Example |
|--|----|---------|
| **SLI** | measured indicator | % requests < 300ms |
| **SLO** | internal target | 99.9% over 28d |
| **SLA** | external contract (+penalty) | 99.5% or refund |

**Why SLO tighter than SLA:** safety margin — your alerting/error-budget fires **before**
you breach the customer contract.

**Good SLIs** measure the **user's** experience (edge success/latency), not CPU; pick a
*small* number that correlate with pain.

---

[↑ Index](./README.md) · [Next →](./02-the-four-golden-signals-and-how-to-alert.md)
