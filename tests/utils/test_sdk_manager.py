import subprocess
from unittest import mock

import pytest

from android_device_manager.exceptions import SDKManagerError


def make_sdkmanager_list_output(installed=None, available=None):
    installed = installed or []
    available = available or []
    lines = (
        [
            "Installed packages:",
            "-------------------",
            "Path | Version | Description | Location",
            "-------|---------|-------------|----------",
        ]
        + [f"{pkg} | 1.0 | desc | /some/path" for pkg in installed]
        + ["", "Available Packages:", "-------------------"]
        + available
    )
    return "\n".join(lines)


def test_is_system_image_installed_true(manager):
    output = make_sdkmanager_list_output(
        installed=["system-images;android-34;google_apis;x86_64"]
    )
    proc = mock.Mock()
    proc.stdout = output
    with mock.patch("subprocess.run", return_value=proc):
        assert (
            manager.is_system_image_installed(
                "system-images;android-34;google_apis;x86_64"
            )
            is True
        )


def test_is_system_image_installed_false(manager):
    output = make_sdkmanager_list_output(installed=["foo", "bar"])
    proc = mock.Mock()
    proc.stdout = output
    with mock.patch("subprocess.run", return_value=proc):
        assert manager.is_system_image_installed("not-present") is False


def test_is_system_image_installed_section_skips(manager):
    output = make_sdkmanager_list_output(
        installed=[], available=["system-images;android-34;google_apis;x86_64"]
    )
    proc = mock.Mock()
    proc.stdout = output
    with mock.patch("subprocess.run", return_value=proc):
        assert (
            manager.is_system_image_installed(
                "system-images;android-34;google_apis;x86_64"
            )
            is False
        )


def test_is_system_image_installed_calledprocesserror(manager):
    with mock.patch(
        "subprocess.run", side_effect=subprocess.CalledProcessError(1, ["foo"])
    ):
        with pytest.raises(SDKManagerError) as excinfo:
            manager.is_system_image_installed("foo")
        assert "Failed to list SDK packages" in str(excinfo.value)


def test_is_system_image_installed_generic_error(manager):
    with mock.patch("subprocess.run", side_effect=RuntimeError("fail")):
        with pytest.raises(SDKManagerError) as excinfo:
            manager.is_system_image_installed("foo")
        assert "Error checking system image installation" in str(excinfo.value)
