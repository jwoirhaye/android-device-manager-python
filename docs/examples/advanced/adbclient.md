# Advanced: Using `AdbClient`

The `AdbClient` class provides **low-level access** to the Android Debug Bridge (ADB) for a running emulator/device.

!!! info

    This interface is intended for **advanced users** who want to directly run commands, manage files, install/uninstall APKs, or query system information without going through the high-level `AndroidDevice` abstraction.

---

## When to use `AdbClient`
You might prefer `AdbClient` over `AndroidDevice` when:
- You want **fine-grained control** over ADB commands.
- You need to **run custom shell commands**.
- You want to **manipulate files** or **query system properties** without creating/deleting AVDs.

---

## Initializing `AdbClient`

```python
from android_device_manager.adb.client import AdbClient
from android_device_manager.utils.android_sdk import AndroidSDK

sdk = AndroidSDK()
port = 5554  # Replace with the actual emulator port

adb_client = AdbClient(port, sdk)
adb_client.wait_for_boot()  # Wait until the emulator is fully booted
print("Emulator is ready!")
```

---

## Key Features and Examples

### 1️⃣ Query System Properties
Retrieve device properties (API level, Android version, manufacturer, etc.).

```python
from android_device_manager.constants import AndroidProp

# Get a specific property
api_level = adb_client.get_prop(AndroidProp.API_LEVEL)
print("API Level:", api_level)

# Or by string
android_version = adb_client.get_prop("ro.build.version.release")
print("Android Version:", android_version)

# Get all properties
all_props = adb_client.get_all_props()
print("All properties:", all_props)
```

---

### 2️⃣ Install and Uninstall APKs
Install or remove applications from the emulator.

```python
apk_path = "/path/to/app.apk"

# Install APK
adb_client.install_apk(apk_path)
print("APK installed successfully.")

# List installed packages
packages = adb_client.list_installed_packages()
print("Installed packages:", packages)

# Uninstall APK
adb_client.uninstall_package("com.example.app")
print("Package uninstalled.")
```

---

### 3️⃣ File Operations
Copy files between the host and the emulator.

```python
# Push file to /sdcard
adb_client.push_file("local_file.txt", "/sdcard/remote_file.txt")
print("File pushed to emulator.")

# Pull file from /sdcard
adb_client.pull_file("/sdcard/remote_file.txt", "downloaded_file.txt")
print("File pulled from emulator.")
```

---

### 4️⃣ Log Management
Access or clear the device logs.

```python
# Retrieve logcat output
logs = adb_client.get_logcat()
print("Logs:", logs)

# Clear logcat buffer
adb_client.clear_logcat()
print("Logcat cleared.")
```

---

### 5️⃣ Execute Shell Commands
Run shell commands directly inside the emulator.

```python
# List files in /sdcard
result = adb_client.shell(["ls", "/sdcard"])
print("Files in /sdcard:", result.stdout)

# Create a directory
adb_client.shell(["mkdir", "/sdcard/test_dir"])
```

!!! warning
    Avoid using destructive commands (`stop`, `reboot`, `poweroff`) unless you handle emulator state manually.  

---

### 6️⃣ Root Access
Gain root privileges (if supported by the emulator image).

```python
# Enable root
if adb_client.root():
    print("ADB is now running as root.")
else:
    print("Root access not available.")

# Check root status
print("Is root?", adb_client.is_root())

# Disable root
adb_client.unroot()
print("Root disabled.")
```

---

### 7️⃣ Stop Emulator
Shut down the emulator instance cleanly.

```python
adb_client.kill_emulator()
print("Emulator killed.")
```

---

## 🔍 Notes for Advanced Users
- `AdbClient` does **not manage emulator lifecycle** — you must ensure an emulator is running before using it.
- Some commands require `root()` to be called before execution.
- Avoid long-running or blocking commands in automation workflows without adjusting `timeout` parameters.
- For bulk file transfers (like `/data`), ensure proper permissions and storage space on the host.

---

✅ `AdbClient` is ideal when you want **direct control of an emulator without the overhead** of creating/managing it via `AndroidDevice`.