# Automation Workflow

## Full Automated Test Setup

This example demonstrates a full automation scenario:
- Create and start an emulator
- Install an application
- Retrieve logs
- Capture a screenshot

```python
from android_device_manager import AndroidDevice
from android_device_manager.avd.config import AVDConfiguration
from android_device_manager.emulator.config import EmulatorConfiguration

# Configure the AVD
avd_config = AVDConfiguration(
    name="automation_avd",
    package="system-images;android-34;google_apis;x86_64"
)

# Configure the Emulator
emulator_config = EmulatorConfiguration(
    no_window=True
)

# APK path
apk_path = "/path/to/app.apk"

with AndroidDevice(avd_config, emulator_config) as device:
    print(f"Device {device.name} started.")

    # Install application
    device.install_apk(apk_path)
    print("APK installed.")

    # Retrieve logs
    logs = device.get_logcat()
    print("Captured logs:")
    print(logs)

    # Capture screenshot
    screenshot_path = "screenshot.png"
    device.shell(["screencap", "-p", f"/tmp/{screenshot_path}"])
    device.pull_file(f"/tmp/{screenshot_path}", screenshot_path)
    print(f"Screenshot saved to {screenshot_path}")
```