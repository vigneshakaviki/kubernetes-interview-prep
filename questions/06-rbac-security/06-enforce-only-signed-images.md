# How do you enforce that only signed images from your registry can run?

[↑ Index](./README.md) · [← Prev](./05-secrets-are-only-base64-in-etcd-give-the.md)

**Difficulty:** Advanced · **Tags:** `security` `supply-chain`

**Short answer:** You gate it at **admission** — a policy controller verifies an image's
**signature** (cosign/Sigstore) and provenance before the Pod is allowed, so an unsigned or
untrusted image is rejected cluster-wide.

**The chain:**
- **Sign** at build (`cosign sign`), keyless (OIDC → Fulcio cert + Rekor transparency log)
  or with a key. Optionally attach **SLSA provenance** / SBOM attestations.
- **Verify at admission** — a validating webhook (**Kyverno** `verifyImages`, **Sigstore
  policy-controller**, or Connaisseur / Ratify) checks the signature + the trusted
  identity/issuer against the image digest **before** scheduling.
- **Pin by digest**, not tag — signatures bind to a digest; a mutable tag defeats the point.

**Policy example (conceptual):** "any image not matching `registry.corp/*` **and** carrying
a valid cosign signature from our CI's OIDC identity → **deny**."

**Pitfalls:**
- `failurePolicy: Fail` on the verify webhook → if it's down, **deploys stop** (and exempt
  kube-system or you brick the cluster). `Ignore` → bypass gap. Run it HA.
- Admission verifies at *create* — pair with a runtime scanner; and lock down who can edit
  the policy or image-pull secrets, or the control is theater.

**Why:** this is the defense against a compromised base image or a typosquatted dependency
making it into prod — the supply-chain attack path.

---

[↑ Index](./README.md) · [← Prev](./05-secrets-are-only-base64-in-etcd-give-the.md)
