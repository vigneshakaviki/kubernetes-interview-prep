# ConfigMap vs Secret — and if Secrets aren't encrypted, how do you secure them?

[↑ Index](./README.md) · [← Prev](./05-deployment-update-strategies-and-how-canary-blue-green.md) · [Next →](./07-init-containers-vs-sidecars-and-what-changed-with.md)

**Difficulty:** Intermediate · **Tags:** `config` `security`

**Short answer:** Both inject config as env/files. ConfigMap = non-sensitive, Secret =
sensitive — but a Secret is only **base64-encoded, not encrypted**. base64 ≠ security.

**Secure in layers:**
- **Encryption at rest** — API-server `EncryptionConfiguration` + KMS provider, so etcd
  holds ciphertext.
- **RBAC** — `get`/`list` on secrets is high-value; scope it tight. Anyone who can
  `exec` into the pod or read its SA token reads mounted secrets too.
- **External store** — Vault / cloud SM via External Secrets Operator or CSI driver;
  secrets short-lived, not parked in etcd.
- **Hygiene** — never bake into images or commit in manifests.

**Rotation gotcha:** file-mounted secrets update in place (eventually) → app can reload;
**env-var secrets are fixed at pod start** → need a restart to rotate.

---

[↑ Index](./README.md) · [← Prev](./05-deployment-update-strategies-and-how-canary-blue-green.md) · [Next →](./07-init-containers-vs-sidecars-and-what-changed-with.md)
