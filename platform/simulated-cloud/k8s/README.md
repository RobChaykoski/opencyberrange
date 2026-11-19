# Kubernetes lab manifests

These manifests simulate AKS-style RBAC, secret handling, and network policy.
Use a disposable `kind` or `k3d` cluster. Do not apply them to a shared cluster.

```bash
k3d cluster create ocr-cloud --agents 1
kubectl apply -f rbac-lab.yaml
kubectl apply -f secret-lab.yaml
kubectl apply -f network-policy.yaml
```

## Labs

### `rbac-lab.yaml`

Creates a namespace and a `report-reader` service account with `get`, `list`,
and `watch` on secrets, configmaps, and pods. That is intentionally too broad.

Learner task:

1. List the role rules.
2. Narrow the role to `get` and `list` on the `report-config` ConfigMap only.
3. Prove the service account can read the ConfigMap.
4. Prove it cannot list secrets or pods.

### `secret-lab.yaml`

Creates a lab-only Secret and a Deployment that consumes it as environment
variables. The password is fake and must not be reused.

Learner task:

1. Show the secret value and where it appears in the workload.
2. Replace the environment variable with a projected secret or an external
   secret reference.
3. Confirm the workload still starts.
4. Explain why a Kubernetes Secret is not automatically encrypted at rest in
   every cluster.

### `network-policy.yaml`

Creates default-deny ingress and egress, allows DNS, and allows one
service-to-service path.

Learner task:

1. Show the default-deny policy.
2. Test a blocked path.
3. Add the minimum allow rule.
4. Test the allowed path and the still-blocked path.

## Safety

- Use a disposable cluster; `kubectl delete -f` and delete the cluster after.
- Do not apply to a cluster that runs real workloads.
- Do not use real secrets.
- Do not add privileged containers or hostPath mounts to solve a lab.
