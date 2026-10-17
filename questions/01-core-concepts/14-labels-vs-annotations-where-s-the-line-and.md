# Labels vs annotations — where's the line, and what breaks if you blur it?

[↑ Index](./README.md) · [← Prev](./13-namespaces-resourcequota-limitrange-how-do-they-stop-one.md) · [Next →](./15-imperative-vs-declarative-kubectl-and-safely-rolling-back.md)

**Difficulty:** Intermediate · **Tags:** `metadata`

| | Labels | Annotations |
|--|--------|-------------|
| For | **selection** (selectors, ownership, grouping) | arbitrary metadata for tools/humans |
| Shape | small, low-cardinality, indexed | can be large, not selectable |

**Blur it:**
- High-cardinality/changing value in a **label** (timestamp, hash per deploy) → index
  bloat, broken selectors, monitoring cardinality blowup.
- Data you need to select on stuck in an **annotation** → can't target it, filter client-side.

**Rule:** decides *which objects an operation applies to* → label; metadata you only read →
annotation.

---

[↑ Index](./README.md) · [← Prev](./13-namespaces-resourcequota-limitrange-how-do-they-stop-one.md) · [Next →](./15-imperative-vs-declarative-kubectl-and-safely-rolling-back.md)
