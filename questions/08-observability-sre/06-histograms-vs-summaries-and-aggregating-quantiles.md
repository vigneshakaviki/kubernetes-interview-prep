# Prometheus histogram vs summary — and why can't you average p99 across instances?

[↑ Index](./README.md) · [← Prev](./05-monitor-cluster-workload-health-with-prometheus-how.md) · [Next →](./07-high-cardinality-metrics-detect-and-bound.md)

**Difficulty:** Hard · **Tags:** `monitoring` `prometheus`

**Short answer:** Use **histograms** for latency you aggregate across instances;
**summaries** compute quantiles client-side and **can't be aggregated**. And you can never
average pre-computed quantiles — `avg(p99)` is mathematically wrong.

**Histogram vs summary:**
| | Histogram | Summary |
|--|-----------|---------|
| Quantile computed | **query-time** (`histogram_quantile`) from buckets | **client-side**, baked in |
| Aggregatable across pods | **yes** (sum the bucket counters) | **no** |
| Cost | bucket cardinality | cheaper, but rigid |

**Why `avg(p99)` is wrong:** a quantile is not linear — the p99 of a merged population ≠ the
average of each instance's p99. One instance's p99 says nothing about how its 99th sits in
the *combined* distribution. Averaging quantiles produces a number with no meaning.

**Right way (histograms):**
```promql
histogram_quantile(0.99, sum by (le) (rate(http_request_duration_seconds_bucket[5m])))
```
Aggregate the **buckets** (`sum by (le)`) first, then compute the quantile once over the
merged distribution.

**Caveats:** histogram accuracy is bounded by bucket boundaries (choose them around your
SLO) — native/exponential histograms fix the fixed-bucket limitation. Summaries are fine for
a single instance where you never aggregate.

---

[↑ Index](./README.md) · [← Prev](./05-monitor-cluster-workload-health-with-prometheus-how.md) · [Next →](./07-high-cardinality-metrics-detect-and-bound.md)
