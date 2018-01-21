import logging
from gettext import gettext as _
from typing import Tuple, Generator

from aai_framework.dial import ColorTxt
from vendor.partinfo.all import Device
from .l_mount import ModulePartMountBase
from .main import Options, vars_, POINT_SWAP_ID

logger = logging.getLogger(__name__)


class Module(ModulePartMountBase):
    ID = POINT_SWAP_ID

    @property
    def is_run(self) -> bool:
        return vars_.swap.is_mount

    def __init__(self):
        super().__init__()
        self.opti_ = Options(self.ID)
        self.conflicts.add(self)

    @property
    def name(self) -> str:
        return _('Раздел подкачки')

    @property
    def menu_item(self) -> Tuple[str, str]:
        text = [self.opti_.partition,
                ColorTxt('(' + _('ВЫПОЛНЕНО') + ')').green.bold if self.is_run else '']

        return super().get_menu_item(text)

    def _get_parts(self) -> Generator[Device, None, None]:
        for dev in Device.get_devices():  # type: Device
            if not dev.mountpoint and dev.id_fs_type and dev.parttype not in self.NO_PART and dev.swap:
                yield dev

    @ModulePartMountBase.decor_can_not_perform
    def run(self) -> bool:
        ret = super().run()
        if ret:
            vars_.swap = self.opti_
            vars_.swap.mount()
        return ret
