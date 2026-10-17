# A Pod fails to start — several reasons look similar. How do you tell them apart fast?

[↑ Index](./README.md) · [← Prev](./01-a-pod-has-been-for-20-minutes-walk.md) · [Next →](./03-a-pod-is-in-find-the-cause-and.md)

**Difficulty:** Medium · **Tags:** `workloads` `troubleshooting`

The **phase + container-state reason** routes everything (`get` then `describe`):
| Reason | Means | First move |
|--------|-------|-----------|
| `Pending` | scheduling/volume | describe → scheduler events |
| `ImagePullBackOff` | registry/tag/secret | check pull error + node→registry |
| `CreateContainerConfigError` | missing ConfigMap/Secret key | check refs |
| `CrashLoopBackOff` | starts then exits | `logs --previous` |
| `RunContainerError` | runtime/mount | describe events |

**Don't guess one cause** — let the state reason classify it, then go to `describe` + `logs
--previous`. State the decision tree out loud.

---

[↑ Index](./README.md) · [← Prev](./01-a-pod-has-been-for-20-minutes-walk.md) · [Next →](./03-a-pod-is-in-find-the-cause-and.md)
