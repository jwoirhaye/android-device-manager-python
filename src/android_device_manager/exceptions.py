class AndroidDeviceManagerError(Exception):
    """
    Base exception for all errors raised by the android-device-manager library.

    All custom exceptions in this library inherit from this class,
    allowing users to catch all library-specific errors with a single except block.
    """


class AndroidDeviceError(AndroidDeviceManagerError):
    """
    This exception is raised when an error occurs while interacting with
    an AndroidDevice.
    """


class AndroidSDKNotFound(AndroidDeviceManagerError):
    """
    Raised when the Android SDK or a required SDK tool cannot be found.
    """


class SDKManagerError(AndroidDeviceManagerError):
    """Base exception for SDK Manager operations"""
