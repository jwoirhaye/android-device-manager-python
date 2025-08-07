import logging
import socket
import subprocess
import time
from typing import Optional

from ..constants import (
    EMULATOR_PORT_STEP,
    DEFAULT_EMULATOR_PORT_END,
    DEFAULT_EMULATOR_PORT_START,
    DEFAULT_EMULATOR_START_DELAY,
)
from ..emulator.config import EmulatorConfiguration
from ..emulator.exceptions import (
    EmulatorPortAllocationError,
    EmulatorStartError,
)
from ..utils.android_sdk import AndroidSDK

logger = logging.getLogger(__name__)


class EmulatorManager:
    """
    Manager for starting and stopping Android emulator instances.
    """

    def __init__(self, sdk: AndroidSDK):
        """
        Initialize the EmulatorManager.

        Args:
            sdk (AndroidSDK): The SDK wrapper containing the path to the emulator.
        """
        self._emulator_path = sdk.emulator_path
        self._process: Optional[subprocess.Popen] = None

    def start_emulator(
        self, avd_name: str, emulator_config: Optional[EmulatorConfiguration] = None
    ) -> int:
        """
        Start an Android emulator for a given AVD.

        Args:
            avd_name (str): The name of the AVD to start.
            emulator_config (Optional[EmulatorConfiguration]): Optional configuration for the emulator.

        Returns:
            int: The port on which the emulator is running.

        Raises:
            EmulatorPortAllocationError: If no free emulator port can be found.
            EmulatorStartError: If the emulator fails to start.
        """
        logger.info(f"Starting emulator for AVD '{avd_name}'")

        free_port = self._find_free_emulator_port()
        if free_port is None:
            raise EmulatorPortAllocationError(
                f"No free emulator port found to emulate AVD {avd_name}"
            )

        cmd = [str(self._emulator_path), "-avd", avd_name, "-port", str(free_port)]

        if emulator_config:
            cmd.extend(emulator_config.to_args())

        try:
            logger.debug(f"Executing command: {' '.join(cmd)}")
            self._process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )

            time.sleep(DEFAULT_EMULATOR_START_DELAY)

            if self._process.poll() is not None:
                stdout, stderr = self._process.communicate()
                logger.error(f"Emulator output: {stdout}")
                logger.error(f"Emulator error: {stderr}")
                raise EmulatorStartError(
                    f"Emulator '{avd_name}' failed to start. Check the logs for details."
                )

            logger.info(
                f"Emulator '{avd_name}' started successfully on port {free_port}"
            )
            return free_port

        except subprocess.CalledProcessError as e:
            raise EmulatorStartError(
                f"Failed to start emulator '{avd_name}': {e.stderr}"
            )
        except Exception as e:
            raise EmulatorStartError(
                f"Unexpected error starting emulator '{avd_name}': {str(e)}"
            )

    def stop_emulator(self) -> None:
        """
        Stop the currently running emulator process.

        Terminates the emulator process if it is still running. If the process does not stop
        gracefully within 10 seconds, it is forcibly killed.
        """
        if self._process and self._process.poll() is None:
            logger.info("Stopping emulator process")
            self._process.terminate()
            try:
                self._process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                logger.warning("Emulator process did not stop gracefully, killing")
                self._process.kill()
            self._process = None

    @staticmethod
    def _find_free_emulator_port(
        start: int = DEFAULT_EMULATOR_PORT_START, end: int = DEFAULT_EMULATOR_PORT_END
    ) -> Optional[int]:
        """
        Find a free even-numbered TCP port suitable for an Android emulator.

        Args:
            start (int): Starting port number to search.
            end (int): Ending port number to search.

        Returns:
            Optional[int]: Free port number if found, else None.
        """
        for port in range(start, end + 1, EMULATOR_PORT_STEP):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(("localhost", port))
                    logger.debug(f"Found free port: {port}")
                    return port
            except OSError:
                logger.debug(f"Port {port} is already in use")
                continue

        logger.warning(f"No free ports found in range {start}-{end}")
        return None

    def __del__(self):
        """Cleanup emulator process on destruction."""
        self.stop_emulator()
