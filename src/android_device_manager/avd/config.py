from dataclasses import dataclass


@dataclass
class AVDConfiguration:
    """
    Configuration for an Android Virtual Device (AVD).

    This dataclass encapsulates the minimal configuration needed to define
    an Android Virtual Device, such as its name and the associated system image package.

    Attributes:
        name (str): The name of the AVD (must be unique within the Android SDK).
        package (str): The system image package path (e.g. "system-images;android-34;google_apis;x86_64").
    """

    name: str
    package: str
