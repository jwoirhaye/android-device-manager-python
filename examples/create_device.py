from android_device_manager import AndroidDevice
from android_device_manager.avd.config import AVDConfiguration

device = AndroidDevice(
    AVDConfiguration(
        name="test_from_lib",
        package="system-images;android-36;google_apis;x86_64"
    )
)

device.create()

print(device._avd_manager.list())

device.delete()

print(device._avd_manager.list())
