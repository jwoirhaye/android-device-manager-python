import re


def is_valid_avd_name(name: str) -> bool:
    """
    Validate that the AVD name follows Android Studio's naming rules.

    Rules:
        - Must start with a letter [a-zA-Z]
        - Can contain letters, numbers, underscores and hyphens
        - No spaces or other special characters
    """
    if not name:
        return False
    return bool(re.match(r"^[a-zA-Z][a-zA-Z0-9_-]*$", name))
