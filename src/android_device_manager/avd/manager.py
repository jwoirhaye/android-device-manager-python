import logging
import subprocess
from typing import List

from ..avd.config import AVDConfiguration
from ..avd.exceptions import AVDCreationError, AVDDeletionError
from ..utils.android_sdk import AndroidSDK
from ..utils.sdk_manager import SDKManager
from ..utils.validation import is_valid_avd_name

logger = logging.getLogger(__name__)


class AVDManager:
    """
    High-level manager for Android Virtual Devices (AVDs).
    """

    def __init__(self, sdk: AndroidSDK):
        """
        Initialize the AVDManager.

        Args:
            sdk (AndroidSDK): The Android SDK abstraction for resolving paths.
        """
        self.sdk = sdk
        self.avd_manager_path = self.sdk.avdmanager_path
        self._sdk_manager = SDKManager(sdk)

    def create(self, config: AVDConfiguration, force: bool = False) -> bool:
        """
        Create a new AVD with the specified configuration.

        Args:
            config: AVDConfiguration instance
            force: Overwrite existing AVD if True

        Returns:
            bool: True if AVD was created successfully

        Raises:
            AVDCreationError: If creation fails
        """
        try:
            logger.info(f"Creating AVD '{config.name}' with package '{config.package}'")

            if not is_valid_avd_name(config.name):
                raise AVDCreationError(
                    config.name,
                    f"Invalid AVD name '{config.name}'. Must start with a letter and contain only letters, digits, underscores or hyphens.",
                )

            if not force and self.exist(config.name):
                raise AVDCreationError(
                    config.name,
                    f"AVD '{config.name}' already exists. Use force=True to overwrite.",
                )

            if not self._sdk_manager.is_system_image_installed(config.package):
                raise AVDCreationError(
                    config.name,
                    f"System image '{config.package}' is not available. Please install it first.",
                )

            args = [
                "-s",
                "create",
                "avd",
                "--name",
                config.name,
                "--package",
                config.package,
            ]
            if force:
                args.append("--force")

            result = self._run_avd_command(args, timeout=120)
            if result.returncode != 0:
                error_msg = result.stderr.strip() if result.stderr else "Unknown error"
                raise AVDCreationError(
                    config.name,
                    f"Failed to create AVD '{config.name}': {error_msg}",
                )

            logger.info(f"AVD '{config.name}' created successfully")
            return True
        except subprocess.TimeoutExpired:
            raise AVDCreationError(
                config.name, f"Timeout while creating AVD '{config.name}'"
            )
        except AVDCreationError:
            raise
        except Exception as e:
            logger.error(
                f"Unexpected error creating AVD '{config.name}': {e}", exc_info=True
            )

            raise AVDCreationError(config.name, str(e)) from e

    def delete(self, name: str) -> bool:
        """
        Delete an existing AVD by name.

        Args:
            name: Name of the AVD to delete

        Returns:
            bool: True if AVD was deleted successfully

        Raises:
            AVDDeletionError: If AVD deletion fails
        """
        try:
            logger.info(f"Deleting AVD '{name}'")

            if not self.exist(name):
                logger.warning(f"AVD '{name}' does not exist")
                return True

            args = ["delete", "avd", "--name", name]
            result = self._run_avd_command(args, timeout=60)

            if result.returncode != 0:
                error_msg = result.stderr.strip() if result.stderr else "Unknown error"
                raise AVDDeletionError(name, error_msg)

            logger.info(f"AVD '{name}' deleted successfully")
            return True

        except subprocess.TimeoutExpired:
            raise AVDDeletionError(name, f"Timeout while deleting AVD '{name}'")
        except AVDDeletionError:
            raise
        except Exception as e:
            raise AVDDeletionError(
                name, f"Unexpected error deleting AVD '{name}': {str(e)}"
            ) from e

    def list(self) -> List[str]:
        """
        List all available AVD names.

        Returns:
            List[str]: Names of all available AVDs
        """
        try:
            cmd = ["list", "avd", "-c"]
            result = self._run_avd_command(cmd, timeout=30, check=True)
            return self._parse_avd_list(result.stdout)
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to list AVDs: {e.stderr}")
            return []
        except subprocess.TimeoutExpired:
            logger.error("Timeout while listing AVDs")
            return []
        except Exception as e:
            logger.error(f"Unexpected error listing AVDs: {str(e)}")
            return []

    def exist(self, name: str) -> bool:
        return name in self.list()

    @staticmethod
    def _parse_avd_list(output: str) -> List[str]:
        """
        Parse the output from 'avdmanager list avd -c' to get AVD names.

        Args:
            output: Raw output string from avdmanager

        Returns:
            List[str]: List of AVD names
        """
        return [line.strip() for line in output.strip().splitlines() if line.strip()]

    def _run_avd_command(
        self,
        args: List[str],
        timeout: int = 60,
        check: bool = True,
    ) -> subprocess.CompletedProcess:
        """
        Internal helper to run an avdmanager CLI command.

        Args:
            args (List[str]): CLI arguments to pass (excluding avdmanager itself).
            timeout (int): Timeout in seconds for the command (default: 60).
            check (bool): If True, CalledProcessError is raised for non-zero return code.

        Returns:
            subprocess.CompletedProcess: The result of the subprocess.run call.

        Raises:
            subprocess.TimeoutExpired: If the command times out.
            subprocess.CalledProcessError: If the command fails (when check=True).
            Exception: For any other unexpected error.
        """
        cmd = [str(self.avd_manager_path)] + args

        logger.debug(f"Running avdmanager command: {' '.join(cmd)}")
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=check,
            )
            logger.debug(f"stdout: {result.stdout.strip()}")
            logger.debug(f"stderr: {result.stderr.strip()}")
            return result
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout expired for command: {' '.join(cmd)}")
            raise
        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed: {e.stderr.strip() if e.stderr else e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error running command: {e}")
            raise
