from ..exceptions import AndroidDeviceManagerError


class EmulatorPortAllocationError(AndroidDeviceManagerError):
    """
    Exception raised when the emulator fails to allocate a valid port.

    This error typically occurs when there are no available ports
    or when the requested port is already in use.
    """


class EmulatorStartError(AndroidDeviceManagerError):
    """
    Exception raised when the Android emulator fails to start properly.
    """
