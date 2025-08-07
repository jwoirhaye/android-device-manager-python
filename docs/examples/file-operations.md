# File Operations

## Push and Pull Files

```python
from android_device_manager import AndroidDevice
from android_device_manager.avd import AVDConfiguration
from android_device_manager.emulator import EmulatorConfiguration

# Configure the AVD
avd_config = AVDConfiguration(
    name="test_avd_from_lib",
    package="system-images;android-36;google_apis;x86_64"
)

# Configure the Emulator (headless mode)
emulator_config = EmulatorConfiguration(
    no_window=True,
)

with AndroidDevice(avd_config, emulator_config=emulator_config) as device:
    # Push a file
    device.push_file("local.txt", "/tmp/local.txt")

    # Pull a file
    device.pull_file("/tmp/local.txt", "downloaded.txt")
```