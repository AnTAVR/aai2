import logging
import subprocess
from io import StringIO
from typing import Generator, List

from libs.log import decor_log_debug
from libs.sizeconvert import SizeConvert

logger = logging.getLogger(__name__)

size_convert = SizeConvert()


def get_mem() -> int:
    ret = subprocess.run(['free', '-wb'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    ret.check_returncode()

    stdout: bytes = ret.stdout
    stdout = stdout.decode()

    stdout: Generator[List[str], None, None] = (x.strip().split() for x in StringIO(stdout))
    stdout = tuple(filter(lambda x: x[0] == 'Mem:', stdout))[0]
    return int(stdout[1])


# noinspection PyUnusedLocal
@decor_log_debug(logger)
def mount_dev(mountpoint: str, dev: str, options: str):
    # @todo: Нужно доделать
    pass


# noinspection PyUnusedLocal
@decor_log_debug(logger)
def umount_dev(mountpoint: str):
    # @todo: Нужно доделать
    pass


# noinspection PyUnusedLocal
@decor_log_debug(logger)
def fstab_dev(mountpoint: str, dev: str, options: str):
    # @todo: Нужно доделать
    pass


# noinspection PyUnusedLocal
@decor_log_debug(logger)
def ufstab_dev(mountpoint: str):
    # @todo: Нужно доделать
    pass


# noinspection PyUnusedLocal
@decor_log_debug(logger)
def mount_swapfile(swap_file: str, options: str, swap_size: str):
    # @todo: Нужно доделать
    pass


# noinspection PyUnusedLocal
@decor_log_debug(logger)
def umount_swapfile(swap_file: str):
    # @todo: Нужно доделать
    pass


# noinspection PyUnusedLocal
@decor_log_debug(logger)
def fstab_swapfile(swap_file: str, options: str):
    # @todo: Нужно доделать
    pass


# noinspection PyUnusedLocal
@decor_log_debug(logger)
def ufstab_swapfile(swap_file: str):
    # @todo: Нужно доделать
    pass
