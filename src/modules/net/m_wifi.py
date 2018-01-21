import logging
from gettext import gettext as _

from .l_connector import ConnectorBase
from .l_net import ModuleStrategyBase
from .main import OptionsWIFI

logger = logging.getLogger(__name__)


# noinspection PyAbstractClass
class Connector(ConnectorBase):
    opti_: OptionsWIFI


class Module(ModuleStrategyBase):
    ID = 'net_wifi'

    opti_: OptionsWIFI
    OptionsClass = OptionsWIFI
    _connector: Connector
    ConnectorClass = Connector

    @property
    def name(self) -> str:
        return _('WIFI')
