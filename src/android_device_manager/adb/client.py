import logging
import subprocess
from pathlib import Path
from typing import Optional

from ..adb.exceptions import ADBError, ADBTimeoutError
from ..constants import AndroidProp
from ..utils.android_sdk import AndroidSDK

logger = logging.getLogger(__name__)


class AdbClient:
    """
    A client for interacting with an Android emulator/device via the Android Debug Bridge (ADB).
    """

    def __init__(self, emulator_port: int, android_sdk: Optional[AndroidSDK] = None):
        """
        Initialize the AdbClient.

        Args:
            emulator_port (int): The TCP port number of the emulator (e.g., 5554).
            android_sdk (AndroidSDK): The Android SDK abstraction providing the adb path.
        """
        self._port = emulator_port
        self._serial = f"emulator-{self._port}"
        self._android_sdk = android_sdk or AndroidSDK()
        self._adb_path = self._android_sdk.adb_path

    def get_all_props(self, timeout: int = 10) -> dict[str, str]:
        """
        Get all Android system properties as a dictionary.

        Args:
            timeout (int): Timeout in seconds.

        Returns:
            dict[str, str]: All system properties as {key: value}

        Raises:
            ADBError: On failure.
        """
        result = self.shell(["getprop"], timeout=timeout)
        props = {}
        for line in result.stdout.splitlines():
            if line.startswith("[") and "]:" in line:
                key, value = line.split("]: [", 1)
                key = key[1:]
                value = value.rstrip("]")
                props[key] = value
        return props

    def get_prop(
        self, key: str | AndroidProp, timeout: int = 10, check: bool = True
    ) -> str:
        """
        Get a single Android system property via adb.

        Args:
            key (str or AndroidProp): The name of the property, or an AndroidProp Enum.
            timeout (int): Timeout in seconds.
            check (bool): Raise if the command fails.

        Returns:
            str: Value of the property, or '' if not found.

        Raises:
            ADBError: If the adb command fails.
        """
        if isinstance(key, AndroidProp):
            key = key.value
        result = self.shell(["getprop", key], timeout=timeout, check=check)
        return result.stdout.strip()

    def wait_for_boot(self, timeout: int = 120) -> bool:
        """
        Wait for the emulator to fully boot (until 'sys.boot_completed' is set).

        Args:
            timeout (int): Maximum time to wait in seconds (default: 120).

        Returns:
            bool: True if the device booted successfully before the timeout.

        Raises:
            TimeoutError: If the device did not boot in the specified time.
        """
        import time

        start_time = time.time()
        while time.time() - start_time < timeout:
            result_boot_completed = self.get_prop(
                AndroidProp.BOOT_COMPLETED, check=False
            )
            if result_boot_completed == "1":
                return True
        raise ADBTimeoutError(
            f"Device {self._serial} did not boot within {timeout} seconds."
        )

    def kill_emulator(self):
        """
        Kill (terminate) the emulator instance via ADB.

        Raises:
            ADBError: If the emulator could not be killed.
        """
        logger.info(f"Killing emulator with serial: {self._serial}")
        try:
            self._run_adb_command(["emu", "kill"])
            logger.info(f"Successfully killed emulator {self._serial}")
        except ADBError as e:
            raise ADBError(f"Failed to kill emulator {self._serial}: {str(e)}")

    def root(self, timeout: int = 10, check: bool = True) -> bool:
        """
        Restart adbd with root permissions, if possible.

        Args:
            timeout (int): Timeout for the command (default: 10s)
            check (bool): Raise if the command fails.

        Returns:
            bool: True if adbd is now running as root, False otherwise.

        Raises:
            ADBError: On failure to restart adbd.
        """
        self._run_adb_command(["root"], timeout=timeout, check=check)
        return self.is_root()

    def unroot(self, timeout: int = 10, check: bool = True) -> bool:
        self._run_adb_command(["unroot"], timeout=timeout, check=check)
        return not self.is_root()

    def is_root(self, timeout: int = 10) -> bool:
        """
        Check if adbd is running as root on the device.

        Returns:
            bool: True if running as root, False otherwise.
        """
        result = self.shell(["id", "-u"], timeout=timeout, check=True)
        return result.stdout.strip() == "0"

    def list_installed_packages(self) -> list[str]:
        """
        List installed package names on the device.
        Returns:
            list[str]: Package names.
        Raises:
            ADBError: On failure.
        """
        result = self.shell(["pm", "list", "packages"], check=True)
        lines = result.stdout.strip().splitlines()
        return [
            line[len("package:") :].strip()
            for line in lines
            if line.startswith("package:")
        ]

    def install_apk(self, apk_path: str, timeout: int = 60):
        """
        Install an APK file on the device.

        Args:
            apk_path (str): Path to the APK file on the host.
            timeout (int): Timeout in seconds for the installation.

        Raises:
            ADBError: If the installation fails.
        """
        try:
            args = ["install", apk_path]
            self._run_adb_command(args, check=True, timeout=timeout)
            logger.info(f"Successfully installed APK {apk_path} on {self._serial}")
        except ADBError as e:
            raise ADBError(f"Failed to install APK {apk_path}: {str(e)}")

    def uninstall_package(
        self, package_name: str, keep_data: bool = False, timeout: int = 60
    ) -> None:
        """
        Uninstall a package from the device.

        Args:
            package_name (str): The full package name to uninstall.
            keep_data (bool): If True, keep app data and cache (default: False).
            timeout (int): Timeout in seconds.

        Raises:
            ADBError: If the uninstallation fails.
        """
        cmd = ["uninstall"]
        if keep_data:
            cmd.append("-k")
        cmd.append(package_name)
        result = self._run_adb_command(cmd, timeout=timeout, check=True)
        output = result.stdout.strip().lower()
        if "success" not in output:
            raise ADBError(f"Failed to uninstall package '{package_name}': {output}")

    def push_file(
        self, local: str | Path, remote: str, timeout: int = 60, check: bool = True
    ) -> None:
        """
        Push a file from the local host to the device.

        Args:
            local (str | Path): Path to the local file.
            remote (str): Destination path on the device (e.g., /sdcard/file.txt).
            timeout (int): Timeout in seconds.
            check (bool): Raise exception on failure.

        Raises:
            ADBError: If the command fails.
            ADBTimeoutError: On timeout.
        """
        local_path = str(local)
        args = ["push", local_path, remote]
        self._run_adb_command(args, timeout=timeout, check=check)

    def pull_file(
        self, remote: str, local: str | Path, timeout: int = 60, check: bool = True
    ) -> None:
        """
        Pull a file from the device to the local host.

        Args:
            remote (str): Path to the file on the device.
            local (str | Path): Destination path on the host.
            timeout (int): Timeout in seconds.
            check (bool): Raise exception on failure.

        Raises:
            ADBError: If the command fails.
            ADBTimeoutError: On timeout.
        """
        local_path = str(local)
        args = ["pull", remote, local_path]
        self._run_adb_command(args, timeout=timeout, check=check)

    def get_logcat(
        self,
        filter_spec: Optional[list[str]] = None,
        timeout: int = 30,
        check: bool = True,
    ) -> str:
        """
        Retrieve logcat output from the device.

        Args:
            filter_spec (Optional[List[str]]): List of filter spec strings, e.g., ['*:E', 'ActivityManager:I']
            timeout (int): Timeout for the command.
            check (bool): Raise on non-zero exit code.

        Returns:
            str: Logcat output (stdout).

        Raises:
            ADBError: If adb command fails.
            ADBTimeoutError: On timeout.
        """
        args = ["logcat", "-d"]
        if filter_spec:
            args.extend(filter_spec)
        result = self._run_adb_command(args, timeout=timeout, check=check)
        return result.stdout

    def clear_logcat(self, timeout: int = 10, check: bool = True) -> None:
        """
        Clear the device logcat buffer.

        Args:
            timeout (int): Timeout for the command (default: 10 seconds).
            check (bool): If True, raise if the command fails.

        Raises:
            ADBError: If the command fails.
            AVDTimeoutError: On timeout.
        """
        args = ["logcat", "-c"]
        self._run_adb_command(args, timeout=timeout, check=check)

    def shell(
        self, cmd: list[str], timeout: int = 30, check: bool = True
    ) -> subprocess.CompletedProcess:
        """
        Execute a shell command on the device/emulator via ADB.

        Args:
            cmd (list[str]): The shell command as a list of arguments. Example: ["ls", "/sdcard"]
            timeout (int): Timeout for the command (default: 30).
            check (bool): If True, raise an exception for non-zero exit code.

        Returns:
            subprocess.CompletedProcess: The result object (stdout, stderr, etc.).

        Raises:
            ADBError: If the command fails (and check=True).
            ADBTimeoutError: On timeout.
        """
        args = ["shell"] + cmd
        return self._run_adb_command(args, timeout=timeout, check=check)

    def _run_adb_command(
        self, args: list[str], timeout: int = 30, check: bool = True
    ) -> subprocess.CompletedProcess:
        """
        Run an ADB command for the associated emulator/device with error handling.

        Args:
            args (list[str]): List of ADB command arguments (excluding adb and -s).
            timeout (int): Timeout in seconds for the command (default: 30).
            check (bool): If True, CalledProcessError is raised for non-zero return codes.

        Returns:
            subprocess.CompletedProcess: The result object from subprocess.run.

        Raises:
            ADBError: If the command fails (non-zero return code or unexpected error).
            ADBTimeoutError: If the command times out.

        """
        cmd = [str(self._adb_path), "-s", self._serial] + args
        logger.debug(f"Executing ADB command: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout, check=check
            )
            logger.debug("ADB stdout: %s", result.stdout.strip())
            logger.debug("ADB stderr: %s", result.stderr.strip())
            return result
        except subprocess.CalledProcessError as e:
            logger.error(
                "ADB (%s): command failed: %r (exit code %d)\nstdout: %s\nstderr: %s",
                self._serial,
                e.cmd,
                e.returncode,
                (e.stdout or "").strip(),
                (e.stderr or "").strip(),
            )
            raise ADBError(
                f"ADB command failed on {self._serial}: {e.cmd} (exit code {e.returncode})\n"
                f"stderr: {(e.stderr or '').strip()}",
                return_code=e.returncode,
                cmd=e.cmd,
                stdout=e.stdout,
                stderr=e.stderr,
                serial=self._serial,
            ) from e

        except subprocess.TimeoutExpired as e:
            logger.error(
                "ADB (%s): command timed out after %ds: %r\nPartial stdout: %s\nPartial stderr: %s",
                self._serial,
                timeout,
                e.cmd,
                e.stdout,
                e.stderr,
            )
            raise ADBTimeoutError(
                f"ADB command timed out after {timeout} seconds on {self._serial}: {e.cmd}"
            ) from e

        except Exception as e:
            logger.exception(
                "ADB (%s): Unexpected error while running ADB command", self._serial
            )
            raise ADBError(
                f"Unexpected error on {self._serial}: {str(e)}",
                cmd=cmd,
                serial=self._serial,
            ) from e

    def __repr__(self):
        return f"<AdbClient serial={self._serial}>"
