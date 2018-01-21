import logging
from gettext import gettext as _

from .l_connector import ConnectorBase
from .l_net import ModuleStrategyBase
from .main import OptionsVPN

logger = logging.getLogger(__name__)


# noinspection PyAbstractClass
class Connector(ConnectorBase):
    opti_: OptionsVPN


class Module(ModuleStrategyBase):
    ID = 'net_vpn'

    opti_: OptionsVPN
    OptionsClass = OptionsVPN
    _connector: Connector
    ConnectorClass = Connector

    @property
    def name(self) -> str:
        return _('VPN')
