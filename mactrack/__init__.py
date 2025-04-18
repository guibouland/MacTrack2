submodules = [
    "analyse",
    "locate",
    "track",
    "video",
    "visualisation",
]


def _get_submodule(name):
    """Get the submodule by name."""
    if name in submodules:
        return __import__(name)
    else:
        raise ImportError(f"Module {name} not found in mactrack.")
        return None


def __getattr__(name):
    """Get the submodule by name."""
    if name in submodules:
        return _get_submodule(name)
    else:
        raise ImportError(f"Module {name} not found in mactrack.")
        return None


def __dir__():
    """List the submodules."""
    return submodules
