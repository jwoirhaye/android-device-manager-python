import pytest

from android_device_manager.emulator.config import EmulatorConfiguration


class TestEmulatorConfiguration:
    """Test suite for EmulatorConfiguration dataclass."""

    def test_default_initialization(self):
        """Test EmulatorConfiguration with default values."""
        config = EmulatorConfiguration()

        assert config.no_window is False
        assert config.no_audio is False
        assert config.gpu == "auto"
        assert config.memory is None
        assert config.cores is None
        assert config.wipe_data is False
        assert config.no_snapshot is False
        assert config.cold_boot is False
        assert config.netdelay == "none"
        assert config.netspeed == "full"
        assert config.verbose is False

    def test_custom_initialization(self):
        """Test EmulatorConfiguration with custom values."""
        config = EmulatorConfiguration(
            no_window=True,
            no_audio=True,
            gpu="host",
            memory=2048,
            cores=4,
            wipe_data=True,
            no_snapshot=True,
            cold_boot=True,
            netdelay="gsm",
            netspeed="edge",
            verbose=True,
        )

        assert config.no_window is True
        assert config.no_audio is True
        assert config.gpu == "host"
        assert config.memory == 2048
        assert config.cores == 4
        assert config.wipe_data is True
        assert config.no_snapshot is True
        assert config.cold_boot is True
        assert config.netdelay == "gsm"
        assert config.netspeed == "edge"
        assert config.verbose is True

    def test_partial_initialization(self):
        """Test EmulatorConfiguration with some custom values."""
        config = EmulatorConfiguration(no_window=True, memory=1024, netdelay="umts")

        
        assert config.no_window is True
        assert config.memory == 1024
        assert config.netdelay == "umts"

        
        assert config.no_audio is False
        assert config.gpu == "auto"
        assert config.cores is None
        assert config.netspeed == "full"

    def test_to_args_default_config(self):
        """Test to_args() with default configuration."""
        config = EmulatorConfiguration()
        args = config.to_args()

        
        assert args == []

    def test_to_args_all_boolean_flags(self):
        """Test to_args() with all boolean flags enabled."""
        config = EmulatorConfiguration(
            no_window=True,
            no_audio=True,
            wipe_data=True,
            no_snapshot=True,
            cold_boot=True,
            verbose=True,
        )
        args = config.to_args()

        expected_args = [
            "-no-window",
            "-no-audio",
            "-wipe-data",
            "-no-snapshot",
            "-cold-boot",
            "-verbose",
        ]

        
        for arg in expected_args:
            assert arg in args

        
        assert len(args) == len(expected_args)

    def test_to_args_with_values(self):
        """Test to_args() with parameters that take values."""
        config = EmulatorConfiguration(
            gpu="host", memory=2048, cores=4, netdelay="gsm", netspeed="edge"
        )
        args = config.to_args()

        expected_pairs = [
            ("-gpu", "host"),
            ("-memory", "2048"),
            ("-cores", "4"),
            ("-netdelay", "gsm"),
            ("-netspeed", "edge"),
        ]

        
        arg_pairs = [(args[i], args[i + 1]) for i in range(0, len(args), 2)]

        assert len(arg_pairs) == len(expected_pairs)
        for pair in expected_pairs:
            assert pair in arg_pairs

    def test_to_args_mixed_configuration(self):
        """Test to_args() with mixed boolean flags and value parameters."""
        config = EmulatorConfiguration(
            no_window=True,
            gpu="swiftshader_indirect",
            memory=1024,
            wipe_data=True,
            netdelay="umts",
            verbose=True,
        )
        args = config.to_args()

        
        assert "-no-window" in args
        assert "-wipe-data" in args
        assert "-verbose" in args
        assert "-gpu" in args
        assert "swiftshader_indirect" in args
        assert "-memory" in args
        assert "1024" in args
        assert "-netdelay" in args
        assert "umts" in args

    def test_to_args_gpu_auto_not_included(self):
        """Test that GPU=auto (default) is not included in args."""
        config = EmulatorConfiguration(gpu="auto")
        args = config.to_args()

        assert "-gpu" not in args
        assert "auto" not in args
        assert args == []

    def test_to_args_gpu_custom_included(self):
        """Test that custom GPU value is included in args."""
        config = EmulatorConfiguration(gpu="host")
        args = config.to_args()

        assert "-gpu" in args
        assert "host" in args

    def test_to_args_netdelay_none_not_included(self):
        """Test that netdelay=none (default) is not included in args."""
        config = EmulatorConfiguration(netdelay="none")
        args = config.to_args()

        assert "-netdelay" not in args
        assert "none" not in args
        assert args == []

    def test_to_args_netspeed_full_not_included(self):
        """Test that netspeed=full (default) is not included in args."""
        config = EmulatorConfiguration(netspeed="full")
        args = config.to_args()

        assert "-netspeed" not in args
        assert "full" not in args
        assert args == []

    def test_to_args_none_values_not_included(self):
        """Test that None values are not included in args."""
        config = EmulatorConfiguration(memory=None, cores=None)
        args = config.to_args()

        assert "-memory" not in args
        assert "-cores" not in args
        assert args == []

    def test_immutability_after_creation(self):
        """Test that configuration can be modified after creation (dataclass is mutable)."""
        config = EmulatorConfiguration()

        
        config.no_window = True
        config.memory = 1024

        assert config.no_window is True
        assert config.memory == 1024

    def test_equality_comparison(self):
        """Test equality comparison between configurations."""
        config1 = EmulatorConfiguration(no_window=True, memory=1024)
        config2 = EmulatorConfiguration(no_window=True, memory=1024)
        config3 = EmulatorConfiguration(no_window=False, memory=1024)

        assert config1 == config2
        assert config1 != config3
        assert config2 != config3

    def test_string_representation(self):
        """Test string representation of configuration."""
        config = EmulatorConfiguration(no_window=True, memory=1024)
        repr_str = repr(config)

        assert "EmulatorConfiguration" in repr_str
        assert "no_window=True" in repr_str
        assert "memory=1024" in repr_str

    def test_dataclass_fields_access(self):
        """Test that we can access dataclass fields programmatically."""
        from dataclasses import fields

        config = EmulatorConfiguration()
        field_names = [field.name for field in fields(config)]

        expected_fields = [
            "no_window",
            "no_audio",
            "gpu",
            "memory",
            "cores",
            "wipe_data",
            "no_snapshot",
            "cold_boot",
            "netdelay",
            "netspeed",
            "verbose",
        ]

        assert len(field_names) == len(expected_fields)
        for field_name in expected_fields:
            assert field_name in field_names


