import ipaddress
import logging
import os
from gettext import gettext as _
from typing import List, Tuple

from aai_framework.dial import ColorTxt
from libs.log import decor_log_debug
from libs.net import is_ipv4, is_ipv6, is_netmask_ipv4, is_netmask_ipv6, write_unit, iface_down
from libs.systemd import systemctl
from libs.utils import remove
from vendor.parser.unit import Option
from .l_connector import ConnectorBase
from .l_net import ModuleStrategyNetBase
from .main import OptionsSTATIC

logger = logging.getLogger(__name__)


# noinspection PyAbstractClass
class Connector(ConnectorBase):
    opti_: OptionsSTATIC

    @decor_log_debug(logger, True)
    def on(self, root: str = '/'):
        self.base_on(root)

        file_unit = os.path.abspath(os.path.join(root, self.SYSTEMD_NETWORK_DIR,
                                                 self.UNIT_NETWORK_FILE.format(self.opti_.iface)))
        unit = self.base_gen_systemd_network()

        section = unit.get('Network')
        section.append(
            Option('Address', [str(ipaddress.ip_interface('{}/{}'.format(self.opti_.address, self.opti_.netmask)))]))
        section.append(Option('Gateway', [self.opti_.gateway]))
        write_unit(unit, file_unit)

        if root == '/':
            systemctl('restart', 'systemd-networkd', root)
            self.dialog_configured()
        else:
            systemctl('enable', 'systemd-networkd', root)

    @decor_log_debug(logger, True)
    def off(self, root: str = '/'):
        self.base_off(root)

        if root == '/':
            systemctl('stop', 'systemd-networkd', root)
            iface_down(self.opti_.iface)
        else:
            systemctl('disable', 'systemd-networkd', root)

        file_unit = os.path.abspath(os.path.join(root, self.SYSTEMD_NETWORK_DIR,
                                                 self.UNIT_NETWORK_FILE.format(self.opti_.iface)))
        remove(file_unit)


