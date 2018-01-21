import logging
import os
from gettext import gettext as _

from libs.log import decor_log_debug
from libs.net import write_unit, iface_down
from libs.systemd import systemctl
from libs.utils import remove
from vendor.parser.unit import Option
from .l_connector import ConnectorBase
from .l_net import ModuleStrategyNetBase
from .main import OptionsDHCP

logger = logging.getLogger(__name__)


class Connector(ConnectorBase):
    opti_: OptionsDHCP

    @decor_log_debug(logger, True)
    def on(self, root: str = '/'):
        self.base_on(root)

        file_unit = os.path.abspath(os.path.join(root, self.SYSTEMD_NETWORK_DIR,
                                                 self.UNIT_NETWORK_FILE.format(self.opti_.iface)))
        unit = self.base_gen_systemd_network()

        section = unit.get('Network')
        section.append(Option('DHCP', ['yes']))
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
    ID = 'net_dhcp'

    opti_: OptionsDHCP
    OptionsClass = OptionsDHCP
    _connector: Connector
    ConnectorClass = Connector

    @property
    def name(self) -> str:
        return _('DHCP')

    @ModuleStrategyNetBase.decor_can_not_perform
    def run(self) -> bool:
        code, value = self.dialog_dns()
        if code in self.my_dialog.ESC_CANCEL:
            return False

        self.opti_.dns = value or self.opti_.__class__.dns

        return super().run_all()