class TestEmulatorConfigurationValidation:
    """Test suite for EmulatorConfiguration validation and edge cases."""

    def test_memory_negative_value(self):
        """Test configuration with negative memory value."""
        
        config = EmulatorConfiguration(memory=-100)
        args = config.to_args()

        assert "-memory" in args
        assert "-100" in args

    def test_cores_negative_value(self):
        """Test configuration with negative cores value."""
        config = EmulatorConfiguration(cores=-1)
        args = config.to_args()

        assert "-cores" in args
        assert "-1" in args

    def test_large_memory_value(self):
        """Test configuration with very large memory value."""
        config = EmulatorConfiguration(memory=999999)
        args = config.to_args()

        assert "-memory" in args
        assert "999999" in args

    def test_empty_string_values(self):
        """Test configuration with empty string values."""
        config = EmulatorConfiguration(gpu="", netdelay="", netspeed="")
        args = config.to_args()

        
        assert "-gpu" in args
        assert "" in args
        assert "-netdelay" in args
        assert "-netspeed" in args

    def test_special_characters_in_strings(self):
        """Test configuration with special characters in string values."""
        config = EmulatorConfiguration(
            gpu="test-gpu_with.special/chars",
            netdelay="custom:delay",
            netspeed="custom@speed",
        )
        args = config.to_args()

        assert "-gpu" in args
        assert "test-gpu_with.special/chars" in args
        assert "-netdelay" in args
        assert "custom:delay" in args
        assert "-netspeed" in args
        assert "custom@speed" in args


@pytest.mark.parametrize(
    "field_name,field_value,expected_in_args",
    [
        ("no_window", True, "-no-window"),
        ("no_audio", True, "-no-audio"),
        ("wipe_data", True, "-wipe-data"),
        ("no_snapshot", True, "-no-snapshot"),
        ("cold_boot", True, "-cold-boot"),
        ("verbose", True, "-verbose"),
    ],
)
def test_boolean_flags_parametrized(field_name, field_value, expected_in_args):
    """Test that boolean flags are correctly converted to arguments."""
    kwargs = {field_name: field_value}
    config = EmulatorConfiguration(**kwargs)
    args = config.to_args()

    assert expected_in_args in args


