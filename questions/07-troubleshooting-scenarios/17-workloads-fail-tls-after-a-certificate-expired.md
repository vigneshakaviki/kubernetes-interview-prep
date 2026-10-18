# Workloads (or kubelets) start failing a year in — certificates expired. Handle it.

[↑ Index](./README.md) · [← Prev](./16-a-node-hits-diskpressure-and-evicts-pods.md) · [Next →](./18-a-node-drain-wont-complete-during-an-upgrade.md)

**Difficulty:** Hard · **Tags:** `security` `control-plane`

**Short answer:** Most K8s PKI certs default to **1-year** lifetimes. A cluster that's run
~a year without rotation hits mass TLS failures — kubelets go `NotReady`, API calls fail
`x509: certificate has expired`.

**Scope:** which cert? control-plane/API, **kubelet client/serving**, etcd peer, a mesh's
mTLS certs, or an app's Ingress cert.

**Diagnose:**
```bash
kubeadm certs check-expiration        # control-plane + kubelet certs (kubeadm clusters)
openssl x509 -enddate -noout -in <cert>
kubectl get csr                       # pending kubelet cert rotations
```

**Causes:** kubelet **cert rotation disabled** (`--rotate-certificates` off, or the CSR
approver not running) → serving/client certs expire; forgotten manual certs; a mesh whose
cert-rotation controller died; Ingress cert where cert-manager failed to renew.

**Fix:** renew (`kubeadm certs renew all` + restart control plane; approve kubelet CSRs;
restart cert-manager/mesh controller). **Prevent:** enable kubelet cert rotation,
cert-manager for app certs, and **alert on cert expiry 30 days out** — this is a pure
preventable-with-monitoring outage.

---

[↑ Index](./README.md) · [← Prev](./16-a-node-hits-diskpressure-and-evicts-pods.md) · [Next →](./18-a-node-drain-wont-complete-during-an-upgrade.md)
