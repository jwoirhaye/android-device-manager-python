# Quickstart

Welcome to **Android Device Manager**!  
This quickstart guide will walk you through the essential steps to create, run, and interact with an Android Device using the library.

## 1️⃣ Verify Installation

After following the [Installation Guide](installation.md), verify your setup:

```bash
adb version
emulator -version
avdmanager list available
```

You should see the versions of each tool and the list of available system images.

---

## 2️⃣ Minimal Example — Create & Run an Emulator

With everything set up, here’s the simplest way to create and run an emulator:

```python
from android_device_manager import AndroidDevice
from android_device_manager.avd import AVDConfiguration
from android_device_manager.emulator import EmulatorConfiguration

# Define AVD configuration
avd_config = AVDConfiguration(
    name="quickstart_avd",
    package="system-images;android-34;google_apis;x86_64"
)

# Define Emulator configuration
emulator_config = EmulatorConfiguration(
    no_window=True  # Run emulator in headless mode
)

# Create and run the device using context manager
with AndroidDevice(avd_config, emulator_config) as device:
    print(f"Device {device.name} is running.")

```

✅ What happens here:

- The AVD is created if it doesn’t already exist.
- The emulator is started.
- When the context exits, the emulator is stopped and the AVD is cleaned up.

--- 

## 3️⃣ Interact with the Device

While the emulator is running, you can:
[constants](../api/constants.md)
- Install APKs
- List installed packages
- Read system properties

Example:
```python
from android_device_manager import AndroidProp

packages = device.list_installed_packages()
print("Installed packages:", packages[:5])

android_version = device.get_prop(AndroidProp.ANDROID_VERSION)
print(f"Android version: {android_version}")
```