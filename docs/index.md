# Android Device Manager

**Android Device Manager** is a modern Python library to **automate and control Android** programmatically.

## 🚀 Features

### 📦 AVD Management
- **Create AVDs programmatically** from system images
- **List existing AVDs** and check availability
- **Delete AVDs** cleanly
- **Validate AVD names** according to Android rules
- **Force recreation** of AVDs with `force=True`

### ▶️ Emulator Control
- **Start emulators** in headless or windowed mode
- **Automatic port allocation** for multiple running instances
- **Stop emulators** gracefully or force-kill when needed
- **Custom emulator options** via `EmulatorConfiguration`

### 📡 ADB Integration
- **Execute `adb` commands** directly from Python
- **Install APKs** and manage applications (install/uninstall)
- **List installed packages** and check if a package is installed
- **Push and pull files** between host and device
- **Access `logcat` output** and clear logs

---

## 🐍 Requirements

- **Python**: 3.10 or higher
- **Android SDK**: Latest version recommended
- **System Resources**: Sufficient RAM and storage for emulators

---

## 📦 Installation

Follow the [Installation Guide](getting-started/installation.md)

```bash
pip install android-device-manager
```

---

## ⚡ Quick Example

```python
from android_device_manager import AndroidDevice
from android_device_manager.avd import AVDConfiguration
from android_device_manager.emulator import EmulatorConfiguration

avd_config = AVDConfiguration(
    name="test_avd_from_lib", 
    package="system-images;android-36;google_apis;x86_64"
)

emulator_config = EmulatorConfiguration(
    no_window=True,
)

with AndroidDevice(avd_config,emulator_config) as device:
    print(device.name)
```



