import logging
import subprocess

from ..exceptions import SDKManagerError
from ..utils.android_sdk import AndroidSDK

logger = logging.getLogger(__name__)


class SDKManager:
    """Wrapper around the `sdkmanager` CLI to interact with the Android SDK."""

    def __init__(self, sdk: AndroidSDK):
        self.sdkmanager_path = sdk.sdkmanager_path

    def is_system_image_installed(self, package: str) -> bool:
        """Checks whether a given Android system image is installed.

        It runs `sdkmanager --list` and parses the output to find if the
        system image is listed in the "Installed packages" section.

        Args:
            package (str): The full system image package path
                (e.g., "system-images;android-30;google_apis;x86").

        Returns:
            bool: True if the system image is installed, False otherwise.

        Raises:
            SDKManagerError: If the command fails or parsing fails.
        """
        try:
            result = subprocess.run(
                [self.sdkmanager_path, "--list"],
                capture_output=True,
                text=True,
                check=True,
            )

            output = result.stdout
            lines = output.split("\n")

            in_installed_section = False

            for line in lines:
                line = line.strip()

                if (
                    not line
                    or line.startswith("[=")
                    or line.startswith("Loading")
                    or line.startswith("Computing")
                ):
                    continue

                if line.startswith("Installed packages:"):
                    in_installed_section = True
                    continue

                if line.startswith("Available Packages:"):
                    break

                if line.startswith("Path") or line.startswith("-------"):
                    continue

                if in_installed_section:
                    parts = line.split("|")
                    if len(parts) >= 1:
                        package_path = parts[0].strip()
                        if package_path == package:
                            logger.debug(f"System image is installed: {package}")
                            return True

            logger.debug(f"System image is not installed: {package}")
            return False

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to execute sdkmanager --list: {e}")
            raise SDKManagerError(f"Failed to list SDK packages: {e}")
        except Exception as e:
            logger.error(f"Error checking system image installation: {e}")
            raise SDKManagerError(f"Error checking system image installation: {e}")
