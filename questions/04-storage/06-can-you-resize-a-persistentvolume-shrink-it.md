# Can you resize a PersistentVolume? Shrink it?

[↑ Index](./README.md) · [← Prev](./05-walk-through-the-pvc-pv-binding-lifecycle-and.md)

**Difficulty:** Intermediate · **Tags:** `storage`

- **Grow:** yes, if StorageClass has `allowVolumeExpansion: true` + CSI supports it. Edit the
  PVC's requested size → volume + filesystem expand (online for many drivers; some need a
  Pod restart to finish).
- **Shrink:** **no** — unsupported.

**Implications:**
- Expansion is one-way → right-size conservatively, grow later. Don't over-provision up front.
- Monitor/alert before full — a full PV wedges a stateful app (writes fail, DB read-only),
  and discovering `allowVolumeExpansion: false` under pressure is a bad time.

---

[↑ Index](./README.md) · [← Prev](./05-walk-through-the-pvc-pv-binding-lifecycle-and.md)
