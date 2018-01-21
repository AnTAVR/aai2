import logging
from gettext import gettext as _
from typing import Tuple

from aai_framework.interface import ModuleCollection, ModuleInterface
from .base.m_main import Module as ModuleBase
from .bootloader.m_main import Module as ModuleBootloader
from .donate.m_main import Module as ModuleDonate
from .main import vars_, Vars
from .net.m_main import Module as ModuleNet
from .part.m_main import Module as ModulePart
from .user.m_main import Module as ModuleUser

if not vars_.cmd_arg.mini:
    from .basedevel.m_main import Module as ModuleBasedevel
    from .baseplus.m_main import Module as ModuleBaseplus
    from .de.m_main import Module as ModuleDe
    from .pkgs.m_main import Module as ModulePkgs
    from .printrs.m_main import Module as ModulePrintrs
    from .webserver.m_main import Module as ModuleWebserver
    from .xorg.m_main import Module as ModuleXorg

logger = logging.getLogger(__name__)

module_net = ModuleNet()
module_part = ModulePart()
module_base = ModuleBase()
module_base.depends.add(module_net, module_part)
module_bootloader = ModuleBootloader()
module_bootloader.depends.add(module_base)
module_user = ModuleUser()
module_user.depends.add(module_base)
module_donate = ModuleDonate()

if not vars_.cmd_arg.mini:
    module_baseplus = ModuleBaseplus()
    module_baseplus.depends.add(module_base)
    module_basedevel = ModuleBasedevel()
    module_basedevel.depends.add(module_base)
    module_webserver = ModuleWebserver()
    module_webserver.depends.add(module_base)
    module_xorg = ModuleXorg()
    module_xorg.depends.add(module_base)
    module_de = ModuleDe()
    module_de.depends.add(module_xorg)
    module_printrs = ModulePrintrs()
    module_printrs.depends.add(module_de)
    module_pkgs = ModulePkgs()
    module_pkgs.depends.add(module_de)


class Module(ModuleInterface):
    ID = 'main'

    @property
    def vars_(self) -> Vars:
        return vars_

    def __init__(self):
        super().__init__()
        self.depends.add(module_net, module_part, module_base, module_bootloader, module_user)

    @property
    def name(self) -> str:
        return _('Инсталлятор Arch Linux')

    def dialog_menu(self, modules_: ModuleCollection, default: str) -> Tuple[str, str]:
        help_txt = []

        return self._dialog_menu(modules_.menu_items, default, help_txt, cancel_label=_('Выход'))

    def run(self):
        save_menu = ''

        modules_ = ModuleCollection()
        modules_.add(module_net, module_part, module_base)
        if not vars_.cmd_arg.mini:
            modules_.add(module_baseplus, module_basedevel)
        modules_.add(module_bootloader)
        if not vars_.cmd_arg.mini:
            modules_.add(module_xorg, module_de, module_printrs, module_pkgs, module_webserver)
        modules_.add(module_user, module_donate)

        while True:
            code, value = self.dialog_menu(modules_, save_menu)
            if code == self.my_dialog.OK:
                save_menu = value
                _module = modules_[save_menu]
                _module.run()
                continue

            if self.run_exit(modules_=modules_):
                break

    def dialog_exit(self) -> str:
        help_txt = [_('Подтвердите выход ПОВЕЛИТЕЛЬ...')]

        tmp = self.depends.txt
        if tmp is not None:
            help_txt += tmp
        help_txt = '\n'.join(help_txt)

        return self.my_dialog.yesno(help_txt, title=_('Выход'),
                                    defaultno=True, yes_label=_('Выполняй холоп!'))

    def run_exit(self, modules_: ModuleCollection = None, yes: bool = False) -> bool:
        if not yes:
            code = self.dialog_exit()

            if code != self.my_dialog.OK:
                return False

        # module_part.off()
        # module_net.off()

        tmp = _('Повинуюсь :(')
        logger.info(tmp)
        print(tmp)

        if logging.root.level == logging.DEBUG:
            if modules_ is None:
                modules_ = ()
            print(self.vars_)
            for _module in modules_:
                print(_module.vars_)

        return True
