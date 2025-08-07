import logging

from android_device_manager import AndroidDevice
from android_device_manager.avd.config import AVDConfiguration
from android_device_manager.emulator.config import EmulatorConfiguration

logging.basicConfig(level=logging.INFO)


avd_configuration = AVDConfiguration(
        name="test_from_lib", package="system-images;android-36;google_apis;x86_64"
    )

emulator_configuration = EmulatorConfiguration()

device = AndroidDevice(
    avd_config=avd_configuration,
    emulator_config=emulator_configuration,
)

device.create()
device.start()
device.stop()
device.delete()

