import logging
from gettext import gettext as _

from aai_framework.interface import ModuleInterface
from .main import Vars, vars_

logger = logging.getLogger(__name__)


class Module(ModuleInterface):
    ID = 'part_raid'

    @property
    def vars_(self) -> Vars:
        return vars_

    @property
    def name(self) -> str:
        return _('RAID')
