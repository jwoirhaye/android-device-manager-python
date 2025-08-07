from android_device_manager.avd import AVDConfiguration


def test_init():
    """Test creation and attribute assignment of AVDConfiguration."""
    name = "test_avd"
    package = "system-images;android-36;google_apis;x86_64"

    config = AVDConfiguration(name, package)

    assert config.name is not None
    assert config.name == name
    assert config.package is not None
    assert config.package == package
