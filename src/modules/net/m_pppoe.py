import logging
from gettext import gettext as _

from .l_connector import ConnectorBase
from .l_net import ModuleStrategyBase
from .main import OptionsPPPoE

logger = logging.getLogger(__name__)


# noinspection PyAbstractClass
class Connector(ConnectorBase):
    opti_: OptionsPPPoE


class Module(ModuleStrategyBase):
    ID = 'net_pppoe'

    opti_: OptionsPPPoE
    OptionsClass = OptionsPPPoE
    _connector: Connector
    ConnectorClass = Connector

    @property
    def name(self) -> str:
        return _('PPPoE')
