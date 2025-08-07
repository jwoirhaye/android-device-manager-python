from pathlib import Path
from unittest import mock

import pytest

from android_device_manager.exceptions import AndroidSDKNotFound
from android_device_manager.utils.android_sdk import AndroidSDK


def test_sdk_manual_path(fake_sdk_path):
    """Test initialization with an explicit, complete SDK path."""
    sdk = AndroidSDK(fake_sdk_path)
    assert sdk.sdk_path == fake_sdk_path
    assert sdk.is_valid()
    assert sdk.adb_path.exists()
    assert sdk.avdmanager_path.exists()
    assert sdk.emulator_path.exists()
    assert sdk.sdkmanager_path.exists()


def test_sdk_invalid_path(tmp_path):
    """Test initialization with a path that lacks required tools."""
    bad_path = tmp_path / "empty-sdk"
    bad_path.mkdir()
    with pytest.raises(AndroidSDKNotFound):
        AndroidSDK(bad_path)


def test_sdk_auto_env(fake_sdk_path):
    """Test auto-detection via environment variable."""
    sdk = AndroidSDK()
    assert sdk.is_valid()
    assert sdk.sdk_path == fake_sdk_path


def test_sdk_auto_env_not_found(monkeypatch):
    """Test auto-detection when nothing is found."""
    monkeypatch.delenv("ANDROID_SDK_ROOT", raising=False)
    monkeypatch.delenv("ANDROID_HOME", raising=False)

    with mock.patch(
        "android_device_manager.utils.android_sdk.Path.exists", return_value=False
    ):
        with pytest.raises(AndroidSDKNotFound):
            AndroidSDK()


@pytest.mark.no_fake_sdk
def test_sdk_path_candidates(tmp_path, monkeypatch):
    """Test detection via default candidates (HOME/Android/Sdk, etc.)."""
    home_sdk = tmp_path / "Android" / "Sdk"
    (home_sdk / "cmdline-tools" / "latest" / "bin").mkdir(parents=True)
    (home_sdk / "platform-tools").mkdir(parents=True)
    (home_sdk / "emulator").mkdir(parents=True)
    (home_sdk / "cmdline-tools" / "latest" / "bin" / "avdmanager").touch()
    (home_sdk / "cmdline-tools" / "latest" / "bin" / "sdkmanager").touch()
    (home_sdk / "platform-tools" / "adb").touch()
    (home_sdk / "emulator" / "emulator").touch()

    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    monkeypatch.setattr(
        "android_device_manager.utils.android_sdk.AndroidSDK._find_sdk_path",
        lambda self: home_sdk,
    )

    sdk = AndroidSDK()
    assert sdk.sdk_path == home_sdk
    assert sdk.is_valid()
