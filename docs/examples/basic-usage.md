# Basic Usage

## Create, start, and stop an emulator with custom configuration

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

# Manage the device lifecycle automatically
with AndroidDevice(avd_config, emulator_config) as device:
    print(f"Device {device.name} is running.")
```

This example:

1. Creates the AVD if it does not exist.

2. Starts the emulator in headless mode (no window).

3. Stops and deletes the AVD automatically when exiting the context.