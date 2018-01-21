import logging
import subprocess
from gettext import gettext as _
from typing import Tuple, List

from aai_framework.dial import ColorTxt
from aai_framework.interface import ModuleCollection, ModuleInterface
from libs.net import Iface, ping_cmd
from .l_net import ModuleStrategyBase
from .m_dhcp import Module as ModuleStrategyDHCP
from .m_pppoe import Module as ModuleStrategyPPPoE
from .m_static import Module as ModuleStrategySTATIC
from .m_vpn import Module as ModuleStrategyVPN
from .m_wifi import Module as ModuleStrategyWIFI
from .main import vars_, Vars

logger = logging.getLogger(__name__)


class Module(ModuleInterface):
    ID = 'net'

    @property
    def vars_(self) -> Vars:
        return vars_

    iface: str = None

    def __init__(self):
        super().__init__()
        self.conflicts.add(self)

    @property
    def is_run(self) -> bool:
        return self.vars_.is_ok

    @property
    def name(self) -> str:
        return _('Сеть')

    @property
    def menu_item(self) -> Tuple[str, str]:
        text = [ColorTxt('(' + _('ВЫПОЛНЕНО') + ')').green.bold if self.is_run else
                ColorTxt('(' + _('ОБЯЗАТЕЛЬНО!!!') + ')').red.bold]
        if not Iface.get_ifaces():
            text.append(ColorTxt(_('УСТРОЙСТВА НЕ НАЙДЕНЫ!!!')).red.bold)

        return super().get_menu_item(text)

    OK_ITEM_ID = 'ok'

    TEST_CONNECT_CMD = (
        ping_cmd('8.8.8.8'),
        ['curl', 'http://www.archlinux.org/check_network_status.txt'],
    )

    def dialog_test_connect(self, cmd: List[str]) -> subprocess.Popen:
        help_txt: List[str] = [_('Подождите...'),
                               '',
                               subprocess.list2cmdline(cmd)]
        help_txt: str = '\n'.join(help_txt)
        help_txt: str = ColorTxt(help_txt).green.bold

        t, p = self.my_dialog.progressbox_cmd(cmd, help_txt, title=self.name)
        return p

    def test_connect(self) -> bool:
        self.dialog_test_connect(self.TEST_CONNECT_CMD[0])
        p = self.dialog_test_connect(self.TEST_CONNECT_CMD[1])
        if p.returncode == 0:
            return True

        text_err: List[str] = [_('Нет подключения к сети!!!'),
                               '',
                               subprocess.list2cmdline(self.TEST_CONNECT_CMD[1]),
                               'returncode={}'.format(p.returncode),
                               ]

        text = '\n'.join(text_err)

        self._dialog_err(text)
        return False

    def dialog_iface(self, default: str) -> Tuple[str, str]:
        items = [(iface.name, 'mac={} brd={}'.format(iface.address, iface.broadcast))
                 for iface in Iface.get_ifaces()]
        items.insert(0, (self.OK_ITEM_ID, _('Уже подключено')))

        help_txt: List[str] = [_('Выберите сетевой адаптер')]

        return self._dialog_menu(items, default, help_txt, cancel_label=_('Главное меню'))

    @ModuleInterface.decor_can_not_perform
    def run(self) -> bool:
        save_menu = ''

        while True:
            code, value = self.dialog_iface(save_menu)
            if code != self.my_dialog.OK:
                return False

            save_menu = self.iface = value
            if value == self.OK_ITEM_ID:
                if self.test_connect():
                    self.vars_.connector = False
                    return True
            else:
                if self.run_type():
                    # @todo: тут подключается сеть
                    if self.test_connect():
                        return True
                    self.vars_.connector = None

            self.iface = None

    def dialog_type(self, modules_: ModuleCollection, default: str) -> Tuple[str, str]:
        help_txt = [_('Сетевой адаптер: {}').format(ColorTxt(self.iface).green.bold),
                    '',
                    _('Выберите тип подключения')]

        return self._dialog_menu(modules_.menu_items, default, help_txt, cancel_label=_('Назад'))

    def run_type(self) -> bool:
        save_menu = ''

        while True:
            modules_ = ModuleCollection()

            dhcp = ModuleStrategyDHCP(self.iface)
            static = ModuleStrategySTATIC(self.iface)
            pppoe = ModuleStrategyPPPoE()
            vpn = ModuleStrategyVPN()
            wifi = ModuleStrategyWIFI()
            # @todo: расставить зависимости
            modules_.add(dhcp, static, pppoe, vpn, wifi)

            code, value = self.dialog_type(modules_, save_menu)
            if code in self.my_dialog.ESC_CANCEL:
                return False

            save_menu = value
            _module: ModuleStrategyBase = modules_[save_menu]

            if _module.run():
                self.vars_.connector = False
                # noinspection PyUnresolvedReferences
                self.vars_.connector = _module.connector
                return True
