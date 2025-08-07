import logging
import subprocess
from enum import Enum
from pathlib import Path
from time import sleep
from typing import Optional, List, Union, Dict


from .avd.config import AVDConfiguration
from .avd.exceptions import AVDCreationError, AVDDeletionError
from .avd.manager import AVDManager
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
        android_sdk: Optional[AndroidSDK] = None,
    ):
        self._avd_config = avd_config
        self.state = AndroidDeviceState.NOT_CREATED

        self._android_sdk = android_sdk or AndroidSDK()
        self._avd_manager = AVDManager(self._android_sdk)

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