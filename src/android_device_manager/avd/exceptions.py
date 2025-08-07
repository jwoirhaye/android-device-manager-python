from ..exceptions import AndroidDeviceManagerError


class AVDCreationError(AndroidDeviceManagerError):
    """
    Raised when the creation of an Android Virtual Device (AVD) fails.

    Attributes:
        name (str): The name of the AVD for which creation failed.
        message (str): Details about the cause of the failure.

    Args:
        name (str): The name of the AVD.
        message (str): Description of the creation error.
    """

    def __init__(self, name: str, message: str):
        super().__init__(f"AVD '{name}': {message}")
        self.name = name
        self.message = message


class AVDDeletionError(AndroidDeviceManagerError):
    """
    Raised when the deletion of an Android Virtual Device (AVD) fails.

    Attributes:
        name (str): The name of the AVD for which deletion failed.
        message (str): Details about the cause of the failure.

    Args:
        name (str): The name of the AVD.
        message (str): Description of the deletion error.
    """

    def __init__(self, name: str, message: str):
        super().__init__(f"AVD '{name}': {message}")
        self.name = name
        self.message = message
