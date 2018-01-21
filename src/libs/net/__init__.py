import ipaddress
import logging
import os
import platform
import subprocess
from typing import Union, List

from libs.log import decor_log_debug
from vendor.parser.unit import Unit

logger = logging.getLogger(__name__)


class Iface:
    _PARAMS = ('address', 'broadcast')

    _SYS_CLASS_NET = '/sys/class/net'
    _LOCAL_IFACES = ('lo',)

    name: str = None
    address: str = None
    broadcast: str = None

    def __init__(self, iface: str):
        self.name = iface
        self._params()

    def _params(self):
        path = os.path.join(self._SYS_CLASS_NET, self.name)

        for param in self._PARAMS:
            f_path = os.path.join(path, param)
            if not os.path.isdir(f_path):
                with open(f_path) as f:
                    lines = f.readlines()
                    if lines:
                        lines = tuple(map(str.strip, lines))
                        if len(lines) > 1:
                            pass
                        else:
                            lines = lines[0]
                    else:
                        lines = None

                    self.__dict__[param] = lines

    @classmethod
    def get_ifaces(cls, local: bool = False):
        ifaces = [x for x in os.listdir(cls._SYS_CLASS_NET)
                  if os.path.isdir(os.path.join(cls._SYS_CLASS_NET, x))]
        ifaces = sorted(ifaces)
        if not local:
            ifaces = [x for x in ifaces if x not in cls._LOCAL_IFACES]

        return tuple(cls(x) for x in ifaces)


def is_ipv4(text: str) -> bool:
    try:
        ipaddress.IPv4Address(text)
    except ipaddress.AddressValueError:
        pass
    else:
        return True
    return False


def is_ipv6(text: str) -> bool:
    try:
        ipaddress.IPv6Address(text)
    except ipaddress.AddressValueError:
        pass
    else:
        return True
    return False


def is_netmask_ipv4(text: str) -> bool:
    try:
        # noinspection PyProtectedMember
        ipaddress.IPv4Address._make_netmask(text)
    except ipaddress.NetmaskValueError:
        pass
    else:
        return True
    return False


def is_netmask_ipv6(text: str) -> bool:
    try:
        # noinspection PyProtectedMember
        ipaddress.IPv6Address._make_netmask(text)
    except ipaddress.NetmaskValueError:
        pass
    else:
        return True
    return False


def ping_cmd(host: str, n: int = 3) -> List[str]:
    return ['ping', '-n' if platform.system().lower() == 'windows' else '-c', str(n), host]


@decor_log_debug(logger)
def set_proxy(type_proxy: str, proxy: str = '', root: Union[str, bytes, os.PathLike] = '/'):
    """Функция устанавливает или удаляет прокси.

    :param type_proxy: http_proxy | https_proxy | ftp_proxy.
    :param proxy: если нет, то удаляется.
    :param root: путь к корню.
    """
    d_proxy = os.path.abspath(os.path.join(root, 'etc/profile.d'))

    f_proxy = os.path.join(d_proxy, '{}.sh'.format(type_proxy))

    if not proxy:
        try:
            del os.environ[type_proxy]
        except KeyError:
            pass
        try:
            os.remove(f_proxy)
        except FileNotFoundError:
            pass
    else:
        os.makedirs(d_proxy, exist_ok=True)
        os.environ[type_proxy] = proxy
        with open(f_proxy, 'w+') as f:
            f.writelines('export {}="{}"'.format(type_proxy, proxy))


@decor_log_debug(logger)
def iface_down(iface: str) -> subprocess.CompletedProcess:
    _command = ['ip', 'link', 'set', iface, 'down']
    return subprocess.run(_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


@decor_log_debug(logger)
def write_unit(unit: Unit, file_unit: Union[str, bytes, os.PathLike]):
    unit.write_file(file_unit)
