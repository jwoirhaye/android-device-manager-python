from ..exceptions import AndroidDeviceManagerError


class ADBTimeoutError(AndroidDeviceManagerError):
    """
    Raised when a timeout occurs during an ADB operation.
    """


class ADBError(AndroidDeviceManagerError):
    """
    Raised for any error encountered while running an ADB (Android Debug Bridge) command.

    Attributes:
        return_code (Optional[int]): The process return code, if available.
        cmd (Optional[Any]): The command that was executed.
        stdout (Optional[str]): The standard output from the failed command.
        stderr (Optional[str]): The standard error from the failed command.
        serial (Optional[str]): The emulator/device serial associated with the error, if relevant.

    Args:
        message (str): A descriptive error message.
        return_code (Optional[int]): The process return code.
        cmd (Optional[Any]): The command executed (as a list or string).
        stdout (Optional[str]): Output from stdout.
        stderr (Optional[str]): Output from stderr.
        serial (Optional[str]): The serial of the target device.
    """

    def __init__(
        self, message, return_code=None, cmd=None, stdout=None, stderr=None, serial=None
    ):
        super().__init__(message)
        self.return_code = return_code
        self.cmd = cmd
        self.stdout = stdout
        self.stderr = stderr
        self.serial = serial