@pytest.mark.parametrize(
    "field_name,field_value,expected_flag,expected_value",
    [
        ("gpu", "host", "-gpu", "host"),
        ("gpu", "swiftshader_indirect", "-gpu", "swiftshader_indirect"),
        ("memory", 1024, "-memory", "1024"),
        ("memory", 2048, "-memory", "2048"),
        ("cores", 2, "-cores", "2"),
        ("cores", 8, "-cores", "8"),
        ("netdelay", "gsm", "-netdelay", "gsm"),
        ("netdelay", "edge", "-netdelay", "edge"),
        ("netspeed", "gsm", "-netspeed", "gsm"),
        ("netspeed", "edge", "-netspeed", "edge"),
    ],
)
def test_value_parameters_parametrized(
    field_name, field_value, expected_flag, expected_value
):
    """Test that value parameters are correctly converted to flag-value pairs."""
    kwargs = {field_name: field_value}
    config = EmulatorConfiguration(**kwargs)
    args = config.to_args()

    assert expected_flag in args
    assert expected_value in args

    
    flag_index = args.index(expected_flag)
    assert args[flag_index + 1] == expected_value


@pytest.mark.parametrize(
    "field_name,default_value",
    [
        ("gpu", "auto"),
        ("netdelay", "none"),
        ("netspeed", "full"),
    ],
)
def test_default_values_not_in_args(field_name, default_value):
    """Test that default values are not included in args."""
    kwargs = {field_name: default_value}
    config = EmulatorConfiguration(**kwargs)
    args = config.to_args()

    
    assert args == []


@pytest.mark.parametrize("memory_value", [1, 512, 1024, 2048, 4096, 8192])
def test_memory_values_range(memory_value):
    """Test various memory values."""
    config = EmulatorConfiguration(memory=memory_value)
    args = config.to_args()

    assert "-memory" in args
    assert str(memory_value) in args


@pytest.mark.parametrize("cores_value", [1, 2, 4, 8, 16])
def test_cores_values_range(cores_value):
    """Test various core count values."""
    config = EmulatorConfiguration(cores=cores_value)
    args = config.to_args()

    assert "-cores" in args
    assert str(cores_value) in args


class TestEmulatorConfigurationIntegration:
    """Integration tests for EmulatorConfiguration with realistic scenarios."""

    def test_headless_configuration(self):
        """Test typical headless emulator configuration."""
        config = EmulatorConfiguration(
            no_window=True, no_audio=True, gpu="swiftshader_indirect", memory=2048
        )
        args = config.to_args()

        expected_elements = [
            "-no-window",
            "-no-audio",
            "-gpu",
            "swiftshader_indirect",
            "-memory",
            "2048",
        ]

        for element in expected_elements:
            assert element in args

    def test_development_configuration(self):
        """Test typical development emulator configuration."""
        config = EmulatorConfiguration(gpu="host", memory=4096, cores=4, verbose=True)
        args = config.to_args()

        expected_elements = [
            "-gpu",
            "host",
            "-memory",
            "4096",
            "-cores",
            "4",
            "-verbose",
        ]

        for element in expected_elements:
            assert element in args

    def test_testing_configuration(self):
        """Test configuration suitable for automated testing."""
        config = EmulatorConfiguration(
            no_window=True,
            no_audio=True,
            wipe_data=True,
            no_snapshot=True,
            cold_boot=True,
            netspeed="full",  
            netdelay="none",  
        )
        args = config.to_args()

        
        expected_flags = [
            "-no-window",
            "-no-audio",
            "-wipe-data",
            "-no-snapshot",
            "-cold-boot",
        ]
        unexpected_flags = ["-netspeed", "-netdelay"]

        for flag in expected_flags:
            assert flag in args

        for flag in unexpected_flags:
            assert flag not in args

    def test_performance_configuration(self):
        """Test high-performance emulator configuration."""
        config = EmulatorConfiguration(
            gpu="host", memory=8192, cores=8, netspeed="full", netdelay="none"
        )
        args = config.to_args()

        
        assert "-gpu" in args and "host" in args
        assert "-memory" in args and "8192" in args
        assert "-cores" in args and "8" in args
        assert "-netspeed" not in args
        assert "-netdelay" not in args

    def test_slow_network_simulation(self):
        """Test configuration for simulating slow network conditions."""
        config = EmulatorConfiguration(netspeed="gsm", netdelay="gsm")
        args = config.to_args()

        assert "-netspeed" in args and "gsm" in args
        assert "-netdelay" in args and "gsm" in args