class Module(ModuleStrategyNetBase):
    ID = 'net_static'

    opti_: OptionsSTATIC
    OptionsClass = OptionsSTATIC
    _connector: Connector
    ConnectorClass = Connector

    @property
    def name(self) -> str:
        return _('Статичный IP')

    def _head_txt(self, help_txt_new: List[str] = None, all_: bool = False) -> List[str]:
        tmp = [
            (_('IP адрес ({}): {}'), 'address', self.opti_.address, all_),
            (_('маска подсети ({}): {}'), 'netmask', self.opti_.netmask, all_),
            (_('широковещательный канал ({}): {}'), 'broadcast', self.opti_.broadcast, all_),
            (_('шлюз ({}): {}'), 'gateway', self.opti_.gateway, all_),
        ]
        help_txt = self.format_head_txt(tmp)

        if help_txt_new is not None:
            help_txt = help_txt_new + help_txt

        return super()._head_txt(help_txt, all_)

    def test_address(self, val: str) -> bool:
        if is_ipv4(val):
            self.opti_.ipv4 = True
            return True
        if is_ipv6(val):
            self.opti_.ipv4 = False
            return True

        text_err: str = _('Не правильный IP адрес ({})').format(val)

        self._dialog_err(text_err)
        return False

    def dialog_address(self) -> Tuple[str, str]:
        key = 'address'

        demo_text = 'формат: ipv4 192.168.0.2 ipv6 2002:C0A8:2::'
        demo_text = ColorTxt(demo_text).blue.bold

        default = '10.0.2.15'

        help_txt = self._head_txt()
        help_txt += ['', _('Введите IP адрес ({})').format(key),
                     demo_text]

        while True:
            code, value = self._dialog_inputbox(default, help_txt)  # type: str str
            if code in self.my_dialog.ESC_CANCEL:
                return code, value
            if self.test_address(value):
                return code, value
            default = value

    def test_netmask(self, val: str) -> bool:
        if is_netmask_ipv4(val) if self.opti_.ipv4 else is_netmask_ipv6(val):
            return True

        text_err: str = _('Не правильная маска подсети ({})').format(val)

        self._dialog_err(text_err)
        return False

    def dialog_netmask(self) -> Tuple[str, str]:
        key = 'netmask'

        demo_text = ''  # todo: Доделать выбор для ipv4 и ipv6!
        demo_text = ColorTxt(demo_text).blue.bold

        default = ''
        if self.opti_.ipv4:
            default = '255.255.255.0'
        else:
            pass  # todo: Доделать выбор для ipv6!

        help_txt = self._head_txt()
        help_txt += ['', _('Введите маску подсети ({})').format(key),
                     demo_text]

        while True:
            code, value = self._dialog_inputbox(default, help_txt)  # type: str str
            if code in self.my_dialog.ESC_CANCEL:
                return code, value
            if self.test_netmask(value):
                return code, value
            default = value

    def test_broadcast(self, val: str) -> bool:
        if is_ipv4(val) if self.opti_.ipv4 else is_ipv6(val):
            return True

        text_err: str = _('Не правильный широковещательный канал ({})').format(val)

        self._dialog_err(text_err)
        return False

    def dialog_broadcast(self) -> Tuple[str, str]:
        key = 'broadcast'

        demo_text = ''  # todo: Доделать выбор для ipv4 и ipv6!
        demo_text = ColorTxt(demo_text).blue.bold

        default = ''
        if self.opti_.address is not None:
            if self.opti_.ipv4:
                address = self.opti_.address.split('.')
                address[3] = '255'
                default = '.'.join(address)
            else:
                pass  # todo: Доделать выбор для ipv6!

        help_txt = self._head_txt()
        help_txt += ['', _('Введите широковещательный канал ({})').format(key),
                     demo_text]

        while True:
            code, value = self._dialog_inputbox(default, help_txt)  # type: str str
            if code in self.my_dialog.ESC_CANCEL:
                return code, value
            if self.test_broadcast(value):
                return code, value
            default = value

    def test_gateway(self, val: str) -> bool:
        if is_ipv4(val) if self.opti_.ipv4 else is_ipv6(val):
            return True

        text_err: str = _('Не правильный шлюз ({})').format(val)

        self._dialog_err(text_err)
        return False

    def dialog_gateway(self) -> Tuple[str, str]:
        key = 'gateway'

        demo_text = ''  # todo: Доделать выбор для ipv4 и ipv6!
        demo_text = ColorTxt(demo_text).blue.bold

        default = ''
        if self.opti_.address is not None:
            if self.opti_.ipv4:
                address = self.opti_.address.split('.')
                address[3] = '2'
                default = '.'.join(address)
            else:
                pass  # todo: Доделать выбор для ipv6!

        help_txt = self._head_txt()
        help_txt += ['', _('Введите шлюз ({})').format(key),
                     demo_text]

        while True:
            code, value = self._dialog_inputbox(default, help_txt)  # type: str str
            if code in self.my_dialog.ESC_CANCEL:
                return code, value
            if self.test_gateway(value):
                return code, value
            default = value

    @ModuleStrategyNetBase.decor_can_not_perform
    def run(self) -> bool:
        code, value = self.dialog_address()
        if code in self.my_dialog.ESC_CANCEL:
            return False
        self.opti_.address = value or self.opti_.__class__.address

        code, value = self.dialog_netmask()
        if code in self.my_dialog.ESC_CANCEL:
            return False
        self.opti_.netmask = value or self.opti_.__class__.netmask

        code, value = self.dialog_broadcast()
        if code in self.my_dialog.ESC_CANCEL:
            return False
        self.opti_.broadcast = value or self.opti_.__class__.broadcast

        code, value = self.dialog_gateway()
        if code in self.my_dialog.ESC_CANCEL:
            return False
        self.opti_.gateway = value or self.opti_.__class__.gateway

        code, value = self.dialog_dns(True)
        if code in self.my_dialog.ESC_CANCEL:
            return False
        self.opti_.dns = value or self.opti_.__class__.dns

        return super().run_all()
