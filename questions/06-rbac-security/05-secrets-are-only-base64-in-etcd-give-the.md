# Secrets are only base64 in etcd. Give the full layered approach to securing them.

[↑ Index](./README.md) · [← Prev](./04-validating-vs-mutating-admission-webhooks-order-and-why.md) · [Next →](./06-enforce-only-signed-images.md)

**Difficulty:** Advanced · **Tags:** `security` `secrets`

base64 = encoding, not encryption. Layers outward:
1. **Encryption at rest** — API-server `EncryptionConfiguration` + **KMS** provider →
   ciphertext in etcd (+ key rotation, key off the etcd disk).
2. **RBAC** — `get`/`list`/`watch` on secrets is high-value; scope tight. `exec` into a Pod
   or its SA token also reads mounted secrets.
3. **External store** — Vault / cloud SM via External Secrets Operator or CSI driver →
   short-lived, auditable, rotating; not parked in etcd.
4. **Hygiene** — never in images or manifests.

**Rotation nuance:** file-mounted secrets update in place (app reloads); **env-var secrets
fixed at Pod start** → need restart. Strongest posture: minimize long-lived secrets
(workload identity, mesh mTLS, dynamic DB creds).

---

[↑ Index](./README.md) · [← Prev](./04-validating-vs-mutating-admission-webhooks-order-and-why.md) · [Next →](./06-enforce-only-signed-images.md)
