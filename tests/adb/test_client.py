import subprocess
from unittest import mock

import pytest

from android_device_manager.adb.client import AdbClient
from android_device_manager.adb.exceptions import ADBError, ADBTimeoutError


def test_init_sets_serial_and_adb_path(fake_sdk):
    client = AdbClient(5554, fake_sdk)
    assert client._port == 5554
    assert client._serial == "emulator-5554"
    assert client._adb_path == fake_sdk.adb_path


def test_run_adb_command_success(fake_sdk):
    client = AdbClient(5554, fake_sdk)
    mock_result = mock.Mock()
    mock_result.stdout = "success"
    mock_result.stderr = ""
    mock_result.returncode = 0

    with mock.patch("subprocess.run", return_value=mock_result) as m_run:
        result = client._run_adb_command(["shell", "echo", "ok"])
        m_run.assert_called_once()
        assert result.stdout == "success"


def test_run_adb_command_called_process_error(fake_sdk):
    client = AdbClient(5554, fake_sdk)
    e = subprocess.CalledProcessError(
        returncode=1, cmd="adb shell", output="out", stderr="fail"
    )
    with mock.patch("subprocess.run", side_effect=e):
        with pytest.raises(ADBError) as excinfo:
            client._run_adb_command(["shell", "fail"])
        assert "ADB command failed" in str(excinfo.value)


def test_run_adb_command_timeoutexpired(fake_sdk):
    client = AdbClient(5554, fake_sdk)
    e = subprocess.TimeoutExpired(
        cmd="adb shell", timeout=10, output="partial out", stderr="timeout"
    )
    with mock.patch("subprocess.run", side_effect=e):
        with pytest.raises(ADBTimeoutError) as excinfo:
            client._run_adb_command(["shell", "sleep"])
        assert "timed out" in str(excinfo.value)


def test_run_adb_command_unexpected_error(fake_sdk):
    client = AdbClient(5554, fake_sdk)
    with mock.patch("subprocess.run", side_effect=RuntimeError("BOOM")):
        with pytest.raises(ADBError) as excinfo:
            client._run_adb_command(["shell", "unknown"])
        assert "Unexpected error" in str(excinfo.value)


def test_wait_for_boot_success(fake_sdk):
    client = AdbClient(5554, fake_sdk)
    result = mock.Mock()
    result.stdout = "0"
    
    with mock.patch.object(
        client,
        "_run_adb_command",
        side_effect=[mock.Mock(stdout="0"), mock.Mock(stdout="1")],
    ):
        assert client.wait_for_boot(timeout=5) is True


def test_wait_for_boot_timeout(fake_sdk):
    client = AdbClient(5554, fake_sdk)
    
    with mock.patch.object(
        client, "_run_adb_command", return_value=mock.Mock(stdout="0")
    ):
        with pytest.raises(ADBTimeoutError):
            client.wait_for_boot(timeout=1)


def test_kill_emulator_success(fake_sdk):
    client = AdbClient(5554, fake_sdk)
    with mock.patch.object(client, "_run_adb_command", return_value=mock.Mock()):
        client.kill_emulator()  


def test_kill_emulator_adberror(fake_sdk):
    client = AdbClient(5554, fake_sdk)
    with mock.patch.object(client, "_run_adb_command", side_effect=ADBError("fail")):
        with pytest.raises(ADBError) as excinfo:
            client.kill_emulator()
        assert "Failed to kill emulator" in str(excinfo.value)
