# RangeBox

RangeBox is an optional desktop container for exercises that need a browser,
terminal, or GUI tools. It is not the lab target; it is the learner's workspace.

## Two modes

| Mode | Network | Use |
|---|---|---|
| Exercise-attached | joins the session `10.100.x.0/24` | the desktop needs to reach the lab target |
| Standalone | its own `10.50.x.0/24` bridge | the RangeBox tab, independent practice |

## Lifecycle

1. The learner requests a RangeBox with the lab or from the RangeBox tab.
2. The backend checks `MAX_CONCURRENT_RANGEBOXES`, CPU reserve, and free disk.
3. It starts the desktop container and waits for VNC port 6080.
4. The browser connects through the backend proxy with noVNC.
5. The scheduler stops the desktop on expiry or when the learner stops it.

## Capacity controls

| Setting | Meaning |
|---|---|
| `MAX_CONCURRENT_RANGEBOXES` | hard cap; empty uses the host policy |
| `RANGEBOX_CPU_RESERVE_CORES` | CPU kept for the platform |
| `RANGEBOX_MIN_FREE_DISK_GB` | refuse to start below this free space |

The backend exposes capacity in the admin panel and rejects a spawn with a clear
message rather than overcommitting the host.

## Security

- VNC is never published directly; the backend proxies it.
- A standalone RangeBox cannot reach a learner's lab network.
- An exercise RangeBox reaches only that session's network.
- The container drops capabilities and uses an isolated network.
- Do not put learner credentials or a private VPN key in the desktop image.

## Tests

```bash
cd platform/backend
python -m pytest tests/test_rangebox_capacity.py tests/test_rangebox_capacity_api.py \
  tests/test_rangebox_transport.py tests/test_rangebox_proxy_network.py \
  tests/test_rangebox_images.py -q
```

## Related

- [Lab runtime](../subsystem-overview.md)
- [RangeBox capacity](../../../docs/RANGEBOX-CAPACITY.md)
- [Backend labs and sessions](../../backend/features/labs-and-sessions/README.md)
- [Frontend lab workspace](../../frontend/features/lab-workspace/README.md)
