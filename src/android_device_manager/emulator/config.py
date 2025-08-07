from dataclasses import dataclass
from typing import Optional, List


@dataclass
class EmulatorConfiguration:
    """
    Configuration options for the Android emulator.

    This dataclass encapsulates various parameters that can be passed
    to the Android emulator at startup. Each field corresponds to a common emulator option.

    Attributes:
        no_window (bool): If True, launch the emulator without a window (headless).
        no_audio (bool): If True, disable audio in the emulator.
        gpu (str): GPU emulation mode (default "auto", e.g., "host", "swiftshader_indirect").
        memory (Optional[int]): Memory (in MB) to allocate for the emulator.
        cores (Optional[int]): Number of CPU cores for the emulator.
        wipe_data (bool): If True, wipe user data when starting the emulator.
        no_snapshot (bool): If True, disable snapshots.
        cold_boot (bool): If True, force cold boot (do not load quick-boot snapshot).
        netdelay (str): Network delay profile (e.g., "none", "gsm", "edge", "umts").
        netspeed (str): Network speed profile (e.g., "full", "gsm", "edge").
        verbose (bool): If True, enable verbose output.
    """

    no_window: bool = False
    no_audio: bool = False
    gpu: str = "auto"
    memory: Optional[int] = None
    cores: Optional[int] = None
    wipe_data: bool = False
    no_snapshot: bool = False
    cold_boot: bool = False
    netdelay: str = "none"
    netspeed: str = "full"
    verbose: bool = False

    def to_args(self) -> List[str]:
        """
        Convert the configuration to a list of command-line arguments for the emulator.

        Returns:
            List[str]: The list of emulator CLI arguments corresponding to this configuration.
        """
        args = []

        if self.no_window:
            args.append("-no-window")
        if self.no_audio:
            args.append("-no-audio")
        if self.gpu != "auto":
            args.extend(["-gpu", self.gpu])
        if self.memory:
            args.extend(["-memory", str(self.memory)])
        if self.cores:
            args.extend(["-cores", str(self.cores)])
        if self.wipe_data:
            args.append("-wipe-data")
        if self.no_snapshot:
            args.append("-no-snapshot")
        if self.cold_boot:
            args.append("-cold-boot")
        if self.netdelay != "none":
            args.extend(["-netdelay", self.netdelay])
        if self.netspeed != "full":
            args.extend(["-netspeed", self.netspeed])
        if self.verbose:
            args.append("-verbose")

        return args
