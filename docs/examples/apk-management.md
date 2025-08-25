# APK Management

## Install, list, and uninstall APKs

```python
from android_device_manager import AndroidDevice
from android_device_manager.avd import AVDConfiguration
from android_device_manager.emulator import EmulatorConfiguration

# Configure your AVD
avd_config = AVDConfiguration(
    name="example_avd",
    package="system-images;android-34;google_apis;x86_64"
)

# Configure your Emulator
emulator_config = EmulatorConfiguration(
    no_window=True
)

with AndroidDevice(avd_config,emulator_config) as device:
    # Install APK
    device.install_apk("/path/to/app.apk")

    # List installed packages
    packages = device.list_installed_packages()
    print("Installed packages:")
    for p in packages:
        print(f"\t- {p}")

    # Uninstall package
    device.uninstall_package("com.example.app")
```