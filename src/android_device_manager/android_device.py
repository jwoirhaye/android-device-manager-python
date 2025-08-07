import logging
from enum import Enum
from typing import Optional

from .adb.client import AdbClient
from .adb.exceptions import ADBError
from .avd.config import AVDConfiguration
from .avd.exceptions import AVDCreationError, AVDDeletionError
from .avd.manager import AVDManager
from .emulator.config import EmulatorConfiguration
from .emulator.exceptions import EmulatorStartError
from .emulator.manager import EmulatorManager
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

    def __repr__(self):
        return f"<AndroidDevice name={self.name} state={self.state.value}>"