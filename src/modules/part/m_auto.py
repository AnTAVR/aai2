import logging
from gettext import gettext as _
from typing import Tuple

from aai_framework.dial import ColorTxt
from aai_framework.interface import ModuleInterface
from .main import Vars, vars_

logger = logging.getLogger(__name__)


class Module(ModuleInterface):
    ID = 'part_auto'

    #
    # def __init__(self):
    #     super().__init__()
    #     self.conflicts.add(self)

    @property
    def vars_(self) -> Vars:
        return vars_

    @property
    def name(self) -> str:
        return _('Авто разметка и монтирование')

    @property
    def menu_item(self) -> Tuple[str, str]:
        text = [ColorTxt('(' + _('ВЫПОЛНЕНО') + ')').green.bold if self.is_run else '']

        return super().get_menu_item(text)
