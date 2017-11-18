import os
import pkgutil


def get_resource_path(filename):
    return os.path.join(os.path.dirname(__file__), 'resources', filename)


def iter_namespace(ns_pkg):
    return pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + ".")
