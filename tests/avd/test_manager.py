from unittest import mock

import pytest

from android_device_manager.avd.config import AVDConfiguration
from android_device_manager.avd.exceptions import AVDCreationError, AVDDeletionError
from android_device_manager.avd.manager import AVDManager


@pytest.fixture
def fake_sdk():
    return mock.Mock()


@pytest.fixture
def fake_sdk_manager():
    return mock.Mock()


@pytest.fixture
def avd_manager(fake_sdk, fake_sdk_manager, monkeypatch):
    monkeypatch.setattr(
        "android_device_manager.avd.manager.SDKManager", lambda sdk: fake_sdk_manager
    )
    monkeypatch.setattr(
        "android_device_manager.avd.manager.is_valid_avd_name", lambda name: True
    )

    with mock.patch.object(AVDManager, "_run_avd_command"):
        yield AVDManager(fake_sdk)


def test_create_success(avd_manager, fake_sdk_manager):
    fake_sdk_manager.is_system_image_installed.return_value = True
    avd_manager.exist = mock.Mock(return_value=False)

    avd_manager._run_avd_command.return_value = mock.Mock(
        returncode=0, stderr="", stdout=""
    )
    config = AVDConfiguration(
        name="MyAVD", package="system-images;android-34;google_apis;x86_64"
    )
    assert avd_manager.create(config) is True


def test_create_invalid_name(avd_manager, monkeypatch):
    monkeypatch.setattr(
        "android_device_manager.avd.manager.is_valid_avd_name", lambda name: False
    )
    config = AVDConfiguration(
        name="bad name", package="system-images;android-34;google_apis;x86_64"
    )
    with pytest.raises(AVDCreationError) as e:
        avd_manager.create(config)
    assert "Invalid AVD name" in str(e.value)


def test_create_existing_avd(avd_manager, fake_sdk_manager):
    avd_manager.exist = mock.Mock(return_value=True)
    config = AVDConfiguration(
        name="MyAVD", package="system-images;android-34;google_apis;x86_64"
    )
    with pytest.raises(AVDCreationError) as e:
        avd_manager.create(config)
    assert "already exists" in str(e.value)


def test_create_image_not_installed(avd_manager, fake_sdk_manager):
    avd_manager.exist = mock.Mock(return_value=False)
    fake_sdk_manager.is_system_image_installed.return_value = False
    config = AVDConfiguration(
        name="MyAVD", package="system-images;android-34;google_apis;x86_64"
    )
    with pytest.raises(AVDCreationError) as e:
        avd_manager.create(config)
    assert "is not available" in str(e.value)


def test_create_run_error(avd_manager, fake_sdk_manager):
    avd_manager.exist = mock.Mock(return_value=False)
    fake_sdk_manager.is_system_image_installed.return_value = True
    avd_manager._run_avd_command.return_value = mock.Mock(
        returncode=1, stderr="fail", stdout=""
    )
    config = AVDConfiguration(
        name="MyAVD", package="system-images;android-34;google_apis;x86_64"
    )
    with pytest.raises(AVDCreationError) as e:
        avd_manager.create(config)
    assert "Failed to create AVD" in str(e.value)


def test_create_timeout(avd_manager, fake_sdk_manager):
    avd_manager.exist = mock.Mock(return_value=False)
    fake_sdk_manager.is_system_image_installed.return_value = True
    avd_manager._run_avd_command.side_effect = Exception("timeout")
    config = AVDConfiguration(
        name="MyAVD", package="system-images;android-34;google_apis;x86_64"
    )
    with pytest.raises(AVDCreationError):
        avd_manager.create(config)


def test_delete_success(avd_manager):
    avd_manager.exist = mock.Mock(return_value=True)
    avd_manager._run_avd_command.return_value = mock.Mock(
        returncode=0, stderr="", stdout=""
    )
    assert avd_manager.delete("MyAVD") is True


def test_delete_avd_not_exists(avd_manager):
    avd_manager.exist = mock.Mock(return_value=False)

    assert avd_manager.delete("NotExist") is True


def test_delete_run_error(avd_manager):
    avd_manager.exist = mock.Mock(return_value=True)
    avd_manager._run_avd_command.return_value = mock.Mock(
        returncode=1, stderr="fail", stdout=""
    )
    with pytest.raises(AVDDeletionError):
        avd_manager.delete("MyAVD")


def test_list_and_exist(avd_manager):
    avd_manager._run_avd_command.return_value = mock.Mock(stdout="foo\nbar\nbaz\n")
    result = avd_manager.list()
    assert result == ["foo", "bar", "baz"]
    avd_manager._run_avd_command.return_value = mock.Mock(stdout="foo\nbar\n")
    assert avd_manager.exist("foo") is True
    assert avd_manager.exist("notfound") is False


def test_parse_avd_list_static():
    from android_device_manager.avd.manager import AVDManager

    output = "foo\nbar\nbaz\n"
    assert AVDManager._parse_avd_list(output) == ["foo", "bar", "baz"]
    output = "\n  \n"
    assert AVDManager._parse_avd_list(output) == []
