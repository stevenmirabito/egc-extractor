import os
import stat
import re
import requests
import platform
import pkgutil
from io import BytesIO
from zipfile import ZipFile


def get_resource_path(filename):
    return os.path.join(os.path.dirname(__file__), "resources", filename)


def iter_namespace(ns_pkg):
    return pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + ".")


def get_chromedriver_path():
    plat = platform.platform().lower()
    if plat.startswith('darwin') or plat.startswith('linux'):
        return get_resource_path("chromedriver")
    elif plat.startswith('win'):
        return get_resource_path("chromedriver.exe")
    else:
        raise Exception("Unsupported platform: {}".format(plat))


CHROMEDRIVER_INFO_URL = (
    'https://sites.google.com/a/chromium.org/chromedriver/downloads'
)
CHROMEDRIVER_URL_TEMPLATE = (
    'http://chromedriver.storage.googleapis.com/{version}/chromedriver_{os_}'
    '{architecture}.zip'
)

CHROMEDRIVER_VERSION_PATTERN = re.compile(r'^\d+\.\d+$')
CROMEDRIVER_LATEST_VERSION_PATTERN = re.compile(
    r'Latest-Release:-ChromeDriver-(\d+\.\d+)'
)


def get_latest_chromedriver_version():
    """
    Retrieves the most recent Chromedriver version.
    """
    content = requests.get(CHROMEDRIVER_INFO_URL).content
    match = CROMEDRIVER_LATEST_VERSION_PATTERN.search(str(content))
    if match:
        return match.group(1)
    else:
        raise Exception('Unable to get latest Chromedriver version from {0}'
                        .format(CHROMEDRIVER_INFO_URL))


def install_chromedriver():
    plat = platform.platform().lower()
    if plat.startswith('darwin'):
        os_ = 'mac'
        architecture = 64
    elif plat.startswith('linux'):
        os_ = 'linux'
        architecture = platform.architecture()[0][:-3]
    elif plat.startswith('win'):
        os_ = 'win'
        architecture = 32
    else:
        raise Exception('Unsupported platform: {0}'.format(plat))

    # Download binary
    request = requests.get(CHROMEDRIVER_URL_TEMPLATE.format(version=get_latest_chromedriver_version(),
                                                            os_=os_,
                                                            architecture=architecture))

    path = get_chromedriver_path()

    # Unzip to resources
    zip_file = ZipFile(BytesIO(request.content))
    zip_file.extractall(os.path.dirname(path))

    # Set executable
    st = os.stat(path)
    os.chmod(path, st.st_mode | stat.S_IEXEC)
