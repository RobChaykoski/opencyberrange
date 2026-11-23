# Local targets

Files in this directory are private to the deployment and are gitignored.

Create `nodes.yml`, `http.yml`, `http-insecure.yml`, or `tcp.yml` here with the
same `file_sd` format as the public examples. Prometheus loads them after the
public `targets/*.yml` files.

```yaml
# local/nodes.yml
- targets:
    - <host-private-address>:9100
  labels:
    environment: production
    host: <short-host-label>
    owner: <team>
```

Do not put secrets in labels. Keep private addresses and internal hostnames out
of the public target files.
