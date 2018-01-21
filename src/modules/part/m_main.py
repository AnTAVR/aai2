import logging
from gettext import gettext as _
from typing import Tuple

from aai_framework.dial import ColorTxt
from aai_framework.interface import ModuleCollection, ModuleInterface
from .m_auto import Module as ModulePartAuto
from .m_format import Module as ModulePartFormat
from .m_lvm import Module as ModulePartLvm
from .m_markup import Module as ModulePartMarkup
from .m_mount import Module as ModulePartMount
from .m_raid import Module as ModulePartRaid
from .main import vars_, Vars

logger = logging.getLogger(__name__)


class Module(ModuleInterface):
    ID = 'part'

    @property
    def vars_(self) -> Vars:
        return vars_

    @property
    def is_run(self) -> bool:
        return self.vars_.is_ok

    @property
    def name(self) -> str:
        return _('Разделы')

    @property
    def menu_item(self) -> Tuple[str, str]:
        text = [ColorTxt('(' + _('ВЫПОЛНЕНО') + ')').green.bold if self.is_run else
                ColorTxt('(' + _('ОБЯЗАТЕЛЬНО!!!') + ')').red.bold]

        return super().get_menu_item(text)

    def dialog_menu(self, modules_: ModuleCollection, default: str) -> Tuple[str, str]:
        return self._dialog_menu(modules_.menu_items, default, cancel_label=_('Главное меню'))

    @ModuleInterface.decor_can_not_perform
    def run(self) -> bool:
        save_menu = ''

        while True:
            modules_ = ModuleCollection()

            markup = ModulePartMarkup()

            mount_ = ModulePartMount()
            auto = ModulePartAuto()
            mount_.conflicts.add(auto)

            raid = ModulePartRaid()
            raid.conflicts.add(mount_, auto)
            lvm = ModulePartLvm()
            lvm.conflicts.add(mount_, auto)
            format_ = ModulePartFormat()

            modules_.add(markup, raid, lvm, format_, mount_, auto)

            code, value = self.dialog_menu(modules_, save_menu)
            if code in self.my_dialog.ESC_CANCEL:
                return False

            save_menu = value
            _module: ModuleInterface = modules_[save_menu]

            if _module.run():
                return True
