import logging
from typing import Optional

import modules.main
from aai_framework.utils import VarsRepr
from libs.part import mount_swapfile, mount_dev, umount_swapfile, umount_dev, fstab_swapfile, fstab_dev, \
    ufstab_swapfile, ufstab_dev

logger = logging.getLogger(__name__)

SWAP_FILE = '/swapfile'
POINT_ROOT_ID = '/'
POINT_BOOT_ID = '/boot'
POINT_EFI_ID = '/boot/efi'
POINT_HOME_ID = '/home'
POINT_SWAP_ID = 'none'
POINT_SWAP_FILE_ID = 'swapfile'


class OptionsBase(VarsRepr):
    is_swap_file: bool = False  # не менять, только для чтения!

    mount_point: str = None
    partition: str = None
    options: str = None
    is_mount: bool = False
    swap_size: str = '4000'

    @property
    def _repr__props(self) -> list:
        return ['mount_point', 'partition', 'options', 'is_mount', 'swap_size', 'is_swap_file', 'is_ok']

    def __init__(self, mount_point: str):
        self.mount_point = mount_point
        self.is_swap_file = mount_point == POINT_SWAP_FILE_ID

    def clear(self):
        # self.mount_point = self.__class__.mount_point
        self.partition = self.__class__.partition
        self.options = self.__class__.options
        self.is_mount = self.__class__.is_mount
        self.swap_size = self.__class__.swap_size

    @property
    def is_ok(self) -> bool:
        if self.is_swap_file:
            return not (None in (self.mount_point, self.partition, self.options, self.swap_size))
        else:
            return not (None in (self.mount_point, self.partition, self.options))


class Options(OptionsBase):
    def mount(self):
        if not self.is_mount:
            if self.is_swap_file:
                mount_swapfile(self.partition, self.options, self.swap_size)
            else:
                mount_dev(self.mount_point, self.partition, self.options)
            self.is_mount = True

    def umount(self):
        if self.is_mount:
            if self.is_swap_file:
                umount_swapfile(self.partition)
            else:
                umount_dev(self.partition)
            self.is_mount = False

    def to_fstab(self):
        if self.is_swap_file:
            fstab_swapfile(self.partition)
        else:
            fstab_dev(self.partition)

    def from_fstab(self):
        if self.is_swap_file:
            ufstab_swapfile(self.partition)
        else:
            ufstab_dev(self.partition)


class Vars(VarsRepr):
    root: Options = Options(POINT_ROOT_ID)
    boot: Options = Options(POINT_BOOT_ID)
    efi: Options = Options(POINT_EFI_ID)
    home: Options = Options(POINT_HOME_ID)
    swap: Options = Options(POINT_SWAP_ID)
    swap_file: Options = Options(POINT_SWAP_FILE_ID)

    __points = ('root', 'boot', 'efi', 'home', 'swap', 'swap_file',)

    @property
    def _repr__props(self) -> list:
        return ['root', 'boot', 'efi', 'home', 'swap', 'swap_file']

    def mount(self):
        for point in self.__points:
            options = self.__getattribute__(point)  # type: Optional[Options]
            options.mount()

    def umount(self):
        for point in reversed(self.__points):
            options = self.__getattribute__(point)  # type: Optional[Options]
            options.umount()

    def to_fstab(self):
        for point in self.__points:
            options = self.__getattribute__(point)  # type: Optional[Options]
            options.to_fstab()

    def from_fstab(self):
        for point in reversed(self.__points):
            options = self.__getattribute__(point)  # type: Optional[Options]
            options.from_fstab()

    @property
    def is_ok(self) -> bool:
        uefi = True
        root = self.root.is_mount

        if not modules.main.vars_.config.bios_sys:
            uefi = self.efi.is_mount

        return root and uefi


vars_ = Vars()
