import logging
from gettext import gettext as _
from typing import Tuple

from aai_framework.dial import ColorTxt
from .l_mount import ModulePartMountBase
from .main import Options, vars_, POINT_ROOT_ID

logger = logging.getLogger(__name__)


class Module(ModulePartMountBase):
    ID = POINT_ROOT_ID

    @property
    def is_run(self) -> bool:
        return vars_.root.is_mount

    def __init__(self):
        super().__init__()
        self.opti_ = Options(self.ID)
        self.conflicts.add(self)

    @property
    def name(self) -> str:
        return _('Корневой раздел')

    @property
    def menu_item(self) -> Tuple[str, str]:
        text = [self.opti_.partition,
                ColorTxt('(' + _('ВЫПОЛНЕНО') + ')').green.bold if self.is_run else
                ColorTxt('(' + _('ОБЯЗАТЕЛЬНО!!!') + ')').red.bold]

        return super().get_menu_item(text)

    @ModulePartMountBase.decor_can_not_perform
    def run(self) -> bool:
        ret = super().run()
        if ret:
            vars_.root = self.opti_
            vars_.root.mount()
        return ret
