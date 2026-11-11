"""RangeBox image availability and error-path tests."""
import docker

from app.services.docker_manager import DockerManager, RangeBoxImageUnavailableError


class _FakeImages:
    def __init__(self, installed):
        self.installed = set(installed)

    def get(self, name):
        if name in self.installed:
            return object()
        raise docker.errors.ImageNotFound("missing")


class _FakeClient:
    def __init__(self, installed):
        self.images = _FakeImages(installed)


def _manager(installed):
    manager = DockerManager.__new__(DockerManager)
    manager.client = _FakeClient(installed)
    return manager


def test_availability_reports_missing_remnux_without_failing_others():
    manager = _manager({
        "opencyberrange/rangebox:lite",
        "opencyberrange/ubuntubox:latest",
    })

    assert manager.rangebox_image_availability() == {
        "kali": True,
        "ubuntu": True,
        "remnux": False,
    }


def test_availability_is_false_when_docker_is_unavailable():
    manager = DockerManager.__new__(DockerManager)
    manager.client = None

    assert manager.rangebox_image_availability() == {
        "kali": False,
        "ubuntu": False,
        "remnux": False,
    }


def test_unavailable_image_error_names_the_image_and_shorthand():
    error = RangeBoxImageUnavailableError(
        "opencyberrange/remnuxbox:noble", "remnux"
    )

    assert error.image == "opencyberrange/remnuxbox:noble"
    assert error.shorthand == "remnux"
    assert "not installed" in str(error)
