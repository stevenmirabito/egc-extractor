import importlib
from egc_extractor.util import iter_namespace

registry = []


def register(cls):
    registry.append(cls)
    return cls


class MerchantPlugin:
    display_name = "Generic Merchant"
    from_email = "noreply@merchant.com"

    def __str__(self):
        return self.display_name


def discover_plugins(package):
    """
    Discover the installed merchant plugins.
    """
    for finder, name, ispkg in iter_namespace(package):
        importlib.import_module(name)

    return registry
