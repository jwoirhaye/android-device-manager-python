import pytest

from android_device_manager.utils.android_sdk import AndroidSDK
from android_device_manager.utils.sdk_manager import SDKManager


@pytest.fixture(autouse=True)
def fake_sdk_path(monkeypatch, tmp_path, request):
    """
    Fixture that creates a fake Android SDK for tests.
    Returns the path to the fake SDK.

    Runs automatically for all tests unless disabled
    with @pytest.mark.no_fake_sdk.
    """
    if "no_fake_sdk" in request.keywords:
        yield None
        return

    sdk_root = tmp_path / "android-sdk"
    (sdk_root / "cmdline-tools" / "latest" / "bin").mkdir(parents=True)
    (sdk_root / "platform-tools").mkdir(parents=True)
    (sdk_root / "emulator").mkdir(parents=True)

    for tool in ("avdmanager", "sdkmanager"):
        (sdk_root / "cmdline-tools" / "latest" / "bin" / tool).touch()
    (sdk_root / "platform-tools" / "adb").touch()
    (sdk_root / "emulator" / "emulator").touch()

    monkeypatch.setenv("ANDROID_SDK_ROOT", str(sdk_root))
    monkeypatch.setattr(
        "android_device_manager.utils.android_sdk.AndroidSDK._find_sdk_path",
        lambda self: sdk_root,
    )

    yield sdk_root


@pytest.fixture
def fake_sdk(fake_sdk_path):
    return AndroidSDK(fake_sdk_path)


@pytest.fixture
def manager(fake_sdk):
    return SDKManager(fake_sdk)
