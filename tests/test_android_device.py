from unittest import mock

import pytest

from android_device_manager.adb.exceptions import ADBError
from android_device_manager.android_device import AndroidDevice, AndroidDeviceState
from android_device_manager.avd.config import AVDConfiguration
from android_device_manager.avd.exceptions import AVDCreationError, AVDDeletionError
from android_device_manager.emulator.config import EmulatorConfiguration
from android_device_manager.emulator.exceptions import EmulatorStartError


@pytest.fixture
def avd_config():
    return AVDConfiguration(
        name="TestAVD", package="system-images;android-34;google_apis;x86_64"
    )


@pytest.fixture
def emulator_config():
    return EmulatorConfiguration(no_window=True)


@pytest.fixture
def device(avd_config, emulator_config, fake_sdk_path):
    """
    Fixture returning an AndroidDevice with all managers mocked.
    Ensures SDK path resolution is patched to avoid AndroidSDKNotFound.
    """
    with (
        mock.patch("android_device_manager.android_device.AVDManager"),
        mock.patch("android_device_manager.android_device.EmulatorManager"),
        mock.patch("android_device_manager.android_device.AdbClient"),
    ):
        yield AndroidDevice(avd_config, emulator_config)


def test_device_init_state(device):
    assert device.state == AndroidDeviceState.NOT_CREATED


def test_create_avd_new(device):
    device._avd_manager.exist.return_value = False
    device._avd_manager.create.return_value = True
    device.create()
    device._avd_manager.create.assert_called_once()
    assert device.state == AndroidDeviceState.CREATED


def test_create_avd_exists(device):
    device._avd_manager.exist.return_value = True
    device.create()
    device._avd_manager.create.assert_not_called()
    assert device.state == AndroidDeviceState.CREATED


def test_create_avd_error(device):
    device._avd_manager.exist.return_value = False
    device._avd_manager.create.side_effect = AVDCreationError("TestAVD", "fail")
    with pytest.raises(AVDCreationError):
        device.create()
    assert device.state == AndroidDeviceState.ERROR


def test_start_success(device):
    device._emulator_manager.start_emulator.return_value = 5554
    device._adb_client = mock.Mock()

    with mock.patch("android_device_manager.android_device.AdbClient") as MockAdbClient:
        MockAdbClient.return_value.wait_for_boot.return_value = True
        device.start()
    assert device.state == AndroidDeviceState.RUNNING


@pytest.mark.parametrize(
    "exc", [EmulatorStartError("fail"), ADBError("fail"), TimeoutError()]
)
def test_start_error(device, exc):
    device._emulator_manager.start_emulator.side_effect = exc
    with pytest.raises(type(exc)):
        device.start()
    assert device.state == AndroidDeviceState.ERROR


def test_stop_success(device):
    device._adb_client = mock.Mock()
    device.state = AndroidDeviceState.RUNNING
    device.stop()
    assert device._adb_client is None
    assert device.state == AndroidDeviceState.STOPPED


def test_stop_error(device):
    device._adb_client = mock.Mock()
    device._adb_client.kill_emulator.side_effect = Exception("fail")
    with pytest.raises(Exception):
        device.stop()
    assert device.state == AndroidDeviceState.ERROR


def test_delete_success(device):
    device._avd_manager.delete.return_value = True
    device.delete()
    device._avd_manager.delete.assert_called_once()
    assert device.state == AndroidDeviceState.NOT_CREATED


def test_delete_error(device):
    device._avd_manager.delete.side_effect = Exception("fail")
    with pytest.raises(AVDDeletionError):
        device.delete()
    assert device.state == AndroidDeviceState.ERROR


def test_context_manager_success(device):
    device._avd_manager.exist.return_value = False
    device._avd_manager.create.return_value = True
    device._emulator_manager.start_emulator.return_value = 5554
    with mock.patch("android_device_manager.android_device.AdbClient") as MockAdbClient:
        MockAdbClient.return_value.wait_for_boot.return_value = True
        with (
            mock.patch.object(device, "stop") as m_stop,
            mock.patch.object(device, "delete") as m_delete,
        ):
            with device as d:
                assert d is device
                assert device.state in (
                    AndroidDeviceState.CREATED,
                    AndroidDeviceState.RUNNING,
                )
            m_stop.assert_called()
            m_delete.assert_called()
