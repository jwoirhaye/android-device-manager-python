import logging
import os
from pathlib import Path
from typing import Optional

from ..exceptions import AndroidSDKNotFound

logger = logging.getLogger(__name__)


class AndroidSDK:
    """Utility class for locating and querying the Android SDK."""

    def __init__(self, sdk_path: Optional[Path] = None):
        """
        Initialize the SDK object.

        Args:
            sdk_path (Optional[Path]): Path to the Android SDK. If None, the SDK path will be auto-detected.

        Raises:
            SDKNotFoundError: If the SDK cannot be found or is invalid.
        """
        self.sdk_path = sdk_path or self._find_sdk_path()
        if not self.sdk_path or not self.is_valid():
            raise AndroidSDKNotFound(str(self.sdk_path))

    @property
    def avdmanager_path(self) -> Path:
        """
        Returns the path to `avdmanager`.

        Returns:
            Path: Absolute path to the avdmanager executable.
        """
        return self.sdk_path / "cmdline-tools" / "latest" / "bin" / "avdmanager"

    @property
    def emulator_path(self) -> Path:
        """
        Returns the path to the emulator binary.

        Returns:
            Path: Absolute path to the emulator executable.
        """
        return self.sdk_path / "emulator" / "emulator"

    @property
    def adb_path(self) -> Path:
        """
        Returns the path to the adb binary.

        Returns:
            Path: Absolute path to the adb executable.
        """
        return self.sdk_path / "platform-tools" / "adb"

    @property
    def sdkmanager_path(self) -> Path:
        """
        Returns the path to `sdkmanager`.

        Returns:
            Path: Absolute path to the sdkmanager executable.
        """
        return self.sdk_path / "cmdline-tools" / "latest" / "bin" / "sdkmanager"

    def is_valid(self) -> bool:
        """
        Checks if the SDK has the required tools.

        Returns:
            bool: True if all required tools exist, False otherwise.
        """
        required = [
            self.avdmanager_path,
            self.emulator_path,
            self.adb_path,
            self.sdkmanager_path,
        ]
        return all(tool.exists() for tool in required)

    @staticmethod
    def _find_sdk_path() -> Optional[Path]:
        """
        Attempts to locate the Android SDK path on the machine.

        Returns:
            Optional[Path]: Path if found, otherwise None.
        """
        for env_var in ("ANDROID_HOME", "ANDROID_SDK_ROOT"):
            p = os.environ.get(env_var)
            if p:
                path = Path(p)
                if path.exists():
                    return path
        candidates = [
            Path.home() / "Android" / "Sdk",
            Path("/usr/local/android-sdk"),
            Path("/opt/android-sdk"),
        ]
        for path in candidates:
            if path.exists():
                return path
        return None
