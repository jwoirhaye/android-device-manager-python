import subprocess
from unittest import mock

import pytest

from android_device_manager.emulator.config import EmulatorConfiguration
from android_device_manager.emulator.exceptions import (
    EmulatorPortAllocationError,
    EmulatorStartError,
)
from android_device_manager.emulator.manager import EmulatorManager


@pytest.fixture
def fake_sdk():
    sdk = mock.Mock()
    sdk.emulator_path = "/fake/emulator"
    return sdk


@pytest.fixture
def manager(fake_sdk):
    return EmulatorManager(fake_sdk)


def test_start_emulator_success(manager, monkeypatch):
    monkeypatch.setattr(manager, "_find_free_emulator_port", lambda *a, **kw: 5554)
    popen_mock = mock.Mock()
    popen_mock.poll.return_value = None
    with mock.patch("subprocess.Popen", return_value=popen_mock):
        with mock.patch("time.sleep"):
            port = manager.start_emulator("TestAVD")
    assert port == 5554
    assert manager._process is popen_mock


def test_start_emulator_port_allocation_error(manager, monkeypatch):
    monkeypatch.setattr(manager, "_find_free_emulator_port", lambda *a, **kw: None)
    with pytest.raises(EmulatorPortAllocationError):
        manager.start_emulator("TestAVD")


def test_start_emulator_failure_on_launch(manager, monkeypatch):
    monkeypatch.setattr(manager, "_find_free_emulator_port", lambda *a, **kw: 5554)
    popen_mock = mock.Mock()

    popen_mock.poll.return_value = 1
    popen_mock.communicate.return_value = ("stdout output", "stderr output")
    with mock.patch("subprocess.Popen", return_value=popen_mock):
        with mock.patch("time.sleep"):
            with pytest.raises(EmulatorStartError) as excinfo:
                manager.start_emulator("TestAVD")
            assert "failed to start" in str(excinfo.value).lower()


def test_start_emulator_other_exception(manager, monkeypatch):
    monkeypatch.setattr(manager, "_find_free_emulator_port", lambda *a, **kw: 5554)
    with mock.patch("subprocess.Popen", side_effect=RuntimeError("fail")):
        with pytest.raises(EmulatorStartError) as excinfo:
            manager.start_emulator("TestAVD")
        assert "unexpected error" in str(excinfo.value).lower()


def test_start_emulator_with_config(manager, monkeypatch):
    monkeypatch.setattr(manager, "_find_free_emulator_port", lambda *a, **kw: 5560)
    popen_mock = mock.Mock()
    popen_mock.poll.return_value = None
    config = EmulatorConfiguration(no_window=True, gpu="swiftshader_indirect")
    with mock.patch("subprocess.Popen", return_value=popen_mock) as m_popen:
        with mock.patch("time.sleep"):
            port = manager.start_emulator("TestAVD", emulator_config=config)

    args = m_popen.call_args[0][0]
    assert "-no-window" in args
    assert "-gpu" in args and "swiftshader_indirect" in args
    assert port == 5560


def test_stop_emulator_graceful(manager):
    process = mock.Mock()
    process.poll.return_value = None
    manager._process = process
    manager.stop_emulator()
    process.terminate.assert_called_once()
    process.wait.assert_called_once_with(timeout=10)
    assert manager._process is None


def test_stop_emulator_kill_on_timeout(manager):
    process = mock.Mock()
    process.poll.return_value = None
    process.wait.side_effect = subprocess.TimeoutExpired(cmd="fake", timeout=10)
    manager._process = process
    manager.stop_emulator()
    process.terminate.assert_called_once()
    process.kill.assert_called_once()
    assert manager._process is None


def test_stop_emulator_nothing_to_do(manager):
    manager._process = None

    manager.stop_emulator()


def test_find_free_emulator_port(monkeypatch):
    from android_device_manager.emulator.manager import EmulatorManager

    called = {}

    def fake_bind(addr):
        called["called"] = True

    class FakeSocket:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            pass

        def bind(self, addr):
            fake_bind(addr)

    monkeypatch.setattr("socket.socket", lambda *a, **kw: FakeSocket())
    port = EmulatorManager._find_free_emulator_port(5554, 5556)
    assert port == 5554
    assert called["called"]


def test_find_free_emulator_port_none(monkeypatch):
    from android_device_manager.emulator.manager import EmulatorManager

    class FakeSocket:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            pass

        def bind(self, addr):
            raise OSError("fail")

    monkeypatch.setattr("socket.socket", lambda *a, **kw: FakeSocket())
    port = EmulatorManager._find_free_emulator_port(5554, 5556)
    assert port is None
