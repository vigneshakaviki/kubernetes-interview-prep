# kubectl Debug Cheatsheet

The commands you reach for in a troubleshooting interview, grouped by what you're chasing.
Pairs with [07-troubleshooting-scenarios.md](../questions/07-troubleshooting-scenarios.md).
`alias k=kubectl`.

## Triage — "what's broken?"

```bash
kubectl get pods -A -o wide --sort-by=.status.startTime   # everything, newest last
kubectl get pods --field-selector=status.phase!=Running   # anything not Running
kubectl get events -A --sort-by=.lastTimestamp | tail -40  # recent cluster events
kubectl get pods -o wide | grep -E 'CrashLoop|Error|Pending|ImagePull|OOM'
```

## A Pod won't start / is crashing

```bash
kubectl describe pod <p>                       # events, conditions, last state, exit code
kubectl logs <p> --previous                    # logs of the crashed instance (key flag)
kubectl logs <p> -c <container> -f             # follow a specific container
kubectl get pod <p> -o jsonpath='{.status.containerStatuses[*].lastState.terminated.reason}{"\n"}'
kubectl get pod <p> -o yaml | less             # full spec+status when events aren't enough
```

## Pending / scheduling

```bash
kubectl describe pod <p> | sed -n '/Events/,$p'   # scheduler predicate failures
kubectl describe nodes | grep -A5 Allocated       # per-node requests vs allocatable
kubectl get nodes -o wide                         # Ready? taints?
kubectl get node <n> -o jsonpath='{.spec.taints}{"\n"}'
```

## Service / networking — "traffic isn't flowing"

```bash
kubectl get endpointslices -l kubernetes.io/service-name=<svc>   # empty = selector/readiness
kubectl describe svc <svc>                                       # selector, ports, targetPort
kubectl get pods --show-labels                                  # do labels match the selector?
kubectl run t --rm -it --image=nicolaka/netshoot -- bash        # curl/dig/tcpdump toolbox
#   inside: curl -sv http://<svc>.<ns>:<port>  ;  dig <svc>.<ns>.svc.cluster.local
kubectl get networkpolicy -A                                    # is something denying it?
```

## DNS

```bash
kubectl run t --rm -it --image=busybox -- nslookup <svc>.<ns>
kubectl -n kube-system get pods -l k8s-app=kube-dns             # CoreDNS healthy?
kubectl -n kube-system logs -l k8s-app=kube-dns --tail=50
kubectl get svc -n kube-system kube-dns                         # has endpoints?
```

## Resources / OOM / throttling

```bash
kubectl top pods -A --sort-by=memory          # needs metrics-server
kubectl top nodes
kubectl get pod <p> -o jsonpath='{.status.containerStatuses[0].lastState.terminated.reason}{"\n"}'  # OOMKilled?
kubectl describe node <n> | grep -iE 'pressure|evict'   # node MemoryPressure/DiskPressure
```

## Rollouts

```bash
kubectl rollout status deploy/<d>
kubectl rollout history deploy/<d>
kubectl rollout undo deploy/<d> [--to-revision=N]
kubectl get rs -l app=<d> -o wide              # old vs new ReplicaSet
```

## RBAC — "am I / is this SA allowed?"

```bash
kubectl auth can-i --list                                  # my effective perms
kubectl auth can-i get secrets -n <ns>
kubectl auth can-i '*' '*' --as=system:serviceaccount:<ns>:<sa>   # what a SA can do
```

## Storage

```bash
kubectl get pvc,pv -A
kubectl describe pvc <pvc>                      # binding + provisioning events
kubectl get storageclass
kubectl -n kube-system logs -l app=<csi-driver> # attach/mount errors
```

## Get onto the node / into a shell-less image

```bash
kubectl debug -it <pod> --image=busybox --target=<container>   # ephemeral container
kubectl debug node/<node> -it --image=busybox                  # node shell via a Pod
kubectl exec -it <pod> -- sh                                    # when the image has a shell
```

## Fast reference

```bash
kubectl explain pod.spec.containers.resources   # field docs, offline
kubectl api-resources                           # kinds + short names
kubectl get <res> -o yaml | kubectl neat        # (if installed) strip managed fields
```
