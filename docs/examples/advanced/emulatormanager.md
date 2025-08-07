# Advanced Usage: `EmulatorManager`

The `EmulatorManager` is responsible for managing Android Emulator instances from Python, without relying on Android Studio's graphical interface.  
It provides low-level control to **start, stop, and allocate emulator ports programmatically**.

---

## Overview

The `EmulatorManager` acts as a thin wrapper around the `emulator` binary found in your Android SDK.

**Main features:**
- Find and allocate free emulator ports automatically.
- Start emulators with a specific AVD and optional configuration.
- Stop emulators gracefully or forcibly.
- Fully compatible with headless and automated environments.

---

## Initialization

To use `EmulatorManager`, you must provide an instance of `AndroidSDK` so the class can locate the `emulator` executable.

```python
from android_device_manager.emulator import EmulatorManager
from android_device_manager.utils.android_sdk import AndroidSDK

sdk = AndroidSDK()  # Automatically detects the SDK path
emulator_manager = EmulatorManager(sdk)
```

---

## Starting an Emulator

You can start an emulator by specifying the **AVD name**.  
Optionally, you can provide an [`EmulatorConfiguration`](../../api/emulator.md#) to control runtime settings like GPU mode, memory, and cold boot.

```python
from android_device_manager.emulator import EmulatorConfiguration

# Configure emulator to run headless
emu_config = EmulatorConfiguration(
    no_window=True,
    gpu="swiftshader_indirect",
    cold_boot=True
)

# Start emulator for AVD named "test_avd"
port = emulator_manager.start_emulator("test_avd", emulator_config=emu_config)

print(f"Emulator started on port {port}")
```

**Key details:**

- A free port is automatically selected between `DEFAULT_EMULATOR_PORT_START` and `DEFAULT_EMULATOR_PORT_END`.
- If no free port is available, an `EmulatorPortAllocationError` is raised.
- If the emulator fails to start, an `EmulatorStartError` is raised with logs.

---

## Stopping an Emulator

Stopping the emulator is straightforward.  
The manager first attempts to terminate the process gracefully, and if it does not stop within **10 seconds**, it is killed.

```python
emulator_manager.stop_emulator()
print("Emulator stopped.")
```

---

## Port Allocation

By default, emulator ports are allocated in **even-numbered ranges** starting at `5554`.  
This is the same behavior as the official Android Emulator.

You can find a free port using the private static method `_find_free_emulator_port`:

```python
free_port = emulator_manager._find_free_emulator_port()
print(f"Free emulator port: {free_port}")
```

!!! warning 

    This is an internal method. Normally, you don't need to call it manually because `start_emulator()` handles port allocation automatically.

---

## Full Example

Here is a complete advanced example that:
1. Starts an emulator in headless mode.
2. Runs it for 15 seconds.
3. Stops it gracefully.

```python
import time
from android_device_manager.utils.android_sdk import AndroidSDK
from android_device_manager.emulator.manager import EmulatorManager
from android_device_manager.emulator.config import EmulatorConfiguration

# Initialize SDK and Emulator Manager
sdk = AndroidSDK()
emulator_manager = EmulatorManager(sdk)

# Emulator configuration (headless)
emu_config = EmulatorConfiguration(no_window=True, cold_boot=True)

# Start emulator
try:
    port = emulator_manager.start_emulator("test_avd", emulator_config=emu_config)
    print(f"Emulator started on port {port}")

    # Simulate work
    time.sleep(15)

finally:
    # Stop emulator
    emulator_manager.stop_emulator()
    print("Emulator stopped.")
```

---

## Best Practices

- Always stop emulators after usage to free system resources.
- Use `no_window=True` in automated pipelines to avoid UI pop-ups.
- Combine `EmulatorManager` with [`AdbClient`](./adbclient.md) for deeper automation (installing APKs, running tests, etc.).
- If running multiple emulators, ensure there are enough free ports.

---

## Exceptions

The `EmulatorManager` raises specific exceptions for better error handling:

- **`EmulatorPortAllocationError`**  
  Raised when no free emulator port can be found.

- **`EmulatorStartError`**  
  Raised when the emulator process fails to start.

These exceptions can be caught individually or through the base exception class.

