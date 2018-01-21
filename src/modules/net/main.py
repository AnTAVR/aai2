import logging
from abc import abstractmethod

from aai_framework.utils import VarsRepr

logger = logging.getLogger(__name__)


class Options(VarsRepr):
    address: str = None
    ipv4: bool = True

    iface: str = None

    dns: str = None

    http_proxy: str = None
    https_proxy: str = None
    ftp_proxy: str = None

    @property
    def _repr__props(self) -> list:
        return ['iface', 'ipv4', 'dns', 'http_proxy', 'https_proxy', 'ftp_proxy']


class Connector(VarsRepr):
    UNIT_NETWORK_FILE = '{}.network'
    SYSTEMD_NETWORK_DIR = 'etc/systemd/network'

    opti_: Options = None

    @property
    def _repr__props(self) -> list:
        return ['opti_']

    def __init__(self, opti_: Options):
        self.opti_ = opti_

    @abstractmethod
    def on(self, root: str = '/'):
        pass

    @abstractmethod
    def off(self, root: str = '/'):
        pass


class OptionsDHCP(Options):
    pass


class OptionsSTATIC(OptionsDHCP):
    netmask: str = None
    broadcast: str = None
    gateway: str = None

    @property
    def _repr__props(self) -> list:
        return super()._repr__props + ['address', 'netmask', 'broadcast', 'gateway']


class OptionsPPPoE(Options):
    pass


class OptionsVPN(Options):
    pass


class OptionsWIFI(Options):
    pass


class Vars(VarsRepr):
    connector: Connector = None

    @property
    def _repr__props(self) -> list:
        return ['connector', 'is_ok']

    @property
    def is_ok(self) -> bool:
        return self.connector is not None


vars_ = Vars()
