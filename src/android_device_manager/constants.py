from enum import Enum

DEFAULT_EMULATOR_PORT_START = 5554
DEFAULT_EMULATOR_PORT_END = 5682
EMULATOR_PORT_STEP = 2
DEFAULT_EMULATOR_START_DELAY = 2


class AndroidProp(Enum):
    """
    Common Android system properties for use with adb shell getprop.
    """

    ANDROID_VERSION = "ro.build.version.release"
    """Android OS version string (e.g. "12", "13")"""
    API_LEVEL = "ro.build.version.sdk"
    """Android API level (e.g. "34")"""
    DEVICE_MODEL = "ro.product.model"
    """Device model name (e.g. "Pixel 5")"""
    MANUFACTURER = "ro.product.manufacturer"
    """Device manufacturer (e.g. "Google")"""
    BRAND = "ro.product.brand"
    """Device brand (e.g. "Pixel")"""
    BOARD = "ro.product.board"
    """Device board (e.g. "goldfish_x86_64")"""
    BOOTLOADER = "ro.bootloader"
    """ Bootloader version"""
    FINGERPRINT = "ro.build.fingerprint"
    """Full build fingerprint (unique ID for the build)"""
    BUILD_ID = "ro.build.display.id"
    """Build display ID (e.g. "TQ3A.230805.001")"""
    HARDWARE = "ro.hardware"
    """Hardware name (e.g. "ranchu")"""
    BOOT_COMPLETED = "sys.boot_completed"
    """Indicates if system boot completed (should be "1" when ready)"""
    BOOTANIM = "init.svc.bootanim"
    """Boot animation service status (should be "stopped" when fully booted)"""
    FIRST_BOOT_COMPLETED = "sys.bootstat.first_boot_completed"
    """First boot completed marker (value "1" when fully booted)"""
    SERIAL = "ro.serialno"
    """Device serial number"""

    def __str__(self):
        return self.value
