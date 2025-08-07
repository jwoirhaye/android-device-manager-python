# Installation

## 🐍 Requirements

Before installing android-device-manager, ensure you have:

- Python 3.10 or higher
- Android SDK installed and configured

---

## Android SDK Setup

### Option 1: Android Studio
1. Download and install [Android Studio](https://developer.android.com/studio)
2. Open Android Studio and follow the setup wizard
3. Install additional SDK packages through SDK Manager

### Option 2: Command Line Tools

#### Installing Command Line Tools

```bash
# Download command line tools
# August 2025 version - check for the latest version at:
# https://developer.android.com/studio#command-line-tools-only
wget https://dl.google.com/android/repository/commandlinetools-linux-13114758_latest.zip

# Extract and organize files
unzip commandlinetools-linux-13114758_latest.zip
mkdir -p ~/Android/Sdk/cmdline-tools/latest
mv cmdline-tools/* ~/Android/Sdk/cmdline-tools/latest/

# Cleanup
rm -rf cmdline-tools commandlinetools-linux-13114758_latest.zip
```

#### Setting Up Environment Variables

```bash
# Add these lines to your ~/.bashrc or ~/.zshrc
export ANDROID_HOME=$HOME/Android/Sdk
export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin
export PATH=$PATH:$ANDROID_HOME/platform-tools
export PATH=$PATH:$ANDROID_HOME/emulator

# Reload your configuration
source ~/.bashrc  # or source ~/.zshrc
```

#### Installing Essential Components

```bash
# Accept licenses
yes | sdkmanager --licenses

# Install basic tools
sdkmanager "platform-tools"
sdkmanager "emulator"
```

#### Verifying Installation

To verify everything works correctly:

```bash
# Check that tools are accessible
adb version
emulator -version

# List installed packages
sdkmanager --list_installed
```

## Install python-android-avd-manager

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