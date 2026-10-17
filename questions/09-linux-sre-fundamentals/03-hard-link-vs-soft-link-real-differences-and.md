# Hard link vs soft link — real differences and where each breaks.

[↑ Index](./README.md) · [← Prev](./02-what-load-average-counts-as-high-and-what.md) · [Next →](./04-and-disagree-why-and-how-do-you-find.md)

**Difficulty:** Easy · **Tags:** `linux` `filesystem`

| | Hard link | Soft (symlink) |
|--|-----------|----------------|
| Is | 2nd dir entry → same **inode** | small file holding a **path** |
| Cross-FS / dirs | no | yes |
| Delete original | data survives (until last link) | **dangles** (broken) |

**Examples:** log rotation + deploy `current →` symlinks use **soft** (atomic repoint across
dirs); dedup/backup tools use **hard** (many names, same bytes, no copy).

---

[↑ Index](./README.md) · [← Prev](./02-what-load-average-counts-as-high-and-what.md) · [Next →](./04-and-disagree-why-and-how-do-you-find.md)
