"""Docker disk-usage parsing for the admin Disk Management panel."""

from __future__ import annotations

from types import SimpleNamespace

from app.services.docker_manager import DockerManager


class _FakeClient:
    def __init__(self, payload=None, error=None):
        self.payload = payload or {}
        self.error = error

    def df(self):
        if self.error is not None:
            raise self.error
        return self.payload


def _manager(client):
    return SimpleNamespace(client=client)


def test_disk_usage_summarises_images_containers_volumes_and_build_cache():
    usage = DockerManager.get_disk_usage(
        _manager(
            _FakeClient(
                {
                    "Images": [
                        {"Size": 100, "Containers": 1},
                        {"Size": 50, "Containers": 0},
                    ],
                    "Containers": [{"SizeRw": 10}, {"SizeRw": 5}],
                    "Volumes": [
                        {"UsageData": {"Size": 30, "RefCount": 0}},
                        {"UsageData": {"Size": 20, "RefCount": 1}},
                    ],
                    "BuildCache": [
                        {"Size": 7, "InUse": False},
                        {"Size": 3, "InUse": True},
                    ],
                }
            )
        )
    )

    assert usage["images"] == {
        "count": 2,
        "total_bytes": 150,
        "reclaimable_bytes": 50,
    }
    assert usage["containers"] == {"count": 2, "total_bytes": 15}
    assert usage["volumes"] == {
        "count": 2,
        "total_bytes": 50,
        "reclaimable_bytes": 30,
    }
    assert usage["build_cache"] == {
        "count": 2,
        "total_bytes": 10,
        "reclaimable_bytes": 7,
    }


def test_disk_usage_reports_unavailable_when_the_socket_proxy_denies_df():
    usage = DockerManager.get_disk_usage(
        _manager(_FakeClient(error=RuntimeError("403 Forbidden")))
    )

    assert usage == {"error": "Docker disk usage is unavailable"}


def test_disk_usage_reports_unavailable_without_a_client():
    assert DockerManager.get_disk_usage(_manager(None)) == {
        "error": "Docker client not available"
    }
