# Device Info & Properties

## Retrieve system properties

```python
from android_device_manager import AndroidDevice, AndroidProp
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

# Start and query the device
with AndroidDevice(avd_config, emulator_config=emulator_config) as device:
    api_level = device.get_prop(AndroidProp.API_LEVEL)
    android_version = device.get_prop("ro.build.version.release")
    print(f"API Level: {api_level}, Android: {android_version}")
```

This example:

1. Starts an emulator for the specified AVD in headless mode.

2. Retrieves the device API level using an AndroidProp enum.

3. Retrieves the Android version directly using a property key.