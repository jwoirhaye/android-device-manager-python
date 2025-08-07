# AVDManager — Advanced Usage

The `AVDManager` class provides programmatic access to the Android Virtual Device (AVD) management functionalities, wrapping the `avdmanager` CLI commands with Python.  

It can be used directly to create, list, and delete AVDs without relying on the higher-level `AndroidDevice` abstraction.

---

## 📦 Import and Initialization

To use `AVDManager`, you need an initialized `AndroidSDK` (which automatically locates your SDK tools):

```python
from android_device_manager.avd.manager import AVDManager
from android_device_manager.avd.config import AVDConfiguration
from android_device_manager.utils.android_sdk import AndroidSDK

# Initialize SDK and AVDManager
sdk = AndroidSDK()
avd_manager = AVDManager(sdk)
```

---

## 🆕 Creating an AVD

The `create()` method creates a new virtual device.  
You need an `AVDConfiguration` specifying at least a name and a system image package.

```python
avd_config = AVDConfiguration(
    name="advanced_avd",
    package="system-images;android-34;google_apis;x86_64"
)

try:
    avd_manager.create(avd_config, force=False)
    print("AVD created successfully.")
except Exception as e:
    print(f"Failed to create AVD: {e}")
```

!!! note

    - The AVD name must follow Android naming rules (letters, digits, `_`, `-`, starting with a letter).
    - If `force=True` is set, an existing AVD with the same name will be overwritten.

---

## 📜 Listing AVDs

You can retrieve the list of existing AVDs using the `list()` method.

```python
avd_list = avd_manager.list()
print("Available AVDs:")
for avd in avd_list:
    print(f" - {avd}")
```

Example output:

```
Available AVDs:
 - Pixel_5_API_34
 - advanced_avd
```

---

## 🔍 Checking if an AVD Exists

You can check for the existence of a specific AVD:

```python
if avd_manager.exist("advanced_avd"):
    print("The AVD exists.")
else:
    print("The AVD does not exist.")
```

---

## 🗑️ Deleting an AVD

The `delete()` method removes a specific AVD by name:

```python
try:
    avd_manager.delete("advanced_avd")
    print("AVD deleted successfully.")
except Exception as e:
    print(f"Failed to delete AVD: {e}")
```

If the AVD does not exist, `delete()` will log a warning but will **not raise an error**.

---

## 🛠️ Under the Hood

Internally, `AVDManager`:
- Uses `avdmanager create avd` and `avdmanager delete avd` CLI commands.
- Validates AVD names with `is_valid_avd_name()`.
- Checks if the system image package is installed through `SDKManager`.

Advanced users can directly call `_run_avd_command()` to execute raw `avdmanager` commands:

```python
result = avd_manager._run_avd_command(["list", "avd"], timeout=30)
print(result.stdout)
```

---

## ⚠️ Common Pitfalls
- **System image not installed**: Ensure your package (`system-images;android-XX;google_apis;x86_64`) is installed via `sdkmanager`.
- **Invalid names**: Follow Android AVD naming rules (no spaces, must start with a letter).
- **Permissions**: Ensure you have write access to the `.android/avd` directory.

---

👉 This advanced control over AVDs is useful when you want to script emulator environments, clean up AVDs, or prepare devices dynamically in CI pipelines.