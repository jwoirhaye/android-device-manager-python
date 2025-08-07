# Android Device Manager Python
Android Device Manager is a Python library for creating, launching, and managing Android emulators (AVDs) programmatically.

![PyPI - Version](https://img.shields.io/pypi/v/android-device-manager)
[![CI](https://github.com/jwoirhaye/android-device-manager-python/actions/workflows/ci.yml/badge.svg)](https://github.com/jwoirhaye/android-device-manager-python/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/jwoirhaye/android-device-manager-python/branch/main/graph/badge.svg)](https://codecov.io/gh/jwoirhaye/android-device-manager-python)
[![Docs](https://img.shields.io/badge/docs-mkdocs-blue?logo=readthedocs)](https://jwoirhaye.github.io/android-device-manager-python/)
[![License](https://img.shields.io/github/license/jwoirhaye/android-device-manager-python)](https://github.com/jwoirhaye/android-device-manager-python/blob/main/LICENSE)
---

## 📖 Table of Contents
- [Features](#-features)
- [Requirements](#-requirements)
- [Installation](#-installation)
- [Quickstart](#-quickstart)
- [License](#-license)
- [Support](#-support)

---

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

### 📦 From PyPI (Recommended)
```bash
pip install python-android-avd-manager
```

### 🚧 From Source
```bash
git clone https://github.com/jwoirhaye/python-android-avd-manager-python.git
cd python-android-avd-manager
pip install -e .
```

--- 

## ⚡ Quickstart

With everything set up, here’s the simplest way to create and run an emulator:

```python
from android_device_manager import AndroidDevice , AndroidProp
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
    print(f"Device {device.name} is running!")
    print("Android Version:", device.get_prop(AndroidProp.ANDROID_VERSION))
    # Or
    #print("Android Version:", device.get_prop("ro.build.version.release"))

```

---

## 📜 License
This project is licensed under the [MIT License](LICENSE).

---

## 📧 Support
- 🐛 Issues: [GitHub Issues](https://github.com/jwoirhaye/android-device-manager-python/issues)  
- 📬 Contact: [jerem.woirhaye@gmail.com]