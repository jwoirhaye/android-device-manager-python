from android_device_manager import AndroidDevice
from android_device_manager.avd import AVDConfiguration
from android_device_manager.emulator import EmulatorConfiguration

# Configure your AVD
avd_config = AVDConfiguration(
    name="example_avd",
    package="system-images;android-36;google_apis;x86_64"
)

# Configure your Emulator
emulator_config = EmulatorConfiguration(
    no_window=False
)

with AndroidDevice(avd_config,emulator_config) as device:
    # Install APK
    device.install_multi_package([
        "/home/jwoirhay/Bureau/temp/apk_download/apks/safetravelsmain.apk",
        "/home/jwoirhay/Bureau/temp/apk_download/apks/sitiosarequipa.apk"
                                  ])

    # List installed packages
    packages = device.list_installed_packages()
    print("Installed packages:")
    for p in packages:
        print(f"\t- {p}")
