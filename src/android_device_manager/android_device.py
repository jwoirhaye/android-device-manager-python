import logging
from enum import Enum
from typing import Optional

from .adb.client import AdbClient
from .adb.exceptions import ADBError
from .avd.config import AVDConfiguration
from .avd.exceptions import AVDCreationError, AVDDeletionError
from .avd.manager import AVDManager
from .constants import AndroidProp
from .emulator.config import EmulatorConfiguration
from .emulator.exceptions import EmulatorStartError
from .emulator.manager import EmulatorManager
from .exceptions import AndroidDeviceError
from .utils.android_sdk import AndroidSDK

logger = logging.getLogger(__name__)


class AndroidDeviceState(Enum):
    """
    Enumeration of possible states for an AndroidDevice.

    Attributes:
        NOT_CREATED: The AVD does not exist yet.
        CREATED: The AVD exists but the emulator is not running.
        RUNNING: The emulator is running and fully booted.
        STOPPED: The emulator was running but is now stopped.
        ERROR: An error occurred during an operation.
    """

    NOT_CREATED = "not_created"
    CREATED = "created"
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"


class AndroidDevice:
    def __init__(
        self,
        avd_config: AVDConfiguration,
        emulator_config: Optional[EmulatorConfiguration] = None,
        android_sdk: Optional[AndroidSDK] = None,
    ):
        self._avd_config = avd_config
        self._emulator_config = emulator_config
        self.state = AndroidDeviceState.NOT_CREATED

        self._android_sdk = android_sdk or AndroidSDK()
        self._avd_manager = AVDManager(self._android_sdk)
        self._emulator_manager = EmulatorManager(self._android_sdk)
        self._adb_client: Optional[AdbClient] = None

    @property
    def name(self) -> str:
        """
        The name of the managed AVD.

        Returns:
            str: The name of the AVD.
        """
        return self._avd_config.name

    def create(self, force: bool = False) -> None:
        """
        Create the AVD if it does not exist.

        Args:
            force (bool): If True, overwrite any existing AVD with the same name.

        Raises:
            AVDCreationError: If the AVD cannot be created.
        """
        logger.info(f"Creating AVD '{self.name}'...")
        try:
            if not self._avd_manager.exist(self.name):
                self._avd_manager.create(self._avd_config, force=force)
                self.state = AndroidDeviceState.CREATED
                logger.info(f"AVD '{self.name}' created.")
            else:
                logger.info(f"AVD '{self.name}' already exists.")
                self.state = AndroidDeviceState.CREATED
        except AVDCreationError as e:
            self.state = AndroidDeviceState.ERROR
            raise e
        except Exception as e:
            self.state = AndroidDeviceState.ERROR
            logger.error(f"Failed to create AVD '{self.name}': {e}")
            raise AVDCreationError(self.name, f"Failed to create AVD : {e}") from e

    def delete(self):
        """
        Delete the AVD.

        Raises:
            AVDDeletionError: If deletion fails.
        """
        logger.info(f"Deleting AVD '{self.name}'...")
        try:
            self._avd_manager.delete(self.name)
            self.state = AndroidDeviceState.NOT_CREATED
            logger.info(f"AVD '{self.name}' deleted.")
        except Exception as e:
            self.state = AndroidDeviceState.ERROR
            logger.error(f"Failed to delete AVD '{self.name}': {e}")
            raise AVDDeletionError(self.name, f"Failed to delete AVD: {e}") from e

    def start(self):
        """
        Start the emulator for the current AVD and wait for it to boot.

        Raises:
            EmulatorStartError: If the emulator fails to start.
            ADBError: If there is an error communicating with the device.
            TimeoutError: If the emulator does not boot within the allowed time.
        """
        logger.info(f"Starting emulator for AVD '{self.name}'...")
        try:
            port = self._emulator_manager.start_emulator(
                avd_name=self.name,
                emulator_config=self._emulator_config,
            )
            self._adb_client = AdbClient(port, self._android_sdk)
            self._adb_client.wait_for_boot()
            self.state = AndroidDeviceState.RUNNING
            logger.info(f"Emulator for AVD '{self.name}' is running (port {port}).")
        except (EmulatorStartError, ADBError, TimeoutError) as e:
            self.state = AndroidDeviceState.ERROR
            logger.error(f"Failed to start emulator for '{self.name}': {e}")
            raise

    def stop(self):
        """
        Stop the running emulator and release resources.

        Raises:
            Exception: If stopping the emulator fails.
        """
        logger.info(f"Stopping emulator for AVD '{self.name}'...")
        try:
            if self._adb_client:
                self._adb_client.kill_emulator()
                self._adb_client = None
            self._emulator_manager.stop_emulator()
            self.state = AndroidDeviceState.STOPPED
            logger.info(f"Emulator for AVD '{self.name}' stopped.")
        except Exception as e:
            self.state = AndroidDeviceState.ERROR
            logger.error(f"Failed to stop emulator for '{self.name}': {e}")
            raise

    def get_prop(
            self, key: str | AndroidProp, timeout: int = 10, check: bool = True
    ) -> str:
        """
        Retrieve a single Android system property from the device.

        Args:
            key (str or AndroidProp): The name of the property, or an AndroidProp Enum.
            timeout (int): Timeout in seconds for the adb command (default: 10).
            check (bool): Whether to raise an exception if the command fails (default: True).

        Returns:
            str: The value of the requested property, or an empty string if not found.

        Raises:
            AndroidDeviceError: If the device is not started or the ADB client is not initialized.
            ADBError: If there is a failure in communicating with the device.
        """
        self._ensure_running()
        return self._adb_client.get_prop(key, timeout=timeout, check=check)

    def get_all_props(self, timeout: int = 10) -> dict[str, str]:
        """
        Retrieve all Android system properties from the device as a dictionary.

        Args:
            timeout (int): Timeout in seconds for the adb command (default: 10).

        Returns:
            dict[str, str]: A dictionary mapping property names to their values.

        Raises:
            AndroidDeviceError: If the device is not started or the ADB client is not initialized.
            ADBError: If there is a failure in communicating with the device.
        """
        self._ensure_running()
        return self._adb_client.get_all_props(timeout=timeout)

    def root(self) -> bool:
        """
        Restart the ADB daemon with root privileges.

        Returns:
            bool: True if the device is now running in root mode, False otherwise.

        Raises:
            AndroidDeviceError: If the device is not started or the ADB client is not initialized.
            ADBError: If the operation fails.
        """
        self._ensure_running()
        return self._adb_client.root()

    def unroot(self) -> bool:
        """
        Restart the ADB daemon without root privileges (back to user mode).

        Returns:
            bool: True if the device is now running in unrooted mode, False otherwise.

        Raises:
            AndroidDeviceError: If the device is not started or the ADB client is not initialized.
            ADBError: If the operation fails.
        """
        self._ensure_running()
        return self._adb_client.unroot()

    def is_root(self) -> bool:
        """
        Check if the ADB daemon is currently running with root privileges.

        Returns:
            bool: True if the device is running in root mode, False otherwise.

        Raises:
            AndroidDeviceError: If the device is not started or the ADB client is not initialized.
            ADBError: If the operation fails.
        """
        self._ensure_running()
        return self._adb_client.is_root()

    def list_installed_packages(self) -> list[str]:
        """
        List all installed package names on the device.

        Returns:
            list[str]: A list of installed package names.

        Raises:
            AndroidDeviceError: If the device is not running or the ADB client is not initialized.
            ADBError: If the command fails.
        """
        self._ensure_running()
        return self._adb_client.list_installed_packages()

    def is_package_installed(self, package_name: str) -> bool:
        """
        Check if a given package is installed on the device.

        Args:
            package_name (str): The package name to check.

        Returns:
            bool: True if the package is installed, False otherwise.

        Raises:
            AndroidDeviceError: If the device is not running or the ADB client is not initialized.
            ADBError: If the command fails.
        """
        self._ensure_running()
        return package_name in self._adb_client.list_installed_packages()

    def install_apk(self, apk_path: str, timeout: int = 30) -> None:
        """
        Install an APK on the device.

        Args:
            apk_path (str): The file path to the APK.
            timeout (int): Timeout in seconds for the installation process (default: 30).

        Raises:
            AndroidDeviceError: If the device is not running or the ADB client is not initialized.
            ADBError: If the command fails.
        """
        self._ensure_running()
        self._adb_client.install_apk(apk_path, timeout=timeout)

    def uninstall_package(self, package_name: str, keep_data: bool = False) -> None:
        """
        Uninstall a package from the device.

        Args:
            package_name (str): The name of the package to uninstall.
            keep_data (bool): If True, application data and cache are retained (default: False).

        Raises:
            AndroidDeviceError: If the device is not running, the ADB client is not initialized,
                or the package is not installed.
            ADBError: If the command fails.
        """
        self._ensure_running()
        if not self.is_package_installed(package_name):
            raise AndroidDeviceError(f"Package '{package_name}' is not installed.")
        self._adb_client.uninstall_package(package_name, keep_data=keep_data)

    def _ensure_running(self):
        """
        Ensure that the Android device is started and the ADB client is initialized.

        Raises:
            AndroidDeviceError: If the device is not running or the ADB client is not available.
        """
        if self.state != AndroidDeviceState.RUNNING or not self._adb_client:
            raise AndroidDeviceError(
                "ADB client not initialized. Device must be started."
            )

    def __enter__(self):
        """
        Context manager entry: ensure device is created and started.
        """
        if self.state == AndroidDeviceState.NOT_CREATED:
            self.create()
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit: stop the emulator and (optionally) delete the AVD.
        """
        try:
            self.stop()
        except Exception as e:
            logger.warning(f"Error while stopping emulator: {e}")
        try:
            self.delete()
        except Exception as e:
            logger.warning(f"Error while deleting AVD: {e}")

    def __repr__(self):
        return f"<AndroidDevice name={self.name} state={self.state.value}>"
