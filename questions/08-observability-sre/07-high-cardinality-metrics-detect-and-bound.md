# High-cardinality metrics are OOMing Prometheus. How do you detect and bound it?

[↑ Index](./README.md) · [← Prev](./06-histograms-vs-summaries-and-aggregating-quantiles.md)

**Difficulty:** Hard · **Tags:** `monitoring` `prometheus`

**Short answer:** Cardinality = unique time series (metric × every label-value combo). A
label with unbounded values (user_id, request_id, full path) multiplies series until
Prometheus's head block eats all RAM. You find the offender, drop the label, and guard
ingestion.

**Detect:**
```promql
topk(10, count by (__name__)({__name__=~".+"}))   # worst metrics by series count
count(count by (<label>) (<metric>))                # distinct values of a suspect label
```
- `prometheus_tsdb_head_series` trending up with no traffic change = a cardinality leak.
- The usual culprits: `user_id`, `request_id`/trace id, raw `path` with IDs, `pod` on a
  churny Deployment, error messages as labels.

**Bound it:**
- **Fix at the source** — don't put unbounded values in labels (put the ID in a log/trace,
  not a metric).
- **metric_relabel_configs** — drop/replace high-card labels at scrape (e.g. regex the IDs
  out of `path`).
- **Recording rules** to pre-aggregate away granularity you don't query.
- **sample/series limits** per scrape target so one bad exporter can't blow up ingestion.

**Why it matters:** it's self-inflicted — one well-meaning "let's label by customer" PR
takes down your monitoring exactly when you need it. Treat cardinality as a budget.

---

[↑ Index](./README.md) · [← Prev](./06-histograms-vs-summaries-and-aggregating-quantiles.md)
