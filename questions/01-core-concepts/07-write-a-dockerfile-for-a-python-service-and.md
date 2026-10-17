# Write a Dockerfile for a Python service and justify every line.

[↑ Index](./README.md) · [← Prev](./06-i-point-at-lines-in-a-deployment-yaml.md) · [Next →](./08-etcd-s-role-consequences-of-it-going-unhealthy.md)

**Difficulty:** Easy · **Tags:** `docker` `containers`

```dockerfile
FROM python:3.12-slim          # small, fewer CVEs; avoids alpine/musl wheel pain
WORKDIR /app
COPY requirements.txt .         # copy deps first → pip layer caches until deps change
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN useradd -m app && chown -R app /app
USER app                        # non-root: baseline for Pod Security "restricted"
EXPOSE 8000
CMD ["python", "main.py"]       # exec form → PID 1 gets SIGTERM for graceful shutdown
```

- Layer order by change-frequency = the main build-speed lever.
- Shell-form `CMD` would swallow signals → no graceful shutdown.
- Mention: multi-stage build to drop build tools, pinned base digest, readiness probe
  instead of Docker healthcheck.

---

[↑ Index](./README.md) · [← Prev](./06-i-point-at-lines-in-a-deployment-yaml.md) · [Next →](./08-etcd-s-role-consequences-of-it-going-unhealthy.md)
